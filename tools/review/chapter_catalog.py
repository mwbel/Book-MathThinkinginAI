#!/usr/bin/env python3
"""Discover chapter/version combinations for the local review tool."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


VARIANT_RE = re.compile(
    r"^(?P<base>.+?)(?:[_-](?P<tag>refined|temp|expanded|conservative|polished\d*|clean))(?P<tail>(?:[_-]clean)?)$"
)
VERSION_RE = re.compile(r"\.v\d+(?:\.\d+)?$", re.IGNORECASE)
LEADING_NUMBER_RE = re.compile(r"^(?P<number>\d{1,3})(?:[-_ ]|$)")


def discover_chapter_catalog(chapters_dir: Path) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for path in sorted(chapters_dir.rglob("*.tex")):
        if not path.is_file():
            continue
        stem = path.stem
        base_stem, variant_key = split_variant(stem)
        entry = grouped.setdefault(
            base_stem,
            {
                "id": slugify(base_stem),
                "baseStem": base_stem,
                "label": build_chapter_label(base_stem),
                "sortKey": build_sort_key(base_stem),
                "versions": [],
            },
        )
        entry["versions"].append(
            {
                "key": variant_key,
                "label": variant_label(variant_key),
                "fileName": path.name,
                "path": str(path.resolve()),
                "sortScore": version_sort_score(variant_key),
            }
        )

    catalog: list[dict[str, Any]] = []
    for entry in grouped.values():
        entry["versions"].sort(key=lambda item: item["sortScore"], reverse=True)
        for item in entry["versions"]:
            item.pop("sortScore", None)
        default_original = choose_default_original(entry["versions"])
        default_target = choose_default_target(entry["versions"], default_original)
        entry["defaultOriginalKey"] = default_original["key"]
        entry["defaultTargetKey"] = default_target["key"]
        catalog.append(entry)

    catalog.sort(key=lambda item: item["sortKey"])
    for entry in catalog:
        entry.pop("sortKey", None)
    return catalog


def split_variant(stem: str) -> tuple[str, str]:
    match = VARIANT_RE.match(stem)
    if not match:
        return stem, "plain"
    key = match.group("tag")
    if match.group("tail"):
        key = f"{key}_clean"
    return match.group("base"), key


def build_chapter_label(base_stem: str) -> str:
    stripped = VERSION_RE.sub("", base_stem)
    number_match = LEADING_NUMBER_RE.match(stripped)
    if not number_match:
        return stripped
    number = number_match.group("number")
    title = stripped[number_match.end() :].strip("-_ ")
    if not title:
        return number
    return f"{number} · {title}"


def build_sort_key(base_stem: str) -> tuple[int, str]:
    stripped = VERSION_RE.sub("", base_stem)
    number_match = LEADING_NUMBER_RE.match(stripped)
    if not number_match:
        return (999, stripped.lower())
    return (int(number_match.group("number")), stripped.lower())


def slugify(value: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff._-]+", "-", value).strip("-._")
    slug = re.sub(r"-{2,}", "-", slug)
    return slug or "chapter"


def variant_label(key: str) -> str:
    if key == "plain":
        return "当前稿"
    if key == "refined":
        return "refined"
    if key == "temp":
        return "temp"
    if key == "expanded":
        return "expanded"
    if key == "conservative":
        return "conservative"
    if key == "clean":
        return "clean"
    if key.startswith("polished"):
        return key.replace("_", " ")
    return key


def version_sort_score(key: str) -> tuple[int, int]:
    if key == "plain":
        return (30, 0)
    if key == "refined":
        return (60, 0)
    if key == "clean":
        return (80, 0)
    if key == "expanded":
        return (20, 0)
    if key == "conservative":
        return (18, 0)
    if key == "temp":
        return (10, 0)
    if key.startswith("polished"):
        polished_match = re.match(r"^polished(?P<num>\d*)(?P<clean>_clean)?$", key)
        if polished_match:
            raw_num = polished_match.group("num")
            number = int(raw_num) if raw_num else -1
            clean_bonus = 1 if polished_match.group("clean") else 0
            return (100 + clean_bonus, number)
    return (0, 0)


def choose_default_original(versions: list[dict[str, Any]]) -> dict[str, Any]:
    for preferred in ("refined", "plain", "conservative", "expanded", "temp", "clean"):
        match = find_version(versions, preferred)
        if match:
            return match
    return versions[0]


def choose_default_target(
    versions: list[dict[str, Any]],
    default_original: dict[str, Any],
) -> dict[str, Any]:
    preferred = sorted(versions, key=lambda item: version_sort_score(item["key"]), reverse=True)
    for candidate in preferred:
        if candidate["key"] != default_original["key"] or len(versions) == 1:
            return candidate
    return preferred[0]


def find_version(versions: list[dict[str, Any]], key: str) -> dict[str, Any] | None:
    for item in versions:
        if item["key"] == key:
            return item
    return None
