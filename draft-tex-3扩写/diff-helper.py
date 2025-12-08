#!/usr/bin/env python3
"""
LaTeX单行修改管理工具
用于逐行查看、接受或拒绝LaTeX文档中的修改
"""

import subprocess
import sys
import os
from pathlib import Path

def get_git_diff(file_path):
    """获取Git diff输出，格式化为可操作的行"""
    try:
        result = subprocess.run(
            ['git', 'diff', file_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(file_path)
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff: {e}")
        return None

def parse_diff_lines(diff_output):
    """解析git diff输出为可读的修改项"""
    if not diff_output:
        return []

    lines = diff_output.split('\n')
    modifications = []

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith('@@'):
            # 文件头信息
            modifications.append({
                'type': 'header',
                'content': line,
                'line_num': None
            })
        elif line.startswith('-'):
            # 删除的行
            modifications.append({
                'type': 'deleted',
                'content': line[1:],  # 去掉开头的'-'
                'line_num': None
            })
        elif line.startswith('+'):
            # 新增的行
            modifications.append({
                'type': 'added',
                'content': line[1:],  # 去掉开头的'+'
                'line_num': None
            })
        elif line.startswith(' '):
            # 未修改的行
            modifications.append({
                'type': 'unchanged',
                'content': line[1:],  # 去掉开头的' '
                'line_num': None
            })

        i += 1

    return modifications

def interactive_review(file_path):
    """交互式审查修改"""
    print(f"\n=== 审查文件: {file_path} ===\n")

    diff_output = get_git_diff(file_path)
    if not diff_output:
        print("没有发现修改或获取diff失败")
        return

    modifications = parse_diff_lines(diff_output)

    current_index = 0
    while current_index < len(modifications):
        mod = modifications[current_index]

        # 显示当前修改
        if mod['type'] == 'header':
            print(f"\n📁 {mod['content']}")
            current_index += 1
            continue

        if mod['type'] == 'unchanged':
            print(f"  {mod['content']}")
            current_index += 1
            continue

        # 显示修改详情
        type_icon = {"added": "➕", "deleted": "❌", "replaced": "🔄"}
        print(f"\n{type_icon.get(mod['type'], '•')} [{mod['type'].upper()}] {mod['content']}")

        # 用户选择
        print("\n操作: [a]ccept 接受 | [r]eject 拒绝 | [s]kip 跳过 | [q]uit 退出")
        choice = input("你的选择: ").lower().strip()

        if choice == 'q':
            break
        elif choice == 'a':
            print(f"✅ 已接受: {mod['content']}")
            current_index += 1
        elif choice == 'r':
            print(f"❌ 已拒绝: {mod['content']}")
            # 这里可以添加还原代码
            current_index += 1
        elif choice == 's':
            current_index += 1
        else:
            print("无效选择，请重试")

def show_summary(file_path):
    """显示修改摘要"""
    diff_output = get_git_diff(file_path)
    if not diff_output:
        print("没有发现修改")
        return

    modifications = parse_diff_lines(diff_output)
    added_count = sum(1 for m in modifications if m['type'] == 'added')
    deleted_count = sum(1 for m in modifications if m['type'] == 'deleted')

    print(f"\n📊 修改摘要:")
    print(f"   ➕ 新增行: {added_count}")
    print(f"   ❌ 删除行: {deleted_count}")
    print(f"   📄 总修改: {added_count + deleted_count}")

def apply_changes(file_path, accepted_indices, rejected_indices):
    """应用接受/拒绝的决定"""
    # 这个功能可以实现具体的文件修改
    # 暂时留作扩展
    pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python diff-helper.py <latex_file>")
        print("示例: python diff-helper.py chapters/ch5/5-Tools.v1_polished_unified_expanded.tex")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        sys.exit(1)

    print("LaTeX单行修改管理工具")
    print("=" * 50)

    while True:
        print("\n可用命令:")
        print("1. [r]eview - 审查修改")
        print("2. [s]ummary - 显示修改摘要")
        print("3. [q]uit - 退出")

        command = input("\n选择操作: ").lower().strip()

        if command == 'q':
            break
        elif command == 'r':
            interactive_review(file_path)
        elif command == 's':
            show_summary(file_path)
        else:
            print("无效命令")