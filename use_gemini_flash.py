#!/usr/bin/env python3
"""
使用 Gemini 2.5 Flash 模型的简单示例
"""

from gemini_wrapper import quick_generate, quick_chat
import json

def test_gemini_flash():
    """测试 Gemini 2.5 Flash 模型"""

    print("🚀 测试 Gemini 2.5 Flash 模型")
    print("=" * 50)

    # 1. 快速文本生成
    print("\n📝 文本生成示例:")
    prompt = "请解释什么是机器学习，用简单的语言"
    result = quick_generate(prompt)
    print(f"输入: {prompt}")
    print(f"输出: {result}")

    # 2. 聊天对话
    print("\n💬 聊天对话示例:")
    chat = quick_chat()
    messages = [
        "你好，我想学习人工智能",
        "请推荐一些入门资源",
        "这些资源适合初学者吗？"
    ]

    for msg in messages:
        response = chat.send_message(msg)
        print(f"用户: {msg}")
        print(f"助手: {response[:200]}...")
        print("-" * 30)

def code_generation_example():
    """代码生成示例"""
    print("\n💻 代码生成示例:")

    prompt = """
    写一个 Python 函数，实现以下功能：
    1. 计算斐波那契数列的第n项
    2. 使用动态规划优化
    3. 包含错误处理
    """

    result = quick_generate(prompt)
    print(result)

def data_analysis_example():
    """数据分析示例"""
    print("\n📊 数据分析示例:")

    prompt = """
    分析以下销售数据并给出建议：
    Q1: 100万, Q2: 120万, Q3: 95万, Q4: 180万

    请分析：
    1. 季度趋势
    2. 可能的原因
    3. 下一年度建议
    """

    result = quick_generate(prompt)
    print(result)

if __name__ == "__main__":
    try:
        test_gemini_flash()
        code_generation_example()
        data_analysis_example()

        print("\n✅ 所有测试完成！")
        print("\n📋 当前配置信息:")
        with open('gemini_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            model_info = config['settings']['model_info']
            print(f"模型: {model_info['name']}")
            print(f"类型: {model_info['type']}")
            print(f"定价: {model_info['pricing_tier']}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        print("请确保配置正确并运行: python3 start_gemini_system.py")