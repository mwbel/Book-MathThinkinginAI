# 测试 /refine 命令

配置文件已更新，现在应该包含以下斜杠命令：

1. `/refine` - 选择润色模式：examples（生成例子）、diff（对照润色）或 expand（深度扩展）
2. `/examples` - 生成例子/类比来解释抽象概念
3. `/diff` - 对照式润色LaTeX文本
4. `/snippet` - 查看VS Code代码片段使用指南
5. `/help` - 显示可用的斜杠命令帮助
6. `/clear` - 清除上下文，开始新对话

配置文件位置：`~/.continue/config.json`

重新启动会话后，`/refine` 命令应该能正常工作。