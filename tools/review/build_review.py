#!/usr/bin/env python3
"""Build paragraph-level review data from a LaTeX source file.

This first-pass parser is deliberately conservative. It protects common
LaTeX environments as opaque blocks, recognizes sectioning commands, and
splits normal prose by blank lines. It does not rewrite source files.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SECTION_LEVELS = {
    "part": 0,
    "chapter": 1,
    "section": 2,
    "subsection": 3,
    "subsubsection": 4,
    "paragraph": 5,
}

PROTECTED_ENVIRONMENTS = {
    "equation",
    "equation*",
    "align",
    "align*",
    "gather",
    "gather*",
    "multline",
    "multline*",
    "figure",
    "figure*",
    "table",
    "table*",
    "itemize",
    "enumerate",
    "description",
    "quote",
    "quotation",
    "center",
    "verbatim",
    "lstlisting",
    "tikzpicture",
}

SECTION_RE = re.compile(
    r"^\\(?P<name>part|chapter|section|subsection|subsubsection|paragraph)\*?"
    r"(?:\[[^\]]*\])?\{(?P<title>.*)\}\s*$"
)
BEGIN_END_RE = re.compile(r"\\(?P<kind>begin|end)\s*\{(?P<env>[^}]+)\}")
LATEX_COMMENT_RE = re.compile(r"^\s*%")
LATEX_METADATA_COMMENT_RE = re.compile(r"^\s*%\s*!TEX\b", re.IGNORECASE)
DIFF_TOKEN_RE = re.compile(
    r"[\u4e00-\u9fff]"
    r"|\\[A-Za-z]+\*?"
    r"|[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*"
    r"|\s+"
    r"|.",
    re.DOTALL,
)


@dataclass
class Block:
    type: str
    content: str
    start_line: int
    end_line: int
    section_path: list[dict[str, Any]]
    env: str | None = None
    title: str | None = None
    level: int | None = None
    id: str = ""

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "startLine": self.start_line,
            "endLine": self.end_line,
            "sectionPath": self.section_path,
            "charCount": len(self.content),
        }
        if self.env:
            data["environment"] = self.env
        if self.title is not None:
            data["title"] = self.title
        if self.level is not None:
            data["level"] = self.level
        return data


@dataclass
class ParserState:
    blocks: list[Block] = field(default_factory=list)
    section_stack: list[dict[str, Any]] = field(default_factory=list)
    paragraph_lines: list[tuple[int, str]] = field(default_factory=list)
    environment_lines: list[tuple[int, str]] = field(default_factory=list)
    environment_stack: list[str] = field(default_factory=list)
    current_environment: str | None = None


def parse_latex(source_text: str) -> list[Block]:
    state = ParserState()
    lines = source_text.splitlines()

    for line_number, line in enumerate(lines, start=1):
        if state.environment_stack:
            state.environment_lines.append((line_number, line))
            update_environment_stack(state, line)
            if not state.environment_stack:
                flush_environment(state)
            continue

        section = parse_section_line(line)
        if section:
            flush_paragraph(state)
            update_section_stack(state, section, line_number)
            state.blocks.append(
                Block(
                    type="section",
                    content=line,
                    start_line=line_number,
                    end_line=line_number,
                    section_path=current_section_path(state),
                    title=section["title"],
                    level=section["level"],
                )
            )
            continue

        if starts_protected_environment(line):
            flush_paragraph(state)
            state.environment_lines.append((line_number, line))
            update_environment_stack(state, line)
            if not state.environment_stack:
                flush_environment(state)
            continue

        comment_type = latex_comment_type(line)
        if comment_type:
            flush_paragraph(state)
            state.blocks.append(
                Block(
                    type=comment_type,
                    content=line.strip(),
                    start_line=line_number,
                    end_line=line_number,
                    section_path=current_section_path(state),
                )
            )
            continue

        if not line.strip():
            flush_paragraph(state)
            continue

        state.paragraph_lines.append((line_number, line))

    flush_paragraph(state)
    if state.environment_lines:
        flush_environment(state, forced=True)

    assign_block_ids(state.blocks)
    return state.blocks


def parse_section_line(line: str) -> dict[str, Any] | None:
    match = SECTION_RE.match(line.strip())
    if not match:
        return None
    name = match.group("name")
    title = match.group("title").strip()
    return {
        "command": name,
        "level": SECTION_LEVELS[name],
        "title": title,
    }


def update_section_stack(state: ParserState, section: dict[str, Any], line_number: int) -> None:
    level = int(section["level"])
    state.section_stack = [item for item in state.section_stack if int(item["level"]) < level]
    state.section_stack.append(
        {
            "level": level,
            "command": section["command"],
            "title": section["title"],
            "line": line_number,
        }
    )


def current_section_path(state: ParserState) -> list[dict[str, Any]]:
    return [dict(item) for item in state.section_stack]


def starts_protected_environment(line: str) -> bool:
    for match in BEGIN_END_RE.finditer(line):
        if match.group("kind") == "begin" and match.group("env") in PROTECTED_ENVIRONMENTS:
            return True
    return False


def latex_comment_type(line: str) -> str | None:
    if not LATEX_COMMENT_RE.match(line):
        return None
    if LATEX_METADATA_COMMENT_RE.match(line):
        return "metadata"
    return "comment"


def update_environment_stack(state: ParserState, line: str) -> None:
    for match in BEGIN_END_RE.finditer(line):
        kind = match.group("kind")
        env = match.group("env")
        if env not in PROTECTED_ENVIRONMENTS:
            continue
        if kind == "begin":
            if not state.environment_stack:
                state.current_environment = env
            state.environment_stack.append(env)
        elif state.environment_stack:
            if state.environment_stack[-1] == env:
                state.environment_stack.pop()
            elif env in state.environment_stack:
                state.environment_stack.remove(env)


def flush_paragraph(state: ParserState) -> None:
    if not state.paragraph_lines:
        return
    start_line = state.paragraph_lines[0][0]
    end_line = state.paragraph_lines[-1][0]
    content = "\n".join(line for _, line in state.paragraph_lines).strip()
    if content:
        state.blocks.append(
            Block(
                type="paragraph",
                content=content,
                start_line=start_line,
                end_line=end_line,
                section_path=current_section_path(state),
            )
        )
    state.paragraph_lines = []


def flush_environment(state: ParserState, forced: bool = False) -> None:
    if not state.environment_lines:
        return
    start_line = state.environment_lines[0][0]
    end_line = state.environment_lines[-1][0]
    content = "\n".join(line for _, line in state.environment_lines).strip()
    env = state.current_environment or infer_first_environment(content)
    state.blocks.append(
        Block(
            type="environment" if not forced else "environment_unclosed",
            env=env,
            content=content,
            start_line=start_line,
            end_line=end_line,
            section_path=current_section_path(state),
        )
    )
    state.environment_lines = []
    state.environment_stack = []
    state.current_environment = None


def infer_first_environment(content: str) -> str | None:
    match = BEGIN_END_RE.search(content)
    if match and match.group("kind") == "begin":
        return match.group("env")
    return None


def assign_block_ids(blocks: list[Block]) -> None:
    counters: dict[str, int] = {}
    for block in blocks:
        counters[block.type] = counters.get(block.type, 0) + 1
        digest = hashlib.sha1(block.content.encode("utf-8")).hexdigest()[:10]
        block.id = f"{block.type}-{counters[block.type]:04d}-{digest}"


def build_review_data(source_path: Path, project_root: Path | None = None) -> dict[str, Any]:
    text = source_path.read_text(encoding="utf-8")
    blocks = parse_latex(text)
    sections = build_sections(blocks)
    root = project_root or source_path.parent
    try:
        relative_source = str(source_path.relative_to(root))
    except ValueError:
        relative_source = str(source_path)
    return {
        "version": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceFile": relative_source,
        "sourceFileAbsolute": str(source_path),
        "parser": {
            "name": "tools/review/build_review.py",
            "strategy": "section_commands + protected_environments + blank_line_paragraphs",
        },
        "summary": summarize_blocks(blocks),
        "sections": sections,
        "blocks": [block.to_dict() for block in blocks],
    }


def build_sections(blocks: list[Block]) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    section_by_key: dict[str, dict[str, Any]] = {}

    for block in blocks:
        if block.type == "section":
            key = section_key(block.section_path)
            section_by_key[key] = {
                "id": block.id,
                "level": block.level,
                "title": block.title,
                "startLine": block.start_line,
                "endLine": block.end_line,
                "path": block.section_path,
                "blockIds": [],
            }
            sections.append(section_by_key[key])
            continue

        if not block.section_path:
            key = "__front_matter__"
            if key not in section_by_key:
                section_by_key[key] = {
                    "id": "front-matter",
                    "level": -1,
                    "title": "Front Matter",
                    "startLine": block.start_line,
                    "endLine": block.end_line,
                    "path": [],
                    "blockIds": [],
                }
                sections.append(section_by_key[key])
        else:
            key = section_key(block.section_path)
            if key not in section_by_key:
                current = block.section_path[-1]
                section_by_key[key] = {
                    "id": f"section-implicit-{len(section_by_key) + 1}",
                    "level": current["level"],
                    "title": current["title"],
                    "startLine": current["line"],
                    "endLine": block.end_line,
                    "path": block.section_path,
                    "blockIds": [],
                }
                sections.append(section_by_key[key])

        section = section_by_key[key]
        section["blockIds"].append(block.id)
        section["endLine"] = block.end_line

    return sections


def section_key(section_path: list[dict[str, Any]]) -> str:
    return " / ".join(f"{item['level']}:{item['title']}:{item['line']}" for item in section_path)


def summarize_blocks(blocks: list[Block]) -> dict[str, int]:
    return {
        "blockCount": len(blocks),
        "sectionCount": sum(1 for block in blocks if block.type == "section"),
        "paragraphCount": sum(1 for block in blocks if block.type == "paragraph"),
        "environmentCount": sum(1 for block in blocks if block.type.startswith("environment")),
        "metadataCount": sum(1 for block in blocks if block.type == "metadata"),
        "commentCount": sum(1 for block in blocks if block.type == "comment"),
    }


def build_compare_data(source_path: Path, target_path: Path, project_root: Path | None = None) -> dict[str, Any]:
    source_text = source_path.read_text(encoding="utf-8")
    target_text = target_path.read_text(encoding="utf-8")
    source_blocks = parse_latex(source_text)
    target_blocks = parse_latex(target_text)
    pairs = match_blocks(source_blocks, target_blocks)
    root = project_root or source_path.parent
    return {
        "version": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceFile": relative_path(source_path, root),
        "targetFile": relative_path(target_path, root),
        "sourceFileAbsolute": str(source_path),
        "targetFileAbsolute": str(target_path),
        "parser": {
            "name": "tools/review/build_review.py",
            "strategy": "section_commands + protected_environments + blank_line_paragraphs",
        },
        "compare": {
            "strategy": "sequence_matcher_on_block_signatures_then_ordered_replace_pairing",
            "summary": summarize_pairs(pairs),
            "pairs": pairs,
        },
        "source": {
            "summary": summarize_blocks(source_blocks),
            "sections": build_sections(source_blocks),
            "blocks": [block.to_dict() for block in source_blocks],
        },
        "target": {
            "summary": summarize_blocks(target_blocks),
            "sections": build_sections(target_blocks),
            "blocks": [block.to_dict() for block in target_blocks],
        },
    }


def relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def match_blocks(source_blocks: list[Block], target_blocks: list[Block]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    source_signatures = [block_signature(block) for block in source_blocks]
    target_signatures = [block_signature(block) for block in target_blocks]
    matcher = difflib.SequenceMatcher(a=source_signatures, b=target_signatures, autojunk=False)

    for tag, source_start, source_end, target_start, target_end in matcher.get_opcodes():
        source_slice = source_blocks[source_start:source_end]
        target_slice = target_blocks[target_start:target_end]
        if tag == "equal":
            for source_block, target_block in zip(source_slice, target_slice):
                pairs.append(make_pair(source_block, target_block))
            continue
        if tag == "delete":
            pairs.extend(make_pair(source_block, None) for source_block in source_slice)
            continue
        if tag == "insert":
            pairs.extend(make_pair(None, target_block) for target_block in target_slice)
            continue

        pairs.extend(pair_replace_slice(source_slice, target_slice))

    for index, pair in enumerate(pairs, start=1):
        pair["id"] = f"pair-{index:04d}"
    return pairs


def pair_replace_slice(source_slice: list[Block], target_slice: list[Block]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    source_index = 0
    target_index = 0
    while source_index < len(source_slice) and target_index < len(target_slice):
        source_block = source_slice[source_index]
        target_block = target_slice[target_index]
        if blocks_are_pairable(source_block, target_block) and blocks_are_similar_enough(source_block, target_block):
            pairs.append(make_pair(source_block, target_block))
            source_index += 1
            target_index += 1
            continue

        match_index = find_similar_target_index(source_block, target_slice, target_index)
        if match_index is not None:
            while target_index < match_index:
                pairs.append(make_pair(None, target_slice[target_index]))
                target_index += 1
            pairs.append(make_pair(source_block, target_slice[target_index]))
            source_index += 1
            target_index += 1
            continue

        pairs.append(make_pair(source_block, None))
        source_index += 1

    while source_index < len(source_slice):
        pairs.append(make_pair(source_slice[source_index], None))
        source_index += 1
    while target_index < len(target_slice):
        pairs.append(make_pair(None, target_slice[target_index]))
        target_index += 1
    return pairs


def blocks_are_pairable(source_block: Block, target_block: Block) -> bool:
    if source_block.type != target_block.type:
        return False
    if source_block.type == "environment":
        return source_block.env == target_block.env
    if source_block.type == "section":
        return source_block.level == target_block.level
    return True


def find_similar_target_index(source_block: Block, target_slice: list[Block], start_index: int) -> int | None:
    best_index: int | None = None
    best_score = 0.0
    for index in range(start_index, min(len(target_slice), start_index + 8)):
        target_block = target_slice[index]
        if not blocks_are_pairable(source_block, target_block):
            continue
        score = block_similarity(source_block, target_block)
        if score > best_score:
            best_score = score
            best_index = index
    if best_index is None:
        return None
    return best_index if best_score >= similarity_threshold(source_block) else None


def blocks_are_similar_enough(source_block: Block, target_block: Block) -> bool:
    return block_similarity(source_block, target_block) >= similarity_threshold(source_block)


def block_similarity(source_block: Block, target_block: Block) -> float:
    source = normalize_for_matching(source_block.content)
    target = normalize_for_matching(target_block.content)
    if source == target:
        return 1.0
    return difflib.SequenceMatcher(a=source, b=target, autojunk=False).ratio()


def similarity_threshold(block: Block) -> float:
    if block.type == "section":
        return 0.72
    if block.type == "environment":
        return 0.45
    if block.type in {"metadata", "comment"}:
        return 0.9
    return 0.34


def make_pair(source_block: Block | None, target_block: Block | None) -> dict[str, Any]:
    source_content = source_block.content if source_block else ""
    target_content = target_block.content if target_block else ""
    if source_block and target_block:
        status = "unchanged" if source_content == target_content and source_block.type == target_block.type else "changed"
    elif source_block:
        status = "removed"
    else:
        status = "added"

    return {
        "id": "",
        "status": status,
        "blockType": source_block.type if source_block else target_block.type if target_block else "unknown",
        "sectionPath": source_block.section_path if source_block else target_block.section_path if target_block else [],
        "sourceBlock": source_block.to_dict() if source_block else None,
        "targetBlock": target_block.to_dict() if target_block else None,
        "diffStats": diff_stats(source_content, target_content),
        "diff": [] if status == "unchanged" else token_diff(source_content, target_content),
        "note": "",
    }


def summarize_pairs(pairs: list[dict[str, Any]]) -> dict[str, int]:
    summary = {
        "pairCount": len(pairs),
        "unchangedCount": 0,
        "changedCount": 0,
        "addedCount": 0,
        "removedCount": 0,
    }
    for pair in pairs:
        status = pair.get("status")
        if status == "unchanged":
            summary["unchangedCount"] += 1
        elif status == "changed":
            summary["changedCount"] += 1
        elif status == "added":
            summary["addedCount"] += 1
        elif status == "removed":
            summary["removedCount"] += 1
    return summary


def block_signature(block: Block) -> str:
    if block.type == "section":
        return f"section:{block.level}:{normalize_for_matching(block.content)}"
    if block.type == "environment":
        return f"environment:{block.env}:{normalize_for_matching(block.content)}"
    return f"{block.type}:{normalize_for_matching(block.content)}"


def normalize_for_matching(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def diff_stats(source: str, target: str) -> dict[str, Any]:
    source_tokens = tokenize_for_diff(source)
    target_tokens = tokenize_for_diff(target)
    matcher = difflib.SequenceMatcher(a=source_tokens, b=target_tokens, autojunk=False)
    equal = inserted = deleted = replaced = 0
    for tag, source_start, source_end, target_start, target_end in matcher.get_opcodes():
        source_len = source_end - source_start
        target_len = target_end - target_start
        if tag == "equal":
            equal += source_len
        elif tag == "insert":
            inserted += target_len
        elif tag == "delete":
            deleted += source_len
        elif tag == "replace":
            replaced += max(source_len, target_len)
    return {
        "sourceCharCount": len(source),
        "targetCharCount": len(target),
        "sourceTokenCount": len(source_tokens),
        "targetTokenCount": len(target_tokens),
        "equalTokenCount": equal,
        "insertedTokenCount": inserted,
        "deletedTokenCount": deleted,
        "replacedTokenCount": replaced,
        "similarity": round(matcher.ratio(), 4),
    }


def token_diff(source: str, target: str) -> list[dict[str, str]]:
    source_tokens = tokenize_for_diff(source)
    target_tokens = tokenize_for_diff(target)
    matcher = difflib.SequenceMatcher(a=source_tokens, b=target_tokens, autojunk=False)
    diff: list[dict[str, str]] = []
    for tag, source_start, source_end, target_start, target_end in matcher.get_opcodes():
        if tag == "equal":
            diff.append({"op": "equal", "text": "".join(source_tokens[source_start:source_end])})
        elif tag == "delete":
            diff.append({"op": "delete", "text": "".join(source_tokens[source_start:source_end])})
        elif tag == "insert":
            diff.append({"op": "insert", "text": "".join(target_tokens[target_start:target_end])})
        elif tag == "replace":
            diff.append({"op": "delete", "text": "".join(source_tokens[source_start:source_end])})
            diff.append({"op": "insert", "text": "".join(target_tokens[target_start:target_end])})
    return [item for item in diff if item["text"]]


def tokenize_for_diff(text: str) -> list[str]:
    return DIFF_TOKEN_RE.findall(text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build paragraph-level review JSON from LaTeX source files.")
    parser.add_argument("--source", required=True, help="Path to the source .tex file.")
    parser.add_argument("--target", default=None, help="Optional revised/target .tex file for pairwise comparison.")
    parser.add_argument("--output", required=True, help="Path to write review-data.json.")
    parser.add_argument(
        "--project-root",
        default=None,
        help="Optional project root used to render sourceFile as a relative path.",
    )
    parser.add_argument("--pretty", action="store_true", help="Write indented JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_path = Path(args.source).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    project_root = Path(args.project_root).expanduser().resolve() if args.project_root else None

    if not source_path.exists():
        raise SystemExit(f"Source file not found: {source_path}")
    if source_path.suffix.lower() != ".tex":
        raise SystemExit(f"Source file must be a .tex file: {source_path}")

    target_path = Path(args.target).expanduser().resolve() if args.target else None
    if target_path:
        if not target_path.exists():
            raise SystemExit(f"Target file not found: {target_path}")
        if target_path.suffix.lower() != ".tex":
            raise SystemExit(f"Target file must be a .tex file: {target_path}")
        data = build_compare_data(source_path, target_path, project_root=project_root)
    else:
        data = build_review_data(source_path, project_root=project_root)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2 if args.pretty else None) + "\n",
        encoding="utf-8",
    )
    if target_path:
        summary = data["compare"]["summary"]
        print(
            "Wrote {output} ({pairs} pairs, {changed} changed, {added} added, {removed} removed)".format(
                output=output_path,
                pairs=summary["pairCount"],
                changed=summary["changedCount"],
                added=summary["addedCount"],
                removed=summary["removedCount"],
            )
        )
    else:
        print(
            "Wrote {output} ({blocks} blocks, {sections} sections, {paragraphs} paragraphs, {envs} environments)".format(
                output=output_path,
                blocks=data["summary"]["blockCount"],
                sections=data["summary"]["sectionCount"],
                paragraphs=data["summary"]["paragraphCount"],
                envs=data["summary"]["environmentCount"],
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
