# Continue斜杠命令测试

## 可用的斜杠命令：

1. `/..` - 跳出预设提示词，进入自由模式
2. `/free` - 进入自由对话模式
3. `/help` - 显示可用命令帮助
4. `/clear` - 清除上下文
5. `/refine` - 润色中文学术文本

## 测试方法：

在Continue中输入以下命令测试：

```
/help
```

应该显示命令列表。

```
/..
```

应该进入自由模式。

## 配置文件位置：

- 主配置：`/.continue/.config.json`
- 斜杠命令：`/.continue/slash-commands.yaml`