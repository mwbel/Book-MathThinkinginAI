#!/usr/bin/env python3
"""Render a static paragraph review page from compare-data JSON."""

from __future__ import annotations

import argparse
import difflib
import html
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS_LABELS = {
    "unchanged": "未变化",
    "changed": "已修改",
    "added": "新增",
    "removed": "删除",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a static HTML review page from compare-data JSON.")
    parser.add_argument("--input", required=True, help="Path to compare-data.json produced by build_review.py.")
    parser.add_argument("--output", required=True, help="Path to write review.html.")
    parser.add_argument("--log-output", default=None, help="Optional path to write review-log.md.")
    parser.add_argument("--diff-output", default=None, help="Optional path to write a unified changes.diff.")
    parser.add_argument("--test-output", default=None, help="Optional path to write a browser self-test page.")
    parser.add_argument("--title", default="教材润色校对页", help="HTML page title.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input JSON not found: {input_path}")

    data = json.loads(input_path.read_text(encoding="utf-8"))
    if "compare" not in data:
        raise SystemExit("Input JSON must contain compare data. Run build_review.py with --target first.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_page(data, page_title=args.title), encoding="utf-8")
    diff_path = None
    if args.diff_output:
        diff_path = Path(args.diff_output).expanduser().resolve()
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.write_text(render_unified_diff(data), encoding="utf-8")
        print(f"Wrote {diff_path}")
    test_path = None
    if args.test_output:
        test_path = Path(args.test_output).expanduser().resolve()
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text(
            render_test_page(
                data,
                page_title=args.title,
                review_path=output_path,
                log_path=Path(args.log_output).expanduser().resolve() if args.log_output else None,
                diff_path=diff_path,
                test_path=test_path,
            ),
            encoding="utf-8",
        )
        print(f"Wrote {test_path}")
    if args.log_output:
        log_path = Path(args.log_output).expanduser().resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            render_log(
                data,
                input_path=input_path,
                output_path=output_path,
                log_path=log_path,
                diff_path=diff_path,
                test_path=test_path,
                page_title=args.title,
            ),
            encoding="utf-8",
        )
        print(f"Wrote {log_path}")
    print(f"Wrote {output_path}")
    return 0


def render_page(data: dict[str, Any], page_title: str) -> str:
    summary = data.get("compare", {}).get("summary", {})
    pairs = data.get("compare", {}).get("pairs", [])
    generated_at = datetime.now(timezone.utc).isoformat()
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
  <header class="app-header">
    <div>
      <p class="eyebrow">LaTeX 教材润色校对</p>
      <h1>{escape(page_title)}</h1>
      <p class="file-line">原文：{escape(data.get("sourceFile", ""))}</p>
      <p class="file-line">修改后：{escape(data.get("targetFile", ""))}</p>
    </div>
    <div class="summary">
      {summary_item("总对照", summary.get("pairCount", 0))}
      {summary_item("已修改", summary.get("changedCount", 0), "changed")}
      {summary_item("新增", summary.get("addedCount", 0), "added")}
      {summary_item("删除", summary.get("removedCount", 0), "removed")}
    </div>
  </header>
  <main class="layout">
    <aside class="sidebar">
      <div class="sidebar-title">章节导航</div>
      {render_nav(data)}
    </aside>
    <section class="content">
      <div class="toolbar">
        <div>
          <strong>段落级对照</strong>
          <span>{escape(generated_at)}</span>
        </div>
        <div class="toolbar-actions">
          {render_filter_controls(summary)}
          <div class="diff-actions">
            <button class="tool-button" type="button" data-diff-action="expand">展开差异</button>
            <button class="tool-button" type="button" data-diff-action="collapse">收起差异</button>
          </div>
        </div>
      </div>
      <div class="result-line" data-result-line>当前显示 {escape(str(summary.get("pairCount", len(pairs))))} 个对照块</div>
      <p class="empty is-hidden" data-filter-empty>当前筛选条件下没有可显示的对照块。</p>
      {render_pairs(pairs)}
    </section>
  </main>
  <script>
{JS}
  </script>
</body>
</html>
"""


def render_log(
    data: dict[str, Any],
    input_path: Path,
    output_path: Path,
    log_path: Path,
    diff_path: Path | None,
    test_path: Path | None,
    page_title: str,
) -> str:
    summary = data.get("compare", {}).get("summary", {})
    source_summary = data.get("source", {}).get("summary", {})
    target_summary = data.get("target", {}).get("summary", {})
    generated_at = datetime.now(timezone.utc).isoformat()
    return f"""# 校对任务日志

## 基本信息

- 标题：{page_title}
- 生成时间：{generated_at}
- 输入 JSON：`{input_path}`
- HTML 输出：`{output_path}`
- Diff 输出：`{diff_path or "未生成"}`
- 测试页输出：`{test_path or "未生成"}`
- 日志输出：`{log_path}`

## 源文件

- 原文文件：`{data.get("sourceFile", "")}`
- 修改后文件：`{data.get("targetFile", "")}`
- 原文绝对路径：`{data.get("sourceFileAbsolute", "")}`
- 修改后绝对路径：`{data.get("targetFileAbsolute", "")}`

## 对照统计

- 总对照块：{summary.get("pairCount", 0)}
- 未变化：{summary.get("unchangedCount", 0)}
- 已修改：{summary.get("changedCount", 0)}
- 新增：{summary.get("addedCount", 0)}
- 删除：{summary.get("removedCount", 0)}

## 解析统计

### 原文

- block：{source_summary.get("blockCount", 0)}
- section：{source_summary.get("sectionCount", 0)}
- paragraph：{source_summary.get("paragraphCount", 0)}
- environment：{source_summary.get("environmentCount", 0)}
- metadata：{source_summary.get("metadataCount", 0)}
- comment：{source_summary.get("commentCount", 0)}

### 修改后

- block：{target_summary.get("blockCount", 0)}
- section：{target_summary.get("sectionCount", 0)}
- paragraph：{target_summary.get("paragraphCount", 0)}
- environment：{target_summary.get("environmentCount", 0)}
- metadata：{target_summary.get("metadataCount", 0)}
- comment：{target_summary.get("commentCount", 0)}

## 本次边界

- 未修改原始 `.tex` 文件。
- 未修改归档目录。
- 未接入 LLM。
- 未执行 `.tex` 回写。
- 未安装外部依赖。
- HTML 页面为单文件静态页面。
- 测试页为本地静态页面，只读取本次生成的校对页。

## 建议人工检查

- 打开 HTML，先筛选“已修改 / 新增 / 删除”。
- 检查章节导航是否能跳转。
- 检查长中文段落是否适合左右对照阅读。
- 检查包含 LaTeX 命令、公式或列表的块是否显示完整。
- 若目标文件包含“原文：”等过程性标记，应先清理或改用干净目标稿再生成正式校对页。
"""


def render_test_page(
    data: dict[str, Any],
    page_title: str,
    review_path: Path,
    log_path: Path | None,
    diff_path: Path | None,
    test_path: Path,
) -> str:
    summary = data.get("compare", {}).get("summary", {})
    source_sections = data.get("source", {}).get("sections", [])
    expected = {
        "title": page_title,
        "pairCount": int(summary.get("pairCount", 0) or 0),
        "statusCounts": {
            "unchanged": int(summary.get("unchangedCount", 0) or 0),
            "changed": int(summary.get("changedCount", 0) or 0),
            "added": int(summary.get("addedCount", 0) or 0),
            "removed": int(summary.get("removedCount", 0) or 0),
        },
        "navCount": sum(1 for section in source_sections if int(section.get("level", 0) or 0) >= 1),
    }
    links = {
        "review": relative_link(test_path, review_path),
        "log": relative_link(test_path, log_path) if log_path else "",
        "diff": relative_link(test_path, diff_path) if diff_path else "",
    }
    payload = json.dumps({"expected": expected, "links": links}, ensure_ascii=False).replace("</", "<\\/")
    embedded_review = json.dumps(review_path.read_text(encoding="utf-8"), ensure_ascii=False).replace("</", "<\\/")
    generated_at = datetime.now(timezone.utc).isoformat()
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(page_title)} · 测试面板</title>
  <style>
{TEST_CSS}
  </style>
</head>
<body>
  <header class="test-header">
    <div>
      <p class="eyebrow">校对页测试面板</p>
      <h1>{escape(page_title)}</h1>
      <p class="meta-line">生成时间：{escape(generated_at)}</p>
    </div>
    <nav class="link-row" aria-label="输出文件">
      <a href="{escape(links["review"])}" target="_blank">打开校对页</a>
      {optional_link("打开日志", links["log"])}
      {optional_link("打开 Diff", links["diff"])}
    </nav>
  </header>

  <main class="test-layout">
    <section class="test-panel" aria-label="测试控制台">
      <div class="stat-grid">
        {test_stat("总对照", expected["pairCount"])}
        {test_stat("已修改", expected["statusCounts"]["changed"])}
        {test_stat("新增", expected["statusCounts"]["added"])}
        {test_stat("删除", expected["statusCounts"]["removed"])}
      </div>

      <div class="control-row">
        <button type="button" data-run-tests>运行自测</button>
        <button type="button" data-frame-size="desktop">桌面宽度</button>
        <button type="button" data-frame-size="mobile">移动宽度</button>
      </div>

      <div class="summary-line" data-test-summary>等待测试</div>
      <ul class="result-list" data-test-results></ul>
    </section>

    <section class="preview-panel" aria-label="校对页预览">
      <iframe class="preview-frame" data-review-frame src="{escape(links["review"])}" title="校对页预览"></iframe>
    </section>
  </main>

  <script id="test-data" type="application/json">{payload}</script>
  <script id="review-html" type="application/json">{embedded_review}</script>
  <script>
{TEST_JS}
  </script>
</body>
</html>
"""


def relative_link(from_path: Path, to_path: Path) -> str:
    relative = os.path.relpath(to_path, start=from_path.parent)
    return Path(relative).as_posix()


def optional_link(label: str, href: str) -> str:
    if not href:
        return ""
    return f'<a href="{escape(href)}" target="_blank">{escape(label)}</a>'


def test_stat(label: str, value: Any) -> str:
    return f"""<div class="stat-item">
        <span>{escape(label)}</span>
        <strong>{escape(str(value))}</strong>
      </div>"""


def render_unified_diff(data: dict[str, Any]) -> str:
    source_path = review_file_path(data, "sourceFileAbsolute", "sourceFile")
    target_path = review_file_path(data, "targetFileAbsolute", "targetFile")
    source_text = source_path.read_text(encoding="utf-8")
    target_text = target_path.read_text(encoding="utf-8")
    return "".join(
        difflib.unified_diff(
            source_text.splitlines(keepends=True),
            target_text.splitlines(keepends=True),
            fromfile=str(data.get("sourceFile", source_path)),
            tofile=str(data.get("targetFile", target_path)),
            lineterm="\n",
        )
    )


def review_file_path(data: dict[str, Any], absolute_key: str, relative_key: str) -> Path:
    raw_path = data.get(absolute_key) or data.get(relative_key)
    if not raw_path:
        raise SystemExit(f"Cannot create diff: missing {absolute_key} / {relative_key}.")
    path = Path(str(raw_path)).expanduser()
    if not path.is_absolute():
        project_root = data.get("projectRootAbsolute") or data.get("projectRoot")
        if project_root:
            path = Path(str(project_root)).expanduser() / path
    path = path.resolve()
    if not path.exists():
        raise SystemExit(f"Cannot create diff: file not found: {path}")
    return path


def summary_item(label: str, value: Any, status: str = "") -> str:
    status_class = f" is-{status}" if status else ""
    return f"""<div class="summary-item{status_class}">
        <span>{escape(label)}</span>
        <strong>{escape(str(value))}</strong>
      </div>"""


def render_filter_controls(summary: dict[str, Any]) -> str:
    items = [
        ("all", "全部", summary.get("pairCount", 0)),
        ("changed", "已修改", summary.get("changedCount", 0)),
        ("added", "新增", summary.get("addedCount", 0)),
        ("removed", "删除", summary.get("removedCount", 0)),
        ("unchanged", "未变化", summary.get("unchangedCount", 0)),
    ]
    buttons = []
    for status, label, count in items:
        active = " is-active" if status == "all" else ""
        buttons.append(
            f'<button class="filter-button{active}" type="button" data-filter-status="{escape(status)}">'
            f"{escape(label)} <span>{escape(str(count))}</span></button>"
        )
    return f'<div class="filter-group" aria-label="筛选对照块">{"".join(buttons)}</div>'


def render_nav(data: dict[str, Any]) -> str:
    sections = data.get("source", {}).get("sections", [])
    if not sections:
        return '<p class="empty">暂无章节结构</p>'
    items: list[str] = []
    for section in sections:
        level = int(section.get("level", 0) or 0)
        if level < 1:
            continue
        title = str(section.get("title", "") or "未命名章节")
        anchor = f"line-{section.get('startLine', '')}"
        indent = min(max(level - 1, 0), 4)
        items.append(
            f'<a class="nav-link indent-{indent}" href="#{escape(anchor)}">{escape(title)}</a>'
        )
    return "\n".join(items) if items else '<p class="empty">暂无章节结构</p>'


def render_pairs(pairs: list[dict[str, Any]]) -> str:
    if not pairs:
        return '<p class="empty">暂无对照数据</p>'
    return "\n".join(render_pair(pair) for pair in pairs)


def render_pair(pair: dict[str, Any]) -> str:
    status = str(pair.get("status", "unknown"))
    source = pair.get("sourceBlock") or {}
    target = pair.get("targetBlock") or {}
    anchor_line = source.get("startLine") or target.get("startLine") or ""
    source_text = str(source.get("content", "") or "")
    target_text = str(target.get("content", "") or "")
    section_title = current_section_title(pair.get("sectionPath") or [])
    block_type = str(pair.get("blockType", "") or "")
    line_label = line_range_label(source, target)
    return f"""<article class="pair-card is-{escape(status)}" id="line-{escape(str(anchor_line))}" data-status="{escape(status)}">
  <div class="pair-head">
    <div>
      <span class="status-badge is-{escape(status)}">{escape(STATUS_LABELS.get(status, status))}</span>
      <strong>{escape(pair.get("id", ""))}</strong>
      <span class="meta">{escape(block_type)} · {escape(line_label)}</span>
    </div>
    <div class="section-title">{escape(section_title)}</div>
  </div>
  <div class="compare-grid">
    <section class="pane">
      <div class="pane-title">原文</div>
      {code_block(source_text, empty_text="无原文")}
    </section>
    <section class="pane">
      <div class="pane-title">修改后</div>
      {code_block(target_text, empty_text="无修改后文本")}
    </section>
  </div>
  {render_diff(pair)}
</article>"""


def render_diff(pair: dict[str, Any]) -> str:
    diff = pair.get("diff") or []
    if not diff:
        return ""
    parts = []
    for item in diff:
        op = str(item.get("op", "equal"))
        text = str(item.get("text", ""))
        if not text:
            continue
        parts.append(f'<span class="diff-token is-{escape(op)}">{escape(text)}</span>')
    if not parts:
        return ""
    return f"""<details class="diff-detail">
    <summary>查看词级差异</summary>
    <div class="diff-inline">{"".join(parts)}</div>
  </details>"""


def code_block(text: str, empty_text: str) -> str:
    if not text.strip():
        return f'<pre class="code-block is-empty"><code>{escape(empty_text)}</code></pre>'
    return f'<pre class="code-block"><code>{escape(text)}</code></pre>'


def current_section_title(section_path: list[dict[str, Any]]) -> str:
    if not section_path:
        return "Front Matter"
    return str(section_path[-1].get("title", "") or "未命名章节")


def line_range_label(source: dict[str, Any], target: dict[str, Any]) -> str:
    source_label = block_line_label(source)
    target_label = block_line_label(target)
    if source_label and target_label and source_label != target_label:
        return f"原文 {source_label} / 修改后 {target_label}"
    return source_label or target_label or "无行号"


def block_line_label(block: dict[str, Any]) -> str:
    if not block:
        return ""
    start = block.get("startLine")
    end = block.get("endLine")
    if start is None:
        return ""
    if end is None or end == start:
        return f"L{start}"
    return f"L{start}-L{end}"


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


TEST_CSS = r"""
:root {
  --bg: #f4efe6;
  --panel: #fffdf8;
  --ink: #1f2937;
  --muted: #667085;
  --line: #e2d7c7;
  --accent: #8a5a12;
  --ok: #157347;
  --bad: #b42318;
  --pending: #7a5d22;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  line-height: 1.6;
}

.test-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  padding: 24px 28px;
  background: #27211a;
  color: #fffaf0;
}

.eyebrow,
.meta-line {
  margin: 0;
  color: #eadfcb;
  font-size: 13px;
}

h1 {
  margin: 4px 0 4px;
  font-size: 26px;
  letter-spacing: 0;
}

.link-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.link-row a,
button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  padding: 7px 12px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: #fffaf1;
  color: #3b3124;
  font: inherit;
  font-size: 14px;
  text-decoration: none;
  cursor: pointer;
}

.link-row a:hover,
button:hover {
  border-color: #c99a46;
  background: #f4e6c9;
}

.test-layout {
  display: grid;
  grid-template-columns: 380px minmax(0, 1fr);
  gap: 18px;
  padding: 18px;
}

.test-panel,
.preview-panel {
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--panel);
}

.test-panel {
  align-self: start;
  padding: 16px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.stat-item {
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fffaf1;
}

.stat-item span {
  display: block;
  color: var(--muted);
  font-size: 12px;
}

.stat-item strong {
  display: block;
  margin-top: 2px;
  font-size: 22px;
}

.control-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.summary-line {
  margin-top: 14px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #f8f4ec;
  color: var(--pending);
  font-weight: 700;
}

.summary-line.is-ok {
  color: var(--ok);
}

.summary-line.is-bad {
  color: var(--bad);
}

.result-list {
  margin: 12px 0 0;
  padding: 0;
  list-style: none;
}

.result-list li {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr);
  gap: 8px;
  padding: 9px 0;
  border-bottom: 1px solid var(--line);
  font-size: 14px;
}

.result-list strong {
  display: block;
}

.result-list span {
  color: var(--muted);
}

.status-mark {
  font-weight: 800;
}

.status-mark.is-ok {
  color: var(--ok);
}

.status-mark.is-bad {
  color: var(--bad);
}

.preview-panel {
  overflow: hidden;
}

.preview-frame {
  display: block;
  width: 100%;
  height: calc(100vh - 132px);
  min-height: 720px;
  border: 0;
  background: #fff;
}

.preview-frame.is-mobile {
  width: 390px;
  max-width: 100%;
  margin: 0 auto;
  border-left: 1px solid var(--line);
  border-right: 1px solid var(--line);
}

@media (max-width: 980px) {
  .test-header,
  .test-layout {
    display: block;
  }

  .link-row {
    margin-top: 14px;
  }

  .preview-panel {
    margin-top: 18px;
  }

  .preview-frame {
    height: 760px;
  }
}
"""


TEST_JS = r"""
(function () {
  const config = JSON.parse(document.getElementById("test-data").textContent);
  const embeddedReviewNode = document.getElementById("review-html");
  const embeddedReviewHtml = embeddedReviewNode ? JSON.parse(embeddedReviewNode.textContent) : "";
  const expected = config.expected || {};
  const frame = document.querySelector("[data-review-frame]");
  const summary = document.querySelector("[data-test-summary]");
  const results = document.querySelector("[data-test-results]");
  const runButton = document.querySelector("[data-run-tests]");
  const sizeButtons = Array.from(document.querySelectorAll("[data-frame-size]"));

  function mark(name, ok, detail) {
    const item = document.createElement("li");
    item.innerHTML = `<div class="status-mark ${ok ? "is-ok" : "is-bad"}">${ok ? "✓" : "×"}</div>
      <div><strong>${escapeHtml(name)}</strong><span>${escapeHtml(detail || "")}</span></div>`;
    results.appendChild(item);
    return ok;
  }

  function escapeHtml(text) {
    return String(text)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function readFrameDocument() {
    try {
      return frame.contentDocument || frame.contentWindow.document;
    } catch (error) {
      return null;
    }
  }

  function visibleCards(doc) {
    return Array.from(doc.querySelectorAll("[data-status]")).filter((card) => {
      return !card.classList.contains("is-hidden");
    });
  }

  function countStatuses(cards) {
    return cards.reduce((acc, card) => {
      const status = card.dataset.status || "unknown";
      acc[status] = (acc[status] || 0) + 1;
      return acc;
    }, {});
  }

  function click(doc, selector) {
    const node = doc.querySelector(selector);
    if (!node) {
      return false;
    }
    node.click();
    return true;
  }

  function waitForFrame() {
    return new Promise((resolve) => {
      const doc = readFrameDocument();
      if (doc && doc.readyState === "complete") {
        window.setTimeout(resolve, 30);
        return;
      }
      frame.addEventListener("load", () => window.setTimeout(resolve, 30), { once: true });
      window.setTimeout(resolve, 1500);
    });
  }

  async function runTests() {
    results.innerHTML = "";
    summary.className = "summary-line";
    summary.textContent = "正在测试";
    await waitForFrame();

    const doc = readFrameDocument();
    if (!doc) {
      mark("读取校对页", false, "浏览器限制了 iframe 读取。可在 tools/review/outputs 中运行 python3 -m http.server 后再打开本页。");
      summary.className = "summary-line is-bad";
      summary.textContent = "测试未完成";
      return;
    }

    const cards = Array.from(doc.querySelectorAll("[data-status]"));
    const counts = countStatuses(cards);
    const expectedCounts = expected.statusCounts || {};
    const checks = [];

    checks.push(mark("页面标题", doc.title === expected.title, doc.title));
    checks.push(mark("对照块数量", cards.length === expected.pairCount, `${cards.length} / ${expected.pairCount}`));
    checks.push(mark("已修改数量", (counts.changed || 0) === expectedCounts.changed, `${counts.changed || 0} / ${expectedCounts.changed}`));
    checks.push(mark("新增数量", (counts.added || 0) === expectedCounts.added, `${counts.added || 0} / ${expectedCounts.added}`));
    checks.push(mark("删除数量", (counts.removed || 0) === expectedCounts.removed, `${counts.removed || 0} / ${expectedCounts.removed}`));
    checks.push(mark("未变化数量", (counts.unchanged || 0) === expectedCounts.unchanged, `${counts.unchanged || 0} / ${expectedCounts.unchanged}`));

    const filterButtons = Array.from(doc.querySelectorAll("[data-filter-status]")).map((button) => button.dataset.filterStatus).join(",");
    checks.push(mark("筛选按钮", filterButtons === "all,changed,added,removed,unchanged", filterButtons || "未找到"));

    const navLinks = Array.from(doc.querySelectorAll(".nav-link"));
    const navTargetsValid = navLinks.every((link) => !!doc.querySelector(link.getAttribute("href") || ""));
    checks.push(mark("章节导航", navLinks.length === expected.navCount && navTargetsValid, `${navLinks.length} 个锚点`));

    checks.push(mark("外部脚本", doc.querySelectorAll("script[src]").length === 0, `${doc.querySelectorAll("script[src]").length} 个外部脚本`));

    for (const status of ["changed", "added", "removed", "unchanged", "all"]) {
      click(doc, `[data-filter-status="${status}"]`);
      const visible = visibleCards(doc).length;
      const expectedVisible = status === "all" ? expected.pairCount : expectedCounts[status];
      checks.push(mark(`筛选：${status}`, visible === expectedVisible, `${visible} / ${expectedVisible}`));
    }

    if ((expectedCounts.changed || 0) > 0) {
      click(doc, '[data-filter-status="changed"]');
      const visible = visibleCards(doc);
      click(doc, '[data-diff-action="expand"]');
      const details = visible.flatMap((card) => Array.from(card.querySelectorAll("details.diff-detail")));
      const opened = details.filter((detail) => detail.open).length;
      click(doc, '[data-diff-action="collapse"]');
      const closed = details.filter((detail) => !detail.open).length;
      checks.push(mark("展开差异", opened === details.length && details.length > 0, `${opened} / ${details.length}`));
      checks.push(mark("收起差异", closed === details.length && details.length > 0, `${closed} / ${details.length}`));
    }

    frame.classList.remove("is-mobile");
    await new Promise((resolve) => requestAnimationFrame(resolve));
    const desktopOverflow = doc.documentElement.scrollWidth > frame.clientWidth + 2;
    checks.push(mark("桌面宽度", !desktopOverflow, desktopOverflow ? "出现横向溢出" : "无横向溢出"));

    frame.classList.add("is-mobile");
    await new Promise((resolve) => requestAnimationFrame(resolve));
    await new Promise((resolve) => requestAnimationFrame(resolve));
    const grid = doc.querySelector(".compare-grid");
    const gridDisplay = grid ? frame.contentWindow.getComputedStyle(grid).display : "";
    const mobileOverflow = doc.documentElement.scrollWidth > frame.clientWidth + 2;
    checks.push(mark("移动宽度", gridDisplay === "block" && !mobileOverflow, `布局：${gridDisplay || "未知"}`));

    const passed = checks.filter(Boolean).length;
    const failed = checks.length - passed;
    summary.className = failed === 0 ? "summary-line is-ok" : "summary-line is-bad";
    summary.textContent = failed === 0 ? `通过 ${passed} 项` : `通过 ${passed} 项，失败 ${failed} 项`;
  }

  function loadPreview() {
    frame.addEventListener("load", runTests, { once: true });
    if (embeddedReviewHtml && "srcdoc" in frame) {
      frame.srcdoc = embeddedReviewHtml;
      return;
    }
    const doc = readFrameDocument();
    if (doc && doc.readyState === "complete") {
      runTests();
    }
  }

  runButton.addEventListener("click", runTests);
  sizeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      frame.classList.toggle("is-mobile", button.dataset.frameSize === "mobile");
    });
  });
  loadPreview();
})();
"""


CSS = r"""
:root {
  --bg: #f6f3ec;
  --paper: #fffdf8;
  --ink: #1f2937;
  --muted: #667085;
  --line: #e6dccb;
  --accent: #8a5a12;
  --changed: #b7791f;
  --added: #157347;
  --removed: #b42318;
  --soft-added: #e9f7ef;
  --soft-removed: #fdecec;
  --soft-changed: #fff6db;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  line-height: 1.65;
}

.app-header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px 36px;
  background: #27211a;
  color: #fffaf0;
}

.eyebrow {
  margin: 0 0 4px;
  color: #d7b56d;
  font-size: 13px;
}

h1 {
  margin: 0 0 10px;
  font-size: 28px;
  letter-spacing: 0;
}

.file-line {
  margin: 2px 0;
  color: #eadfcb;
  font-size: 13px;
}

.summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(110px, 1fr));
  gap: 10px;
  min-width: 300px;
}

.summary-item {
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.08);
}

.summary-item span {
  display: block;
  color: #eadfcb;
  font-size: 12px;
}

.summary-item strong {
  display: block;
  margin-top: 2px;
  font-size: 22px;
}

.layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  min-height: calc(100vh - 160px);
}

.sidebar {
  position: sticky;
  top: 0;
  align-self: start;
  max-height: 100vh;
  overflow: auto;
  padding: 22px 18px;
  border-right: 1px solid var(--line);
}

.sidebar-title {
  margin-bottom: 12px;
  color: var(--accent);
  font-weight: 700;
}

.nav-link {
  display: block;
  padding: 7px 8px;
  border-radius: 6px;
  color: #3b3124;
  text-decoration: none;
  font-size: 14px;
}

.nav-link:hover {
  background: #ebe1d0;
}

.indent-1 { padding-left: 18px; }
.indent-2 { padding-left: 30px; }
.indent-3 { padding-left: 42px; }
.indent-4 { padding-left: 54px; }

.content {
  padding: 24px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding: 14px 16px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
}

.toolbar-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar span,
.meta,
.section-title {
  color: var(--muted);
  font-size: 13px;
}

.filter-group,
.diff-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-button,
.tool-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 34px;
  padding: 6px 10px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: #fffaf1;
  color: #3b3124;
  cursor: pointer;
  font: inherit;
  font-size: 13px;
}

.filter-button:hover,
.tool-button:hover,
.filter-button.is-active {
  border-color: #c99a46;
  background: #f4e6c9;
}

.filter-button span {
  color: var(--accent);
  font-weight: 700;
}

.result-line {
  margin: -4px 0 12px;
  color: var(--muted);
  font-size: 13px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.changed { background: var(--changed); }
.status-dot.added { background: var(--added); }
.status-dot.removed { background: var(--removed); }

.pair-card {
  margin-bottom: 16px;
  border: 1px solid var(--line);
  border-left: 4px solid transparent;
  border-radius: 10px;
  background: var(--paper);
  overflow: hidden;
}

.pair-card.is-hidden,
.empty.is-hidden {
  display: none;
}

.pair-card.is-changed { border-left-color: var(--changed); }
.pair-card.is-added { border-left-color: var(--added); }
.pair-card.is-removed { border-left-color: var(--removed); }

.pair-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--line);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  margin-right: 8px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  background: #ece7dd;
  color: #4a3b27;
}

.status-badge.is-changed { background: var(--soft-changed); color: var(--changed); }
.status-badge.is-added { background: var(--soft-added); color: var(--added); }
.status-badge.is-removed { background: var(--soft-removed); color: var(--removed); }

.compare-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
}

.pane {
  min-width: 0;
  padding: 14px 16px 16px;
}

.pane + .pane {
  border-left: 1px solid var(--line);
}

.pane-title {
  margin-bottom: 8px;
  color: var(--accent);
  font-size: 13px;
  font-weight: 700;
}

.code-block {
  min-height: 76px;
  margin: 0;
  padding: 14px;
  border: 1px solid #eadfcb;
  border-radius: 8px;
  background: #fffaf1;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 14px;
  line-height: 1.7;
}

.code-block.is-empty {
  color: var(--muted);
  background: #f8f4ec;
}

.diff-detail {
  padding: 0 16px 16px;
}

.diff-detail summary {
  cursor: pointer;
  color: var(--accent);
  font-weight: 700;
}

.diff-inline {
  margin-top: 10px;
  padding: 12px;
  border-radius: 8px;
  background: #fbf7ef;
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
}

.diff-token.is-insert {
  background: var(--soft-added);
  color: var(--added);
}

.diff-token.is-delete {
  background: var(--soft-removed);
  color: var(--removed);
  text-decoration: line-through;
}

.empty {
  color: var(--muted);
}

@media (max-width: 980px) {
  .app-header,
  .toolbar,
  .pair-head {
    display: block;
  }

  .summary {
    margin-top: 18px;
  }

  .toolbar-actions {
    justify-content: flex-start;
    margin-top: 10px;
  }

  .layout,
  .compare-grid {
    display: block;
  }

  .sidebar {
    position: static;
    max-height: none;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }

  .pane + .pane {
    border-left: 0;
    border-top: 1px solid var(--line);
  }
}
"""


JS = r"""
(function () {
  const cards = Array.from(document.querySelectorAll("[data-status]"));
  const buttons = Array.from(document.querySelectorAll("[data-filter-status]"));
  const resultLine = document.querySelector("[data-result-line]");
  const empty = document.querySelector("[data-filter-empty]");

  function applyFilter(status) {
    let visibleCount = 0;
    cards.forEach((card) => {
      const show = status === "all" || card.dataset.status === status;
      card.classList.toggle("is-hidden", !show);
      if (show) {
        visibleCount += 1;
      }
    });
    buttons.forEach((button) => {
      button.classList.toggle("is-active", button.dataset.filterStatus === status);
    });
    if (resultLine) {
      resultLine.textContent = `当前显示 ${visibleCount} 个对照块`;
    }
    if (empty) {
      empty.classList.toggle("is-hidden", visibleCount !== 0);
    }
  }

  buttons.forEach((button) => {
    button.addEventListener("click", () => applyFilter(button.dataset.filterStatus || "all"));
  });

  document.querySelectorAll("[data-diff-action]").forEach((button) => {
    button.addEventListener("click", () => {
      const shouldOpen = button.dataset.diffAction === "expand";
      cards.forEach((card) => {
        if (card.classList.contains("is-hidden")) {
          return;
        }
        card.querySelectorAll("details.diff-detail").forEach((detail) => {
          detail.open = shouldOpen;
        });
      });
    });
  });
})();
"""


if __name__ == "__main__":
    raise SystemExit(main())
