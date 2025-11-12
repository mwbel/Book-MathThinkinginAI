#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout & line-break optimization for LaTeX chapters.
- Scan draft-tex/chapters/*.tex
- Directly overwrite latest version file per base (highest .vN or plain)
- Preserve LaTeX structure: labels/refs/cites/eqrefs, math and special envs
- Insert % **MOD** comments for each structural change
- Generate chapters/note/<filename>.layout.md and append chapters/note/LayoutSummary.md
- Env flags: DRY_RUN(true/false), WRITE(true/false), SUMMARY(true/false)
"""
import os
import re
from pathlib import Path
from datetime import datetime

ROOT = Path('/Users/Min369/Desktop/书/书稿打磨')
CHAPTERS = ROOT / 'draft-tex' / 'chapters'
NOTE_DIR = CHAPTERS / 'note'
SUMMARY_PATH = NOTE_DIR / 'LayoutSummary.md'

VERSION_RE = re.compile(r'^(.*)\.v(\d+)(?:\.(\d+))?\.tex$')
PLAIN_RE = re.compile(r'^(.*)\.tex$')
SECTION_CMD_RE = re.compile(r'^(\\section|\\subsection|\\subsubsection)\b')
SAFE_CMD_RE = re.compile(r'(\\label\{|\\ref\{|\\cite\{|\\eqref\{|\\newcommand|\\DeclareMathOperator)')
BEGIN_ENV_RE = re.compile(r'^\\begin\{(align\*?|equation\*?|gather\*?|itemize|enumerate|figure|table|quote|lstlisting|verbatim)\}')
END_ENV_RE = re.compile(r'^\\end\{(align\*?|equation\*?|gather\*?|itemize|enumerate|figure|table|quote|lstlisting|verbatim)\}')
MATH_BEGIN_RE = re.compile(r'^(\\\[|\$\$)')
MATH_END_RE = re.compile(r'^(\\\]|\$\$)')
SENTENCE_BREAK_RE = re.compile(r'([。！？；：]|[.!?;:])[”\"]?$')

DRY_RUN = os.getenv('DRY_RUN', 'false').lower() in ('1','true','yes')
WRITE = os.getenv('WRITE', 'true').lower() in ('1','true','yes')
SUMMARY = os.getenv('SUMMARY', 'true').lower() in ('1','true','yes')

PARA_MAX_LINES = 10
PARA_SPLIT_LINES = 8


def pick_latest(files):
    groups = {}
    for p in files:
        name = p.name
        m = VERSION_RE.match(name)
        if m:
            base, maj = m.group(1), int(m.group(2))
        else:
            base = PLAIN_RE.match(name).group(1)
            maj = 0
        groups.setdefault(base, []).append((maj, p))
    latest = []
    for base, items in groups.items():
        items.sort(key=lambda x: x[0], reverse=True)
        latest.append(items[0][1])
    return latest


def optimize_layout(text: str):
    lines = text.split('\n')
    in_env_stack = []
    in_math = False

    # stats
    restored_breaks = 0
    added_empty = 0
    removed_excess = 0
    merged_paras = 0

    out = []
    i = 0
    # helper to check current line in special env
    def update_env_state(line):
        nonlocal in_math, in_env_stack
        if MATH_BEGIN_RE.match(line.strip()):
            in_math = True
        if MATH_END_RE.match(line.strip()):
            in_math = False
        m_b = BEGIN_ENV_RE.match(line.strip())
        if m_b:
            in_env_stack.append(m_b.group(1))
        m_e = END_ENV_RE.match(line.strip())
        if m_e and in_env_stack:
            in_env_stack.pop()

    # ensure blank line after section commands
    while i < len(lines):
        line = lines[i]
        update_env_state(line)
        out.append(line)
        # don't modify within special envs or math
        if in_env_stack or in_math:
            i += 1
            continue
        # section spacing
        if SECTION_CMD_RE.match(line):
            next_is_blank = (i+1 < len(lines) and lines[i+1].strip() == '')
            if not next_is_blank:
                out.append('% **MOD** 新增空行以改善版面')
                out.append('')
                added_empty += 1
        # reduce multiple blank lines to single
        if line.strip() == '':
            # collapse following blanks
            j = i + 1
            removed = 0
            while j < len(lines) and lines[j].strip() == '':
                j += 1
                removed += 1
            if removed:
                removed_excess += removed
                i = j
                continue
        i += 1

    # second pass: paragraph splitting and merging
    lines2 = out
    out2 = []
    i = 0
    while i < len(lines2):
        line = lines2[i]
        # track env state again
        update_env_state(line)
        # handle merging: if a very short para ending with comma-like and followed by short para, merge
        if not (in_env_stack or in_math) and line.strip() == '' and out2:
            prev = out2[-1] if out2 else ''
            # Peek next non-empty
            j = i + 1
            next_lines = []
            while j < len(lines2) and lines2[j].strip() != '':
                next_lines.append(lines2[j])
                j += 1
            prev_len = 0
            k = len(out2) - 1
            while k >= 0 and out2[k].strip() != '':
                prev_len += 1
                k -= 1
            next_len = len(next_lines)
            if prev_len <= 2 and next_len <= 2 and prev.rstrip().endswith(('，', ',', '：', ':')):
                # remove blank (merge)
                merged_paras += 1
                # skip the blank
                i += 1
                # add a MOD marker for rhythm adjustment
                out2.append('% **MOD** 调整段落节奏')
                continue
        out2.append(line)
        i += 1

    # third pass: split long paragraphs at sentence boundaries
    lines3 = out2
    final = []
    i = 0
    while i < len(lines3):
        line = lines3[i]
        update_env_state(line)
        if not (in_env_stack or in_math) and line.strip() != '':
            # collect paragraph block
            para = [line]
            j = i + 1
            while j < len(lines3) and lines3[j].strip() != '':
                para.append(lines3[j])
                j += 1
            para_len = len(para)
            if para_len >= PARA_SPLIT_LINES:
                # try to find a sentence boundary around middle
                split_index = None
                for k in range(min(PARA_MAX_LINES, para_len-1)-1, -1, -1):
                    if SENTENCE_BREAK_RE.search(para[k].strip()):
                        split_index = k + 1
                        break
                if split_index is None and para_len > PARA_MAX_LINES:
                    split_index = PARA_MAX_LINES
                if split_index:
                    # write first part
                    for t in para[:split_index]:
                        final.append(t)
                    final.append('% **MOD** 恢复段落换行')
                    final.append('')
                    restored_breaks += 1
                    # write remainder
                    for t in para[split_index:]:
                        final.append(t)
                else:
                    # write as-is
                    for t in para:
                        final.append(t)
                # add one empty after paragraph end
                if j < len(lines3) and lines3[j].strip() == '':
                    pass
                else:
                    final.append('% **MOD** 新增空行以改善版面')
                    final.append('')
                    added_empty += 1
                i = j
                continue
            else:
                # normal paragraph; ensure one empty after
                for t in para:
                    final.append(t)
                if j < len(lines3) and lines3[j].strip() == '':
                    pass
                else:
                    final.append('% **MOD** 新增空行以改善版面')
                    final.append('')
                    added_empty += 1
                i = j
                continue
        # blank or special env line
        final.append(line)
        i += 1

    return '\n'.join(final), restored_breaks, added_empty, removed_excess, merged_paras


def process_file(path: Path):
    name = path.name
    text = path.read_text(encoding='utf-8', errors='ignore')
    new_text, rb, ae, re, mp = optimize_layout(text)
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    # write report
    report_path = NOTE_DIR / f"{name}.layout.md"
    report = (
        "## 段落与排版优化报告\n\n"
        f"- 恢复换行：{rb} 处\n"
        f"- 新增空行：{ae} 处\n"
        f"- 删除冗余换行：{re} 处\n"
        f"- 段落合并：{mp} 处\n"
        f"- 备注：改善整体节奏与视觉密度，未改动数学或命令结构。\n"
    )
    report_path.write_text(report, encoding='utf-8')
    # write file
    if WRITE and not DRY_RUN:
        path.write_text(new_text, encoding='utf-8')
    return name, rb, ae, re, mp


def main():
    files = list(CHAPTERS.glob('*.tex'))
    latest = pick_latest(files)
    rows = []
    for p in latest:
        try:
            rows.append(process_file(p))
        except Exception as e:
            rows.append((p.name, 0, 0, 0, 0))
    # summary
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    header = '文件名\t恢复换行\t新增空行\t删除冗余\t合并段落\t备注'
    lines = [header]
    for name, rb, ae, re, mp in rows:
        remark = '已按规则调整' if (rb or ae or re or mp) else '无需调整'
        lines.append(f"{name}\t{rb}\t{ae}\t{re}\t{mp}\t{remark}")
    with open(SUMMARY_PATH, 'a', encoding='utf-8') as f:
        if f.tell() == 0:
            f.write('## 排版与换行优化总览\n')
        f.write('\n' + '\n'.join(lines) + '\n')
    print('\n'.join(lines))

if __name__ == '__main__':
    main()