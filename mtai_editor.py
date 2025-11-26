#!/usr/bin/env python3
"""
MTAI专业书稿编辑工具
基于《人工智能的数学思维》编辑手册的专业提示词系统
"""

import sys
import os
import argparse
import json
from pathlib import Path
from gemini_wrapper import quick_generate, quick_chat
from prompt_manager import PromptManager

class MTAIEditor:
    def __init__(self):
        self.chat = quick_chat()
        # 加载MTAI专用提示词
        self.mtai_prompts = self._load_mtai_prompts()

    def _load_mtai_prompts(self):
        """加载MTAI专用提示词"""
        try:
            with open('mtai_prompts.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data["categories"]["mtai_book_editing"]["prompts"]
        except FileNotFoundError:
            print("❌ MTAI提示词文件 mtai_prompts.json 不存在")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ MTAI提示词文件格式错误: {e}")
            return {}

    def get_mtai_prompt(self, prompt_name: str, **kwargs):
        """获取MTAI提示词"""
        if prompt_name not in self.mtai_prompts:
            print(f"❌ 找不到MTAI提示词: {prompt_name}")
            return None

        template = self.mtai_prompts[prompt_name]["template"]
        try:
            return template.format(**kwargs)
        except KeyError as e:
            print(f"❌ 提示词模板参数错误: {e}")
            return None

    def list_mtai_prompts(self):
        """列出所有MTAI提示词"""
        print("📋 MTAI专业书稿编辑提示词:")
        print("=" * 60)

        for prompt_id, prompt_info in self.mtai_prompts.items():
            print(f"\n🏷️  {prompt_id}: {prompt_info['name']}")
            print(f"   描述: {prompt_info['template'][:100]}...")

    def gen_examples(self, concept: str):
        """生成例子和类比"""
        prompt = self.get_mtai_prompt("mtai_gen_examples", concept=concept)
        if prompt:
            print(f"🎯 为概念'{concept}'生成例子:")
            print("=" * 50)
            result = quick_generate(prompt)
            print(result)

    def refine_with_diff(self, latex_code: str):
        """对照式润色并生成diff"""
        prompt = self.get_mtai_prompt("mtai_refine_diff", latex_code=latex_code)
        if prompt:
            print("📝 对照式润色 (diff视图):")
            print("=" * 50)
            result = quick_generate(prompt)
            print(result)

    def diff_expand(self, latex_code: str):
        """扩写并生成diff"""
        prompt = self.get_mtai_prompt("mtai_diff_expand", latex_code=latex_code)
        if prompt:
            print("📈 扩写 (diff模式):")
            print("=" * 50)
            result = quick_generate(prompt)
            print(result)

    def struct_diagnose(self, latex_code: str):
        """结构诊断"""
        prompt = self.get_mtai_prompt("mtai_struct_diagnose", latex_code=latex_code)
        if prompt:
            print("🔍 结构诊断:")
            print("=" * 50)
            result = quick_generate(prompt)
            print(result)

    def struct_edit(self, latex_code: str):
        """结构编辑"""
        prompt = self.get_mtai_prompt("mtai_struct_edit", latex_code=latex_code)
        if prompt:
            print("🏗️  结构编辑:")
            print("=" * 50)
            result = quick_generate(prompt)
            print(result)

    def diff_selection(self, latex_code: str):
        """选区diff编辑"""
        prompt = self.get_mtai_prompt("mtai_diff_selection", latex_code=latex_code)
        if prompt:
            print("✏️  选区编辑 (diff):")
            print("=" * 50)
            result = quick_generate(prompt)
            print(result)

    def process_file(self, file_path: str, command: str):
        """处理文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if command == "gen-examples":
                # 从文件中提取概念
                print("📖 从文件中读取概念...")
                concept = input("请输入要解释的概念: ").strip()
                self.gen_examples(concept)
            else:
                # 其他命令处理整个文件内容
                getattr(self, command.replace("-", "_"))(content)

        except FileNotFoundError:
            print(f"❌ 文件 {file_path} 不存在")
        except Exception as e:
            print(f"❌ 处理文件时出错: {e}")

def main():
    parser = argparse.ArgumentParser(description="MTAI专业书稿编辑工具")
    parser.add_argument("command", choices=[
        "list", "gen-examples", "refine-diff", "diff-expand",
        "struct-diagnose", "struct-edit", "diff-selection"
    ], help="MTAI编辑命令")
    parser.add_argument("--file", "-f", help="输入LaTeX文件路径")
    parser.add_argument("--concept", "-c", help="数学概念")
    parser.add_argument("--text", "-t", help="直接输入LaTeX文本")
    parser.add_argument("--latex-code", help="LaTeX代码片段")

    args = parser.parse_args()
    editor = MTAIEditor()

    if args.command == "list":
        editor.list_mtai_prompts()
        return

    # 获取输入内容
    content = ""
    if args.file:
        editor.process_file(args.file, args.command)
        return
    elif args.text:
        content = args.text
    elif args.latex_code:
        content = args.latex_code
    elif args.concept and args.command == "gen-examples":
        editor.gen_examples(args.concept)
        return
    else:
        # 从标准输入读取
        print("📝 请输入LaTeX文本 (Ctrl+D 结束):")
        content = sys.stdin.read().strip()

    if not content and args.command != "gen-examples":
        print("❌ 没有输入内容")
        return

    # 执行相应的命令
    try:
        if args.command == "gen-examples":
            if args.concept:
                editor.gen_examples(args.concept)
            else:
                concept = input("请输入要生成例子的概念: ").strip()
                editor.gen_examples(concept)
        else:
            # 调用对应的方法
            method_name = args.command.replace("-", "_")
            if hasattr(editor, method_name):
                getattr(editor, method_name)(content)
            else:
                print(f"❌ 未知命令: {args.command}")

    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")

if __name__ == "__main__":
    main()