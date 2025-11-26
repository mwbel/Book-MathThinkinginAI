#!/usr/bin/env python3
"""
批量书稿修改工具
"""

import os
import glob
from pathlib import Path
from book_editor import BookEditor
import time

class BatchEditor:
    def __init__(self):
        self.editor = BookEditor()
        self.supported_formats = ['.md', '.txt', '.tex']

    def find_files(self, pattern: str = "*") -> list:
        """查找符合条件的文件"""
        files = []
        for ext in self.supported_formats:
            files.extend(glob.glob(f"{pattern}{ext}"))
        return sorted(files)

    def batch_edit(self, file_pattern: str, edit_type: str, extra_arg: str = ""):
        """批量修改文件"""
        files = self.find_files(file_pattern)

        if not files:
            print(f"❌ 未找到匹配的文件: {file_pattern}")
            return

        print(f"📁 找到 {len(files)} 个文件:")
        for i, file in enumerate(files, 1):
            print(f"  {i}. {file}")

        # 确认
        confirm = input(f"\n⚠️  确定要批量修改这 {len(files)} 个文件吗？ (y/N): ").lower()
        if confirm != 'y':
            print("❌ 操作已取消")
            return

        print(f"\n🚀 开始批量修改 (类型: {edit_type})...")
        print("=" * 50)

        success_count = 0
        error_count = 0

        for i, file_path in enumerate(files, 1):
            print(f"\n📄 [{i}/{len(files)}] 处理文件: {file_path}")

            try:
                # 读取文件
                content = self.editor.read_file(file_path)
                if not content:
                    print(f"❌ 无法读取文件，跳过")
                    error_count += 1
                    continue

                # 创建备份
                backup_path = self.editor.create_backup(file_path)
                if backup_path:
                    print(f"💾 备份: {backup_path}")

                # 修改内容
                if edit_type == "polish":
                    result = self.editor.polish_writing(content)
                elif edit_type == "simplify":
                    result = self.editor.simplify_language(content)
                elif edit_type == "formal":
                    result = self.editor.enhance_formality(content)
                elif edit_type == "examples":
                    result = self.editor.add_examples(content, extra_arg)
                elif edit_type == "summary":
                    result = self.editor.extract_key_points(content)
                elif edit_type == "translate":
                    target_lang = extra_arg if extra_arg else "中文"
                    result = self.editor.translate_content(content, target_lang)
                elif edit_type == "custom":
                    if not extra_arg:
                        print(f"❌ 自定义模式需要指令，跳过文件")
                        error_count += 1
                        continue
                    result = self.editor.edit_text(content, extra_arg)
                else:
                    print(f"❌ 不支持的修改类型: {edit_type}")
                    error_count += 1
                    continue

                # 保存结果
                if result and result != content:
                    if self.editor.write_file(file_path, result):
                        print(f"✅ 修改完成")
                        success_count += 1
                    else:
                        print(f"❌ 保存失败")
                        error_count += 1
                else:
                    print(f"⚠️  无修改或修改失败")
                    error_count += 1

                # 避免请求过快
                time.sleep(3)

            except Exception as e:
                print(f"❌ 处理出错: {e}")
                error_count += 1

        print(f"\n" + "=" * 50)
        print("📊 批量修改完成")
        print("=" * 50)
        print(f"✅ 成功: {success_count} 个文件")
        print(f"❌ 失败: {error_count} 个文件")
        print(f"📁 处理的文件: {len(files)} 个")

    def batch_polish_chapters(self, chapter_pattern: str = "chapter*"):
        """批量润色章节"""
        self.batch_edit(chapter_pattern, "polish")

    def batch_translate_to_chinese(self, file_pattern: str = "*"):
        """批量翻译成中文"""
        self.batch_edit(file_pattern, "translate", "中文")

def main():
    print("📚 批量书稿修改工具")
    print("=" * 30)

    if len(sys.argv) < 3:
        print("用法: python3 batch_edit.py <文件模式> <修改类型> [额外参数]")
        print()
        print("示例:")
        print("  python3 batch_edit.py 'chapter*' polish")
        print("  python3 batch_edit.py '*.md' examples '机器学习'")
        print("  python3 batch_edit.py 'introduction*' formal")
        print("  python3 batch_edit.py '*' translate '中文'")
        sys.exit(1)

    file_pattern = sys.argv[1]
    edit_type = sys.argv[2].lower()
    extra_arg = sys.argv[3] if len(sys.argv) > 3 else ""

    batcher = BatchEditor()
    batcher.batch_edit(file_pattern, edit_type, extra_arg)

if __name__ == "__main__":
    import sys
    main()