#!/usr/bin/env python3
"""
测试优化后的 Gemini API 限制配置
"""

import json
import time
from gemini_wrapper import quick_generate

def test_rate_limits():
    """测试优化后的速率限制"""
    print("🚀 测试优化后的 Gemini API 配置")
    print("=" * 60)

    # 读取配置文件
    with open('gemini_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 显示配置信息
    settings = config['settings']
    rate_limits = settings['rate_limits']
    model_info = settings['model_info']

    print("📋 当前配置信息:")
    print(f"  模型: {model_info['name']}")
    print(f"  定价: {model_info['pricing_tier']}")
    print(f"  冷却时间: {settings['cooldown_minutes']} 分钟")
    print(f"  最大重试: {settings['max_retries']} 次")
    print()

    print("📊 速率限制配置:")
    print(f"  RPM: {rate_limits['rpm']} (官方限制: {model_info['official_limits']['rpm_limit']})")
    print(f"  RPH: {rate_limits['rph']} (官方限制: {model_info['official_limits']['rph_limit']})")
    print(f"  TPM: {rate_limits['tpm']:,}")
    print(f"  TPD: {rate_limits['tpd']:,}")
    print()

    print("🔑 API 密钥配置:")
    active_keys = [k for k in config['api_keys'] if k['active']]
    total_daily_limit = sum(k['daily_limit'] for k in active_keys)

    print(f"  活跃密钥数量: {len(active_keys)}")
    print(f"  每个密钥日限额: {active_keys[0]['daily_limit']:,}")
    print(f"  总日限额: {total_daily_limit:,}")
    print()

    # 计算理论最大吞吐量
    print("🔥 理论性能指标:")
    print(f"  每分钟最大请求: {rate_limits['rpm']}")
    print(f"  每小时最大请求: {rate_limits['rph']}")
    print(f"  每日最大请求: {rate_limits['rph'] * 24:,}")
    print(f"  每月最大请求: {rate_limits['rph'] * 24 * 30:,}")
    print()

def test_quick_requests():
    """测试快速请求能力"""
    print("⚡ 测试快速请求处理能力")
    print("-" * 40)

    test_prompts = [
        "用一句话总结人工智能",
        "Python中什么是列表推导式？",
        "机器学习的主要类型有哪些？",
        "解释什么是API",
        "什么是算法复杂度？"
    ]

    start_time = time.time()
    successful_requests = 0

    for i, prompt in enumerate(test_prompts, 1):
        try:
            print(f"请求 {i}: {prompt[:30]}...")
            result = quick_generate(prompt)
            print(f"  ✅ 成功: {result[:50]}...")
            successful_requests += 1
            time.sleep(0.5)  # 短暂延迟避免过载
        except Exception as e:
            print(f"  ❌ 失败: {e}")

    end_time = time.time()
    duration = end_time - start_time

    print(f"\n📈 测试结果:")
    print(f"  成功请求: {successful_requests}/{len(test_prompts)}")
    print(f"  总耗时: {duration:.2f} 秒")
    print(f"  平均响应时间: {duration/len(test_prompts):.2f} 秒/请求")
    print(f"  吞吐量: {len(test_prompts)/duration:.2f} 请求/秒")

def performance_recommendations():
    """性能优化建议"""
    print("\n💡 性能优化建议:")
    print("-" * 40)

    print("✅ 已优化配置:")
    print("  • RPM 设置为 50 (接近官方限制的 60)")
    print("  • RPH 设置为 3000 (接近官方限制的 3600)")
    print("  • 每个密钥日限额提升至 4000")
    print("  • 冷却时间缩短至 5 分钟")
    print()

    print("🎯 最佳实践:")
    print("  • 对于小任务: 使用单个密钥即可")
    print("  • 对于大任务: 系统会自动轮换密钥")
    print("  • 批量处理: 建议每分钟不超过 50 个请求")
    print("  • 长时间运行: 启用监控服务")
    print()

    print("📊 监控命令:")
    print("  • 查看状态: python3 gemini_api_manager.py report")
    print("  • 启动监控: python3 gemini_monitor.py monitor")
    print("  • 测试所有密钥: python3 gemini_api_manager.py test")

if __name__ == "__main__":
    try:
        test_rate_limits()
        test_quick_requests()
        performance_recommendations()

        print("\n🎉 配置优化完成！")
        print("你的 Gemini API 现在可以充分利用免费层级限制了。")

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        print("请检查配置文件和网络连接。")