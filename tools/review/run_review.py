#!/usr/bin/env python3
"""Run the full local review-page pipeline for one source/target pair."""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build compare JSON, review HTML, review log, and unified diff in one command."
    )
    parser.add_argument("--source", required=True, help="Path to the original .tex file.")
    parser.add_argument("--target", required=True, help="Path to the revised .tex file.")
    parser.add_argument("--name", default="review", help="Output name prefix, for example ch12.")
    parser.add_argument("--title", default="教材润色校对页", help="HTML page title.")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for generated outputs. Defaults to tools/review/outputs under project root.",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Project root used for relative file labels. Defaults to the book-polish folder.",
    )
    parser.add_argument("--pretty", action="store_true", help="Write indented compare-data JSON.")
    parser.add_argument(
        "--build-pdf-preview",
        action="store_true",
        help="Compile standalone SyncTeX PDFs and page PNGs for render.html.",
    )
    parser.add_argument(
        "--tex-root",
        default=None,
        help="TeX project root containing elegantbook.cls. Defaults to the book-polish folder.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    default_project_root = script_dir.parent.parent
    project_root = resolve_path(args.project_root, Path.cwd()) if args.project_root else default_project_root
    source_path = resolve_path(args.source, project_root)
    target_path = resolve_path(args.target, project_root)
    output_dir = resolve_path(args.output_dir, project_root) if args.output_dir else script_dir / "outputs"

    validate_tex_file(source_path, "source")
    validate_tex_file(target_path, "target")

    output_dir.mkdir(parents=True, exist_ok=True)
    compare_json = output_dir / f"{args.name}-compare-data.json"
    review_html = output_dir / f"{args.name}-review.html"
    review_log = output_dir / f"{args.name}-review-log.md"
    changes_diff = output_dir / f"{args.name}-changes.diff"
    test_html = output_dir / f"{args.name}-test.html"
    render_html = output_dir / f"{args.name}-render.html"

    build_command = [
        sys.executable,
        str(script_dir / "build_review.py"),
        "--source",
        str(source_path),
        "--target",
        str(target_path),
        "--output",
        str(compare_json),
        "--project-root",
        str(project_root),
    ]
    if args.pretty:
        build_command.append("--pretty")

    render_command = [
        sys.executable,
        str(script_dir / "render_review.py"),
        "--input",
        str(compare_json),
        "--output",
        str(review_html),
        "--log-output",
        str(review_log),
        "--diff-output",
        str(changes_diff),
        "--test-output",
        str(test_html),
        "--title",
        args.title,
    ]
    preview_command = [
        sys.executable,
        str(script_dir / "render_tex_preview.py"),
        "--source",
        str(target_path),
        "--original-source",
        str(source_path),
        "--output",
        str(render_html),
        "--title",
        f"{args.title} · 渲染预览",
    ]
    if args.tex_root:
        preview_command.extend(["--tex-root", str(resolve_path(args.tex_root, project_root))])
    if args.build_pdf_preview:
        preview_command.append("--build-pdf-preview")

    run_step("Build compare data", build_command, cwd=project_root)
    run_step("Render review outputs", render_command, cwd=project_root)
    run_step("Render polished preview", preview_command, cwd=project_root)
    print()
    print("Review outputs:")
    print(f"- compare-data: {compare_json}")
    print(f"- review-html:  {review_html}")
    print(f"- review-log:   {review_log}")
    print(f"- changes-diff: {changes_diff}")
    print(f"- test-html:    {test_html}")
    print(f"- render-html:  {render_html}")
    return 0


def resolve_path(raw_path: str | None, base: Path) -> Path:
    if raw_path is None:
        return base.resolve()
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def validate_tex_file(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"{label} file not found: {path}")
    if path.suffix.lower() != ".tex":
        raise SystemExit(f"{label} file must be a .tex file: {path}")


def run_step(label: str, command: list[str], cwd: Path) -> None:
    print(f"==> {label}", flush=True)
    print(" ".join(shlex.quote(item) for item in command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


if __name__ == "__main__":
    raise SystemExit(main())
