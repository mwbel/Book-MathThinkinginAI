#!/usr/bin/env python3
"""
书稿快速修改工具 - 使用 Gemini API
支持多种编辑模式和快捷操作
"""

import sys
import os
import argparse
from pathlib import Path
from gemini_wrapper import quick_generate, quick_chat
from prompt_manager import PromptManager

class BookEditor:
    def __init__(self):
        self.chat = quick_chat()
        self.prompt_manager = PromptManager()
        self.current_file = None
        # 加载MTAI提示词
        self.mtai_prompts = self._load_mtai_prompts()

    def _load_mtai_prompts(self):
        """加载MTAI专用提示词"""
        try:
            import json
            with open('mtai_prompts.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data["categories"]["mtai_book_editing"]["prompts"]
        except:
            return {}

    def get_mtai_prompt(self, prompt_name: str, **kwargs):
        """获取MTAI提示词"""
        if prompt_name not in self.mtai_prompts:
            return None

        template = self.mtai_prompts[prompt_name]["template"]
        try:
            return template.format(**kwargs)
        except KeyError:
            return None

    def polish_text(self, text, style="academic"):
        """润色文本"""
        prompt = self.prompt_manager.get_prompt("polish", style, text=text)
        if not prompt:
            # 回退到默认提示词
            style_prompts = {
                "academic": "请将以下文本改写为更严谨的学术风格，保持原意但提升表达质量：",
                "lecture": "请将以下文本改写为课堂讲解风格，更加生动易懂：",
                "concise": "请将以下文本进行精炼，删除冗余表达，保留核心概念：",
                "expand": "请对以下文本进行扩写，增加详细解释和例子，使其更加丰富："
            }
            prompt = f"{style_prompts.get(style, style_prompts['academic'])}\n\n{text}"

        return quick_generate(prompt)

    def translate_to_chinese(self, text):
        """翻译为中文"""
        prompt = self.prompt_manager.get_prompt("translation", "to_chinese", text=text)
        if not prompt:
            prompt = f"请将以下英文文本翻译为专业的中文学术表达：\n\n{text}"
        return quick_generate(prompt)

    def explain_concept(self, concept):
        """解释概念"""
        prompt = self.prompt_manager.get_prompt("math", "explain_concept", concept=concept)
        if not prompt:
            prompt = f"请详细解释数学概念'{concept}'，包括定义、性质、应用和例子："
        return quick_generate(prompt)

    def generate_example(self, concept):
        """生成例子"""
        prompt = self.prompt_manager.get_prompt("math", "generate_examples", concept=concept)
        if not prompt:
            prompt = f"请为数学概念'{concept}'提供3个具体例子，从简单到复杂："
        return quick_generate(prompt)

    def improve_formula_explanation(self, formula, context=""):
        """改进公式解释"""
        prompt = self.prompt_manager.get_prompt("math", "improve_formula", formula=formula, context=context)
        if not prompt:
            prompt = f"请为以下公式提供更详细的解释，包括每个符号的含义和推导过程：\n\n公式：{formula}\n\n上下文：{context}"
        return quick_generate(prompt)

    def check_math_rigor(self, text):
        """检查数学严谨性"""
        prompt = self.prompt_manager.get_prompt("math", "check_rigor", text=text)
        if not prompt:
            prompt = f"请检查以下数学文本的严谨性，指出逻辑漏洞或不精确的表述，并给出改进建议：\n\n{text}"
        return quick_generate(prompt)

    def use_custom_prompt(self, prompt_name: str, **kwargs):
        """使用自定义提示词"""
        prompt = self.prompt_manager.get_custom_prompt(prompt_name, **kwargs)
        if not prompt:
            print(f"❌ 找不到自定义提示词: {prompt_name}")
            return ""
        return quick_generate(prompt)

    def generate_chapter_intro(self, chapter_number: str, chapter_title: str):
        """生成章节引言"""
        prompt = self.prompt_manager.get_prompt("book_specific", "chapter_intro",
                                               chapter_number=chapter_number,
                                               chapter_title=chapter_title)
        if prompt:
            return quick_generate(prompt)
        return ""

    def enhance_example(self, example: str, concept: str):
        """增强例子"""
        prompt = self.prompt_manager.get_prompt("book_specific", "example_enhancement",
                                               example=example, concept=concept)
        if prompt:
            return quick_generate(prompt)
        return ""

    def generate_exercises(self, topic: str):
        """生成习题"""
        prompt = self.prompt_manager.get_prompt("book_specific", "exercise_generation", topic=topic)
        if prompt:
            return quick_generate(prompt)
        return ""

    # MTAI专业方法
    def mtai_gen_examples(self, concept: str):
        """MTAI生成例子和类比"""
        prompt = self.get_mtai_prompt("mtai_gen_examples", concept=concept)
        if prompt:
            return quick_generate(prompt)
        return ""

    def mtai_refine_diff(self, latex_code: str):
        """MTAI对照式润色(diff)"""
        prompt = self.get_mtai_prompt("mtai_refine_diff", latex_code=latex_code)
        if prompt:
            return quick_generate(prompt)
        return ""

    def mtai_diff_expand(self, latex_code: str):
        """MTAI扩写(diff模式)"""
        prompt = self.get_mtai_prompt("mtai_diff_expand", latex_code=latex_code)
        if prompt:
            return quick_generate(prompt)
        return ""

    def mtai_struct_diagnose(self, latex_code: str):
        """MTAI结构诊断"""
        prompt = self.get_mtai_prompt("mtai_struct_diagnose", latex_code=latex_code)
        if prompt:
            return quick_generate(prompt)
        return ""

    def mtai_diff_selection(self, latex_code: str):
        """MTAI选区diff编辑"""
        prompt = self.get_mtai_prompt("mtai_diff_selection", latex_code=latex_code)
        if prompt:
            return quick_generate(prompt)
        return ""

def main():
    parser = argparse.ArgumentParser(description="书稿快速修改工具")
    parser.add_argument("command", choices=[
        "polish", "translate", "explain", "example", "formula", "check", "interactive",
        "custom", "intro", "enhance", "exercise", "prompts",
        # MTAI专业命令
        "mtai-examples", "mtai-refine", "mtai-expand", "mtai-diagnose", "mtai-edit"
    ], help="编辑命令")
    parser.add_argument("--file", "-f", help="输入文件路径")
    parser.add_argument("--text", "-t", help="直接输入文本")
    parser.add_argument("--style", "-s", default="academic",
                       choices=["academic", "lecture", "concise", "expand"],
                       help="润色风格")
    parser.add_argument("--concept", "-c", help="数学概念")
    parser.add_argument("--formula", help="数学公式")
    parser.add_argument("--context", help="上下文信息")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--prompt-name", "-p", help="自定义提示词名称")
    parser.add_argument("--chapter", help="章节编号")
    parser.add_argument("--title", help="章节标题")
    parser.add_argument("--list-prompts", action="store_true", help="列出可用提示词")

    args = parser.parse_args()
    editor = BookEditor()

    # 获取输入文本
    text = ""
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return
    elif args.text:
        text = args.text

    # 对于需要特定参数的命令，允许不输入文本
    if args.command in ["explain", "example"] and args.concept:
        text = args.concept
    elif args.command == "formula" and args.formula:
        text = args.formula
    elif args.command in ["intro", "exercise", "enhance", "prompts", "custom",
                       "mtai-examples", "mtai-refine", "mtai-expand",
                       "mtai-diagnose", "mtai-edit"]:
        # 这些命令不需要默认文本输入
        pass
    elif not text and args.command != "interactive":
        # 交互式输入
        print("📝 请输入要处理的文本 (Ctrl+D 结束输入):")
        text = sys.stdin.read().strip()

    # 验证需要输入文本的命令
    commands_needing_text = ["polish", "translate", "check", "enhance",
                           "mtai-refine", "mtai-expand", "mtai-diagnose", "mtai-edit"]
    if args.command in commands_needing_text and not text:
        print("❌ 没有输入文本")
        return

    # 执行命令
    try:
        if args.command == "polish":
            result = editor.polish_text(text, args.style)
            print(f"✨ 润色完成 ({args.style} 风格):")

        elif args.command == "translate":
            result = editor.translate_to_chinese(text)
            print("🌍 翻译完成:")

        elif args.command == "explain":
            if not args.concept:
                args.concept = text
            result = editor.explain_concept(args.concept)
            print(f"📚 概念解释: {args.concept}")

        elif args.command == "example":
            if not args.concept:
                args.concept = text
            result = editor.generate_example(args.concept)
            print(f"💡 生成例子: {args.concept}")

        elif args.command == "formula":
            if not args.formula:
                args.formula = text
            context = args.context or ""
            result = editor.improve_formula_explanation(args.formula, context)
            print("🔐 公式解释:")

        elif args.command == "check":
            result = editor.check_math_rigor(text)
            print("🔍 严谨性检查:")

        elif args.command == "interactive":
            print("🤖 进入交互模式 (输入 'quit' 退出)")
            while True:
                user_input = input("\n💬 您: ").strip()
                if user_input.lower() in ['quit', 'exit', '退出']:
                    break
                response = editor.chat.send_message(user_input)
                print(f"🤖 助手: {response}")
            return

        elif args.command == "prompts":
            # 对于 prompts 命令，不需要输入文本
            if args.list_prompts:
                print("📋 可用提示词:")
                print("=" * 50)
                categories = editor.prompt_manager.list_categories()
                for cat_id, description in categories.items():
                    print(f"\n🏷️  {cat_id}: {description}")
                    prompts = editor.prompt_manager.list_prompts(cat_id)
                    for prompt_id, name in prompts.items():
                        print(f"    {prompt_id}: {name}")
                return
            else:
                print("💡 使用 --list-prompts 查看所有可用提示词")
                return

        elif args.command == "custom":
            if not args.prompt_name:
                print("❌ 请指定自定义提示词名称 (--prompt-name)")
                return
            result = editor.use_custom_prompt(args.prompt_name, text=text)
            print(f"🎨 自定义提示词结果:")

        elif args.command == "intro":
            if not args.chapter or not args.title:
                print("❌ 请指定章节编号 (--chapter) 和章节标题 (--title)")
                return
            result = editor.generate_chapter_intro(args.chapter, args.title)
            print(f"📖 章节引言 (第{args.chapter}章: {args.title}):")

        elif args.command == "enhance":
            if not args.concept:
                print("❌ 请指定相关概念 (--concept)")
                return
            result = editor.enhance_example(text, args.concept)
            print(f"🎯 增强例子 ({args.concept}):")

        elif args.command == "exercise":
            if not args.concept:
                args.concept = text
            if not args.concept:
                print("❌ 请指定要生成习题的主题")
                return
            result = editor.generate_exercises(args.concept)
            print(f"📝 生成习题 ({args.concept}):")

        # MTAI专业命令
        elif args.command == "mtai-examples":
            if not args.concept:
                args.concept = text if text else input("请输入要生成例子的概念: ").strip()
            result = editor.mtai_gen_examples(args.concept)
            print(f"🎯 MTAI生成例子 ({args.concept}):")

        elif args.command == "mtai-refine":
            result = editor.mtai_refine_diff(text)
            print("📝 MTAI对照式润色 (diff):")

        elif args.command == "mtai-expand":
            result = editor.mtai_diff_expand(text)
            print("📈 MTAI扩写 (diff模式):")

        elif args.command == "mtai-diagnose":
            result = editor.mtai_struct_diagnose(text)
            print("🔍 MTAI结构诊断:")

        elif args.command == "mtai-edit":
            result = editor.mtai_diff_selection(text)
            print("✏️  MTAI选区编辑 (diff):")

        # 输出结果
        print("\n" + "="*60)
        print(result)
        print("="*60)

        # 保存到文件
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"\n💾 结果已保存到: {args.output}")

    except Exception as e:
        print(f"❌ 处理失败: {e}")

if __name__ == "__main__":
    main()