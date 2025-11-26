#!/usr/bin/env python3
"""
提示词管理系统
管理用于书稿修改的各种提示词模板
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class PromptManager:
    def __init__(self, prompts_file: str = "prompts.json"):
        self.prompts_file = prompts_file
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, Any]:
        """加载提示词配置"""
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 提示词文件 {self.prompts_file} 不存在")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ 提示词文件格式错误: {e}")
            return {}

    def get_prompt(self, category: str, prompt_name: str, **kwargs) -> str:
        """获取格式化后的提示词"""
        try:
            template = self.prompts["categories"][category]["prompts"][prompt_name]["template"]
            return template.format(**kwargs)
        except KeyError as e:
            print(f"❌ 找不到提示词: {e}")
            return ""

    def list_categories(self) -> Dict[str, str]:
        """列出所有类别"""
        return {
            cat_id: cat_info["description"]
            for cat_id, cat_info in self.prompts.get("categories", {}).items()
        }

    def list_prompts(self, category: str) -> Dict[str, str]:
        """列出指定类别的所有提示词"""
        if category not in self.prompts.get("categories", {}):
            return {}

        return {
            prompt_id: prompt_info["name"]
            for prompt_id, prompt_info in self.prompts["categories"][category]["prompts"].items()
        }

    def get_prompt_info(self, category: str, prompt_name: str) -> Dict[str, Any]:
        """获取提示词详细信息"""
        try:
            return self.prompts["categories"][category]["prompts"][prompt_name]
        except KeyError:
            return {}

    def add_custom_prompt(self, name: str, template: str, description: str = ""):
        """添加自定义提示词"""
        if "custom_prompts" not in self.prompts:
            self.prompts["custom_prompts"] = {"templates": {}}

        self.prompts["custom_prompts"]["templates"][name] = {
            "template": template,
            "description": description
        }
        self._save_prompts()
        print(f"✅ 自定义提示词 '{name}' 已添加")

    def get_custom_prompt(self, name: str, **kwargs) -> str:
        """获取自定义提示词"""
        try:
            template = self.prompts["custom_prompts"]["templates"][name]["template"]
            return template.format(**kwargs)
        except KeyError:
            print(f"❌ 找不到自定义提示词: {name}")
            return ""

    def _save_prompts(self):
        """保存提示词配置"""
        try:
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(self.prompts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存提示词文件失败: {e}")

    def search_prompts(self, keyword: str) -> Dict[str, Any]:
        """搜索包含关键词的提示词"""
        results = {}
        keyword = keyword.lower()

        for cat_id, cat_info in self.prompts.get("categories", {}).items():
            for prompt_id, prompt_info in cat_info["prompts"].items():
                if (keyword in prompt_info["name"].lower() or
                    keyword in prompt_info["template"].lower()):
                    results[f"{cat_id}.{prompt_id}"] = {
                        "name": prompt_info["name"],
                        "category": cat_info["description"],
                        "template": prompt_info["template"][:100] + "..."
                    }

        return results

    def show_examples(self, category: str, prompt_name: str):
        """显示提示词的示例"""
        prompt_info = self.get_prompt_info(category, prompt_name)
        if not prompt_info:
            return

        examples = prompt_info.get("examples", [])
        if not examples:
            print(f"💡 提示词 '{prompt_info['name']}' 没有预设示例")
            return

        print(f"💡 '{prompt_info['name']}' 的使用示例:")
        print("=" * 50)

        for i, example in enumerate(examples, 1):
            if isinstance(example, str):
                print(f"\n示例 {i}: {example}")
            elif isinstance(example, dict):
                print(f"\n示例 {i}:")
                for key, value in example.items():
                    print(f"  {key}: {value}")

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="提示词管理工具")
    parser.add_argument("command", choices=["list", "get", "add", "search", "examples"],
                       help="操作命令")
    parser.add_argument("--category", "-c", help="提示词类别")
    parser.add_argument("--name", "-n", help="提示词名称")
    parser.add_argument("--keyword", "-k", help="搜索关键词")
    parser.add_argument("--template", "-t", help="提示词模板")
    parser.add_argument("--description", "-d", default="", help="提示词描述")

    args = parser.parse_args()
    pm = PromptManager()

    if args.command == "list":
        if args.category:
            prompts = pm.list_prompts(args.category)
            if prompts:
                print(f"📋 {args.category} 类别的提示词:")
                for pid, name in prompts.items():
                    print(f"  {pid}: {name}")
            else:
                print(f"❌ 类别 '{args.category}' 不存在")
        else:
            categories = pm.list_categories()
            print("📋 可用的提示词类别:")
            for cat_id, description in categories.items():
                print(f"  {cat_id}: {description}")

    elif args.command == "get":
        if not args.category or not args.name:
            print("❌ 请指定类别和名称")
            return

        # 构造参数（这里只是演示）
        kwargs = {"text": "示例文本", "concept": "示例概念", "formula": "示例公式"}
        prompt = pm.get_prompt(args.category, args.name, **kwargs)
        if prompt:
            print(f"📝 生成的提示词:\n{prompt}")
        else:
            print("❌ 无法获取提示词")

    elif args.command == "add":
        if not args.name or not args.template:
            print("❌ 请指定提示词名称和模板")
            return

        pm.add_custom_prompt(args.name, args.template, args.description)

    elif args.command == "search":
        if not args.keyword:
            print("❌ 请指定搜索关键词")
            return

        results = pm.search_prompts(args.keyword)
        if results:
            print(f"🔍 搜索结果 (关键词: {args.keyword}):")
            for prompt_id, info in results.items():
                print(f"\n{prompt_id}: {info['name']}")
                print(f"  类别: {info['category']}")
                print(f"  模板: {info['template']}")
        else:
            print(f"❌ 没有找到包含 '{args.keyword}' 的提示词")

    elif args.command == "examples":
        if not args.category or not args.name:
            print("❌ 请指定类别和名称")
            return

        pm.show_examples(args.category, args.name)

if __name__ == "__main__":
    main()