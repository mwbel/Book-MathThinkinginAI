#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def emergency_fix_microcases(file_path):
    """Replace microcase environment with a simpler framebox-based version"""

    # Read the file with UTF-8 encoding
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace microcase environment with simple framed box
    content = content.replace(
        '\\begin{microcase}{',
        '\\begin{tcolorbox}[colback=blue!5!white,colframe=blue!75!black,title='
    )

    content = content.replace(
        '\\end{microcase}',
        '\\end{tcolorbox}'
    )

    # Write the result back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Emergency fix applied!")
    return True

if __name__ == "__main__":
    file_path = "/Users/Min369/Desktop/书/书稿打磨/draft-tex-3扩写/chapters/ch4/4-Thinking.v1_polished_unified_expanded.tex"
    success = emergency_fix_microcases(file_path)

    if success:
        print("✅ Emergency fix completed!")