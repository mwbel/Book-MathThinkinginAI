#!/usr/bin/env python3
"""
Gemini API 智能调用包装器
自动处理 API key 轮换、重试和错误处理
"""

import os
import json
import requests
import time
from typing import Dict, Optional, Any
from gemini_api_manager import GeminiAPIManager
import logging

logger = logging.getLogger(__name__)

class GeminiAPIWrapper:
    def __init__(self, config_file: str = "gemini_config.json"):
        self.manager = GeminiAPIManager(config_file)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.5-flash"  # 使用 Gemini 2.5-Flash 模型

    def _make_request(self, endpoint: str, payload: Dict, max_retries: int = None) -> Optional[Dict]:
        """发起 API 请求，自动处理重试和 API key 轮换"""
        if max_retries is None:
            max_retries = self.manager.config["settings"]["max_retries"]

        last_error = None

        for attempt in range(max_retries):
            # 获取当前可用的 API key
            api_key = self.manager.get_current_api_key()
            if not api_key:
                logger.error("没有可用的 API key")
                return None

            url = f"{self.base_url}{endpoint}?key={api_key}"

            try:
                logger.info(f"尝试请求 (第{attempt + 1}次): {endpoint}")

                response = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=30
                )

                # 处理响应
                if response.status_code == 200:
                    # 成功
                    self.manager.record_usage(api_key, success=True)
                    logger.info("API 请求成功")
                    return response.json()

                elif response.status_code == 429:
                    # 额度超限
                    error_msg = "API 额度已用完"
                    self.manager.record_usage(api_key, success=False, error_msg=error_msg)
                    logger.warning(f"API key 额度用完，切换到下一个")
                    last_error = error_msg
                    continue

                elif response.status_code == 403:
                    # API key 无效或权限不足
                    error_msg = "API key 无效或权限不足"
                    self.manager.record_usage(api_key, success=False, error_msg=error_msg)
                    logger.warning(f"API key 无效，切换到下一个")
                    last_error = error_msg
                    continue

                elif response.status_code >= 500:
                    # 服务器错误，可以重试
                    error_msg = f"服务器错误: {response.status_code}"
                    logger.warning(f"{error_msg}，重试中...")
                    last_error = error_msg
                    time.sleep(2 ** attempt)  # 指数退避
                    continue

                else:
                    # 其他错误
                    error_msg = f"API 请求失败: {response.status_code} - {response.text}"
                    self.manager.record_usage(api_key, success=False, error_msg=error_msg)
                    logger.error(error_msg)
                    last_error = error_msg
                    return None

            except requests.exceptions.RequestException as e:
                error_msg = f"网络请求异常: {str(e)}"
                logger.error(error_msg)
                self.manager.record_usage(api_key, success=False, error_msg=error_msg)
                last_error = error_msg
                time.sleep(2 ** attempt)  # 指数退避
                continue

        # 所有重试都失败了
        logger.error(f"API 请求最终失败: {last_error}")
        return None

    def generate_content(self, prompt: str, **kwargs) -> Optional[str]:
        """生成文本内容"""
        endpoint = f"/models/{self.model}:generateContent"

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "topK": kwargs.get("topK", 40),
                "topP": kwargs.get("topP", 0.95),
                "maxOutputTokens": kwargs.get("maxOutputTokens", 8192),
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
        }

        response = self._make_request(endpoint, payload)

        if response and "candidates" in response:
            candidates = response["candidates"]
            if candidates and len(candidates) > 0:
                content = candidates[0]["content"]["parts"][0]["text"]
                return content

        return None

    def start_chat(self, **kwargs) -> 'ChatSession':
        """开始聊天会话"""
        return ChatSession(self, **kwargs)

class ChatSession:
    def __init__(self, wrapper: GeminiAPIWrapper, **kwargs):
        self.wrapper = wrapper
        self.history = []
        self.generation_config = {
            "temperature": kwargs.get("temperature", 0.7),
            "topK": kwargs.get("topK", 40),
            "topP": kwargs.get("topP", 0.95),
            "maxOutputTokens": kwargs.get("maxOutputTokens", 8192),
        }

    def send_message(self, message: str) -> Optional[str]:
        """发送消息并获取回复"""
        # 添加用户消息到历史记录
        self.history.append({
            "role": "user",
            "parts": [{"text": message}]
        })

        endpoint = f"/models/{self.wrapper.model}:generateContent"

        payload = {
            "contents": self.history,
            "generationConfig": self.generation_config,
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
        }

        response = self.wrapper._make_request(endpoint, payload)

        if response and "candidates" in response:
            candidates = response["candidates"]
            if candidates and len(candidates) > 0:
                reply = candidates[0]["content"]["parts"][0]["text"]

                # 添加助手回复到历史记录
                self.history.append({
                    "role": "model",
                    "parts": [{"text": reply}]
                })

                return reply

        return None

    def clear_history(self):
        """清空对话历史"""
        self.history = []

# 便捷函数
def quick_generate(prompt: str, **kwargs) -> Optional[str]:
    """快速生成文本"""
    wrapper = GeminiAPIWrapper()
    return wrapper.generate_content(prompt, **kwargs)

def quick_chat() -> ChatSession:
    """快速开始聊天"""
    wrapper = GeminiAPIWrapper()
    return wrapper.start_chat()

if __name__ == "__main__":
    # 测试示例
    print("=== Gemini API 测试 ===")

    # 初始化 API 管理器
    manager = GeminiAPIManager()

    # 显示使用报告
    print(manager.get_usage_report())

    # 测试 API 调用
    wrapper = GeminiAPIWrapper()
    response = wrapper.generate_content("请用一句话介绍你自己")

    if response:
        print(f"API 测试成功: {response}")
    else:
        print("API 测试失败")