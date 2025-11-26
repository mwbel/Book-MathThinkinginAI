#!/usr/bin/env python3
"""
设置 VS Code 快捷键和任务配置
"""

import json
import os
from pathlib import Path

def setup_vscode_shortcuts():
    """设置 VS Code 快捷键配置"""

    vscode_dir = Path.home() / ".vscode"
    if not vscode_dir.exists():
        vscode_dir.mkdir()

    shortcuts = {
        "version": "0.2.0",
        "keybindings": [
            {
                "key": "ctrl+alt+p",
                "command": "workbench.action.terminal.runSelectedText",
                "args": {
                    "command": "cd '/Users/Min369/Desktop/书/书稿打磨' && python3 quick_edit.py polish --style academic --text"
                },
                "when": "editorTextFocus"
            },
            {
                "key": "ctrl+alt+l",
                "command": "workbench.action.terminal.runSelectedText",
                "args": {
                    "command": "cd '/Users/Min369/Desktop/书/书稿打磨' && python3 quick_edit.py polish --style lecture --text"
                },
                "when": "editorTextFocus"
            },
            {
                "key": "ctrl+alt+c",
                "command": "workbench.action.terminal.runSelectedText",
                "args": {
                    "command": "cd '/Users/Min369/Desktop/书/书稿打磨' && python3 quick_edit.py polish --style concise --text"
                },
                "when": "editorTextFocus"
            },
            {
                "key": "ctrl+alt+e",
                "command": "workbench.action.terminal.runSelectedText",
                "args": {
                    "command": "cd '/Users/Min369/Desktop/书/书稿打磨' && python3 quick_edit.py explain --concept"
                },
                "when": "editorTextFocus"
            },
            {
                "key": "ctrl+alt+x",
                "command": "workbench.action.terminal.runSelectedText",
                "args": {
                    "command": "cd '/Users/Min369/Desktop/书/书稿打磨' && python3 quick_edit.py example --concept"
                },
                "when": "editorTextFocus"
            },
            {
                "key": "ctrl+alt+t",
                "command": "workbench.action.terminal.runSelectedText",
                "args": {
                    "command": "cd '/Users/Min369/Desktop/书/书稿打磨' && python3 quick_edit.py translate --text"
                },
                "when": "editorTextFocus"
            }
        ]
    }

    tasks = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "润色文本 (学术风格)",
                "type": "shell",
                "command": "python3",
                "args": ["quick_edit.py", "polish", "--style", "academic", "--text", "${selectedText}"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "new"
                }
            },
            {
                "label": "润色文本 (课堂风格)",
                "type": "shell",
                "command": "python3",
                "args": ["quick_edit.py", "polish", "--style", "lecture", "--text", "${selectedText}"],
                "group": "build"
            },
            {
                "label": "精炼文本",
                "type": "shell",
                "command": "python3",
                "args": ["quick_edit.py", "polish", "--style", "concise", "--text", "${selectedText}"],
                "group": "build"
            },
            {
                "label": "解释概念",
                "type": "shell",
                "command": "python3",
                "args": ["quick_edit.py", "explain", "--concept", "${selectedText}"],
                "group": "build"
            },
            {
                "label": "生成例子",
                "type": "shell",
                "command": "python3",
                "args": ["quick_edit.py", "example", "--concept", "${selectedText}"],
                "group": "build"
            },
            {
                "label": "翻译中文",
                "type": "shell",
                "command": "python3",
                "args": ["quick_edit.py", "translate", "--text", "${selectedText}"],
                "group": "build"
            },
            {
                "label": "检查严谨性",
                "type": "shell",
                "command": "python3",
                "args": ["quick_edit.py", "check", "--text", "${selectedText}"],
                "group": "build"
            }
        ]
    }

    # 写入配置文件
    shortcuts_path = vscode_dir / "keybindings.json"
    with open(shortcuts_path, 'w', encoding='utf-8') as f:
        json.dump(shortcuts, f, indent=2, ensure_ascii=False)

    print(f"✅ VS Code 快捷键配置已生成: {shortcuts_path}")

    # 在工作目录创建 tasks
    workspace_vscode = Path("/Users/Min369/Desktop/书/书稿打磨/.vscode")
    if not workspace_vscode.exists():
        workspace_vscode.mkdir()

    tasks_path = workspace_vscode / "tasks.json"
    with open(tasks_path, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

    print(f"✅ VS Code 任务配置已生成: {tasks_path}")

def show_shortcuts():
    """显示快捷键说明"""
    print("🎹 VS Code 快捷键配置")
    print("="*50)
    print("选中文本后使用以下快捷键:")
    print()
    print("📝 文本润色:")
    print("  Ctrl+Alt+P  - 学术风格润色")
    print("  Ctrl+Alt+L  - 课堂风格润色")
    print("  Ctrl+Alt+C  - 精炼文本")
    print()
    print("🔧 概念处理:")
    print("  Ctrl+Alt+E  - 解释概念")
    print("  Ctrl+Alt+X  - 生成例子")
    print("  Ctrl+Alt+T  - 翻译中文")
    print()
    print("💡 使用方法:")
    print("  1. 选中要处理的文本")
    print("  2. 按相应快捷键")
    print("  3. 在终端查看结果")
    print()
    print("📋 任务面板 (Ctrl+Shift+P → Tasks):")
    print("  - 润色文本 (学术风格)")
    print("  - 润色文本 (课堂风格)")
    print("  - 精炼文本")
    print("  - 解释概念")
    print("  - 生成例子")
    print("  - 翻译中文")
    print("  - 检查严谨性")

if __name__ == "__main__":
    setup_vscode_shortcuts()
    show_shortcuts()