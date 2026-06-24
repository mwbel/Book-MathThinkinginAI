#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def convert_microcases(file_path):
    """Convert all microcase paragraphs to microcase environment"""

    # Read the file with UTF-8 encoding
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # List of microcases to convert
    microcases = [
        "微案例：从直觉到公式——注意力机制的形式化历程",
        "微案例：梯度下降收敛性的严谨分析"
    ]

    # Convert each microcase
    for case_title in microcases:
        old_pattern = f"\\paragraph{{{case_title}}}\n\n"

        if old_pattern in content:
            new_pattern = f"\\begin{{microcase}}{{{case_title}}}\n\n"
            content = content.replace(old_pattern, new_pattern)

            # Find the end of the microcase and close it
            # Look for the next paragraph or section to determine where to close
            start_pos = content.find(new_pattern)
            if start_pos != -1:
                # Find the next major heading after this microcase
                remaining_content = content[start_pos + len(new_pattern):]

                # Look for the end of this microcase (next \paragraph, \section, \subsection)
                end_patterns = [
                    '\n\n\\paragraph{',
                    '\n\\section{',
                    '\n\\subsection{',
                    '\n%\\paragraph{'
                ]

                min_pos = len(remaining_content)
                for pattern in end_patterns:
                    pos = remaining_content.find(pattern)
                    if pos != -1 and pos < min_pos:
                        min_pos = pos

                # Insert the end microcase tag
                end_pos = start_pos + len(new_pattern) + min_pos
                content = content[:end_pos] + "\n\n\\end{microcase}\n\n" + content[end_pos:]

    # Write the result back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Successfully converted microcases!")
    return True

if __name__ == "__main__":
    file_path = "/Users/Min369/Desktop/书/书稿打磨/draft-tex-3扩写/chapters/ch4/4-Thinking.v1_polished_unified_expanded.tex"
    success = convert_microcases(file_path)

    if success:
        print("✅ Microcase conversion completed successfully!")
    else:
        print("❌ Failed to convert microcases.")