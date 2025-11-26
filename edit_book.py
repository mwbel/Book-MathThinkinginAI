#!/usr/bin/env python3
"""
命令行书稿修改工具
用法: python3 edit_book.py <文件路径> <修改类型> [参数]
"""

import sys
import os
from pathlib import Path
from book_editor import BookEditor

def print_usage():
    """打印使用说明"""
    print("📚 书稿修改工具使用说明")
    print("=" * 40)
    print("用法: python3 edit_book.py <文件路径> <修改类型> [参数]")
    print()
    print("修改类型:")
    print("  polish    - 润色文本")
    print("  simplify  - 简化语言")
    print("  formal    - 增强学术性")
    print("  examples  - 添加例子")
    print("  summary   - 提取要点")
    print("  translate - 翻译内容")
    print("  custom    - 自定义指令")
    print()
    print("示例:")
    print("  python3 edit_book.py chapter1.md polish")
    print("  python3 edit_book.py chapter1.md examples \"机器学习\"")
    print("  python3 edit_book.py chapter1.md translate English")
    print("  python3 edit_book.py chapter1.md custom \"请将这段文字改得更生动有趣\"")

def main():
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    file_path = sys.argv[1]
    edit_type = sys.argv[2].lower()
    extra_arg = sys.argv[3] if len(sys.argv) > 3 else ""

    editor = BookEditor()

    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)

    # 读取原文件
    print(f"📄 正在读取文件: {file_path}")
    original_content = editor.read_file(file_path)
    if not original_content:
        print("❌ 无法读取文件")
        sys.exit(1)

    # 创建备份
    backup_path = editor.create_backup(file_path)
    if backup_path:
        print(f"💾 已创建备份: {backup_path}")

    # 显示文件信息
    file_size = len(original_content)
    estimated_tokens = editor.estimate_tokens(original_content)
    print(f"📊 文件信息:")
    print(f"   大小: {file_size:,} 字符")
    print(f"   预估tokens: {estimated_tokens:,}")

    # 根据类型进行修改
    print(f"\n🔧 开始修改 (类型: {edit_type})...")

    if edit_type == "polish":
        result = editor.polish_writing(original_content)
    elif edit_type == "simplify":
        result = editor.simplify_language(original_content)
    elif edit_type == "formal":
        result = editor.enhance_formality(original_content)
    elif edit_type == "examples":
        result = editor.add_examples(original_content, extra_arg)
    elif edit_type == "summary":
        result = editor.extract_key_points(original_content)
    elif edit_type == "translate":
        target_lang = extra_arg if extra_arg else "中文"
        result = editor.translate_content(original_content, target_lang)
    elif edit_type == "custom":
        if not extra_arg:
            print("❌ 自定义模式需要提供修改指令")
            sys.exit(1)
        result = editor.edit_text(original_content, extra_arg)
    else:
        print(f"❌ 不支持的修改类型: {edit_type}")
        print_usage()
        sys.exit(1)

    # 检查结果
    if result and result != original_content:
        # 保存结果
        success = editor.write_file(file_path, result)
        if success:
            print(f"✅ 修改完成并保存到: {file_path}")

            # 显示统计信息
            new_size = len(result)
            print(f"📊 修改统计:")
            print(f"   原文件大小: {file_size:,} 字符")
            print(f"   新文件大小: {new_size:,} 字符")
            print(f"   变化: {new_size - file_size:+,} 字符 ({((new_size - file_size) / file_size * 100):+1.1f}%)")
        else:
            print("❌ 保存失败")
            sys.exit(1)
    else:
        print("⚠️  没有进行任何修改或修改失败")
        sys.exit(1)

if __name__ == "__main__":
    main()