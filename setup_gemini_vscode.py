#!/usr/bin/env python3
"""
VS Code Gemini API 配置脚本
自动配置 VS Code 使用轮换的 API key
"""

import json
import os
import subprocess
from pathlib import Path
from gemini_api_manager import GeminiAPIManager

def setup_vscode_config():
    """配置 VS Code 使用动态 API key"""
    manager = GeminiAPIManager()

    # 获取 VS Code 设置文件路径
    vscode_settings_path = Path.home() / "Library/Application Support/Code/User/settings.json"

    if not vscode_settings_path.exists():
        print("❌ 未找到 VS Code 设置文件")
        return False

    # 读取现有设置
    with open(vscode_settings_path, 'r', encoding='utf-8') as f:
        settings = json.load(f)

    # 创建动态 API key 脚本路径
    script_path = os.path.abspath("get_current_gemini_key.py")
    key_script_content = f'''#!/usr/bin/env python3
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
'''

    with open("get_current_gemini_key.py", 'w', encoding='utf-8') as f:
        f.write(key_script_content)

    # 更新 VS Code 设置
    gemini_config = {
        "gemini.apiKeyCommand": f"python3 {os.path.abspath('get_current_gemini_key.py')}",
        "gemini.model": "gemini-2.5-pro",
        "gemini.maxTokens": 8192,
        "gemini.temperature": 0.7,
        "gemini.autoRetry": True,
        "gemini.maxRetries": 3
    }

    # 合并配置
    settings.update(gemini_config)

    # 保存设置
    with open(vscode_settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

    print("✅ VS Code 配置已更新")
    return True

def create_shell_aliases():
    """创建便捷的 shell 别名"""
    aliases = """
# Gemini API 管理别名
alias gemini-current='python3 /Users/Min369/Desktop/书/书稿打磨/gemini_api_manager.py current'
alias gemini-report='python3 /Users/Min369/Desktop/书/书稿打磨/gemini_api_manager.py report'
alias gemini-test='python3 /Users/Min369/Desktop/书/书稿打磨/gemini_api_manager.py test'
alias gemini-quick='python3 /Users/Min369/Desktop/书/书稿打磨/gemini_wrapper.py'
"""

    print("\n=== 将以下别名添加到 ~/.zshrc ===")
    print(aliases)

    # 自动添加到 .zshrc
    zshrc_path = Path.home() / ".zshrc"
    if zshrc_path.exists():
        with open(zshrc_path, 'a', encoding='utf-8') as f:
            f.write("\n" + aliases)
        print("✅ 别名已添加到 ~/.zshrc")
        print("请运行 'source ~/.zshrc' 使别名生效")

def install_requirements():
    """安装必要的依赖"""
    requirements = [
        "requests>=2.28.0",
        "python-dotenv>=0.19.0"
    ]

    print("📦 安装必要的 Python 包...")
    for req in requirements:
        try:
            subprocess.run(["pip3", "install", req], check=True, capture_output=True)
            print(f"✅ {req} 安装成功")
        except subprocess.CalledProcessError:
            print(f"❌ {req} 安装失败，请手动安装: pip3 install {req}")

def main():
    """主设置流程"""
    print("🚀 开始配置 VS Code Gemini API 轮换系统\n")

    # 1. 安装依赖
    install_requirements()

    print("\n" + "="*50)

    # 2. 配置 VS Code
    setup_vscode_config()

    print("\n" + "="*50)

    # 3. 创建 shell 别名
    create_shell_aliases()

    print("\n" + "="*50)
    print("✅ 配置完成！")
    print("\n📋 下一步操作:")
    print("1. 编辑 gemini_config.json 文件，添加你的真实 API keys")
    print("2. 运行 'source ~/.zshrc' 使别名生效")
    print("3. 使用 'gemini-test' 测试 API keys")
    print("4. 使用 'gemini-report' 查看使用情况")
    print("5. 重启 VS Code 使配置生效")

    # 显示当前配置状态
    manager = GeminiAPIManager()
    print(f"\n📊 当前配置状态:")
    print(f"- API key 数量: {len(manager.config['api_keys'])}")
    print(f"- 日限额/key: {manager.config['api_keys'][0]['daily_limit'] if manager.config['api_keys'] else 0}")
    print(f"- 冷却时间: {manager.config['settings']['cooldown_minutes']} 分钟")

if __name__ == "__main__":
    main()