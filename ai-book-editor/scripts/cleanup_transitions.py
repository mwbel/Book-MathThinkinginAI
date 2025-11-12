#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove stiff transition phrases like "为承接上一节，本文在此部分集中讨论“...”" across chapters.
- Target: draft-tex/chapters/*.tex (latest and plain)
- Replace with neutral phrasing: "本节聚焦“...”" and drop trailing "，并与前文观点保持一致。"
- Add % **MOD** 标注 on modified lines
"""
import re
from pathlib import Path

ROOT = Path('/Users/Min369/Desktop/书/书稿打磨')
CHAPTERS = ROOT / 'draft-tex' / 'chapters'

PAT = re.compile(r'(?:^|\s)为承接上一节，本文在此部分集中讨论“([^”]+)”(?:，并与前文观点保持一致。)?')


def process(path: Path):
    text = path.read_text(encoding='utf-8', errors='ignore')
    count = 0
    def repl(m):
        nonlocal count
        count += 1
        topic = m.group(1)
        return f" 本节聚焦“{topic}”。% **MOD** 删除生硬承接"
    new = PAT.sub(repl, text)
    if new != text:
        path.write_text(new, encoding='utf-8')
    return count


def main():
    files = list(CHAPTERS.glob('*.tex'))
    total = 0
    details = []
    for p in files:
        c = process(p)
        if c:
            details.append((p.name, c))
            total += c
    print('已移除生硬承接措辞：', total)
    for name, c in details:
        print(f"{name}\t{c}")

if __name__ == '__main__':
    main()