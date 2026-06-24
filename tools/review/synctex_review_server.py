#!/usr/bin/env python3
"""Serve review outputs and expose a small SyncTeX API for the local preview UI."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from chapter_catalog import discover_chapter_catalog, find_version


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve local review pages with SyncTeX jump APIs.")
    parser.add_argument("--root", default=None, help="Static root. Defaults to tools/review/outputs.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=8766, help="Port to bind.")
    return parser.parse_args()


def summarize_build_error(message: str) -> str:
    """Return a short UI-safe explanation while keeping raw logs out of the header."""
    text = message.strip()
    if not text:
        return "章节生成失败，请查看终端日志。"
    missing_input = re.search(r"(?:Missing input file|not found on input line)[^'\n]*(?:'([^']+)')?", text, re.I)
    if missing_input:
        target = missing_input.group(1) or "图片、参考文献或 LaTeX 输入文件"
        return f"章节正文预览已优先生成；PDF 编译缺少 {target}。需要 PDF 时请补齐资源后在高级设置中重编译。"
    if re.search(r"latexmk|xelatex|bibtex|bbl|Unable to load picture", text, re.I):
        return "章节正文预览已优先生成；PDF 编译失败，通常是缺少图片、参考文献或 LaTeX 依赖。需要 PDF 时请在高级设置中重编译。"
    first_line = text.splitlines()[0]
    return first_line[:220]


def main() -> int:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    root = Path(args.root).expanduser().resolve() if args.root else script_dir / "outputs"
    root.mkdir(parents=True, exist_ok=True)
    project_root = script_dir.parent.parent
    default_chapters_dir = project_root / "draft-tex-3扩写" / "chapters-20251105"

    handler = make_handler(root, project_root, default_chapters_dir)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Serving review outputs from {root}")
    print(f"Open http://{args.host}:{args.port}/ch12-clean-render.html")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping SyncTeX review server.")
    finally:
        server.server_close()
    return 0


def make_handler(root: Path, project_root: Path, chapters_dir: Path) -> type[SimpleHTTPRequestHandler]:
    current_chapters_dir = {"path": chapters_dir}

    class SyncTexReviewHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(root), **kwargs)

        def end_headers(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            super().end_headers()

        def do_OPTIONS(self) -> None:
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()

        def do_GET(self) -> None:
            if self.path == "/api/chapters":
                try:
                    current_dir = current_chapters_dir["path"]
                    self.write_json(
                        {
                            "ok": True,
                            "chaptersDir": str(current_dir),
                            "chapters": discover_chapter_catalog(current_dir),
                        }
                    )
                except Exception as exc:  # noqa: BLE001
                    self.write_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            super().do_GET()

        def do_POST(self) -> None:
            try:
                if self.path == "/api/synctex/edit":
                    self.write_json(handle_synctex_edit(self.read_json()))
                    return
                if self.path == "/api/synctex/view":
                    self.write_json(handle_synctex_view(self.read_json()))
                    return
                if self.path == "/api/rebuild-preview":
                    self.write_json(handle_rebuild_preview(self.read_json()))
                    return
                if self.path == "/api/build-chapter":
                    self.write_json(handle_build_chapter(self.read_json(), root, project_root, current_chapters_dir["path"]))
                    return
                if self.path == "/api/import-chapters-dir":
                    self.write_json(
                        handle_import_chapters_dir(self.read_json(), current_chapters_dir, project_root)
                    )
                    return
                self.write_json({"ok": False, "error": f"Unknown API route: {self.path}"}, HTTPStatus.NOT_FOUND)
            except Exception as exc:  # noqa: BLE001 - local tool should return actionable errors.
                self.write_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)

        def read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("JSON body must be an object.")
            return data

        def write_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return SyncTexReviewHandler


def handle_synctex_edit(payload: dict[str, Any]) -> dict[str, Any]:
    pdf_path = require_existing_path(payload.get("pdfPath"), "pdfPath")
    page = require_int(payload.get("page"), "page")
    x = require_float(payload.get("x"), "x")
    y = require_float(payload.get("y"), "y")
    result = run_synctex(["synctex", "edit", "-o", f"{page}:{x:.6f}:{y:.6f}:{pdf_path}"])
    matches = parse_synctex_output(result.stdout)
    if not matches:
        raise ValueError("SyncTeX did not return a source location.")
    first = matches[0]
    return {"ok": True, "matches": matches, **first}


def handle_synctex_view(payload: dict[str, Any]) -> dict[str, Any]:
    pdf_path = require_existing_path(payload.get("pdfPath"), "pdfPath")
    source_path = require_existing_path(payload.get("sourcePath"), "sourcePath")
    line = require_int(payload.get("line"), "line")
    column = require_int(payload.get("column", 1), "column")
    result = run_synctex(
        [
            "synctex",
            "view",
            "-i",
            f"{line}:{column}:{source_path}",
            "-o",
            str(pdf_path),
        ]
    )
    matches = parse_synctex_output(result.stdout)
    if not matches:
        raise ValueError("SyncTeX did not return a PDF location.")
    first = matches[0]
    return {"ok": True, "matches": matches, **first}


def handle_rebuild_preview(payload: dict[str, Any]) -> dict[str, Any]:
    script_path = Path(__file__).resolve().with_name("render_tex_preview.py")
    source_path = require_existing_path(payload.get("sourcePath"), "sourcePath")
    output_path = require_output_path(payload.get("outputPath"), "outputPath")
    tex_root = require_existing_dir(payload.get("texRoot"), "texRoot")
    title = str(payload.get("title") or "校对稿渲染预览")

    command = [
        sys.executable,
        str(script_path),
        "--source",
        str(source_path),
        "--output",
        str(output_path),
        "--title",
        title,
        "--tex-root",
        str(tex_root),
        "--build-pdf-preview",
    ]
    original_source = str(payload.get("originalSourcePath") or "").strip()
    if original_source:
        command.extend(["--original-source", str(require_existing_path(original_source, "originalSourcePath"))])

    result = subprocess.run(
        command,
        cwd=script_path.parent.parent.parent,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    if result.returncode != 0:
        tail = "\n".join((result.stderr or result.stdout).splitlines()[-40:])
        raise RuntimeError(tail or "Preview rebuild failed.")
    return {
        "ok": True,
        "outputPath": str(output_path),
        "stdoutTail": "\n".join(result.stdout.splitlines()[-12:]),
    }


def handle_build_chapter(
    payload: dict[str, Any],
    root: Path,
    project_root: Path,
    chapters_dir: Path,
) -> dict[str, Any]:
    chapter_id = str(payload.get("chapterId") or "").strip()
    if not chapter_id:
        raise ValueError("Missing required field: chapterId")

    catalog = discover_chapter_catalog(chapters_dir)
    chapter = next((item for item in catalog if item["id"] == chapter_id), None)
    if not chapter:
        raise ValueError(f"Unknown chapterId: {chapter_id}")

    original_key = str(payload.get("originalKey") or chapter["defaultOriginalKey"]).strip()
    target_key = str(payload.get("targetKey") or chapter["defaultTargetKey"]).strip()
    original = find_version(chapter["versions"], original_key)
    target = find_version(chapter["versions"], target_key)
    if not original:
        raise ValueError(f"Unknown originalKey for chapter {chapter_id}: {original_key}")
    if not target:
        raise ValueError(f"Unknown targetKey for chapter {chapter_id}: {target_key}")

    run_review_path = Path(__file__).resolve().with_name("run_review.py")
    output_name = build_output_name(chapter["baseStem"], original["key"], target["key"])
    title = f"{chapter['label']} 校对页"
    command = [
        sys.executable,
        str(run_review_path),
        "--source",
        original["path"],
        "--target",
        target["path"],
        "--name",
        output_name,
        "--title",
        title,
        "--output-dir",
        str(root),
        "--project-root",
        str(project_root),
        "--tex-root",
        str(project_root / "draft-tex-3扩写"),
        "--pretty",
    ]
    if bool(payload.get("buildPdfPreview")):
        command.append("--build-pdf-preview")

    result = subprocess.run(
        command,
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
        timeout=360,
    )
    if result.returncode != 0:
        tail = "\n".join((result.stderr or result.stdout).splitlines()[-60:])
        raise RuntimeError(summarize_build_error(tail or "Chapter build failed."))

    return {
        "ok": True,
        "chapterId": chapter_id,
        "originalKey": original_key,
        "targetKey": target_key,
        "outputName": output_name,
        "renderUrl": f"/{output_name}-render.html",
        "reviewUrl": f"/{output_name}-review.html",
        "stdoutTail": "\n".join(result.stdout.splitlines()[-12:]),
    }


def handle_import_chapters_dir(
    payload: dict[str, Any],
    current_chapters_dir: dict[str, Path],
    project_root: Path,
) -> dict[str, Any]:
    raw_dir = str(payload.get("chaptersDir") or "").strip()
    if not raw_dir:
        raise ValueError("Missing required field: chaptersDir")
    chapters_dir = Path(raw_dir).expanduser()
    if not chapters_dir.is_absolute():
        chapters_dir = (project_root / chapters_dir).resolve()
    else:
        chapters_dir = chapters_dir.resolve()
    if not chapters_dir.exists():
        raise ValueError(f"chaptersDir does not exist: {chapters_dir}")
    if not chapters_dir.is_dir():
        raise ValueError(f"chaptersDir must be a directory: {chapters_dir}")
    current_chapters_dir["path"] = chapters_dir
    catalog = discover_chapter_catalog(chapters_dir)
    return {"ok": True, "chaptersDir": str(chapters_dir), "chapterCount": len(catalog)}


def build_output_name(base_stem: str, original_key: str, target_key: str) -> str:
    stem = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff._-]+", "-", base_stem).strip("-._")
    original_part = re.sub(r"[^0-9A-Za-z._-]+", "-", original_key).strip("-._") or "source"
    target_part = re.sub(r"[^0-9A-Za-z._-]+", "-", target_key).strip("-._") or "target"
    stem = stem or "chapter"
    return f"{stem}__{original_part}__{target_part}"


def run_synctex(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or "SyncTeX command failed."
        raise RuntimeError(error)
    return result


def parse_synctex_output(output: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("This is SyncTeX") or line.startswith("SyncTeX result"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key == "Output" and current:
            matches.append(current)
            current = {}
        normalized = normalize_key(key)
        current[normalized] = normalize_value(value)
    if current:
        matches.append(current)
    return matches


def normalize_key(key: str) -> str:
    mapping = {
        "Output": "output",
        "Input": "input",
        "Line": "line",
        "Column": "column",
        "Offset": "offset",
        "Context": "context",
        "Page": "page",
        "x": "x",
        "y": "y",
        "h": "h",
        "v": "v",
        "W": "width",
        "H": "height",
    }
    return mapping.get(key, key)


def normalize_value(value: str) -> Any:
    if value == "":
        return value
    try:
        if "." not in value:
            return int(value)
        return float(value)
    except ValueError:
        return value


def require_existing_path(raw_value: Any, label: str) -> Path:
    if not raw_value:
        raise ValueError(f"Missing required field: {label}")
    path = Path(str(raw_value)).expanduser().resolve()
    if not path.exists():
        raise ValueError(f"{label} does not exist: {path}")
    return path


def require_existing_dir(raw_value: Any, label: str) -> Path:
    path = require_existing_path(raw_value, label)
    if not path.is_dir():
        raise ValueError(f"{label} must be a directory: {path}")
    return path


def require_output_path(raw_value: Any, label: str) -> Path:
    if not raw_value:
        raise ValueError(f"Missing required field: {label}")
    path = Path(str(raw_value)).expanduser().resolve()
    if not path.parent.exists():
        raise ValueError(f"{label} parent does not exist: {path.parent}")
    return path


def require_int(raw_value: Any, label: str) -> int:
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be an integer.") from exc
    if value <= 0:
        raise ValueError(f"{label} must be positive.")
    return value


def require_float(raw_value: Any, label: str) -> float:
    try:
        value = float(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a number.") from exc
    if value < 0:
        raise ValueError(f"{label} must be non-negative.")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
