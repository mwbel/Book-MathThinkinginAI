#!/usr/bin/env python3
"""
Gemini API 轮换系统一键启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查 Python 版本"""
    if sys.version_info < (3, 7):
        print("❌ 需要 Python 3.7 或更高版本")
        return False
    print(f"✅ Python 版本: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """安装依赖包"""
    print("\n📦 安装依赖包...")

    required_packages = [
        "requests>=2.28.0",
        "schedule>=1.2.0",
        "python-dotenv>=0.19.0"
    ]

    for package in required_packages:
        try:
            print(f"安装 {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package],
                         check=True, capture_output=True)
            print(f"✅ {package} 安装成功")
        except subprocess.CalledProcessError:
            print(f"❌ {package} 安装失败")
            return False

    return True

def initialize_config():
    """初始化配置文件"""
    print("\n📝 初始化配置文件...")

    # 检查配置文件是否存在
    if not os.path.exists("gemini_config.json"):
        print("创建默认配置文件...")
        from gemini_api_manager import GeminiAPIManager
        manager = GeminiAPIManager()
        print("✅ 配置文件已创建: gemini_config.json")
    else:
        print("✅ 配置文件已存在")

    # 检查是否需要编辑配置
    with open("gemini_config.json", "r", encoding="utf-8") as f:
        import json
        config = json.load(f)

    # 检查是否有默认的 API key
    has_default_keys = any("your_" in key_info["key"] for key_info in config["api_keys"])

    if has_default_keys:
        print("\n⚠️  检测到默认 API key，请编辑 gemini_config.json 添加你的真实 API keys")
        print("📝 编辑命令: code gemini_config.json")
        response = input("是否现在编辑配置文件？(y/n): ").lower()
        if response == 'y':
            try:
                subprocess.run(["code", "gemini_config.json"], check=True)
            except:
                print("请手动编辑 gemini_config.json 文件")

    return True

def setup_permissions():
    """设置文件权限"""
    print("\n🔐 设置文件权限...")

    scripts = [
        "gemini_api_manager.py",
        "gemini_wrapper.py",
        "gemini_monitor.py",
        "setup_gemini_vscode.py",
        "quick_gemini_demo.py"
    ]

    for script in scripts:
        if os.path.exists(script):
            os.chmod(script, 0o755)
            print(f"✅ {script} 权限已设置")

    return True

def test_system():
    """测试系统是否正常工作"""
    print("\n🧪 测试系统...")

    try:
        # 测试 API 管理器
        from gemini_api_manager import GeminiAPIManager
        manager = GeminiAPIManager()
        print("✅ API 管理器加载成功")

        # 测试获取当前 key
        current_key = manager.get_current_api_key()
        if current_key and "your_" not in current_key:
            print("✅ 找到有效的 API key")
            return True
        else:
            print("⚠️  需要配置真实的 API key")
            return False

    except Exception as e:
        print(f"❌ 系统测试失败: {e}")
        return False

def show_usage_info():
    """显示使用信息"""
    print("\n" + "="*60)
    print("🎉 Gemini API 轮换系统启动完成！")
    print("="*60)

    print("\n📚 可用命令:")
    print("  python3 gemini_api_manager.py current     # 获取当前 API key")
    print("  python3 gemini_api_manager.py report      # 查看使用报告")
    print("  python3 gemini_api_manager.py test        # 测试所有 API keys")
    print("  python3 gemini_monitor.py monitor         # 启动监控服务")
    print("  python3 quick_gemini_demo.py              # 运行演示")

    print("\n🔧 管理命令:")
    print("  python3 gemini_api_manager.py enable  --key-name Gemini-1")
    print("  python3 gemini_api_manager.py disable --key-name Gemini-2")

    print("\n💡 使用建议:")
    print("  1. 编辑 gemini_config.json 添加你的 API keys")
    print("  2. 运行 'python3 gemini_api_manager.py test' 测试配置")
    print("  3. 运行 'python3 quick_gemini_demo.py' 验证系统")
    print("  4. 启动监控服务: 'python3 gemini_monitor.py monitor'")

    print("\n📊 配置状态:")
    from gemini_api_manager import GeminiAPIManager
    manager = GeminiAPIManager()
    print(f"  - API key 数量: {len(manager.config['api_keys'])}")
    print(f"  - 每日限额/key: {manager.config['api_keys'][0]['daily_limit'] if manager.config['api_keys'] else 0}")
    print(f"  - 冷却时间: {manager.config['settings']['cooldown_minutes']} 分钟")

    print(f"\n📁 工作目录: {os.getcwd()}")
    print("="*60)

def main():
    """主启动流程"""
    print("🚀 启动 Gemini API 轮换系统\n")

    steps = [
        ("检查 Python 版本", check_python_version),
        ("安装依赖包", install_dependencies),
        ("初始化配置", initialize_config),
        ("设置权限", setup_permissions),
        ("测试系统", test_system)
    ]

    for step_name, step_func in steps:
        print(f"\n📍 {step_name}...")
        if not step_func():
            print(f"❌ {step_name} 失败")
            return False
        print(f"✅ {step_name} 完成")

    # 显示使用信息
    show_usage_info()

    # 询问是否运行演示
    print("\n" + "-"*40)
    response = input("是否现在运行演示测试？(y/n): ").lower()
    if response == 'y':
        print("\n🎬 运行演示...")
        try:
            subprocess.run([sys.executable, "quick_gemini_demo.py"], check=True)
        except KeyboardInterrupt:
            print("\n🛑 演示已中断")
        except subprocess.CalledProcessError:
            print("❌ 演示运行失败")

    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎯 系统启动成功！")
        else:
            print("\n💥 系统启动失败，请检查错误信息")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 启动过程已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 启动过程出错: {e}")
        sys.exit(1)