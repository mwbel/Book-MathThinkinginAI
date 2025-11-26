#!/usr/bin/env python3
"""
交互式 API Keys 配置脚本
"""

import json
import os

def setup_api_keys():
    """交互式设置 API keys"""
    config_file = "gemini_config.json"

    # 读取现有配置
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        print("❌ 配置文件不存在，请先运行启动脚本")
        return

    print("🔧 配置 Gemini API Keys")
    print("=" * 40)

    # 获取用户输入
    api_keys = []
    for i in range(3):  # 支持 3 个 API keys
        print(f"\n📝 设置第 {i+1} 个 API Key:")

        key = input(f"请输入 Gemini API Key #{i+1}: ").strip()
        if not key:
            print(f"⚠️  跳过第 {i+1} 个 API Key")
            continue

        name = input(f"请输入名称 (默认: Gemini-{i+1}): ").strip()
        if not name:
            name = f"Gemini-{i+1}"

        daily_limit = input(f"请输入日限额 (默认: 1000): ").strip()
        if not daily_limit:
            daily_limit = 1000
        else:
            try:
                daily_limit = int(daily_limit)
            except ValueError:
                print("⚠️  日限额必须是数字，使用默认值 1000")
                daily_limit = 1000

        api_keys.append({
            "key": key,
            "name": name,
            "daily_limit": daily_limit,
            "active": True
        })

    if not api_keys:
        print("❌ 没有输入任何有效的 API Key")
        return

    # 更新配置
    config["api_keys"] = api_keys

    # 保存配置
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 配置已保存到 {config_file}")
    print("\n📋 配置摘要:")
    for i, key_info in enumerate(api_keys, 1):
        masked_key = key_info["key"][:10] + "..." + key_info["key"][-4:]
        print(f"  {i}. {key_info['name']}: {masked_key}")
        print(f"     日限额: {key_info['daily_limit']}")

    print(f"\n🎉 API Keys 配置完成！")
    print("💡 接下来可以运行 'python3 gemini_api_manager.py test' 测试配置")

if __name__ == "__main__":
    setup_api_keys()