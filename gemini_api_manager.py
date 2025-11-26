#!/usr/bin/env python3
"""
Gemini API Key 池管理器
自动轮换 API key，检测额度并切换到可用的 key
"""

import json
import os
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiAPIManager:
    def __init__(self, config_file: str = "gemini_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.usage_file = "gemini_usage.json"
        self.usage_data = self.load_usage()

    def load_config(self) -> Dict:
        """加载 API key 配置"""
        default_config = {
            "api_keys": [
                {
                    "key": "your_first_api_key_here",
                    "name": "Gemini-1",
                    "daily_limit": 1000,  # 每日请求限制
                    "active": True
                },
                {
                    "key": "your_second_api_key_here",
                    "name": "Gemini-2",
                    "daily_limit": 1000,
                    "active": True
                },
                {
                    "key": "your_third_api_key_here",
                    "name": "Gemini-3",
                    "daily_limit": 1000,
                    "active": True
                }
            ],
            "settings": {
                "cooldown_minutes": 60,  # 冷却时间
                "retry_on_quota_exceeded": True,
                "max_retries": 3
            }
        }

        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 确保所有必要字段存在
                if 'settings' not in config:
                    config['settings'] = default_config['settings']
                return config
        else:
            # 创建默认配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            logger.info(f"已创建默认配置文件: {self.config_file}")
            logger.info("请编辑配置文件，添加你的真实 API keys")
            return default_config

    def load_usage(self) -> Dict:
        """加载使用情况数据"""
        if os.path.exists(self.usage_file):
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_usage(self):
        """保存使用情况数据"""
        with open(self.usage_file, 'w', encoding='utf-8') as f:
            json.dump(self.usage_data, f, indent=2, ensure_ascii=False)

    def get_daily_usage(self, api_key: str) -> int:
        """获取指定 API key 今日使用量"""
        today = datetime.now().strftime("%Y-%m-%d")
        key_data = self.usage_data.get(api_key, {})
        return key_data.get(today, {}).get("count", 0)

    def is_key_available(self, api_key_info: Dict) -> bool:
        """检查 API key 是否可用"""
        api_key = api_key_info["key"]
        daily_limit = api_key_info["daily_limit"]

        # 检查是否被禁用
        if not api_key_info.get("active", True):
            return False

        # 检查今日使用量
        daily_usage = self.get_daily_usage(api_key)
        if daily_usage >= daily_limit:
            logger.info(f"API key {api_key_info['name']} 已达到日限额: {daily_usage}/{daily_limit}")
            return False

        # 检查冷却时间
        key_data = self.usage_data.get(api_key, {})
        last_error_time = key_data.get("last_error_time")
        if last_error_time:
            error_time = datetime.fromisoformat(last_error_time)
            cooldown_minutes = self.config["settings"]["cooldown_minutes"]
            if datetime.now() < error_time + timedelta(minutes=cooldown_minutes):
                logger.info(f"API key {api_key_info['name']} 仍在冷却中")
                return False

        return True

    def get_current_api_key(self) -> Optional[str]:
        """获取当前可用的 API key"""
        # 按优先级获取可用的 API key
        for api_key_info in self.config["api_keys"]:
            if self.is_key_available(api_key_info):
                return api_key_info["key"]

        logger.warning("没有可用的 API key！")
        return None

    def record_usage(self, api_key: str, success: bool = True, error_msg: str = None):
        """记录 API 使用情况"""
        today = datetime.now().strftime("%Y-%m-%d")

        if api_key not in self.usage_data:
            self.usage_data[api_key] = {}

        if today not in self.usage_data[api_key]:
            self.usage_data[api_key][today] = {
                "count": 0,
                "success_count": 0,
                "error_count": 0,
                "last_used": None
            }

        # 更新使用统计
        self.usage_data[api_key][today]["count"] += 1
        self.usage_data[api_key][today]["last_used"] = datetime.now().isoformat()

        if success:
            self.usage_data[api_key][today]["success_count"] += 1
        else:
            self.usage_data[api_key][today]["error_count"] += 1
            self.usage_data[api_key]["last_error_time"] = datetime.now().isoformat()
            self.usage_data[api_key]["last_error"] = error_msg

        self.save_usage()

    def test_api_key(self, api_key: str) -> bool:
        """测试 API key 是否有效"""
        try:
            # 这里使用简单的请求测试 API key
            headers = {"Content-Type": "application/json"}
            url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"

            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"测试 API key 失败: {e}")
            return False

    def get_usage_report(self) -> str:
        """生成使用情况报告"""
        report = ["=== Gemini API 使用情况报告 ===\n"]
        today = datetime.now().strftime("%Y-%m-%d")

        for api_key_info in self.config["api_keys"]:
            api_key = api_key_info["key"]
            name = api_key_info["name"]
            daily_limit = api_key_info["daily_limit"]

            daily_usage = self.get_daily_usage(api_key)
            usage_percent = (daily_usage / daily_limit * 100) if daily_limit > 0 else 0

            key_data = self.usage_data.get(api_key, {})
            today_data = key_data.get(today, {})
            success_count = today_data.get("success_count", 0)
            error_count = today_data.get("error_count", 0)

            status = "✅ 可用" if self.is_key_available(api_key_info) else "❌ 不可用"

            report.append(f"📊 {name}:")
            report.append(f"   状态: {status}")
            report.append(f"   今日使用: {daily_usage}/{daily_limit} ({usage_percent:.1f}%)")
            report.append(f"   成功/失败: {success_count}/{error_count}")
            report.append("")

        return "\n".join(report)

    def set_active_key(self, key_name: str, active: bool):
        """手动启用/禁用指定的 API key"""
        for api_key_info in self.config["api_keys"]:
            if api_key_info["name"] == key_name:
                api_key_info["active"] = active
                self.save_config()
                logger.info(f"已{('启用' if active else '禁用')} API key: {key_name}")
                return True
        logger.error(f"未找到名为 {key_name} 的 API key")
        return False

    def save_config(self):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="Gemini API Key 管理器")
    parser.add_argument("action", choices=["current", "report", "test", "enable", "disable"],
                       help="要执行的操作")
    parser.add_argument("--key-name", help="API key 名称（用于 enable/disable 操作）")

    args = parser.parse_args()

    manager = GeminiAPIManager()

    if args.action == "current":
        current_key = manager.get_current_api_key()
        if current_key:
            print(f"当前可用 API key: {current_key[:20]}...")
        else:
            print("没有可用的 API key")

    elif args.action == "report":
        print(manager.get_usage_report())

    elif args.action == "test":
        for api_key_info in manager.config["api_keys"]:
            key = api_key_info["key"]
            name = api_key_info["name"]
            if manager.test_api_key(key):
                print(f"✅ {name}: API key 有效")
            else:
                print(f"❌ {name}: API key 无效")

    elif args.action == "enable" and args.key_name:
        manager.set_active_key(args.key_name, True)

    elif args.action == "disable" and args.key_name:
        manager.set_active_key(args.key_name, False)

if __name__ == "__main__":
    main()