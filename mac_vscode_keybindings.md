# Mac VS Code 快捷键配置方案

## 当前配置问题
Mac上的快捷键可能不生效，需要尝试不同的键位组合。

## 解决方案

### 方案1：标准Mac键位（推荐）
```json
{
  "key": "cmd+alt+p",
  "command": "workbench.action.terminal.runSelectedText",
  "args": {
    "command": "cd '/Users/Min369/Desktop/书/书稿打磨' && python3 quick_edit.py polish --style academic --text"
  },
  "when": "editorTextFocus"
}
```

### 方案2：使用Command键替代
```json
{
  "key": "cmd+shift+p",
  "command": "workbench.action.terminal.runSelectedText",
  "args": {
    "command": "cd '/Users/Min369/Desktop/书/书稿打磨' && python3 quick_edit.py polish --style academic --text"
  },
  "when": "editorTextFocus"
}
```

## Mac键盘对应关系
- Windows `Ctrl` → Mac `Control` (⌃)
- Windows `Alt` → Mac `Option` (⌥)
- Windows `Win` → Mac `Command` (⌘)

## 建议的Mac快捷键组合

| 功能 | Windows组合 | Mac组合 | 备注 |
|------|-------------|---------|------|
| 学术润色 | Ctrl+Alt+P | **Cmd+Alt+P** 或 **⌘+⌥+P** | 推荐 |
| 课堂润色 | Ctrl+Alt+L | **Cmd+Alt+L** 或 **⌘+⌥+L** | 推荐 |
| 精炼文本 | Ctrl+Alt+C | **Cmd+Alt+C** 或 **⌘+⌥+C** | 推荐 |
| 解释概念 | Ctrl+Alt+E | **Cmd+Alt+E** 或 **⌘+⌥+E** | 推荐 |
| 生成例子 | Ctrl+Alt+X | **Cmd+Alt+X** 或 **⌘+⌥+X** | 推荐 |
| 翻译中文 | Ctrl+Alt+T | **Cmd+Alt+T** 或 **⌘+⌥+T** | 推荐 |

## 故障排除

1. **重启VS Code**: 配置后需要重启
2. **检查冲突**: 查看VS Code快捷键设置是否有冲突
3. **手动设置**: 在VS Code中手动设置快捷键
4. **使用任务面板**: Ctrl+Shift+P → "Tasks: Run Task"