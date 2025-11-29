#!/usr/bin/env python3
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from gemini_api_manager import GeminiAPIManager

if __name__ == "__main__":
    manager = GeminiAPIManager()
    current_key = manager.get_current_api_key()
    if current_key:
        print(current_key)
    else:
        print("NO_AVAILABLE_KEYS")
