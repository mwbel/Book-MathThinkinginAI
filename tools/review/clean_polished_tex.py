#!/usr/bin/env python3
"""Clean process-marked polished LaTeX into a plain revised .tex file."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ORIGINAL_MARKER_RE = re.compile(r"^\s*原文：\s*$")
REVISED_MARKER_RE = re.compile(r"^\s*%\s*修改后版本：\s*$")
SUGGESTION_COMMENT_RE = re.compile(r"^\s*%\s*ChatGPT建议：")
SECTION_DIVIDER_RE = re.compile(r"^\s*%\s*(=+|——)")
TEX_METADATA_RE = re.compile(r"^\s*%\s*!TEX\b", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean process-marked polished LaTeX into a plain .tex file.")
    parser.add_argument("--input", required=True, help="Input process-marked polished .tex file.")
    parser.add_argument("--output", required=True, help="Output clean polished .tex file.")
    parser.add_argument("--force", action="store_true", help="Overwrite output if it already exists.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")
    if input_path.suffix.lower() != ".tex":
        raise SystemExit(f"Input file must be a .tex file: {input_path}")
    if output_path.exists() and not args.force:
        raise SystemExit(f"Output already exists, use --force to overwrite: {output_path}")

    source = input_path.read_text(encoding="utf-8")
    cleaned, stats = clean_polished_tex(source)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(cleaned, encoding="utf-8")

    print(f"Wrote {output_path}")
    print(
        "Removed {original_blocks} original blocks, {suggestions} suggestion comments, "
        "{revised_markers} revised markers, {dividers} divider comments.".format(**stats)
    )
    print(f"Output lines: {len(cleaned.splitlines())}")
    return 0


def clean_polished_tex(source: str) -> tuple[str, dict[str, int]]:
    lines = source.splitlines(keepends=True)
    output: list[str] = []
    skipping_original = False
    stats = {
        "original_blocks": 0,
        "suggestions": 0,
        "revised_markers": 0,
        "dividers": 0,
    }

    for line in lines:
        stripped = line.strip()

        if TEX_METADATA_RE.match(line):
            output.append(line)
            continue

        if ORIGINAL_MARKER_RE.match(line):
            skipping_original = True
            stats["original_blocks"] += 1
            trim_trailing_blank_lines(output, keep=1)
            continue

        if REVISED_MARKER_RE.match(line):
            skipping_original = False
            stats["revised_markers"] += 1
            trim_trailing_blank_lines(output, keep=1)
            continue

        if SUGGESTION_COMMENT_RE.match(line):
            stats["suggestions"] += 1
            continue

        if SECTION_DIVIDER_RE.match(line):
            stats["dividers"] += 1
            continue

        if skipping_original:
            continue

        if not output and not stripped:
            continue

        output.append(line)

    cleaned = "".join(output)
    cleaned = normalize_excess_blank_lines(cleaned)
    if cleaned and not cleaned.endswith("\n"):
        cleaned += "\n"
    return cleaned, stats


def trim_trailing_blank_lines(lines: list[str], keep: int) -> None:
    blank_count = 0
    index = len(lines) - 1
    while index >= 0 and not lines[index].strip():
        blank_count += 1
        index -= 1
    remove_count = max(blank_count - keep, 0)
    if remove_count:
        del lines[-remove_count:]


def normalize_excess_blank_lines(text: str) -> str:
    return re.sub(r"\n{4,}", "\n\n\n", text)


if __name__ == "__main__":
    raise SystemExit(main())
