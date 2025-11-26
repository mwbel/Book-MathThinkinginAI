#!/usr/bin/env python3
"""
Gemini API 快速使用演示
展示如何使用轮换的 API key 进行文本生成
"""

from gemini_wrapper import GeminiAPIWrapper, quick_generate, quick_chat
import sys

def demo_simple_generation():
    """演示简单文本生成"""
    print("=== 简单文本生成演示 ===")

    prompt = "请用中文写一首关于编程的五言绝句"
    print(f"📝 输入: {prompt}")

    result = quick_generate(prompt, temperature=0.8, maxOutputTokens=500)

    if result:
        print(f"✨ 输出: {result}")
        return True
    else:
        print("❌ 生成失败")
        return False

def demo_chat_session():
    """演示聊天会话"""
    print("\n=== 聊天会话演示 ===")

    chat = quick_chat()

    messages = [
        "你好，我是小王，请记住我的名字",
        "我刚才叫什么名字？",
        "请给我推荐 3 本学习 Python 的书籍",
        "谢谢你的推荐"
    ]

    for i, msg in enumerate(messages, 1):
        print(f"\n👤 用户 [{i}]: {msg}")
        response = chat.send_message(msg)
        if response:
            print(f"🤖 助手: {response}")
        else:
            print("❌ 回复失败")
            return False

    return True

def demo_code_generation():
    """演示代码生成"""
    print("\n=== 代码生成演示 ===")

    prompt = """
请用 Python 写一个函数，实现以下功能：
1. 接收一个字符串列表
2. 返回最长的字符串
3. 如果有多个相同长度的字符串，返回第一个
请包含类型提示和文档字符串
"""

    print(f"📝 需求: {prompt.strip()}")

    result = quick_generate(prompt, temperature=0.3)

    if result:
        print(f"💻 生成的代码:\n{result}")
        return True
    else:
        print("❌ 代码生成失败")
        return False

def demo_translation():
    """演示翻译功能"""
    print("\n=== 翻译演示 ===")

    text = "Artificial Intelligence is transforming the way we work and live."
    prompt = f"请将以下英文翻译成中文，保持自然流畅：\n\n{text}"

    print(f"🌍 原文: {text}")

    result = quick_generate(prompt, temperature=0.5)

    if result:
        print(f"🇨🇳 译文: {result}")
        return True
    else:
        print("❌ 翻译失败")
        return False

def check_api_status():
    """检查 API 状态"""
    from gemini_api_manager import GeminiAPIManager

    print("🔍 检查 API 状态...")
    manager = GeminiAPIManager()

    current_key = manager.get_current_api_key()
    if current_key:
        print(f"✅ 当前可用 API key: {current_key[:20]}...")
    else:
        print("❌ 没有可用的 API key")
        return False

    # 显示使用报告
    report = manager.get_usage_report()
    print(report)

    return True

def main():
    """主演示流程"""
    print("🚀 Gemini API 轮换系统演示\n")

    # 检查 API 状态
    if not check_api_status():
        print("❌ API 状态检查失败，请先配置 API keys")
        sys.exit(1)

    demos = [
        demo_simple_generation,
        demo_chat_session,
        demo_code_generation,
        demo_translation
    ]

    success_count = 0
    total_count = len(demos)

    for demo_func in demos:
        try:
            if demo_func():
                success_count += 1
        except Exception as e:
            print(f"❌ 演示出错: {e}")

    print(f"\n📊 演示完成: {success_count}/{total_count} 成功")

    if success_count == total_count:
        print("🎉 所有演示都成功完成！API 轮换系统工作正常。")
    else:
        print("⚠️  部分演示失败，请检查配置和日志。")

if __name__ == "__main__":
    main()