#!/usr/bin/env python3
"""
使用 Gemini 2.5-Flash 进行书稿修改的专用工具
"""

import os
import json
import re
import time
from pathlib import Path
from gemini_wrapper import GeminiAPIWrapper
from rate_limiter import wait_for_rate_limit, record_api_usage

class BookEditor:
    def __init__(self):
        self.wrapper = GeminiAPIWrapper()
        self.supported_formats = ['.md', '.txt', '.tex']

    def read_file(self, file_path: str) -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return ""

    def write_file(self, file_path: str, content: str) -> bool:
        """写入文件内容"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"❌ 写入文件失败: {e}")
            return False

    def create_backup(self, file_path: str) -> str:
        """创建文件备份"""
        backup_path = f"{file_path}.backup_{int(time.time())}"
        try:
            content = self.read_file(file_path)
            self.write_file(backup_path, content)
            return backup_path
        except:
            return ""

    def estimate_tokens(self, text: str) -> int:
        """估算文本的 token 数量"""
        # 简单估算：中文约1.5字符=1token，英文约4字符=1token
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        return int(chinese_chars / 1.5 + english_chars / 4 + len(text.split()))

    def edit_text(self, original_text: str, instruction: str, chunk_size: int = 3000) -> str:
        """编辑文本内容（支持大文本分块处理）"""
        total_tokens = self.estimate_tokens(original_text)

        if total_tokens <= chunk_size:
            # 小文本直接处理
            return self._edit_single_chunk(original_text, instruction)
        else:
            # 大文本分块处理
            return self._edit_text_chunks(original_text, instruction, chunk_size)

    def _edit_single_chunk(self, text: str, instruction: str) -> str:
        """处理单个文本块"""
        prompt = f"""请根据以下指令修改文本内容：

修改指令：{instruction}

原文内容：
```
{text}
```

要求：
1. 严格按照指令进行修改
2. 保持原文的逻辑结构和专业术语
3. 如果是学术文本，保持严谨的学术风格
4. 只返回修改后的文本，不要解释

修改后的文本："""

        # 等待速率限制
        wait_for_rate_limit(self.estimate_tokens(prompt))

        # 调用 API
        result = self.wrapper.generate_content(prompt, temperature=0.3)

        # 记录使用量
        record_api_usage(
            self.wrapper.manager.get_current_api_key(),
            self.estimate_tokens(prompt),
            self.estimate_tokens(result) if result else 0
        )

        return result if result else text

    def _edit_text_chunks(self, text: str, instruction: str, chunk_size: int) -> str:
        """分块处理大文本"""
        # 按段落分割文本
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if self.estimate_tokens(current_chunk + para) <= chunk_size:
                current_chunk += para + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + '\n\n'

        if current_chunk:
            chunks.append(current_chunk.strip())

        print(f"📄 文本已分割为 {len(chunks)} 个块进行处理")

        edited_chunks = []
        for i, chunk in enumerate(chunks, 1):
            print(f"🔧 处理第 {i}/{len(chunks)} 块...")

            # 为每块添加上下文
            context = f"这是文本的第 {i} 部分，总共 {len(chunks)} 部分。"
            chunk_instruction = f"{context}\n{instruction}"

            edited_chunk = self._edit_single_chunk(chunk, chunk_instruction)
            edited_chunks.append(edited_chunk)

            # 避免请求过快
            time.sleep(2)

        return '\n\n'.join(edited_chunks)

    def polish_writing(self, text: str) -> str:
        """润色文本"""
        instruction = """请对以下文本进行润色，要求：
1. 修正语法错误和表达不清晰的地方
2. 优化句式结构，使表达更加流畅
3. 保持原文的核心意思和专业术语不变
4. 提升文本的可读性和学术性"""
        return self.edit_text(text, instruction)

    def simplify_language(self, text: str) -> str:
        """简化语言表达"""
        instruction = """请简化以下文本的语言表达，要求：
1. 将复杂的专业术语解释得更通俗易懂
2. 简化长句和复杂句式
3. 保持原文的核心内容和准确性
4. 使文本更适合初学者理解"""
        return self.edit_text(text, instruction)

    def enhance_formality(self, text: str) -> str:
        """增强文本的正式性和学术性"""
        instruction = """请增强以下文本的正式性和学术性，要求：
1. 使用更规范的学术表达
2. 增强逻辑性和严谨性
3. 修正不正式的表达方式
4. 保持内容的准确性和专业性"""
        return self.edit_text(text, instruction)

    def add_examples(self, text: str, topic: str = "") -> str:
        """添加具体例子和说明"""
        instruction = f"""请在以下文本中适当添加具体的例子和说明，主题是：{topic}

要求：
1. 在适当位置插入相关的具体例子
2. 添加必要的解释和说明
3. 使用通俗易懂的语言
4. 保持原文结构，只是丰富内容"""
        return self.edit_text(text, instruction)

    def extract_key_points(self, text: str) -> str:
        """提取关键点"""
        instruction = """请从以下文本中提取关键要点，要求：
1. 以列表形式呈现重要观点
2. 保持原文的逻辑顺序
3. 用简洁的语言概括每个要点
4. 突出核心概念和重要结论"""
        return self.edit_text(text, instruction)

    def translate_content(self, text: str, target_lang: str = "中文") -> str:
        """翻译内容"""
        instruction = f"""请将以下文本翻译成{target_lang}，要求：
1. 保持原文的专业性和准确性
2. 使用自然流畅的目标语言表达
3. 专业术语要准确翻译
4. 保持原文的格式和结构"""
        return self.edit_text(text, instruction)

    def interactive_edit(self, file_path: str):
        """交互式编辑模式"""
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return

        # 检查文件格式
        file_ext = Path(file_path).suffix
        if file_ext not in self.supported_formats:
            print(f"⚠️  不支持的文件格式: {file_ext}")
            print(f"支持的格式: {', '.join(self.supported_formats)}")
            return

        # 读取原文件
        original_content = self.read_file(file_path)
        if not original_content:
            return

        print(f"📄 已加载文件: {file_path}")
        print(f"📊 文件大小: {len(original_content)} 字符")
        print(f"🔢 预估tokens: {self.estimate_tokens(original_content):,}")

        # 创建备份
        backup_path = self.create_backup(file_path)
        if backup_path:
            print(f"💾 已创建备份: {backup_path}")

        print("\n🎯 可用的编辑功能：")
        print("1. 润色文本 - 提升语言质量和流畅度")
        print("2. 简化语言 - 使内容更易懂")
        print("3. 增强学术性 - 提升正式性和严谨性")
        print("4. 添加例子 - 丰富内容和说明")
        print("5. 提取要点 - 生成关键点摘要")
        print("6. 翻译内容 - 翻译成其他语言")
        print("7. 自定义指令 - 使用自己的修改要求")

        while True:
            print("\n" + "="*50)
            choice = input("请选择功能 (1-7, q退出): ").strip()

            if choice == 'q':
                break
            elif choice == '1':
                edited_content = self.polish_writing(original_content)
            elif choice == '2':
                edited_content = self.simplify_language(original_content)
            elif choice == '3':
                edited_content = self.enhance_formality(original_content)
            elif choice == '4':
                topic = input("请输入主题关键词 (可选): ").strip()
                edited_content = self.add_examples(original_content, topic)
            elif choice == '5':
                edited_content = self.extract_key_points(original_content)
            elif choice == '6':
                target_lang = input("请输入目标语言: ").strip()
                edited_content = self.translate_content(original_content, target_lang)
            elif choice == '7':
                instruction = input("请输入自定义修改指令: ").strip()
                edited_content = self.edit_text(original_content, instruction)
            else:
                print("❌ 无效选择，请重新输入")
                continue

            if edited_content:
                # 预览结果
                print("\n📝 修改结果预览 (前500字符):")
                print("-" * 40)
                print(edited_content[:500] + ("..." if len(edited_content) > 500 else ""))
                print("-" * 40)

                # 询问是否保存
                save = input("\n💾 是否保存修改？ (y/n): ").lower()
                if save == 'y':
                    if self.write_file(file_path, edited_content):
                        print(f"✅ 修改已保存到: {file_path}")
                        original_content = edited_content  # 更新为当前内容
                    else:
                        print("❌ 保存失败")
                else:
                    print("❌ 修改未保存")
            else:
                print("❌ 编辑失败")

def main():
    editor = BookEditor()

    print("📚 Gemini 书稿编辑器")
    print("=" * 30)

    # 检查目录中的书稿文件
    current_dir = "."
    book_files = []
    for ext in editor.supported_formats:
        book_files.extend(Path(current_dir).glob(f"*{ext}"))

    if book_files:
        print(f"📁 发现 {len(book_files)} 个书稿文件:")
        for i, file in enumerate(book_files, 1):
            print(f"  {i}. {file.name}")

        print(f"  {len(book_files)+1}. 其他文件路径")
        choice = input(f"\n请选择文件 (1-{len(book_files)+1}): ").strip()

        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(book_files):
                selected_file = str(book_files[choice_num-1])
                editor.interactive_edit(selected_file)
            elif choice_num == len(book_files)+1:
                file_path = input("请输入文件路径: ").strip()
                editor.interactive_edit(file_path)
            else:
                print("❌ 无效选择")
        else:
            print("❌ 无效选择")
    else:
        file_path = input("请输入书稿文件路径: ").strip()
        editor.interactive_edit(file_path)

if __name__ == "__main__":
    import time
    main()