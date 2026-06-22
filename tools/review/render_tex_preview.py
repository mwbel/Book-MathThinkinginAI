#!/usr/bin/env python3
"""Render a clean LaTeX chapter into a local Typora/Overleaf-style preview page."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import struct
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SECTION_RE = re.compile(
    r"^\\(?P<name>chapter|section|subsection|subsubsection|paragraph)\*?"
    r"(?:\[[^\]]*\])?\{(?P<title>.*)\}\s*$"
)
BEGIN_RE = re.compile(r"^\\begin\{(?P<env>[^}]+)\}(?:\[(?P<title>.*)\])?\s*$")
END_RE = re.compile(r"^\\end\{(?P<env>[^}]+)\}\s*$")
METADATA_RE = re.compile(r"^\s*%\s*!TEX\b", re.IGNORECASE)
COMMENT_RE = re.compile(r"^\s*%")
PDF_PREVIEW_DPI = 180


@dataclass
class RenderState:
    body: list[str] = field(default_factory=list)
    outline: list[dict[str, Any]] = field(default_factory=list)
    paragraph_lines: list[str] = field(default_factory=list)
    paragraph_start_line: int = 0
    math_lines: list[str] = field(default_factory=list)
    math_start_line: int = 0
    list_items: list[str] = field(default_factory=list)
    list_start_line: int = 0
    in_display_math: bool = False
    in_list: bool = False
    list_env: str = ""
    intro_title: str = ""
    intro_items: list[str] = field(default_factory=list)
    intro_start_line: int = 0
    in_intro: bool = False
    section_counter: int = 0
    anchor_prefix: str = "sec"
    chapter_label: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a clean LaTeX chapter into an HTML preview page.")
    parser.add_argument("--source", required=True, help="Clean revised .tex file to preview.")
    parser.add_argument("--original-source", default=None, help="Optional original .tex file for side-by-side preview.")
    parser.add_argument("--output", required=True, help="Output preview HTML path.")
    parser.add_argument("--title", default="校对稿渲染预览", help="Page title.")
    parser.add_argument(
        "--build-pdf-preview",
        action="store_true",
        help="Compile standalone PDFs with SyncTeX and render page PNGs for the side-by-side preview panes.",
    )
    parser.add_argument(
        "--tex-root",
        default=None,
        help="TeX project root containing elegantbook.cls. Defaults to the nearest parent of --source.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_path = Path(args.source).expanduser().resolve()
    original_path = Path(args.original_source).expanduser().resolve() if args.original_source else None
    output_path = Path(args.output).expanduser().resolve()

    if not source_path.exists():
        raise SystemExit(f"Source file not found: {source_path}")
    if source_path.suffix.lower() != ".tex":
        raise SystemExit(f"Source file must be a .tex file: {source_path}")
    if original_path:
        if not original_path.exists():
            raise SystemExit(f"Original source file not found: {original_path}")
        if original_path.suffix.lower() != ".tex":
            raise SystemExit(f"Original source file must be a .tex file: {original_path}")

    source_text = source_path.read_text(encoding="utf-8")
    original_text = original_path.read_text(encoding="utf-8") if original_path else ""
    chapter_label = infer_chapter_label(source_path)
    rendered = render_latex_preview(source_text, anchor_prefix="target", chapter_label=chapter_label)
    original_rendered = (
        render_latex_preview(original_text, anchor_prefix="original", chapter_label=chapter_label) if original_path else None
    )
    tex_root = resolve_tex_root(source_path, args.tex_root)
    sync_assets = (
        build_sync_pdf_assets(
            output_path=output_path,
            tex_root=tex_root,
            source_path=source_path,
            original_path=original_path,
        )
        if args.build_pdf_preview
        else {}
    )
    if args.build_pdf_preview:
        sync_assets["rebuild"] = {
            "sourcePath": str(source_path),
            "originalSourcePath": str(original_path) if original_path else "",
            "outputPath": str(output_path),
            "texRoot": str(tex_root),
            "title": args.title,
        }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_page(
            page_title=args.title,
            output_path=output_path,
            source_path=source_path,
            source_text=source_text,
            rendered_body=rendered["body"],
            outline=rendered["outline"],
            original_path=original_path,
            original_text=original_text,
            original_body=original_rendered["body"] if original_rendered else "",
            original_outline=original_rendered["outline"] if original_rendered else [],
            chapter_label=chapter_label,
            sync_assets=sync_assets,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")
    return 0


def render_latex_preview(source_text: str, anchor_prefix: str = "sec", chapter_label: str = "") -> dict[str, Any]:
    state = RenderState(anchor_prefix=anchor_prefix, chapter_label=chapter_label)
    lines = source_text.splitlines()

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()

        if state.in_list:
            end = END_RE.match(stripped)
            if end and end.group("env") == state.list_env:
                flush_list(state, line_no)
                continue
            if stripped.startswith(r"\item"):
                state.list_items.append(stripped[len(r"\item") :].strip())
            elif stripped:
                if state.list_items:
                    state.list_items[-1] += " " + stripped
                else:
                    state.list_items.append(stripped)
            continue

        if state.in_display_math:
            if stripped == r"\]":
                flush_display_math(state, line_no)
            else:
                state.math_lines.append(line)
            continue

        if state.in_intro:
            if END_RE.match(stripped):
                flush_intro(state, line_no)
                continue
            if stripped.startswith(r"\item"):
                state.intro_items.append(stripped[len(r"\item") :].strip())
            elif stripped:
                if state.intro_items:
                    state.intro_items[-1] += " " + stripped
                else:
                    state.intro_items.append(stripped)
            continue

        if not stripped:
            flush_paragraph(state, line_no - 1)
            continue

        if METADATA_RE.match(line) or COMMENT_RE.match(line):
            flush_paragraph(state, line_no - 1)
            continue

        section = SECTION_RE.match(stripped)
        if section:
            flush_paragraph(state, line_no - 1)
            append_section(state, section.group("name"), section.group("title"), line_no)
            continue

        begin = BEGIN_RE.match(stripped)
        if begin and begin.group("env") == "introduction":
            flush_paragraph(state, line_no - 1)
            state.in_intro = True
            state.intro_title = clean_inline_latex(begin.group("title") or "提示")
            state.intro_items = []
            state.intro_start_line = line_no
            continue
        if begin and begin.group("env") in {"itemize", "enumerate"}:
            flush_paragraph(state, line_no - 1)
            state.in_list = True
            state.list_env = begin.group("env")
            state.list_items = []
            state.list_start_line = line_no
            continue

        if stripped == r"\[":
            flush_paragraph(state, line_no - 1)
            state.in_display_math = True
            state.math_lines = []
            state.math_start_line = line_no
            continue

        if not state.paragraph_lines:
            state.paragraph_start_line = line_no
        state.paragraph_lines.append(line)

    last_line = len(lines)
    flush_paragraph(state, last_line)
    if state.in_display_math:
        flush_display_math(state, last_line)
    if state.in_intro:
        flush_intro(state, last_line)
    if state.in_list:
        flush_list(state, last_line)
    return {"body": "\n".join(state.body), "outline": state.outline}


def append_section(state: RenderState, command: str, title: str, line_no: int) -> None:
    level_map = {
        "chapter": 1,
        "section": 2,
        "subsection": 3,
        "subsubsection": 4,
        "paragraph": 5,
    }
    level = level_map[command]
    state.section_counter += 1
    anchor = f"{state.anchor_prefix}-sec-{state.section_counter}"
    clean_title = clean_inline_latex(title)
    state.outline.append({"level": level, "title": clean_title, "anchor": anchor})
    tag = f"h{min(level, 4)}"
    label = f'<span class="chapter-label">{escape(state.chapter_label)}</span>' if command == "chapter" and state.chapter_label else ""
    state.body.append(
        f'<{tag} id="{escape(anchor)}" class="latex-heading latex-{escape(command)}" '
        f'data-heading-level="{level}" {source_attrs(line_no)}>{label}{clean_title}</{tag}>'
    )


def infer_chapter_label(source_path: Path) -> str:
    match = re.match(r"^\D*(\d{1,3})(?=[\s._-]|$)", source_path.stem)
    if not match:
        return ""
    number = int(match.group(1))
    return f"第{to_chinese_number(number)}章"


def to_chinese_number(number: int) -> str:
    digits = "零一二三四五六七八九"
    if 0 <= number <= 10:
        return "十" if number == 10 else digits[number]
    if number < 20:
        return "十" + digits[number % 10]
    if number < 100:
        tens, ones = divmod(number, 10)
        return digits[tens] + "十" + (digits[ones] if ones else "")
    return str(number)


def flush_paragraph(state: RenderState, end_line: int) -> None:
    if not state.paragraph_lines:
        return
    text = "\n".join(line.rstrip() for line in state.paragraph_lines).strip()
    state.paragraph_lines = []
    if not text:
        return
    html_text = render_inline_latex(text)
    html_text = html_text.replace("\n", "<br>")
    state.body.append(f"<p {source_attrs(state.paragraph_start_line, end_line)}>{html_text}</p>")
    state.paragraph_start_line = 0


def flush_intro(state: RenderState, end_line: int) -> None:
    items = "\n".join(f"<li>{render_inline_latex(item)}</li>" for item in state.intro_items)
    state.body.append(
        f"""<section class="intro-box" {source_attrs(state.intro_start_line, end_line)}>
  <div class="intro-title">{escape(state.intro_title)}</div>
  <ul>{items}</ul>
</section>"""
    )
    state.in_intro = False
    state.intro_title = ""
    state.intro_items = []
    state.intro_start_line = 0


def flush_list(state: RenderState, end_line: int) -> None:
    tag = "ol" if state.list_env == "enumerate" else "ul"
    items = "\n".join(f"<li>{render_inline_latex(item)}</li>" for item in state.list_items)
    state.body.append(f'<{tag} class="latex-list" {source_attrs(state.list_start_line, end_line)}>{items}</{tag}>')
    state.in_list = False
    state.list_env = ""
    state.list_items = []
    state.list_start_line = 0


def flush_display_math(state: RenderState, end_line: int) -> None:
    formula = "\n".join(line.strip() for line in state.math_lines).strip()
    state.body.append(f'<pre class="formula" {source_attrs(state.math_start_line, end_line)}><code>{escape(formula)}</code></pre>')
    state.math_lines = []
    state.in_display_math = False
    state.math_start_line = 0


def source_attrs(start_line: int, end_line: int | None = None) -> str:
    if start_line <= 0:
        return ""
    resolved_end = end_line if end_line and end_line >= start_line else start_line
    return f'data-source-line="{start_line}" data-source-end-line="{resolved_end}"'


def render_inline_latex(text: str) -> str:
    rendered = escape(text)
    rendered = replace_balanced_command(rendered, "textbf", "strong")
    rendered = replace_balanced_command(rendered, "emph", "em")
    rendered = replace_balanced_command(rendered, "text", "span")
    rendered = re.sub(r"\$([^$]+)\$", r'<span class="inline-math">$\1$</span>', rendered)
    rendered = rendered.replace(r"\ldots", "…")
    rendered = rendered.replace(r"\;", " ")
    rendered = re.sub(r"\\fa[A-Za-z]+", "", rendered)
    return rendered


def clean_inline_latex(text: str) -> str:
    cleaned = render_inline_latex(text)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = html.unescape(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return escape(cleaned)


def replace_balanced_command(text: str, command: str, tag: str) -> str:
    pattern = re.compile(rf"\\{command}\{{([^{{}}]*)\}}")
    while True:
        updated = pattern.sub(rf"<{tag}>\1</{tag}>", text)
        if updated == text:
            return text
        text = updated


def render_page(
    page_title: str,
    output_path: Path,
    source_path: Path,
    source_text: str,
    rendered_body: str,
    outline: list[dict[str, Any]],
    original_path: Path | None,
    original_text: str,
    original_body: str,
    original_outline: list[dict[str, Any]],
    chapter_label: str,
    sync_assets: dict[str, Any] | None = None,
) -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    outline_html = render_outline(outline)
    original_article = original_body or '<p class="muted">未提供原文。</p>'
    original_label = original_path.name if original_path else "未提供原文"
    sync_assets = sync_assets or {}
    payload = json.dumps(
        {
            "generatedAt": generated_at,
            "syncTex": sync_assets,
            "chapterPicker": {
                "currentSourcePath": str(source_path),
                "currentOriginalPath": str(original_path) if original_path else "",
                "currentRenderPath": output_path.name,
            },
            "chaptersDir": str(sync_assets.get("chaptersDir", "")),
        },
        ensure_ascii=False,
    ).replace("</", "<\\/")
    original_sync = sync_assets.get("variants", {}).get("original")
    target_sync = sync_assets.get("variants", {}).get("target")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(page_title)}</title>
  <style>
{CSS}
  </style>
</head>
<body>
  <header class="topbar">
    <div>
      <p class="eyebrow">校对稿渲染预览</p>
      <h1>{escape(page_title)}</h1>
      <p class="file-line">原文：{escape(original_label)}</p>
      <p class="file-line">修改稿：{escape(source_path.name)} · {escape(generated_at)}</p>
    </div>
    <div class="top-actions">
      <div class="mode-switch" aria-label="视图模式">
        <button type="button" class="is-active" data-mode="read">Typora 阅读</button>
        <button type="button" data-mode="dual">双栏对照</button>
        <button type="button" data-mode="quad">四栏校对</button>
      </div>
      <div class="chapter-picker" data-chapter-picker>
        <label class="picker-field picker-field-wide">
          <span>章节文件夹</span>
          <input type="text" data-chapters-dir placeholder="/路径/到/chapters" value="{escape(sync_assets.get("chaptersDir", ""))}">
        </label>
        <button type="button" class="picker-button" data-import-chapters>导入文件夹</button>
        <label class="picker-field">
          <span>章节</span>
          <select data-chapter-select>
            <option value="">正在读取章节...</option>
          </select>
        </label>
        <label class="picker-field">
          <span>原文版本</span>
          <select data-original-select disabled>
            <option value="">请先选择章节</option>
          </select>
        </label>
        <label class="picker-field">
          <span>修改稿版本</span>
          <select data-target-select disabled>
            <option value="">请先选择章节</option>
          </select>
        </label>
        <button type="button" class="picker-button" data-open-chapter disabled>打开章节</button>
        <p class="chapter-picker-state" data-chapter-picker-status>通过本地 HTTP 服务可切换到任意章节。</p>
      </div>
      <div class="compile-controls">
        <button type="button" class="compile-button" data-rebuild-preview>重新编译 PDF</button>
        <p class="compile-state" data-compile-status>PDF 对应最近一次编译结果</p>
      </div>
    </div>
  </header>

  <main class="workspace is-read" data-workspace data-chapter-label="{escape(chapter_label)}">
    <aside class="outline">
      <div class="outline-head">
        <div class="outline-title">目录</div>
        <button type="button" class="collapse-button" data-toggle-outline>收起</button>
      </div>
      <nav class="outline-body">
        {outline_html}
      </nav>
    </aside>
    <section class="view-panel read-view" data-view="read">
      <article class="article target-read-article">
        {rendered_body}
      </article>
    </section>

    <section class="view-panel dual-view" data-view="dual">
      <div class="two-column-grid">
        {render_render_panel("原文渲染", original_article, "original", original_sync)}
        {render_render_panel("修改稿渲染", rendered_body, "target", target_sync)}
      </div>
    </section>

    <section class="view-panel quad-view" data-view="quad">
      <div class="quad-grid">
        {render_source_panel("原文源码", original_text or "未提供原文。", "original")}
        {render_render_panel("原文渲染", original_article, "original", original_sync)}
        {render_source_panel("修改稿源码", source_text, "target")}
        {render_render_panel("修改稿渲染", rendered_body, "target", target_sync)}
      </div>
    </section>
  </main>
  <script id="preview-data" type="application/json">{payload}</script>
  <script>
{JS}
  </script>
</body>
</html>
"""


def render_render_panel(title: str, body: str, variant: str, sync_asset: dict[str, Any] | None = None) -> str:
    reader = render_sync_pdf_reader(sync_asset, variant) if sync_asset else render_html_reader(body, variant)
    return f"""<section class="compare-pane render-pane is-{escape(variant)}">
  <div class="pane-title"><span>{escape(title)}</span><button type="button" class="collapse-button" data-toggle-pane>收起</button></div>
  {reader}
</section>"""


def render_html_reader(body: str, variant: str) -> str:
    return f"""<div class="page-reader html-page-reader" data-page-reader="{escape(variant)}">
    <article class="article article-compact" data-render-content>{body}</article>
  </div>"""


def render_sync_pdf_reader(sync_asset: dict[str, Any], variant: str) -> str:
    pages_html = []
    for page in sync_asset.get("pages", []):
        pages_html.append(
            f"""<figure class="real-pdf-page" data-pdf-page="{int(page["page"])}">
      <img
        class="pdf-page-image"
        data-src="{escape(page["imageUrl"])}"
        loading="lazy"
        decoding="async"
        width="{int(page["imageWidth"])}"
        height="{int(page["imageHeight"])}"
        alt="{escape(variant)} PDF page {int(page["page"])}">
      <figcaption>{int(page["page"])} / {int(sync_asset.get("pageCount", 0))}</figcaption>
    </figure>"""
        )
    if not pages_html:
        pages_html.append('<p class="muted">PDF 预览未生成。</p>')
    return f"""<div class="pdf-reader-shell" data-pdf-shell="{escape(variant)}">
    <div class="pdf-toolbar" data-pdf-toolbar="{escape(variant)}">
      <button type="button" data-pdf-prev>上一页</button>
      <span class="pdf-page-state"><span data-current-page>1</span> / {int(sync_asset.get("pageCount", 0))}</span>
      <button type="button" data-pdf-next>下一页</button>
      <span class="pdf-toolbar-separator"></span>
      <button type="button" data-pdf-zoom-out>缩小</button>
      <span class="pdf-zoom-state" data-pdf-zoom-state>100%</span>
      <button type="button" data-pdf-zoom-in>放大</button>
    </div>
    <div class="synctex-status" data-synctex-status="{escape(variant)}">真实 PDF 预览 · 右键点击页面可跳转源码行</div>
    <div
    class="page-reader real-pdf-reader"
    data-page-reader="{escape(variant)}"
    data-synctex-reader="{escape(variant)}"
    data-pdf-path="{escape(sync_asset.get("pdfPath", ""))}"
    data-source-path="{escape(sync_asset.get("sourcePath", ""))}"
    data-page-width-pt="{escape(sync_asset.get("pageWidthPt", ""))}"
    data-page-height-pt="{escape(sync_asset.get("pageHeightPt", ""))}">
    {"".join(pages_html)}
  </div>
  </div>"""


def render_source_panel(title: str, source_text: str, variant: str) -> str:
    return f"""<section class="compare-pane source-pane is-{escape(variant)}">
  <div class="pane-title"><span>{escape(title)}<small data-source-state="{escape(variant)}">可临时编辑；SyncTeX 对应最近一次编译的 PDF</small></span><button type="button" class="collapse-button" data-toggle-pane>收起</button></div>
  <div class="source-workbench">
    <div class="source-gutter" data-source-gutter="{escape(variant)}" aria-hidden="true"></div>
    <textarea class="source-editor" data-source-editor="{escape(variant)}" spellcheck="false" wrap="off">{escape(source_text)}</textarea>
  </div>
</section>"""


def render_outline(outline: list[dict[str, Any]]) -> str:
    if not outline:
        return '<p class="muted">暂无目录</p>'
    links = []
    for item in outline:
        level = min(max(int(item["level"]), 1), 5)
        indent = max(level - 1, 0)
        links.append(
            f'<a class="outline-link indent-{indent}" href="#{escape(item["anchor"])}">'
            f'{item["title"]}</a>'
        )
    return "\n".join(links)


def resolve_tex_root(source_path: Path, explicit_root: str | None) -> Path:
    if explicit_root:
        tex_root = Path(explicit_root).expanduser().resolve()
        if not (tex_root / "elegantbook.cls").exists():
            raise SystemExit(f"TeX root does not contain elegantbook.cls: {tex_root}")
        return tex_root

    for candidate in [source_path.parent, *source_path.parents]:
        if (candidate / "elegantbook.cls").exists():
            return candidate
    raise SystemExit(
        "Unable to infer TeX root. Pass --tex-root with the directory containing elegantbook.cls."
    )


def build_sync_pdf_assets(
    output_path: Path,
    tex_root: Path,
    source_path: Path,
    original_path: Path | None,
) -> dict[str, Any]:
    asset_root = output_path.parent / f"{output_path.stem}-assets"
    variants: list[tuple[str, Path | None]] = [("target", source_path), ("original", original_path)]
    assets: dict[str, Any] = {
        "enabled": True,
        "assetRoot": str(asset_root),
        "apiBase": "",
        "variants": {},
    }

    for variant, path in variants:
        if path is None:
            continue
        assets["variants"][variant] = build_one_sync_pdf_asset(
            variant=variant,
            source_path=path,
            output_path=output_path,
            asset_root=asset_root,
            tex_root=tex_root,
        )
    return assets


def build_one_sync_pdf_asset(
    variant: str,
    source_path: Path,
    output_path: Path,
    asset_root: Path,
    tex_root: Path,
) -> dict[str, Any]:
    try:
        source_input = source_path.relative_to(tex_root).as_posix()
    except ValueError as exc:
        raise SystemExit(f"Source file must be inside TeX root for SyncTeX preview: {source_path}") from exc

    variant_dir = asset_root / variant
    if variant_dir.exists():
        shutil.rmtree(variant_dir)
    png_dir = variant_dir / "png"
    png_dir.mkdir(parents=True, exist_ok=True)

    main_tex = variant_dir / f"preview-{variant}.tex"
    main_tex.write_text(standalone_tex(source_input), encoding="utf-8")

    command = [
        "latexmk",
        "-g",
        "-xelatex",
        "-synctex=1",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-outdir={variant_dir}",
        str(main_tex),
    ]
    subprocess.run(command, cwd=tex_root, check=True)

    pdf_path = variant_dir / f"preview-{variant}.pdf"
    synctex_path = variant_dir / f"preview-{variant}.synctex.gz"
    if not pdf_path.exists():
        raise SystemExit(f"PDF preview was not created: {pdf_path}")
    if not synctex_path.exists():
        raise SystemExit(f"SyncTeX file was not created: {synctex_path}")

    page_count, page_width_pt, page_height_pt = read_pdf_info(pdf_path)
    subprocess.run(
        ["pdftoppm", "-r", str(PDF_PREVIEW_DPI), "-png", str(pdf_path), str(png_dir / "page")],
        check=True,
    )
    image_paths = sorted(png_dir.glob("page-*.png"), key=page_number_from_png)
    if len(image_paths) != page_count:
        raise SystemExit(f"Expected {page_count} rendered PNG pages, got {len(image_paths)} in {png_dir}")

    pages = []
    for image_path in image_paths:
        image_width, image_height = read_png_size(image_path)
        page_number = page_number_from_png(image_path)
        pages.append(
            {
                "page": page_number,
                "imageUrl": relative_url(image_path, output_path.parent),
                "imageWidth": image_width,
                "imageHeight": image_height,
            }
        )

    manifest = {
        "variant": variant,
        "sourcePath": str(source_path),
        "sourceInput": source_input,
        "pdfPath": str(pdf_path),
        "pdfUrl": relative_url(pdf_path, output_path.parent),
        "synctexPath": str(synctex_path),
        "pageCount": page_count,
        "pageWidthPt": page_width_pt,
        "pageHeightPt": page_height_pt,
        "pages": pages,
    }
    (variant_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def standalone_tex(source_input: str) -> str:
    return f"""\\documentclass[lang=cn,scheme=chinese,12pt]{{elegantbook}}

\\usepackage{{fontawesome5}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{xurl}}
\\usepackage{{microtype}}

\\title{{人工智能的数学思维}}
\\institute{{华东师范大学 软件工程学院}}
\\date{{2024}}

\\begin{{document}}

\\mainmatter
\\input{{{source_input}}}

\\end{{document}}
"""


def read_pdf_info(pdf_path: Path) -> tuple[int, float, float]:
    result = subprocess.run(["pdfinfo", str(pdf_path)], check=True, capture_output=True, text=True)
    page_count = 0
    width = 0.0
    height = 0.0
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            page_count = int(line.split(":", 1)[1].strip())
        elif line.startswith("Page size:"):
            match = re.search(r"([0-9.]+)\s+x\s+([0-9.]+)\s+pts", line)
            if match:
                width = float(match.group(1))
                height = float(match.group(2))
    if page_count <= 0 or width <= 0 or height <= 0:
        raise SystemExit(f"Unable to read PDF page metadata: {pdf_path}")
    return page_count, width, height


def read_png_size(image_path: Path) -> tuple[int, int]:
    with image_path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"Not a PNG file: {image_path}")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def page_number_from_png(image_path: Path) -> int:
    match = re.search(r"-(\d+)\.png$", image_path.name)
    return int(match.group(1)) if match else 0


def relative_url(path: Path, base_dir: Path) -> str:
    try:
        return path.relative_to(base_dir).as_posix()
    except ValueError:
        return path.as_posix()


def render_source_lines(source_text: str) -> str:
    rows = []
    for index, line in enumerate(source_text.splitlines(), start=1):
        rows.append(
            f'<span class="source-row"><span class="line-no">{index}</span>'
            f'<code>{escape(line) or " "}</code></span>'
        )
    return "\n".join(rows)


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


CSS = r"""
:root {
  --bg: #f5f1e9;
  --panel: #fffdf8;
  --paper: #fffaf2;
  --ink: #1f2937;
  --muted: #667085;
  --line: #e2d7c7;
  --accent: #8a5a12;
  --eb-structure: #3c71b7;
  --eb-main: #00a652;
  --eb-second: #ff8618;
  --eb-third: #00aef7;
  --eb-paper: #fffefb;
  --eb-ink: #252525;
  --eb-rule: rgba(60, 113, 183, 0.34);
  --source-bg: #1f2933;
  --source-ink: #e8edf3;
  --reader-height: calc(100vh - 214px);
  --page-height: 760px;
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  line-height: 1.78;
}

.topbar {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 22px;
  padding: 22px 30px;
  background: #27211a;
  color: #fffaf0;
}

.eyebrow,
.file-line {
  margin: 0;
  color: #eadfcb;
  font-size: 13px;
}

h1 {
  margin: 4px 0 4px;
  font-size: 26px;
  letter-spacing: 0;
}

.top-actions {
  display: grid;
  justify-items: end;
  gap: 10px;
}

.mode-switch {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chapter-picker {
  display: grid;
  grid-template-columns: minmax(180px, 240px) minmax(140px, 180px) minmax(140px, 180px) auto;
  gap: 10px 12px;
  align-items: end;
}

.picker-field {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.picker-field span {
  color: #eadfcb;
  font-size: 12px;
}

.picker-field select {
  min-width: 0;
  min-height: 36px;
  padding: 6px 12px;
  border: 1px solid rgba(255, 250, 240, 0.28);
  border-radius: 10px;
  background: rgba(255, 250, 240, 0.08);
  color: #fffaf0;
  font: inherit;
}

.picker-field select:disabled {
  opacity: 0.58;
  cursor: not-allowed;
}

.picker-button {
  min-height: 36px;
  border-color: rgba(255, 250, 240, 0.48);
  background: rgba(255, 250, 240, 0.12);
}

.picker-button:disabled {
  opacity: 0.58;
  cursor: not-allowed;
}

.chapter-picker-state {
  grid-column: 1 / -1;
  margin: -2px 0 0;
  color: #eadfcb;
  font-size: 12px;
  line-height: 1.35;
  text-align: right;
}

.chapter-picker-state.is-error {
  color: #ffb4a8;
}

.chapter-picker-state.is-ok {
  color: #d6f5cf;
}

.compile-controls {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

.compile-button {
  border-color: rgba(255, 250, 240, 0.48);
  background: rgba(255, 250, 240, 0.08);
}

.compile-state {
  max-width: 360px;
  margin: 0;
  color: #eadfcb;
  font-size: 12px;
  line-height: 1.35;
  text-align: right;
}

.compile-state.is-dirty {
  color: #ffd98a;
}

.compile-state.is-error {
  color: #ffb4a8;
}

.compile-state.is-ok {
  color: #d6f5cf;
}

button {
  min-height: 34px;
  padding: 7px 12px;
  border: 1px solid rgba(255, 255, 255, 0.24);
  border-radius: 999px;
  background: transparent;
  color: #fffaf0;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
}

button.is-active,
button:hover {
  background: #fffaf0;
  color: #2d2418;
}

.workspace {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  min-height: calc(100vh - 112px);
}

.workspace.is-outline-collapsed {
  grid-template-columns: 58px minmax(0, 1fr);
}

.view-panel {
  display: none;
  min-width: 0;
  padding: 32px 28px 60px;
}

.workspace.is-read .read-view,
.workspace.is-dual .dual-view,
.workspace.is-quad .quad-view {
  display: block;
}

.outline {
  position: sticky;
  top: 0;
  align-self: start;
  max-height: 100vh;
  overflow: auto;
  padding: 22px 18px;
  border-right: 1px solid var(--line);
}

.workspace.is-outline-collapsed .outline {
  padding: 18px 8px;
  overflow: hidden;
}

.outline-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 10px;
}

.outline-title {
  color: var(--accent);
  font-weight: 800;
}

.workspace.is-outline-collapsed .outline-head {
  display: block;
  text-align: center;
}

.workspace.is-outline-collapsed .outline-title {
  writing-mode: vertical-rl;
  margin: 0 auto 10px;
}

.workspace.is-outline-collapsed .outline-body {
  display: none;
}

.workspace.is-outline-collapsed .outline .collapse-button {
  min-width: 38px;
  padding: 6px 4px;
}

.collapse-button {
  min-height: 28px;
  padding: 4px 8px;
  border-color: var(--line);
  background: #fffaf1;
  color: #5c3f12;
  font-size: 12px;
}

.outline-link {
  display: block;
  padding: 7px 8px;
  border-radius: 6px;
  color: #3b3124;
  text-decoration: none;
  font-size: 14px;
}

.outline-link:hover {
  background: #ebe1d0;
}

.indent-1 { padding-left: 18px; }
.indent-2 { padding-left: 30px; }
.indent-3 { padding-left: 42px; }
.indent-4 { padding-left: 54px; }

.article {
  max-width: 820px;
  margin: 0 auto;
  padding: 42px 54px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
  box-shadow: 0 18px 42px rgba(68, 49, 24, 0.08);
}

.article-compact {
  max-width: none;
  height: 100%;
  margin: 0;
  padding: 24px 26px;
  box-shadow: none;
}

.article h1,
.article h2,
.article h3,
.article h4 {
  color: #2b241a;
  line-height: 1.35;
}

.chapter-label {
  display: block;
  margin-bottom: 8px;
  color: var(--eb-structure);
  font-size: 0.56em;
  font-weight: 800;
  letter-spacing: 0;
}

.article h1 {
  margin: 0 0 28px;
  font-size: 32px;
}

.article h2 {
  margin: 34px 0 14px;
  padding-top: 8px;
  border-top: 1px solid var(--line);
  font-size: 24px;
}

.article h3 {
  margin: 24px 0 10px;
  font-size: 19px;
}

.article p {
  margin: 12px 0;
  font-size: 16px;
}

.article em {
  color: #7a4e12;
  font-style: normal;
}

.article strong {
  color: #3b3124;
}

.intro-box {
  margin: 18px 0;
  padding: 16px 20px;
  border: 1px solid #e3c784;
  border-left: 4px solid var(--accent);
  border-radius: 8px;
  background: #fff9e8;
}

.intro-title {
  margin-bottom: 8px;
  color: var(--accent);
  font-weight: 800;
}

.intro-box ul {
  margin: 0;
  padding-left: 20px;
}

.intro-box li {
  margin: 5px 0;
}

.latex-list {
  margin: 12px 0;
  padding-left: 24px;
}

.latex-list li {
  margin: 6px 0;
}

.formula {
  margin: 18px 0;
  padding: 16px 18px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fbf7ef;
  overflow: auto;
  text-align: center;
  font-family: "Times New Roman", "STIX Two Text", serif;
  font-size: 17px;
  line-height: 1.7;
}

.inline-math {
  padding: 0 2px;
  color: #6b3f08;
  font-family: "Times New Roman", serif;
}

.two-column-grid,
.quad-grid {
  display: grid;
  gap: 14px;
  align-items: stretch;
  grid-auto-columns: minmax(0, 1fr);
}

.two-column-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.quad-grid {
  grid-template-columns: repeat(4, minmax(260px, 1fr));
}

.two-column-grid:has(.compare-pane.is-collapsed),
.quad-grid:has(.compare-pane.is-collapsed) {
  grid-template-columns: repeat(auto-fit, minmax(54px, 1fr));
}

.compare-pane {
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  background: var(--panel);
}

.compare-pane.is-collapsed {
  width: 54px;
  min-width: 54px;
}

.compare-pane.is-collapsed .article,
.compare-pane.is-collapsed .source-editor,
.compare-pane.is-collapsed .source-workbench {
  display: none;
}

.compare-pane.is-collapsed .page-reader {
  display: none;
}

.compare-pane.is-collapsed .pane-title {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
  height: 100%;
  min-height: 260px;
  padding: 8px 6px 12px;
  writing-mode: horizontal-tb;
  text-align: center;
}

.compare-pane.is-collapsed .pane-title span {
  writing-mode: vertical-rl;
}

.compare-pane.is-collapsed .pane-title .collapse-button {
  order: -1;
  writing-mode: horizontal-tb;
  margin: 0;
  padding: 4px;
}

.source-pane {
  background: var(--source-bg);
  color: var(--source-ink);
}

.pane-title {
  position: sticky;
  top: 0;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--line);
  background: #fff7e8;
  color: var(--accent);
  font-weight: 800;
}

.pane-title small {
  display: block;
  margin-top: 2px;
  color: var(--muted);
  font-size: 11px;
  font-weight: 500;
}

.source-pane .pane-title small {
  color: #9fb3c8;
}

.source-pane .pane-title {
  border-bottom-color: rgba(255, 255, 255, 0.12);
  background: #17202a;
  color: #d7b56d;
}

.source-pane.is-source-jump {
  box-shadow: 0 0 0 3px rgba(60, 113, 183, 0.42), 0 0 24px rgba(60, 113, 183, 0.36);
}

.source-pane.is-source-jump .pane-title {
  background: #203a5f;
  color: #f8d88a;
}

.source-workbench {
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr);
  width: 100%;
  height: var(--reader-height);
  min-height: 560px;
  overflow: hidden;
  background: var(--source-bg);
}

.source-gutter {
  height: 100%;
  padding: 18px 8px 28px 0;
  overflow: hidden;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  background: #18222d;
  color: #77889a;
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 13px;
  line-height: 1.7;
  text-align: right;
  user-select: none;
}

.source-gutter-line {
  height: 22.1px;
  padding-right: 6px;
  border-right: 2px solid transparent;
}

.source-gutter-line.is-line-hit {
  border-right-color: #f8d88a;
  background: rgba(248, 216, 138, 0.12);
  color: #f8d88a;
  font-weight: 700;
}

.source-editor {
  display: block;
  width: 100%;
  height: 100%;
  min-height: 0;
  margin: 0;
  padding: 18px 16px 28px;
  border: 0;
  outline: 0;
  resize: none;
  overflow: auto;
  background: var(--source-bg);
  color: var(--source-ink);
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 13px;
  line-height: 1.7;
  white-space: pre;
  overflow-wrap: normal;
}

.page-reader {
  height: var(--reader-height);
  min-height: 560px;
  padding: 18px 14px 24px;
  overflow: auto;
  background:
    linear-gradient(90deg, rgba(60, 113, 183, 0.05), transparent 28%, transparent 72%, rgba(60, 113, 183, 0.05)),
    #ded8cf;
}

.pdf-reader-shell {
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr);
  height: var(--reader-height);
  min-height: 560px;
  padding: 18px 18px 28px;
  overflow: hidden;
  background:
    linear-gradient(90deg, rgba(60, 113, 183, 0.05), transparent 28%, transparent 72%, rgba(60, 113, 183, 0.05)),
    #ded8cf;
}

.real-pdf-reader {
  height: 100%;
  min-height: 0;
  padding: 0 0 4px;
}

.pdf-toolbar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: min(100%, 540px);
  margin: 0 auto 8px;
  padding: 7px 8px;
  border: 1px solid rgba(60, 113, 183, 0.18);
  border-radius: 6px;
  background: rgba(255, 253, 248, 0.985);
  color: #44546a;
  font-size: 12px;
  line-height: 1.2;
}

.pdf-toolbar button {
  min-height: 26px;
  padding: 3px 8px;
  border-color: rgba(60, 113, 183, 0.24);
  background: #ffffff;
  color: #2f5f9f;
  font-size: 12px;
}

.pdf-page-state,
.pdf-zoom-state {
  min-width: 50px;
  text-align: center;
  font-variant-numeric: tabular-nums;
}

.pdf-toolbar-separator {
  width: 1px;
  height: 18px;
  background: rgba(60, 113, 183, 0.22);
}

.synctex-status {
  margin: 0 auto 12px;
  max-width: 540px;
  padding: 7px 10px;
  border: 1px solid rgba(60, 113, 183, 0.22);
  border-radius: 6px;
  background: rgba(255, 253, 248, 0.96);
  color: #44546a;
  font-size: 12px;
  line-height: 1.4;
}

.synctex-status.is-error {
  border-color: rgba(170, 40, 40, 0.36);
  color: #8f1d1d;
}

.synctex-status.is-ok {
  border-color: rgba(60, 113, 183, 0.4);
  color: #254f8f;
}

.real-pdf-page {
  position: relative;
  width: min(100%, 540px);
  max-width: none;
  margin: 0 auto 18px;
  padding: 0;
  border: 1px solid #d7deea;
  border-radius: 2px;
  background: white;
  box-shadow: 0 14px 32px rgba(31, 45, 64, 0.18);
  overflow: hidden;
}

.real-pdf-page img {
  display: block;
  width: 100%;
  height: auto;
  user-select: none;
  cursor: context-menu;
}

.real-pdf-page img:not([src]) {
  min-height: 420px;
  background:
    linear-gradient(90deg, rgba(60, 113, 183, 0.06), transparent 30%, transparent 70%, rgba(60, 113, 183, 0.06)),
    #fff;
}

.real-pdf-page figcaption {
  position: absolute;
  left: 50%;
  bottom: 8px;
  transform: translateX(-50%);
  padding: 2px 7px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  color: var(--eb-structure);
  font-size: 11px;
  line-height: 1.2;
  pointer-events: none;
}

.real-pdf-page.is-sync-hit {
  outline: 2px solid rgba(60, 113, 183, 0.72);
  outline-offset: 3px;
}

.pdf-sync-marker {
  position: absolute;
  width: 16px;
  height: 16px;
  border: 2px solid #2f72c6;
  border-radius: 999px;
  background: rgba(47, 114, 198, 0.14);
  transform: translate(-50%, -50%);
  pointer-events: none;
  box-shadow: 0 0 0 5px rgba(47, 114, 198, 0.12);
}

.render-pane .article-compact {
  max-width: none;
  height: auto;
  min-height: 0;
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}

.pdf-page {
  width: min(100%, 540px);
  height: var(--page-height);
  margin: 0 auto 18px;
  padding: 0;
  border: 1px solid #d7deea;
  border-radius: 2px;
  background: var(--eb-paper);
  box-shadow: 0 14px 32px rgba(31, 45, 64, 0.18);
  display: grid;
  grid-template-rows: 48px minmax(0, 1fr) 42px;
  overflow: hidden;
  position: relative;
}

.pdf-page-header {
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  min-width: 0;
  padding: 18px 40px 7px;
  border-bottom: 1px solid var(--eb-structure);
  color: var(--eb-structure);
  font-family: "TeX Gyre Heros", "Helvetica Neue", Arial, "PingFang SC", sans-serif;
  font-size: 11px;
  line-height: 1.2;
  white-space: nowrap;
}

.pdf-page-header span {
  overflow: hidden;
  text-overflow: ellipsis;
}

.pdf-page-body {
  min-height: 0;
  padding: 24px 42px 8px;
  overflow: hidden;
}

.pdf-page-footer {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
  padding: 8px 40px 15px;
  color: var(--eb-structure);
  font-family: "TeX Gyre Heros", "Helvetica Neue", Arial, "PingFang SC", sans-serif;
  font-size: 12px;
  line-height: 1.2;
}

.pdf-page-footer .footer-left,
.pdf-page-footer .footer-right {
  min-width: 0;
  color: rgba(60, 113, 183, 0.66);
  font-size: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pdf-page-footer .footer-right {
  text-align: right;
}

.pdf-page-footer .page-number {
  min-width: 48px;
  text-align: center;
  font-weight: 700;
}

.pdf-page h1 {
  margin: 0 0 24px;
  padding: 0 0 16px;
  border-bottom: 1px solid var(--eb-rule);
  color: var(--eb-structure);
  font-family: "TeX Gyre Heros", "Helvetica Neue", Arial, "PingFang SC", sans-serif;
  font-size: clamp(24px, 6vw, 30px);
  line-height: 1.25;
  text-align: center;
}

.pdf-page h2 {
  margin: 24px 0 12px;
  padding-top: 0;
  border-top: 0;
  color: var(--eb-structure);
  font-family: "TeX Gyre Heros", "Helvetica Neue", Arial, "PingFang SC", sans-serif;
  font-size: 21px;
  line-height: 1.35;
}

.pdf-page h3 {
  margin: 18px 0 8px;
  color: var(--eb-structure);
  font-size: 17px;
}

.pdf-page h4 {
  margin: 14px 0 6px;
  color: var(--eb-structure);
  font-size: 15px;
}

.pdf-page p,
.pdf-page li {
  color: var(--eb-ink);
  font-family: "TeX Gyre Termes", "Times New Roman", "Songti SC", "SimSun", serif;
  font-size: 14.5px;
  line-height: 1.78;
}

.pdf-page p {
  margin: 8px 0;
  text-align: justify;
  text-justify: inter-ideograph;
}

.pdf-page em {
  color: var(--eb-structure);
}

.pdf-page strong {
  color: #1f3760;
}

.pdf-page .intro-box {
  margin: 16px 0;
  padding: 0;
  border: 0;
  border-radius: 2px;
  background: transparent;
  overflow: hidden;
}

.pdf-page .intro-title {
  margin: 0;
  padding: 7px 12px;
  background: var(--eb-main);
  color: white;
  font-family: "TeX Gyre Heros", "Helvetica Neue", Arial, "PingFang SC", sans-serif;
  font-weight: 800;
}

.pdf-page .intro-box ul {
  margin: 0;
  padding: 10px 18px 10px 30px;
  border: 1px solid rgba(0, 166, 82, 0.42);
  border-top: 0;
  background: rgba(0, 166, 82, 0.055);
}

.pdf-page .latex-list {
  padding-left: 22px;
}

.pdf-page .formula {
  margin: 12px 0;
  padding: 10px 12px;
  border: 1px solid rgba(60, 113, 183, 0.28);
  border-radius: 2px;
  background: #f7faff;
  color: #17233d;
  font-size: 13.5px;
  line-height: 1.55;
}

.pdf-page .inline-math {
  color: #7d1c1c;
}

.render-pane [data-source-line] {
  cursor: context-menu;
}

.render-pane .is-sync-hit {
  outline: 2px solid rgba(60, 113, 183, 0.72);
  outline-offset: 3px;
  border-radius: 3px;
  background-color: rgba(60, 113, 183, 0.055);
}

.muted {
  color: var(--muted);
}

@media (max-width: 1100px) {
  .topbar {
    align-items: stretch;
  }

  .top-actions {
    justify-items: stretch;
  }

  .chapter-picker {
    grid-template-columns: 1fr;
  }

  .chapter-picker-state,
  .compile-state {
    text-align: left;
  }

  .workspace,
  .workspace.is-read,
  .workspace.is-dual,
  .workspace.is-quad {
    display: block;
  }

  .outline {
    position: static;
    max-height: none;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }

  .two-column-grid,
  .quad-grid {
    grid-template-columns: 1fr;
  }

  .article {
    padding: 28px 24px;
  }
}
"""


JS = r"""
(function () {
  const workspace = document.querySelector("[data-workspace]");
  const buttons = Array.from(document.querySelectorAll("[data-mode]"));
  const outlineToggle = document.querySelector("[data-toggle-outline]");
  const rebuildButton = document.querySelector("[data-rebuild-preview]");
  const compileStatus = document.querySelector("[data-compile-status]");
  const chapterSelect = document.querySelector("[data-chapter-select]");
  const originalSelect = document.querySelector("[data-original-select]");
  const targetSelect = document.querySelector("[data-target-select]");
  const openChapterButton = document.querySelector("[data-open-chapter]");
  const chapterPickerStatus = document.querySelector("[data-chapter-picker-status]");
  const chaptersDirInput = document.querySelector("[data-chapters-dir]");
  const importChaptersButton = document.querySelector("[data-import-chapters]");
  const editors = Array.from(document.querySelectorAll("[data-source-editor]"));
  const chapterLabel = workspace ? workspace.dataset.chapterLabel || "" : "";
  const previewDataElement = document.getElementById("preview-data");
  const previewData = previewDataElement ? JSON.parse(previewDataElement.textContent || "{}") : {};
  const syncTex = previewData.syncTex || {};
  const chapterPicker = previewData.chapterPicker || {};
  const defaultChaptersDir = previewData.chaptersDir || "";
  const syncApiBase = window.location.protocol.startsWith("http") ? "" : "http://127.0.0.1:8766";
  const pdfImageObserver = "IntersectionObserver" in window
    ? new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            loadPdfImage(entry.target);
            pdfImageObserver.unobserve(entry.target);
          }
        });
      }, { rootMargin: "700px 0px" })
    : null;
  let hasUnsavedBrowserEdits = false;
  let chapterCatalog = [];

  function setCompileStatus(message, kind) {
    if (!compileStatus) {
      return;
    }
    compileStatus.textContent = message;
    compileStatus.classList.toggle("is-dirty", kind === "dirty");
    compileStatus.classList.toggle("is-error", kind === "error");
    compileStatus.classList.toggle("is-ok", kind === "ok");
  }

  function setChapterPickerStatus(message, kind) {
    if (!chapterPickerStatus) {
      return;
    }
    chapterPickerStatus.textContent = message;
    chapterPickerStatus.classList.toggle("is-error", kind === "error");
    chapterPickerStatus.classList.toggle("is-ok", kind === "ok");
  }

  function apiUrl(path) {
    return `${syncApiBase}${path}`;
  }

  async function getApiJson(path) {
    const response = await fetch(apiUrl(path));
    const data = await response.json().catch(() => ({}));
    if (!response.ok || data.ok === false) {
      throw new Error(data.error || `Request failed: ${response.status}`);
    }
    return data;
  }

  async function postApiJson(path, payload) {
    const response = await fetch(apiUrl(path), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok || data.ok === false) {
      throw new Error(data.error || `Request failed: ${response.status}`);
    }
    return data;
  }

  function replaceSelectOptions(select, items, selectedValue, placeholder) {
    if (!select) {
      return;
    }
    select.innerHTML = "";
    if (!items.length) {
      const option = document.createElement("option");
      option.value = "";
      option.textContent = placeholder;
      select.appendChild(option);
      select.disabled = true;
      return;
    }
    items.forEach((item) => {
      const option = document.createElement("option");
      option.value = item.value;
      option.textContent = item.label;
      if (item.value === selectedValue) {
        option.selected = true;
      }
      select.appendChild(option);
    });
    select.disabled = false;
  }

  function chapterById(chapterId) {
    return chapterCatalog.find((item) => item.id === chapterId) || null;
  }

  function currentChapterSelection() {
    return {
      chapterId: chapterSelect ? chapterSelect.value : "",
      originalKey: originalSelect ? originalSelect.value : "",
      targetKey: targetSelect ? targetSelect.value : "",
    };
  }

  function populateVersionSelects(chapter, originalKey, targetKey) {
    const versions = chapter ? chapter.versions || [] : [];
    replaceSelectOptions(
      originalSelect,
      versions.map((item) => ({ value: item.key, label: item.label })),
      originalKey || (chapter ? chapter.defaultOriginalKey : ""),
      "当前章节没有可选版本"
    );
    replaceSelectOptions(
      targetSelect,
      versions.map((item) => ({ value: item.key, label: item.label })),
      targetKey || (chapter ? chapter.defaultTargetKey : ""),
      "当前章节没有可选版本"
    );
    if (openChapterButton) {
      openChapterButton.disabled = !chapter || !versions.length;
    }
  }

  function findCurrentCatalogSelection(chapters) {
    const currentSource = chapterPicker.currentSourcePath || "";
    const currentOriginal = chapterPicker.currentOriginalPath || "";
    for (const chapter of chapters) {
      let sourceVersion = null;
      let originalVersion = null;
      for (const version of chapter.versions || []) {
        if (version.path === currentSource) {
          sourceVersion = version;
        }
        if (version.path === currentOriginal) {
          originalVersion = version;
        }
      }
      if (sourceVersion || originalVersion) {
        return {
          chapterId: chapter.id,
          originalKey: originalVersion ? originalVersion.key : chapter.defaultOriginalKey,
          targetKey: sourceVersion ? sourceVersion.key : chapter.defaultTargetKey,
        };
      }
    }
    return chapters.length
      ? {
          chapterId: chapters[0].id,
          originalKey: chapters[0].defaultOriginalKey,
          targetKey: chapters[0].defaultTargetKey,
        }
      : null;
  }

  function syncChapterControls(selection) {
    if (!selection || !chapterSelect) {
      return;
    }
    chapterSelect.value = selection.chapterId;
    const chapter = chapterById(selection.chapterId);
    populateVersionSelects(chapter, selection.originalKey, selection.targetKey);
  }

  function updateChapterPickerPrompt(text) {
    if (chaptersDirInput && !chaptersDirInput.value) {
      chaptersDirInput.value = defaultChaptersDir;
    }
    if (!chapterSelect) {
      return;
    }
    if (!chapterCatalog.length) {
      setChapterPickerStatus(text || "请先导入包含章节 .tex 的文件夹，再打开章节。", "error");
    }
  }

  function setMode(mode) {
    workspace.classList.remove("is-read", "is-dual", "is-quad");
    workspace.classList.add(`is-${mode}`);
    buttons.forEach((button) => {
      button.classList.toggle("is-active", button.dataset.mode === mode);
    });
    updateAllGrids();
  }

  function loadPdfImage(image) {
    if (!image || image.dataset.loaded === "1") {
      return;
    }
    const source = image.dataset.src;
    if (!source) {
      return;
    }
    image.src = source;
    image.dataset.loaded = "1";
  }

  function preparePdfImages(root) {
    const scope = root || document;
    scope.querySelectorAll(".pdf-page-image[data-src]").forEach((image) => {
      if (image.dataset.observed === "1" || image.dataset.loaded === "1") {
        return;
      }
      image.dataset.observed = "1";
      if (pdfImageObserver) {
        pdfImageObserver.observe(image);
      } else {
        loadPdfImage(image);
      }
    });
  }

  function loadFirstVisiblePdfPages() {
    document.querySelectorAll(".real-pdf-reader").forEach((reader) => {
      if (reader.getClientRects().length === 0) {
        return;
      }
      Array.from(reader.querySelectorAll(".pdf-page-image[data-src]"))
        .slice(0, 2)
        .forEach(loadPdfImage);
    });
  }

  function pdfPages(reader) {
    return Array.from(reader.querySelectorAll(".real-pdf-page"));
  }

  function readerShell(reader) {
    return reader ? reader.closest(".pdf-reader-shell") || reader : null;
  }

  function readerBasePageWidth(reader) {
    const available = Math.max(240, reader.clientWidth - 36);
    return Math.min(540, available);
  }

  function setReaderZoom(reader, zoom) {
    const shell = readerShell(reader);
    const previousZoom = Number(reader.dataset.pdfZoom || "1");
    const previousCenter = reader.scrollLeft + reader.clientWidth / 2;
    const nextZoom = Math.min(1.6, Math.max(0.72, zoom));
    const baseWidth = readerBasePageWidth(reader);
    reader.dataset.pdfZoom = String(nextZoom);
    reader.dataset.pdfBaseWidth = String(baseWidth);
    pdfPages(reader).forEach((page) => {
      page.style.width = `${Math.round(baseWidth * nextZoom)}px`;
    });
    const state = shell ? shell.querySelector("[data-pdf-zoom-state]") : null;
    if (state) {
      state.textContent = `${Math.round(nextZoom * 100)}%`;
    }
    if (previousZoom > 0 && reader.scrollWidth > reader.clientWidth) {
      const ratio = nextZoom / previousZoom;
      reader.scrollLeft = Math.max(0, previousCenter * ratio - reader.clientWidth / 2);
    }
    loadFirstVisiblePdfPages();
  }

  function refreshVisibleReaderZooms() {
    document.querySelectorAll(".real-pdf-reader").forEach((reader) => {
      if (reader.getClientRects().length === 0) {
        return;
      }
      const currentBase = readerBasePageWidth(reader);
      const previousBase = Number(reader.dataset.pdfBaseWidth || "0");
      if (Math.abs(currentBase - previousBase) > 2) {
        setReaderZoom(reader, Number(reader.dataset.pdfZoom || "1"));
      }
    });
  }

  function updateReaderPageState(reader, pageNumber) {
    const shell = readerShell(reader);
    const current = shell ? shell.querySelector("[data-current-page]") : null;
    if (current) {
      current.textContent = String(pageNumber || 1);
    }
    reader.dataset.currentPage = String(pageNumber || 1);
  }

  function visiblePdfPage(reader) {
    const pages = pdfPages(reader);
    if (!pages.length) {
      return 1;
    }
    const probeY = reader.scrollTop + reader.clientHeight * 0.35;
    let selected = pages[0];
    for (const page of pages) {
      if (page.offsetTop <= probeY) {
        selected = page;
      } else {
        break;
      }
    }
    return Number(selected.dataset.pdfPage || "1");
  }

  function scrollReaderToPage(reader, pageNumber) {
    const targetPage = Math.max(1, Number(pageNumber) || 1);
    const page = reader.querySelector(`[data-pdf-page="${targetPage}"]`);
    if (!page) {
      return;
    }
    const image = page.querySelector(".pdf-page-image");
    if (image) {
      loadPdfImage(image);
    }
    reader.scrollTop = Math.max(0, page.offsetTop - 54);
    updateReaderPageState(reader, targetPage);
  }

  function initPdfToolbars(root) {
    const scope = root || document;
    scope.querySelectorAll(".real-pdf-reader").forEach((reader) => {
      if (reader.dataset.pdfToolbarReady === "1") {
        return;
      }
      reader.dataset.pdfToolbarReady = "1";
      reader.dataset.pdfZoom = reader.dataset.pdfZoom || "1";
      const shell = readerShell(reader);
      const pageCount = pdfPages(reader).length;
      const previous = shell ? shell.querySelector("[data-pdf-prev]") : null;
      const next = shell ? shell.querySelector("[data-pdf-next]") : null;
      const zoomIn = shell ? shell.querySelector("[data-pdf-zoom-in]") : null;
      const zoomOut = shell ? shell.querySelector("[data-pdf-zoom-out]") : null;
      if (previous) {
        previous.addEventListener("click", () => {
          scrollReaderToPage(reader, Math.max(1, visiblePdfPage(reader) - 1));
        });
      }
      if (next) {
        next.addEventListener("click", () => {
          scrollReaderToPage(reader, Math.min(pageCount, visiblePdfPage(reader) + 1));
        });
      }
      if (zoomIn) {
        zoomIn.addEventListener("click", () => {
          setReaderZoom(reader, Number(reader.dataset.pdfZoom || "1") + 0.12);
        });
      }
      if (zoomOut) {
        zoomOut.addEventListener("click", () => {
          setReaderZoom(reader, Number(reader.dataset.pdfZoom || "1") - 0.12);
        });
      }
      reader.addEventListener("scroll", () => {
        window.clearTimeout(reader._pageStateTimer);
        reader._pageStateTimer = window.setTimeout(() => {
          updateReaderPageState(reader, visiblePdfPage(reader));
        }, 80);
      });
      setReaderZoom(reader, Number(reader.dataset.pdfZoom || "1"));
      updateReaderPageState(reader, visiblePdfPage(reader));
    });
  }

  function updateGrid(grid) {
    const panes = Array.from(grid.querySelectorAll(".compare-pane"));
    if (!panes.length) {
      return;
    }
    grid.style.gridTemplateColumns = panes
      .map((pane) => (pane.classList.contains("is-collapsed") ? "54px" : "minmax(260px, 1fr)"))
      .join(" ");
  }

  function updateAllGrids() {
    document.querySelectorAll(".two-column-grid, .quad-grid").forEach(updateGrid);
    window.requestAnimationFrame(() => {
      paginateVisibleReaders();
      preparePdfImages(document);
      loadFirstVisiblePdfPages();
      initPdfToolbars(document);
      refreshVisibleReaderZooms();
    });
  }

  window.addEventListener("resize", () => {
    window.clearTimeout(window._pdfResizeTimer);
    window._pdfResizeTimer = window.setTimeout(refreshVisibleReaderZooms, 120);
  });

  buttons.forEach((button) => {
    button.addEventListener("click", () => setMode(button.dataset.mode || "read"));
  });

  if (chapterSelect) {
    chapterSelect.addEventListener("change", () => {
      const chapter = chapterById(chapterSelect.value);
      if (!chapter) {
        populateVersionSelects(null, "", "");
        return;
      }
      populateVersionSelects(chapter, chapter.defaultOriginalKey, chapter.defaultTargetKey);
      setChapterPickerStatus("已切换章节，请点击“打开章节”生成对应页面。", "");
    });
  }

  if (originalSelect) {
    originalSelect.addEventListener("change", () => {
      setChapterPickerStatus("原文版本已更新，请点击“打开章节”生成对应页面。", "");
    });
  }

  if (targetSelect) {
    targetSelect.addEventListener("change", () => {
      setChapterPickerStatus("修改稿版本已更新，请点击“打开章节”生成对应页面。", "");
    });
  }

  if (openChapterButton) {
    openChapterButton.addEventListener("click", async () => {
      const selection = currentChapterSelection();
      if (!selection.chapterId) {
        setChapterPickerStatus("请先选择章节。", "error");
        return;
      }
      openChapterButton.disabled = true;
      setChapterPickerStatus("正在生成所选章节的校对页，请稍候...", "ok");
      try {
        const result = await postSyncTex("/api/build-chapter", selection);
        setChapterPickerStatus("章节页面生成完成，正在打开...", "ok");
        window.location.href = result.renderUrl;
      } catch (error) {
        setChapterPickerStatus(error.message || "章节生成失败。", "error");
        openChapterButton.disabled = false;
      }
    });
  }

  if (importChaptersButton) {
    importChaptersButton.addEventListener("click", async () => {
      const chaptersDir = chaptersDirInput ? chaptersDirInput.value.trim() : "";
      if (!chaptersDir) {
        setChapterPickerStatus("请先填写章节文件夹路径。", "error");
        return;
      }
      importChaptersButton.disabled = true;
      setChapterPickerStatus("正在导入章节文件夹，请稍候...", "ok");
      try {
        const result = await postApiJson("/api/import-chapters-dir", { chaptersDir });
        if (chaptersDirInput) {
          chaptersDirInput.value = result.chaptersDir || chaptersDir;
        }
        setChapterPickerStatus(`已导入章节文件夹，发现 ${result.chapterCount || 0} 个章节。`, "ok");
        await loadChapterCatalog();
      } catch (error) {
        setChapterPickerStatus(error.message || "章节文件夹导入失败。", "error");
      } finally {
        importChaptersButton.disabled = false;
      }
    });
  }

  async function loadChapterCatalog() {
    if (!chapterSelect) {
      return;
    }
    try {
      const data = await getApiJson("/api/chapters");
      if (chaptersDirInput && data.chaptersDir) {
        chaptersDirInput.value = data.chaptersDir;
      }
      chapterCatalog = Array.isArray(data.chapters) ? data.chapters : [];
      replaceSelectOptions(
        chapterSelect,
        chapterCatalog.map((item) => ({ value: item.id, label: item.label })),
        "",
        "没有可用章节"
      );
      const selection = findCurrentCatalogSelection(chapterCatalog);
      if (!selection) {
        populateVersionSelects(null, "", "");
        updateChapterPickerPrompt("没有发现可用章节。请导入一个包含章节 .tex 的文件夹。");
        return;
      }
      syncChapterControls(selection);
      setChapterPickerStatus("可直接切换到任意章节与版本组合。", "ok");
    } catch (error) {
      replaceSelectOptions(chapterSelect, [], "", "无法读取章节目录");
      populateVersionSelects(null, "", "");
      setChapterPickerStatus(error.message || "章节目录读取失败。请确认本地 HTTP 服务已启动。", "error");
    }
  }

  if (outlineToggle) {
    outlineToggle.addEventListener("click", () => {
      const collapsed = workspace.classList.toggle("is-outline-collapsed");
      outlineToggle.textContent = collapsed ? "展开" : "收起";
    });
  }

  document.querySelectorAll("[data-toggle-pane]").forEach((button) => {
    button.addEventListener("click", () => {
      const pane = button.closest(".compare-pane");
      if (!pane) {
        return;
      }
      const collapsed = pane.classList.toggle("is-collapsed");
      button.textContent = collapsed ? "展开" : "收起";
      const grid = pane.closest(".two-column-grid, .quad-grid");
      if (grid) {
        updateGrid(grid);
      }
    });
  });

  if (rebuildButton) {
    rebuildButton.addEventListener("click", async () => {
      const rebuildPayload = syncTex.rebuild || null;
      if (!rebuildPayload) {
        setCompileStatus("当前页面没有可重新编译的 PDF 配置。", "error");
        return;
      }
      if (hasUnsavedBrowserEdits) {
        const proceed = window.confirm("源码栏有浏览器内临时修改。重新编译会读取磁盘上的 .tex 文件，这些临时修改不会进入 PDF。是否继续？");
        if (!proceed) {
          return;
        }
      }
      rebuildButton.disabled = true;
      setCompileStatus("正在重新编译 PDF，请稍候...", "ok");
      try {
        await postSyncTex("/api/rebuild-preview", rebuildPayload);
        setCompileStatus("重新编译完成，正在刷新页面...", "ok");
        window.location.reload();
      } catch (error) {
        setCompileStatus(error.message || "重新编译失败。", "error");
        rebuildButton.disabled = false;
      }
    });
  }

  function visibleMode() {
    if (workspace.classList.contains("is-quad")) {
      return "quad";
    }
    if (workspace.classList.contains("is-dual")) {
      return "dual";
    }
    return "read";
  }

  function sourceEditorForVariant(variant) {
    return document.querySelector(`[data-source-editor="${variant}"]`);
  }

  function renderPaneForVariant(variant) {
    const mode = visibleMode();
    return (
      document.querySelector(`.${mode}-view .render-pane.is-${variant}`) ||
      document.querySelector(`.quad-view .render-pane.is-${variant}`) ||
      document.querySelector(`.dual-view .render-pane.is-${variant}`)
    );
  }

  function syncAssetForVariant(variant) {
    return syncTex && syncTex.variants ? syncTex.variants[variant] : null;
  }

  function sourceGutterForVariant(variant) {
    return document.querySelector(`[data-source-gutter="${variant}"]`);
  }

  function editorVariant(editor) {
    return editor ? editor.dataset.sourceEditor || "target" : "target";
  }

  function sourceLineCount(text) {
    return String(text).split(/\r?\n/).length;
  }

  function updateSourceGutter(editor) {
    if (!editor) {
      return;
    }
    const gutter = sourceGutterForVariant(editorVariant(editor));
    if (!gutter) {
      return;
    }
    const lineCount = sourceLineCount(editor.value);
    if (Number(gutter.dataset.lineCount || "0") === lineCount) {
      return;
    }
    const rows = [];
    for (let line = 1; line <= lineCount; line += 1) {
      rows.push(`<div class="source-gutter-line" data-line="${line}">${line}</div>`);
    }
    gutter.innerHTML = rows.join("");
    gutter.dataset.lineCount = String(lineCount);
    gutter.scrollTop = editor.scrollTop;
  }

  function syncSourceGutterScroll(editor) {
    const gutter = sourceGutterForVariant(editorVariant(editor));
    if (gutter) {
      gutter.scrollTop = editor.scrollTop;
    }
  }

  function markSourceDirty(variant) {
    hasUnsavedBrowserEdits = true;
    document.querySelectorAll(`[data-source-state="${variant}"]`).forEach((item) => {
      item.textContent = "浏览器内已有临时修改；PDF/SyncTeX 仍对应最近一次编译";
    });
    setCompileStatus("源码栏有临时修改，PDF 尚未重新编译；重新编译会读取磁盘上的 .tex 文件。", "dirty");
  }

  function markSourceLines(editor, startLine, endLine) {
    const gutter = sourceGutterForVariant(editorVariant(editor));
    if (!gutter) {
      return null;
    }
    gutter.querySelectorAll(".is-line-hit").forEach((line) => line.classList.remove("is-line-hit"));
    const safeStart = Math.max(1, Number(startLine) || 1);
    const safeEnd = Math.max(safeStart, Number(endLine) || safeStart);
    let first = null;
    for (let line = safeStart; line <= safeEnd; line += 1) {
      const item = gutter.querySelector(`[data-line="${line}"]`);
      if (item) {
        item.classList.add("is-line-hit");
        if (!first) {
          first = item;
        }
      }
      if (line - safeStart > 80) {
        break;
      }
    }
    return first;
  }

  function sourceScrollTopForLine(editor, lineElement, startLine) {
    if (lineElement) {
      return Math.max(0, lineElement.offsetTop - editor.clientHeight * 0.35);
    }
    const style = window.getComputedStyle(editor);
    const parsedLineHeight = Number.parseFloat(style.lineHeight);
    const fontSize = Number.parseFloat(style.fontSize) || 13;
    const lineHeight = Number.isFinite(parsedLineHeight) ? parsedLineHeight : fontSize * 1.7;
    return Math.max(0, (Math.max(1, startLine) - 1) * lineHeight - editor.clientHeight * 0.35);
  }

  function openPane(pane) {
    if (!pane || !pane.classList.contains("is-collapsed")) {
      return;
    }
    pane.classList.remove("is-collapsed");
    const button = pane.querySelector("[data-toggle-pane]");
    if (button) {
      button.textContent = "收起";
    }
    const grid = pane.closest(".two-column-grid, .quad-grid");
    if (grid) {
      updateGrid(grid);
    }
  }

  function lineStartOffset(text, lineNumber) {
    const line = Math.max(1, Number(lineNumber) || 1);
    if (line <= 1) {
      return 0;
    }
    let offset = 0;
    for (let current = 1; current < line; current += 1) {
      const nextBreak = text.indexOf("\n", offset);
      if (nextBreak === -1) {
        return text.length;
      }
      offset = nextBreak + 1;
    }
    return offset;
  }

  function lineEndOffset(text, lineNumber) {
    const start = lineStartOffset(text, lineNumber);
    const nextBreak = text.indexOf("\n", start);
    return nextBreak === -1 ? text.length : nextBreak;
  }

  function flashSourcePane(pane) {
    pane.classList.add("is-source-jump");
    window.clearTimeout(pane._sourceJumpTimer);
    pane._sourceJumpTimer = window.setTimeout(() => {
      pane.classList.remove("is-source-jump");
    }, 1200);
  }

  function flashRenderBlock(block) {
    document.querySelectorAll(".is-sync-hit").forEach((item) => item.classList.remove("is-sync-hit"));
    block.classList.add("is-sync-hit");
    window.clearTimeout(block._syncHitTimer);
    block._syncHitTimer = window.setTimeout(() => {
      block.classList.remove("is-sync-hit");
    }, 1200);
  }

  function syncStatus(variant, message, kind) {
    const statuses = Array.from(document.querySelectorAll(`[data-synctex-status="${variant}"]`));
    if (!statuses.length) {
      return;
    }
    statuses.forEach((status) => {
      status.textContent = message;
      status.classList.toggle("is-error", kind === "error");
      status.classList.toggle("is-ok", kind === "ok");
    });
  }

  async function postSyncTex(path, payload) {
    const response = await fetch(`${syncApiBase}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok || data.ok === false) {
      throw new Error(data.error || `SyncTeX request failed: ${response.status}`);
    }
    return data;
  }

  function flashPdfPage(pageElement, xPercent, yPercent) {
    document.querySelectorAll(".real-pdf-page.is-sync-hit").forEach((page) => {
      page.classList.remove("is-sync-hit");
    });
    pageElement.classList.add("is-sync-hit");
    let marker = pageElement.querySelector(".pdf-sync-marker");
    if (!marker) {
      marker = document.createElement("span");
      marker.className = "pdf-sync-marker";
      pageElement.appendChild(marker);
    }
    marker.style.left = `${xPercent}%`;
    marker.style.top = `${yPercent}%`;
    window.clearTimeout(pageElement._pdfSyncTimer);
    pageElement._pdfSyncTimer = window.setTimeout(() => {
      pageElement.classList.remove("is-sync-hit");
    }, 1600);
  }

  async function jumpFromPdfToSource(variant, pageElement, event) {
    const asset = syncAssetForVariant(variant);
    const image = pageElement.querySelector(".pdf-page-image");
    if (!asset || !image) {
      syncStatus(variant, "缺少 PDF/SyncTeX 资源，请重新生成预览。", "error");
      return;
    }
    const rect = image.getBoundingClientRect();
    const xRatio = Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width));
    const yRatio = Math.min(1, Math.max(0, (event.clientY - rect.top) / rect.height));
    const x = xRatio * Number(asset.pageWidthPt || 0);
    const y = yRatio * Number(asset.pageHeightPt || 0);
    const page = Number(pageElement.dataset.pdfPage || "1");
    flashPdfPage(pageElement, xRatio * 100, yRatio * 100);
    syncStatus(variant, `正在用 SyncTeX 定位第 ${page} 页...`, "ok");
    const result = await postSyncTex("/api/synctex/edit", {
      pdfPath: asset.pdfPath,
      page,
      x,
      y,
    });
    const line = Number(result.line || 0);
    if (!line) {
      throw new Error("SyncTeX 没有返回源码行号。");
    }
    syncStatus(variant, `已定位到源码第 ${line} 行。`, "ok");
    jumpToSource(variant, line, line);
  }

  function scrollToPdfPosition(variant, page, x, y) {
    const pane = renderPaneForVariant(variant);
    openPane(pane);
    const asset = syncAssetForVariant(variant);
    const reader = pane ? pane.querySelector("[data-synctex-reader]") : null;
    const pageElement = reader ? reader.querySelector(`[data-pdf-page="${page}"]`) : null;
    if (!asset || !reader || !pageElement) {
      return;
    }
    const image = pageElement.querySelector(".pdf-page-image");
    if (image) {
      loadPdfImage(image);
    }
    if (visibleMode() !== "quad") {
      setMode("quad");
    }
    const xPercent = Number(asset.pageWidthPt || 0) ? (Number(x) / Number(asset.pageWidthPt)) * 100 : 50;
    const yPercent = Number(asset.pageHeightPt || 0) ? (Number(y) / Number(asset.pageHeightPt)) * 100 : 50;
    reader.scrollTop = Math.max(0, pageElement.offsetTop - reader.clientHeight * 0.2);
    flashPdfPage(pageElement, xPercent, yPercent);
  }

  async function jumpFromSourceToPdf(variant, lineNumber) {
    const asset = syncAssetForVariant(variant);
    if (!asset) {
      return;
    }
    syncStatus(variant, `正在用 SyncTeX 定位源码第 ${lineNumber} 行...`, "ok");
    const result = await postSyncTex("/api/synctex/view", {
      pdfPath: asset.pdfPath,
      sourcePath: asset.sourcePath,
      line: lineNumber,
      column: 1,
    });
    const first = result.matches && result.matches.length ? result.matches[0] : result;
    if (!first.page) {
      throw new Error("SyncTeX 没有返回 PDF 页码。");
    }
    syncStatus(variant, `已定位到 PDF 第 ${first.page} 页。`, "ok");
    scrollToPdfPosition(variant, Number(first.page), Number(first.x || 0), Number(first.y || 0));
  }

  function jumpToSource(variant, startLine, endLine) {
    if (visibleMode() !== "quad") {
      setMode("quad");
    }

    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        const editor = sourceEditorForVariant(variant);
        if (!editor) {
          return;
        }
        const pane = editor.closest(".compare-pane");
        openPane(pane);
        updateSourceGutter(editor);
        const start = lineStartOffset(editor.value, startLine);
        const end = lineEndOffset(editor.value, endLine || startLine);
        editor.focus({ preventScroll: true });
        editor.setSelectionRange(start, Math.max(start, end));
        const lineElement = markSourceLines(editor, startLine, endLine || startLine);
        editor.scrollTop = sourceScrollTopForLine(editor, lineElement, startLine);
        syncSourceGutterScroll(editor);
        if (pane) {
          flashSourcePane(pane);
        }
      });
    });
  }

  document.querySelectorAll(".render-pane").forEach((pane) => {
    pane.addEventListener("contextmenu", (event) => {
      const pdfPage = event.target.closest(".real-pdf-page");
      if (pdfPage && pane.contains(pdfPage)) {
        const variant = pane.classList.contains("is-original") ? "original" : "target";
        event.preventDefault();
        jumpFromPdfToSource(variant, pdfPage, event).catch((error) => {
          syncStatus(variant, error.message || "SyncTeX 定位失败。", "error");
        });
        return;
      }

      const block = event.target.closest("[data-source-line]");
      if (!block || !pane.contains(block)) {
        return;
      }
      const variant = pane.classList.contains("is-original") ? "original" : "target";
      const startLine = Number.parseInt(block.dataset.sourceLine || "", 10);
      const endLine = Number.parseInt(block.dataset.sourceEndLine || block.dataset.sourceLine || "", 10);
      if (!Number.isFinite(startLine)) {
        return;
      }
      event.preventDefault();
      flashRenderBlock(block);
      jumpToSource(variant, startLine, endLine);
    });
  });

  document.addEventListener("contextmenu", (event) => {
    const lineElement = event.target.closest(".source-gutter-line");
    if (!lineElement) {
      return;
    }
    const gutter = lineElement.closest("[data-source-gutter]");
    const variant = gutter ? gutter.dataset.sourceGutter || "target" : "target";
    const lineNumber = Number(lineElement.dataset.line || "0");
    if (!lineNumber || !syncAssetForVariant(variant)) {
      return;
    }
    event.preventDefault();
    jumpFromSourceToPdf(variant, lineNumber).catch((error) => {
      syncStatus(variant, error.message || "SyncTeX 定位失败。", "error");
    });
  });

  function escapeHtml(text) {
    return String(text)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function replaceCommand(text, command, tag) {
    const pattern = new RegExp("\\\\" + command + "\\{([^{}]*)\\}", "g");
    let current = text;
    while (true) {
      const next = current.replace(pattern, `<${tag}>$1</${tag}>`);
      if (next === current) {
        return current;
      }
      current = next;
    }
  }

  function renderInlineLatex(text) {
    let rendered = escapeHtml(text);
    rendered = replaceCommand(rendered, "textbf", "strong");
    rendered = replaceCommand(rendered, "emph", "em");
    rendered = replaceCommand(rendered, "text", "span");
    rendered = rendered.replace(/\$([^$]+)\$/g, (_, body) => `<span class="inline-math">$${body}$</span>`);
    rendered = rendered.replaceAll("\\ldots", "…");
    rendered = rendered.replaceAll("\\;", " ");
    rendered = rendered.replace(/\\fa[A-Za-z]+/g, "");
    return rendered;
  }

  function cleanInlineLatex(text) {
    const holder = document.createElement("div");
    holder.innerHTML = renderInlineLatex(text);
    return holder.textContent.trim();
  }

  function renderLatexPreview(source) {
    const lines = source.split(/\r?\n/);
    const state = {
      body: [],
      paragraph: [],
      paragraphStartLine: 0,
      math: [],
      mathStartLine: 0,
      introTitle: "",
      introItems: [],
      introStartLine: 0,
      listEnv: "",
      listItems: [],
      listStartLine: 0,
      inMath: false,
      inIntro: false,
      inList: false,
      sectionCounter: 0,
    };

    function sourceAttrs(startLine, endLine) {
      if (!startLine || startLine < 1) {
        return "";
      }
      const resolvedEnd = endLine && endLine >= startLine ? endLine : startLine;
      return `data-source-line="${startLine}" data-source-end-line="${resolvedEnd}"`;
    }

    function flushParagraph(endLine) {
      if (!state.paragraph.length) {
        return;
      }
      const text = state.paragraph.map((line) => line.trimEnd()).join("\n").trim();
      state.paragraph = [];
      if (text) {
        state.body.push(`<p ${sourceAttrs(state.paragraphStartLine, endLine)}>${renderInlineLatex(text).replaceAll("\n", "<br>")}</p>`);
      }
      state.paragraphStartLine = 0;
    }

    function flushMath(endLine) {
      const formula = state.math.map((line) => line.trim()).join("\n").trim();
      state.body.push(`<pre class="formula" ${sourceAttrs(state.mathStartLine, endLine)}><code>${escapeHtml(formula)}</code></pre>`);
      state.math = [];
      state.mathStartLine = 0;
      state.inMath = false;
    }

    function flushIntro(endLine) {
      const items = state.introItems.map((item) => `<li>${renderInlineLatex(item)}</li>`).join("\n");
      state.body.push(`<section class="intro-box" ${sourceAttrs(state.introStartLine, endLine)}>
  <div class="intro-title">${escapeHtml(state.introTitle || "提示")}</div>
  <ul>${items}</ul>
</section>`);
      state.introTitle = "";
      state.introItems = [];
      state.introStartLine = 0;
      state.inIntro = false;
    }

    function flushList(endLine) {
      const tag = state.listEnv === "enumerate" ? "ol" : "ul";
      const items = state.listItems.map((item) => `<li>${renderInlineLatex(item)}</li>`).join("\n");
      state.body.push(`<${tag} class="latex-list" ${sourceAttrs(state.listStartLine, endLine)}>${items}</${tag}>`);
      state.listEnv = "";
      state.listItems = [];
      state.listStartLine = 0;
      state.inList = false;
    }

    function appendSection(command, title) {
      const levels = { chapter: 1, section: 2, subsection: 3, subsubsection: 4, paragraph: 5 };
      const level = levels[command] || 2;
      const tag = `h${Math.min(level, 4)}`;
      state.sectionCounter += 1;
      const label = command === "chapter" && chapterLabel
        ? `<span class="chapter-label">${escapeHtml(chapterLabel)}</span>`
        : "";
      state.body.push(
        `<${tag} id="live-sec-${state.sectionCounter}" class="latex-heading latex-${command}" data-heading-level="${level}" ${sourceAttrs(state.currentLine || 1)}>${label}${renderInlineLatex(title)}</${tag}>`
      );
    }

    lines.forEach((line, index) => {
      const lineNumber = index + 1;
      state.currentLine = lineNumber;
      const stripped = line.trim();

      if (state.inList) {
        const endList = stripped.match(/^\\end\{([^}]+)\}\s*$/);
        if (endList && endList[1] === state.listEnv) {
          flushList(lineNumber);
          return;
        }
        if (stripped.startsWith("\\item")) {
          state.listItems.push(stripped.slice("\\item".length).trim());
        } else if (stripped) {
          if (state.listItems.length) {
            state.listItems[state.listItems.length - 1] += " " + stripped;
          } else {
            state.listItems.push(stripped);
          }
        }
        return;
      }

      if (state.inMath) {
        if (stripped === "\\]") {
          flushMath(lineNumber);
        } else {
          state.math.push(line);
        }
        return;
      }

      if (state.inIntro) {
        if (/^\\end\{introduction\}\s*$/.test(stripped)) {
          flushIntro(lineNumber);
          return;
        }
        if (stripped.startsWith("\\item")) {
          state.introItems.push(stripped.slice("\\item".length).trim());
        } else if (stripped) {
          if (state.introItems.length) {
            state.introItems[state.introItems.length - 1] += " " + stripped;
          } else {
            state.introItems.push(stripped);
          }
        }
        return;
      }

      if (!stripped) {
        flushParagraph(lineNumber - 1);
        return;
      }

      if (/^\s*%\s*!TEX\b/i.test(line) || /^\s*%/.test(line)) {
        flushParagraph(lineNumber - 1);
        return;
      }

      const section = stripped.match(/^\\(chapter|section|subsection|subsubsection|paragraph)\*?(?:\[[^\]]*\])?\{(.*)\}\s*$/);
      if (section) {
        flushParagraph(lineNumber - 1);
        appendSection(section[1], section[2]);
        return;
      }

      const begin = stripped.match(/^\\begin\{([^}]+)\}(?:\[(.*)\])?\s*$/);
      if (begin && begin[1] === "introduction") {
        flushParagraph(lineNumber - 1);
        state.inIntro = true;
        state.introTitle = cleanInlineLatex(begin[2] || "提示");
        state.introItems = [];
        state.introStartLine = lineNumber;
        return;
      }
      if (begin && (begin[1] === "itemize" || begin[1] === "enumerate")) {
        flushParagraph(lineNumber - 1);
        state.inList = true;
        state.listEnv = begin[1];
        state.listItems = [];
        state.listStartLine = lineNumber;
        return;
      }

      if (stripped === "\\[") {
        flushParagraph(lineNumber - 1);
        state.inMath = true;
        state.math = [];
        state.mathStartLine = lineNumber;
        return;
      }

      if (!state.paragraph.length) {
        state.paragraphStartLine = lineNumber;
      }
      state.paragraph.push(line);
    });

    const lastLine = lines.length;
    flushParagraph(lastLine);
    if (state.inMath) {
      flushMath(lastLine);
    }
    if (state.inIntro) {
      flushIntro(lastLine);
    }
    if (state.inList) {
      flushList(lastLine);
    }
    return state.body.join("\n") || '<p class="muted">暂无内容</p>';
  }

  function createPage(pageNumber) {
    const wrapper = document.createElement("section");
    wrapper.className = "pdf-page";
    wrapper.dataset.pageNumber = String(pageNumber);
    const header = document.createElement("div");
    header.className = "pdf-page-header";
    const headerText = document.createElement("span");
    header.appendChild(headerText);
    const body = document.createElement("div");
    body.className = "pdf-page-body";
    const footer = document.createElement("div");
    footer.className = "pdf-page-footer";
    footer.innerHTML = '<span class="footer-left">人工智能的数学思维</span><span class="page-number"></span><span class="footer-right">ElegantBook Preview</span>';
    wrapper.append(header, body, footer);
    return { wrapper, header, headerText, body, footer };
  }

  function pageHeadingText(page, fallback) {
    const heading = page.querySelector("h1, h2, h3, h4");
    if (!heading) {
      return fallback;
    }
    const text = heading.textContent.replace(/\s+/g, " ").trim();
    return text || fallback;
  }

  function updatePageFooters(article) {
    const pages = Array.from(article.querySelectorAll(".pdf-page"));
    let runningTitle = chapterLabel || document.title;
    pages.forEach((page, index) => {
      runningTitle = pageHeadingText(page, runningTitle);
      const headerText = page.querySelector(".pdf-page-header span");
      if (headerText) {
        headerText.textContent = runningTitle;
      }
      const pageNumber = page.querySelector(".page-number");
      if (pageNumber) {
        pageNumber.textContent = `${index + 1} / ${pages.length}`;
      }
    });
  }

  function paginateArticle(article) {
    if (!article || article.dataset.paginating === "1") {
      return;
    }
    if (!article.dataset.rawHtml) {
      article.dataset.rawHtml = article.innerHTML;
    }
    article.dataset.paginating = "1";

    const holder = document.createElement("div");
    holder.innerHTML = article.dataset.rawHtml;
    const blocks = Array.from(holder.children);
    article.innerHTML = "";

    let pageNumber = 1;
    let page = createPage(pageNumber);
    article.appendChild(page.wrapper);
    blocks.forEach((block) => {
      const clone = block.cloneNode(true);
      page.body.appendChild(clone);
      if (page.body.scrollHeight > page.body.clientHeight && page.body.children.length > 1) {
        page.body.removeChild(clone);
        pageNumber += 1;
        page = createPage(pageNumber);
        article.appendChild(page.wrapper);
        page.body.appendChild(clone);
      }
    });

    updatePageFooters(article);
    article.dataset.paginating = "0";
  }

  function paginateVisibleReaders() {
    document.querySelectorAll(".render-pane [data-render-content]").forEach(paginateArticle);
  }

  function updatePreview(variant, source) {
    const rendered = renderLatexPreview(source);
    document.querySelectorAll(`.render-pane.is-${variant} .article`).forEach((article) => {
      article.dataset.rawHtml = rendered;
      article.innerHTML = rendered;
      paginateArticle(article);
    });
    if (variant === "target") {
      const readArticle = document.querySelector(".target-read-article");
      if (readArticle) {
        readArticle.innerHTML = rendered;
      }
    }
  }

  editors.forEach((editor) => {
    let timer = 0;
    updateSourceGutter(editor);
    editor.addEventListener("scroll", () => {
      syncSourceGutterScroll(editor);
    });
    editor.addEventListener("input", () => {
      markSourceDirty(editor.dataset.sourceEditor || "target");
      updateSourceGutter(editor);
      syncSourceGutterScroll(editor);
      window.clearTimeout(timer);
      timer = window.setTimeout(() => {
        updatePreview(editor.dataset.sourceEditor || "target", editor.value);
      }, 120);
    });
  });

  updateAllGrids();
  preparePdfImages(document);
  loadFirstVisiblePdfPages();
  paginateVisibleReaders();
  updateChapterPickerPrompt();
  loadChapterCatalog();
})();
"""


if __name__ == "__main__":
    raise SystemExit(main())
