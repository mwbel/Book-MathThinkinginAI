#!/usr/bin/env python3
"""
Gemini API 速率限制管理器
处理 RPM、TPM、RPD 限制
"""

import time
import json
from datetime import datetime, timedelta
from collections import deque, defaultdict
from typing import Dict, List
import threading

class RateLimiter:
    def __init__(self, config_file: str = "gemini_config.json"):
        self.config = self.load_config(config_file)
        self.rate_limits = self.config.get("settings", {}).get("rate_limits", {
            "rpm": 15,
            "tpm": 1000000,
            "rpd": 250
        })

        # 请求记录（用于 RPM 限制）
        self.requests = deque()
        self.lock = threading.Lock()

        # Token 记录（用于 TPM 限制）
        self.tokens = deque()

        # 每日请求计数（用于 RPD 限制）
        self.daily_requests = defaultdict(int)
        self.last_reset_date = datetime.now().date()

    def load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"settings": {"rate_limits": {"rpm": 10, "tpm": 250000, "tpd": 250000}}}

    def reset_daily_counters(self):
        """重置每日计数器（北京时间下午4点重置）"""
        now = datetime.now()
        beijing_time = now + timedelta(hours=8)  # 转换为北京时间
        current_date = beijing_time.date()

        # 检查是否需要重置（北京时间下午4点后）
        if current_date > self.last_reset_date and beijing_time.hour >= 16:
            self.daily_requests.clear()
            self.last_reset_date = current_date
            print("🔄 每日限制计数器已重置")

    def can_make_request(self, estimated_tokens: int = 100) -> tuple[bool, str]:
        """检查是否可以发起请求"""
        with self.lock:
            self.reset_daily_counters()

            now = time.time()

            # 检查每日Token限制 (TPD) - Gemini 2.5-Flash: 250K tokens/day
            today = datetime.now().date()
            daily_tokens = sum(token_record["count"] for token_record in self.tokens
                              if datetime.fromtimestamp(token_record["time"]).date() == today)
            if daily_tokens + estimated_tokens > self.rate_limits["tpd"]:
                wait_time = self._time_until_daily_reset()
                return False, f"已达到每日token限制 {self.rate_limits['tpd']:,}，请等待 {wait_time}"

            # 检查 RPM 限制 (Gemini 2.5-Flash: 10 RPM)
            # 清理1分钟前的请求记录
            one_minute_ago = now - 60
            while self.requests and self.requests[0] < one_minute_ago:
                self.requests.popleft()

            if len(self.requests) >= self.rate_limits["rpm"]:
                wait_time = 60 - (now - self.requests[0])
                return False, f"已达到每分钟请求限制 {self.rate_limits['rpm']} (Gemini 2.5-Flash)，请等待 {wait_time:.1f} 秒"

            # 检查 TPM 限制 (Gemini 2.5-Flash: 250K TPM)
            # 清理1分钟前的token记录
            while self.tokens and self.tokens[0]["time"] < one_minute_ago:
                self.tokens.popleft()

            current_tpm = sum(token_record["count"] for token_record in self.tokens)
            if current_tpm + estimated_tokens > self.rate_limits["tpm"]:
                available_tokens = self.rate_limits["tpm"] - current_tpm
                return False, f"已达到每分钟token限制 {self.rate_limits['tpm']:,} (Gemini 2.5-Flash)，本分钟内只能再使用 {available_tokens:,} tokens"

            return True, "可以发起请求"

    def record_request(self, api_key: str, input_tokens: int = 0, output_tokens: int = 0):
        """记录一次请求"""
        with self.lock:
            now = time.time()

            # 记录请求时间（用于 RPM）
            self.requests.append(now)

            # 记录token使用（用于 TPM）
            total_tokens = input_tokens + output_tokens
            self.tokens.append({
                "time": now,
                "count": total_tokens
            })

            # 记录每日请求数（用于 RPD）
            today = datetime.now().date()
            self.daily_requests[api_key] += 1

    def _time_until_daily_reset(self) -> str:
        """计算距离每日重置的时间"""
        now = datetime.now()
        beijing_time = now + timedelta(hours=8)

        # 下一次重置是北京时间下午3点 (PT午夜 + 15小时)
        if beijing_time.hour >= 15:
            # 明天下午3点
            reset_time = beijing_time.replace(hour=15, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:
            # 今天下午3点
            reset_time = beijing_time.replace(hour=15, minute=0, second=0, microsecond=0)

        time_until_reset = reset_time - beijing_time
        hours = time_until_reset.seconds // 3600
        minutes = (time_until_reset.seconds % 3600) // 60

        return f"{hours}小时{minutes}分钟"

    def get_status(self) -> Dict:
        """获取当前速率限制状态"""
        with self.lock:
            now = time.time()
            one_minute_ago = now - 60

            # 计算当前RPM
            recent_requests = [req_time for req_time in self.requests if req_time >= one_minute_ago]
            current_rpm = len(recent_requests)

            # 计算当前TPM
            recent_tokens = [token_record for token_record in self.tokens if token_record["time"] >= one_minute_ago]
            current_tpm = sum(token_record["count"] for token_record in recent_tokens)

            # 计算每日Token使用 (TPD)
            today = datetime.now().date()
            daily_tokens = sum(token_record["count"] for token_record in self.tokens
                              if datetime.fromtimestamp(token_record["time"]).date() == today)

            return {
                "current_rpm": current_rpm,
                "max_rpm": self.rate_limits["rpm"],
                "rpm_remaining": self.rate_limits["rpm"] - current_rpm,
                "current_tpm": current_tpm,
                "max_tpm": self.rate_limits["tpm"],
                "tpm_remaining": self.rate_limits["tpm"] - current_tpm,
                "current_tpd": daily_tokens,
                "max_tpd": self.rate_limits["tpd"],
                "tpd_remaining": self.rate_limits["tpd"] - daily_tokens,
                "time_until_reset": self._time_until_daily_reset()
            }

    def wait_if_needed(self, estimated_tokens: int = 100):
        """如果需要，等待直到可以发起请求"""
        while True:
            can_request, reason = self.can_make_request(estimated_tokens)
            if can_request:
                break

            print(f"⏳ {reason}")
            time.sleep(2)  # 每2秒检查一次

# 全局速率限制器实例
rate_limiter = RateLimiter()

def check_rate_limit(estimated_tokens: int = 100) -> tuple[bool, str]:
    """检查速率限制的便捷函数"""
    return rate_limiter.can_make_request(estimated_tokens)

def record_api_usage(api_key: str, input_tokens: int = 0, output_tokens: int = 0):
    """记录API使用的便捷函数"""
    rate_limiter.record_request(api_key, input_tokens, output_tokens)

def wait_for_rate_limit(estimated_tokens: int = 100):
    """等待速率限制的便捷函数"""
    rate_limiter.wait_if_needed(estimated_tokens)

def get_rate_limit_status():
    """获取速率限制状态的便捷函数"""
    return rate_limiter.get_status()

if __name__ == "__main__":
    # 测试速率限制器
    print("🧪 测试 Gemini API 速率限制器")
    print("=" * 40)

    # 显示当前状态
    status = get_rate_limit_status()
    print(f"📊 当前状态:")
    print(f"   RPM: {status['current_rpm']}/{status['max_rpm']} (剩余: {status['rpm_remaining']})")
    print(f"   TPM: {status['current_tpm']:,}/{status['max_tpm']:,} (剩余: {status['tpm_remaining']:,})")
    print(f"   TPD (每日Token): {status['current_tpd']:,}/{status['max_tpd']:,} (剩余: {status['tpd_remaining']:,})")
    print(f"   距离重置: {status['time_until_reset']}")

    # 测试请求检查
    can_request, reason = check_rate_limit(1000)
    print(f"\n✅ 是否可以发起请求: {'是' if can_request else '否'}")
    if not can_request:
        print(f"   原因: {reason}")