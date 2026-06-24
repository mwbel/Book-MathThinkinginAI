#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def remove_reddelete_tags(file_path):
    """Remove all \reddelete{...} tags while preserving the content inside."""

    # Read the file with UTF-8 encoding
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Store original for verification
    original_content = content

    # Define patterns to handle multi-line reddelete tags
    patterns = [
        # Pattern 1: Simple single-line \reddelete{...}
        r'\\reddelete\{([^{}]*)\}',

        # Pattern 2: \reddelete{...} with nested braces (single line)
        r'\\reddelete\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',

        # Pattern 3: Multi-line \reddelete{...}
        r'\\reddelete\{([^{}]*(?:\{[^{}]*\}[^{}]*)*\{[^{}]*\}[^{}]*)\}',
    ]

    # Apply the patterns iteratively
    for pattern in patterns:
        content = re.sub(pattern, r'\1', content, flags=re.DOTALL)

    # Additional manual cleaning for specific cases that might be missed
    # Handle cases where \reddelete{ spans multiple lines
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if '\\reddelete{' in line:
            # Find the start of reddelete
            start_pos = line.find('\\reddelete{')
            prefix = line[:start_pos]

            # Look for the closing brace
            brace_count = 1
            j = start_pos + 10  # position after \reddelete{
            content_inside = ""

            while i < len(lines) and brace_count > 0:
                current_line = lines[i] if j > 0 else lines[i+1]
                if j == 0:
                    current_line = lines[i]
                    j = current_line.find('\\reddelete{') + 10

                while j < len(current_line) and brace_count > 0:
                    char = current_line[j]
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                    if brace_count > 0:
                        content_inside += char
                    j += 1

                if brace_count > 0:
                    content_inside += '\n'
                    i += 1
                    j = 0

            new_line = prefix + content_inside
            new_lines.append(new_line)
        else:
            new_lines.append(line)
        i += 1

    content = '\n'.join(new_lines)

    # Write the result back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Verify that reddelete tags are removed
    reddelete_count = content.count('\\reddelete')
    print(f"Successfully processed file. Remaining \\reddelete tags: {reddelete_count}")

    return reddelete_count == 0

if __name__ == "__main__":
    file_path = "/Users/Min369/Desktop/书/书稿打磨/draft-tex-3扩写/chapters/ch4/4-Thinking.v1_polished_unified_expanded.tex"
    success = remove_reddelete_tags(file_path)

    if success:
        print("✅ All \\reddelete{} tags successfully removed!")
    else:
        print("❌ Some \\reddelete{} tags may remain. Manual inspection needed.")