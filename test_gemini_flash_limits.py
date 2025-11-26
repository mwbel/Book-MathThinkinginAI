#!/usr/bin/env python3
"""
测试 Gemini 2.5 Flash 模型的免费额度限制
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple

class GeminiFlashLimitTester:
    def __init__(self):
        self.base_url = "https://generativelanguage.googleapis.com"
        self.model = "gemini-2.5-flash"  # 测试 Flash 模型

    def get_api_keys(self) -> List[str]:
        """从配置文件获取 API keys"""
        try:
            with open("gemini_config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            return [key_info["key"] for key_info in config["api_keys"] if key_info.get("active", True)]
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return []

    def test_single_request(self, api_key: str) -> Tuple[bool, str, Dict]:
        """测试单个请求"""
        url = f"{self.base_url}/v1beta/models/{self.model}:generateContent?key={api_key}"

        payload = {
            "contents": [{
                "parts": [{
                    "text": "Hello, please respond with just 'OK'"
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": 10,
                "temperature": 0.1
            }
        }

        try:
            start_time = time.time()
            response = requests.post(url, json=payload, timeout=10)
            end_time = time.time()

            if response.status_code == 200:
                return True, f"成功 (耗时: {end_time - start_time:.2f}s)", response.json()
            else:
                return False, f"失败: HTTP {response.status_code} - {response.text}", {}

        except Exception as e:
            return False, f"异常: {str(e)}", {}

    def test_rpm_limit(self, api_key: str, test_count: int = 20) -> Dict:
        """测试每分钟请求限制 (RPM)"""
        print(f"🧪 测试 RPM 限制 (连续发起 {test_count} 个请求)...")

        success_count = 0
        fail_count = 0
        responses = []

        for i in range(test_count):
            success, message, response_data = self.test_single_request(api_key)
            responses.append({
                "request": i + 1,
                "success": success,
                "message": message,
                "time": datetime.now().strftime("%H:%M:%S")
            })

            if success:
                success_count += 1
                print(f"  ✅ 请求 #{i+1}: {message}")
            else:
                fail_count += 1
                print(f"  ❌ 请求 #{i+1}: {message}")

            # 短暂间隔避免瞬间过载
            time.sleep(0.5)

        return {
            "total_requests": test_count,
            "success_count": success_count,
            "fail_count": fail_count,
            "responses": responses
        }

    def test_daily_limit(self, api_key: str, max_requests: int = 30) -> Dict:
        """测试每日请求限制"""
        print(f"🧪 测试每日限制 (最多测试 {max_requests} 个请求)...")

        results = []
        consecutive_failures = 0

        for i in range(max_requests):
            success, message, response_data = self.test_single_request(api_key)

            results.append({
                "request": i + 1,
                "success": success,
                "message": message,
                "time": datetime.now().strftime("%H:%M:%S")
            })

            if success:
                consecutive_failures = 0
                print(f"  ✅ 请求 #{i+1}: 成功")
            else:
                consecutive_failures += 1
                print(f"  ❌ 请求 #{i+1}: {message}")

                # 如果连续3次失败，可能是达到限制
                if consecutive_failures >= 3:
                    print(f"  ⚠️  连续 {consecutive_failures} 次失败，可能已达到限制")
                    break

            # 每10个请求后等待更长时间
            if (i + 1) % 10 == 0:
                print(f"  ⏳ 已完成 {i+1} 个请求，等待 10 秒...")
                time.sleep(10)
            else:
                time.sleep(2)

        success_count = sum(1 for r in results if r["success"])

        return {
            "total_requests": len(results),
            "success_count": success_count,
            "fail_count": len(results) - success_count,
            "results": results
        }

    def test_model_availability(self, api_key: str) -> bool:
        """测试模型是否可用"""
        url = f"{self.base_url}/v1beta/models?key={api_key}"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                flash_models = [m for m in models if "flash" in m.get("name", "").lower()]

                if flash_models:
                    print(f"✅ 发现 Flash 模型:")
                    for model in flash_models:
                        print(f"   - {model.get('name', 'Unknown')}")
                    return True
                else:
                    print(f"❌ 未找到 Flash 模型")
                    print(f"可用模型: {[m.get('name', 'Unknown') for m in models[:5]]}")
                    return False
            else:
                print(f"❌ 无法获取模型列表: HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ 测试模型可用性失败: {e}")
            return False

    def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 开始 Gemini 2.5 Flash 限制测试")
        print("=" * 50)

        api_keys = self.get_api_keys()
        if not api_keys:
            print("❌ 没有可用的 API keys")
            return

        print(f"📋 找到 {len(api_keys)} 个 API keys，使用第一个进行测试")
        test_api_key = api_keys[0]
        print(f"🔑 测试 API Key: {test_api_key[:20]}...")

        # 1. 测试模型可用性
        print(f"\n1️⃣ 测试模型可用性...")
        model_available = self.test_model_availability(test_api_key)

        if not model_available:
            print(f"❌ Flash 模型不可用，尝试测试标准模型...")
            self.model = "gemini-1.5-flash"
            model_available = self.test_model_availability(test_api_key)

            if not model_available:
                print(f"❌ 无法找到可用的 Flash 模型")
                return

        # 2. 测试基本请求
        print(f"\n2️⃣ 测试基本请求功能...")
        success, message, response_data = self.test_single_request(test_api_key)
        if success:
            print(f"✅ 基本请求测试成功: {message}")
        else:
            print(f"❌ 基本请求测试失败: {message}")
            return

        # 3. 测试 RPM 限制
        print(f"\n3️⃣ 测试 RPM 限制...")
        rpm_results = self.test_rpm_limit(test_api_key, 15)

        # 4. 测试每日限制（少量测试）
        print(f"\n4️⃣ 测试每日限制 (快速测试)...")
        daily_results = self.test_daily_limit(test_api_key, 10)

        # 5. 生成报告
        print(f"\n" + "=" * 50)
        print("📊 测试报告")
        print("=" * 50)

        print(f"🤖 测试模型: {self.model}")
        print(f"🔑 API Key: {test_api_key[:20]}...")

        print(f"\n📈 RPM 测试结果:")
        print(f"   总请求数: {rpm_results['total_requests']}")
        print(f"   成功: {rpm_results['success_count']}")
        print(f"   失败: {rpm_results['fail_count']}")
        print(f"   成功率: {rpm_results['success_count']/rpm_results['total_requests']*100:.1f}%")

        print(f"\n📅 每日限制测试结果:")
        print(f"   测试请求数: {daily_results['total_requests']}")
        print(f"   成功: {daily_results['success_count']}")
        print(f"   失败: {daily_results['fail_count']}")

        print(f"\n💡 建议配置:")
        if rpm_results['success_count'] >= 10:
            print(f"   RPM 限制: 至少 15 (成功测试了 {rpm_results['success_count']})")
        else:
            print(f"   RPM 限制: 可能较低，只成功 {rpm_results['success_count']}")

        print(f"   建议日限额: 250 (官方文档值)")
        print(f"   建议配置模型: {self.model}")

def main():
    tester = GeminiFlashLimitTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()