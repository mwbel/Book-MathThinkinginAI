#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def normalize_headings(file_path):
    """Normalize heading levels: subsubsection -> paragraph, subparagraph -> regular paragraph"""

    # Read the file with UTF-8 encoding
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Replace all subsubsection with paragraph
    content = content.replace('\\subsubsection{', '\\paragraph{')

    # 2. Convert subparagraph to regular paragraph with emphasized text
    lines = content.split('\n')
    new_lines = []

    for line in lines:
        if '\\subparagraph{' in line:
            # Convert subparagraph to regular paragraph with emphasized text
            line = line.replace('\\subparagraph{', '\\paragraph{\\textbf{')
            # Find the closing brace and add closing brace for textbf
            if '}:' in line:
                line = line.replace('}:', '}}：')
            elif '}' in line:
                # Find the position of first closing brace
                brace_pos = line.find('}')
                if brace_pos != -1:
                    line = line[:brace_pos] + '}' + line[brace_pos+1:]
        new_lines.append(line)

    content = '\n'.join(new_lines)

    # 3. Handle special cases: textbf headings like "第一层：算法的正确性"
    # These should be converted to paragraph
    content = content.replace(
        '\\textbf{第一层：算法的正确性}',
        '\\paragraph{第一层：算法的正确性}'
    )
    content = content.replace(
        '\\textbf{第二层：收敛速度的量化}',
        '\\paragraph{第二层：收敛速度的量化}'
    )
    content = content.replace(
        '\\textbf{第三层：最优学习率的推导}',
        '\\paragraph{第三层：最优学习率的推导}'
    )

    # Write the result back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Count changes
    subsubsection_count = original_content.count('\\subsubsection{')
    subparagraph_count = original_content.count('\\subparagraph{')
    paragraph_count_new = content.count('\\paragraph{')

    print(f"Successfully normalized headings!")
    print(f"- Converted {subsubsection_count} subsubsection to paragraph")
    print(f"- Converted {subparagraph_count} subparagraph to paragraph")
    print(f"- Total paragraphs after normalization: {paragraph_count_new}")

    return True

if __name__ == "__main__":
    file_path = "/Users/Min369/Desktop/书/书稿打磨/draft-tex-3扩写/chapters/ch4/4-Thinking.v1_polished_unified_expanded.tex"
    success = normalize_headings(file_path)

    if success:
        print("✅ Heading normalization completed successfully!")
    else:
        print("❌ Failed to normalize headings.")