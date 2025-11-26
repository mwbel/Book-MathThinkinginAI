#!/usr/bin/env python3
"""
简单的 Gemini API 测试脚本
"""

import requests
import json
import time

def test_api_key(api_key, key_name, timeout=30):
    """测试单个 API key"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

    print(f"🧪 测试 {key_name} (超时: {timeout}秒)...")

    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        end_time = time.time()

        if response.status_code == 200:
            print(f"✅ {key_name}: 成功! (耗时: {end_time - start_time:.2f}s)")

            # 解析响应，检查可用模型
            data = response.json()
            models = data.get("models", [])
            flash_models = [m for m in models if "flash" in m.get("name", "").lower()]

            if flash_models:
                print(f"   📱 可用 Flash 模型:")
                for model in flash_models:
                    print(f"      - {model.get('name', 'Unknown')}")
            else:
                print(f"   📋 可用模型: {[m.get('name', 'Unknown') for m in models[:3]]}")

            return True, models
        else:
            print(f"❌ {key_name}: HTTP {response.status_code} - {response.text[:100]}")
            return False, None

    except requests.exceptions.Timeout:
        print(f"⏰ {key_name}: 连接超时")
        return False, None
    except requests.exceptions.ConnectionError:
        print(f"🔌 {key_name}: 连接错误")
        return False, None
    except Exception as e:
        print(f"💥 {key_name}: 异常 - {str(e)}")
        return False, None

def main():
    print("🚀 Gemini API 连接测试")
    print("=" * 50)

    # 读取配置
    try:
        with open("gemini_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return

    api_keys = config["api_keys"]
    print(f"📋 找到 {len(api_keys)} 个 API keys")
    print()

    successful_keys = 0
    all_models = set()

    for key_info in api_keys:
        if not key_info.get("active", True):
            print(f"⏸️  {key_info['name']}: 已禁用，跳过")
            continue

        success, models = test_api_key(
            key_info["key"],
            key_info["name"],
            timeout=15  # 15秒超时
        )

        if success:
            successful_keys += 1
            if models:
                model_names = [m.get("name", "") for m in models]
                all_models.update(model_names)

        print()  # 空行分隔

    # 总结
    print("=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    print(f"✅ 成功连接: {successful_keys}/{len(api_keys)} 个 API keys")

    if successful_keys > 0:
        print(f"🤖 发现模型: {len(all_models)} 个")
        if all_models:
            print("   模型列表:")
            for model in sorted(all_models):
                print(f"      - {model}")
        print()
        print("🎉 系统可以正常使用！")
    else:
        print("⚠️  没有可用的 API keys")
        print("💡 建议:")
        print("   1. 检查网络连接")
        print("   2. 验证 API keys 是否正确")
        print("   3. 确认 Google Cloud 项目状态")

if __name__ == "__main__":
    main()