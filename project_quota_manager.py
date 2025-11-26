#!/usr/bin/env python3
"""
项目级额度管理器
正确处理 Gemini API 的项目级共享额度
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProjectQuotaManager:
    def __init__(self, config_file: str = "gemini_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.quota_file = "project_quota.json"
        self.quota_data = self.load_quota_data()

    def load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"api_keys": [], "settings": {"rate_limits": {"tpd": 250000}}}

    def load_quota_data(self) -> Dict:
        """加载项目额度数据"""
        if os.path.exists(self.quota_file):
            with open(self.quota_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 初始化项目额度数据
        return {
            "project_id": "shared_project",  # 所有 keys 共享同一个项目
            "daily_quota": self.config.get("settings", {}).get("rate_limits", {}).get("tpd", 250000),
            "daily_usage": 0,
            "last_reset_date": datetime.now().strftime("%Y-%m-%d"),
            "reset_time_beijing": "15:00",  # 下午3点重置
            "api_keys_usage": {},  # 跟踪每个 key 的使用情况
            "warnings_sent": []
        }

    def save_quota_data(self):
        """保存项目额度数据"""
        with open(self.quota_file, 'w', encoding='utf-8') as f:
            json.dump(self.quota_data, f, indent=2, ensure_ascii=False)

    def check_and_reset_quota(self):
        """检查是否需要重置额度（北京时间下午3点）"""
        now = datetime.now()
        beijing_time = now + timedelta(hours=8)
        today = beijing_time.strftime("%Y-%m-%d")

        # 检查是否是新的重置周期
        if (beijing_time.hour >= 15 and
            self.quota_data["last_reset_date"] < today):

            logger.info(f"🔄 项目额度重置 (北京时间 {beijing_time.strftime('%Y-%m-%d %H:%M')})")

            # 重置额度
            self.quota_data["daily_usage"] = 0
            self.quota_data["last_reset_date"] = today
            self.quota_data["warnings_sent"] = []

            # 保留 key 使用统计，但重置警告
            for key_name in self.quota_data["api_keys_usage"]:
                self.quota_data["api_keys_usage"][key_name]["warnings_sent"] = []

            self.save_quota_data()
            return True

        return False

    def get_quota_status(self) -> Dict:
        """获取项目额度状态"""
        self.check_and_reset_quota()

        daily_quota = self.quota_data["daily_quota"]
        daily_usage = self.quota_data["daily_usage"]
        remaining = daily_quota - daily_usage
        usage_percent = (daily_usage / daily_quota * 100) if daily_quota > 0 else 0

        # 计算距离重置时间
        now = datetime.now()
        beijing_time = now + timedelta(hours=8)

        if beijing_time.hour >= 15:
            # 明天下午3点
            reset_time = beijing_time.replace(hour=15, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:
            # 今天下午3点
            reset_time = beijing_time.replace(hour=15, minute=0, second=0, microsecond=0)

        time_until_reset = reset_time - beijing_time
        hours = time_until_reset.seconds // 3600
        minutes = (time_until_reset.seconds % 3600) // 60

        return {
            "daily_quota": daily_quota,
            "daily_usage": daily_usage,
            "remaining": remaining,
            "usage_percent": usage_percent,
            "time_until_reset": f"{hours}小时{minutes}分钟",
            "status": "normal" if usage_percent < 80 else "warning" if usage_percent < 95 else "critical",
            "api_keys_count": len([k for k in self.config.get("api_keys", []) if k.get("active", True)])
        }

    def can_use_tokens(self, estimated_tokens: int) -> tuple[bool, str]:
        """检查是否可以使用指定数量的 tokens"""
        self.check_and_reset_quota()

        daily_quota = self.quota_data["daily_quota"]
        daily_usage = self.quota_data["daily_usage"]

        if daily_usage + estimated_tokens > daily_quota:
            shortage = (daily_usage + estimated_tokens) - daily_quota
            return False, f"项目额度不足，需要 {shortage:,} 更多 tokens"

        return True, "额度充足"

    def record_usage(self, api_key_name: str, input_tokens: int, output_tokens: int, success: bool = True):
        """记录 API 使用情况"""
        self.check_and_reset_quota()

        total_tokens = input_tokens + output_tokens

        # 更新项目总使用量
        if success:
            self.quota_data["daily_usage"] += total_tokens
        else:
            # 失败的请求也算消耗（因为已经发送了输入）
            self.quota_data["daily_usage"] += input_tokens

        # 更新单个 key 的使用统计
        if api_key_name not in self.quota_data["api_keys_usage"]:
            self.quota_data["api_keys_usage"][api_key_name] = {
                "total_usage": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "last_used": None,
                "warnings_sent": []
            }

        key_stats = self.quota_data["api_keys_usage"][api_key_name]
        key_stats["total_usage"] += total_tokens
        key_stats["last_used"] = datetime.now().isoformat()

        if success:
            key_stats["successful_requests"] += 1
        else:
            key_stats["failed_requests"] += 1

        # 检查是否需要发送警告
        self.check_warnings()

        self.save_quota_data()

    def check_warnings(self):
        """检查并发送额度警告"""
        quota_status = self.get_quota_status()
        usage_percent = quota_status["usage_percent"]

        # 警告阈值
        warning_thresholds = [50, 80, 90, 95]

        for threshold in warning_thresholds:
            if (usage_percent >= threshold and
                threshold not in self.quota_data["warnings_sent"]):

                self.quota_data["warnings_sent"].append(threshold)

                if threshold == 50:
                    logger.warning(f"⚠️  项目额度已使用 {usage_percent:.1f}%")
                elif threshold == 80:
                    logger.warning(f"🚨 项目额度已使用 {usage_percent:.1f}%，请注意")
                elif threshold == 90:
                    logger.error(f"🚨🚨 项目额度已使用 {usage_percent:.1f}%，即将用完")
                elif threshold == 95:
                    logger.error(f"🚨🚨🚨 项目额度已使用 {usage_percent:.1f}%，即将耗尽")

    def get_best_api_key(self) -> Optional[str]:
        """获取最佳 API key（轮询选择）"""
        active_keys = [k for k in self.config.get("api_keys", []) if k.get("active", True)]

        if not active_keys:
            return None

        # 轮询选择使用最少的 key
        key_usage = {}
        for key_info in active_keys:
            key_name = key_info["name"]
            if key_name in self.quota_data["api_keys_usage"]:
                key_usage[key_name] = self.quota_data["api_keys_usage"][key_name]["total_usage"]
            else:
                key_usage[key_name] = 0

        # 选择使用最少的 key
        best_key_name = min(key_usage, key=key_usage.get)

        for key_info in active_keys:
            if key_info["name"] == best_key_name:
                return key_info["key"]

        return None

    def get_detailed_report(self) -> str:
        """生成详细的项目额度报告"""
        status = self.get_quota_status()

        report = [
            "=" * 60,
            "📊 Gemini API 项目额度报告",
            "=" * 60,
            "",
            f"🎯 项目状态: {status['status'].upper()}",
            f"📅 今日日期: {datetime.now().strftime('%Y-%m-%d')}",
            f"⏰ 重置时间: 北京时间下午3点",
            f"⏳ 距离重置: {status['time_until_reset']}",
            "",
            "📈 额度使用情况:",
            f"   总额度: {status['daily_quota']:,} tokens",
            f"   已使用: {status['daily_usage']:,} tokens",
            f"   剩余: {status['remaining']:,} tokens",
            f"   使用率: {status['usage_percent']:.1f}%",
            "",
            f"🔑 活跃 API Keys: {status['api_keys_count']} 个"
        ]

        # 添加各 key 的使用统计
        if self.quota_data["api_keys_usage"]:
            report.extend([
                "",
                "📊 API Key 使用统计:",
                "-" * 40
            ])

            for key_name, stats in self.quota_data["api_keys_usage"].items():
                last_used = stats.get("last_used", "从未使用")
                if last_used != "从未使用":
                    last_used = datetime.fromisoformat(last_used).strftime("%H:%M:%S")

                report.extend([
                    f"🔑 {key_name}:",
                    f"   总使用: {stats['total_usage']:,} tokens",
                    f"   成功请求: {stats['successful_requests']}",
                    f"   失败请求: {stats['failed_requests']}",
                    f"   最后使用: {last_used}",
                    ""
                ])

        report.extend([
            "💡 使用建议:",
            "   - 额度按项目计算，所有 keys 共享",
            "   - 建议在北京时间下午3点后大量使用",
            "   - 使用率超过80%时请谨慎使用",
            "",
            "=" * 60
        ])

        return "\n".join(report)

# 全局项目额度管理器
project_quota_manager = ProjectQuotaManager()

def get_project_quota_status():
    """获取项目额度状态的便捷函数"""
    return project_quota_manager.get_quota_status()

def can_use_project_tokens(estimated_tokens: int):
    """检查项目额度的便捷函数"""
    return project_quota_manager.can_use_tokens(estimated_tokens)

def record_project_usage(api_key_name: str, input_tokens: int, output_tokens: int, success: bool = True):
    """记录项目使用量的便捷函数"""
    project_quota_manager.record_usage(api_key_name, input_tokens, output_tokens, success)

def get_best_api_key():
    """获取最佳 API key 的便捷函数"""
    return project_quota_manager.get_best_api_key()

if __name__ == "__main__":
    # 测试项目额度管理器
    print(get_project_quota_status())
    print(project_quota_manager.get_detailed_report())