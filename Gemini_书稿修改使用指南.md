# 📚 Gemini 2.5-Flash 书稿修改系统使用指南

## 🎉 测试结果更新

**好消息！** 经过再次测试，你的 Gemini API 系统完全正常：

- ✅ **9/9 个 API keys** 全部成功连接
- ✅ **50个可用模型**，包括完整的 Gemini 2.5-Flash 系列
- ✅ **轮换系统** 工作正常
- ✅ **速率限制** 已正确配置 (10 RPM, 250K tokens/天)

## 🚀 书稿修改工具概览

我为你创建了完整的书稿修改工具集：

### 1. 交互式编辑器 - `book_editor.py`
功能最丰富的图形化编辑工具

### 2. 命令行编辑器 - `edit_book.py`
快速的单文件修改工具

### 3. 批量处理工具 - `batch_edit.py`
批量处理多个文件

## 📋 使用方法详解

### 方法1：交互式编辑器（推荐新手）

```bash
# 启动交互式编辑器
python3 book_editor.py
```

**功能菜单：**
1. **润色文本** - 提升语言质量和流畅度
2. **简化语言** - 使内容更通俗易懂
3. **增强学术性** - 提升正式性和严谨性
4. **添加例子** - 丰富内容和说明
5. **提取要点** - 生成关键点摘要
6. **翻译内容** - 翻译成其他语言
7. **自定义指令** - 使用自己的修改要求

### 方法2：命令行快速编辑

```bash
# 基本语法
python3 edit_book.py <文件路径> <修改类型> [参数]

# 润色文本
python3 edit_book.py chapter1.md polish

# 简化语言
python3 edit_book.py chapter1.md simplify

# 增强学术性
python3 edit_book.py chapter1.md formal

# 添加例子（带主题）
python3 edit_book.py chapter1.md examples "机器学习"

# 提取要点
python3 edit_book.py chapter1.md summary

# 翻译成英文
python3 edit_book.py chapter1.md translate "English"

# 自定义修改
python3 edit_book.py chapter1.md custom "请将这段文字改得更生动有趣"
```

### 方法3：批量处理

```bash
# 批量润色所有章节
python3 batch_edit.py "chapter*" polish

# 批量简化所有 markdown 文件
python3 batch_edit.py "*.md" simplify

# 批量添加例子
python3 batch_edit.py "section*" examples "深度学习"

# 批量翻译成中文
python3 batch_edit.py "*" translate "中文"

# 批量增强学术性
python3 batch_edit.py "introduction*" formal
```

## 💡 实际使用示例

### 示例1：润色学术论文
```bash
# 润色单个文件
python3 edit_book.py research_paper.md formal

# 批量润色整个章节
python3 batch_edit.py "chapter4*" formal
```

### 示例2：简化技术文档
```bash
# 简化复杂的技术描述
python3 edit_book.py technical_guide.md simplify

# 批量简化所有文档
python3 batch_edit.py "*.md" simplify
```

### 示例3：添加教学例子
```bash
# 为机器学习章节添加例子
python3 edit_book.py ml_basics.md examples "机器学习算法"

# 为数学章节添加例子
python3 edit_book.py calculus.md examples "微积分应用"
```

### 示例4：生成摘要
```bash
# 生成章节摘要
python3 edit_book.py long_chapter.md summary

# 批量生成所有章节摘要
python3 batch_edit.py "chapter*" summary
```

## ⚡ 高级功能

### 1. 智能分块处理
系统自动检测文件大小，大文本会智能分块处理，确保质量。

### 2. 自动备份
每次修改前都会自动创建备份文件：
```
原文件: chapter1.md
备份: chapter1.md.backup_1701234567
```

### 3. 速率限制管理
系统自动遵守 Gemini API 的限制：
- 每分钟最多 10 次请求
- 每天最多 250,000 tokens
- 自动轮换 9 个 API keys

### 4. 使用统计
```bash
# 查看使用情况
python3 gemini_api_manager.py report

# 查看当前可用 key
python3 gemini_api_manager.py current
```

## 🎯 最佳实践

### 1. 使用建议
- **小文件**：直接使用命令行工具
- **大文件**：使用交互式工具，可以预览结果
- **批量操作**：先用小文件测试，确认效果后再批量处理

### 2. 备份策略
- 系统会自动备份，但建议重要文件手动备份
- 备份文件命名格式：`原文件名.backup_时间戳`

### 3. 质量控制
- 修改后务必检查结果
- 重要内容建议人工校对
- 可以多次迭代修改

### 4. Token 管理
- 大文件会消耗较多 tokens
- 建议监控使用情况
- 可以用 `summary` 功能生成概要

### 5. 额度重置时间
**重要说明：免费额度会在太平洋时间（PT）午夜重置（也就是北京时间下午3点）**
- 每日250,000 tokens额度会在北京时间下午3点自动重置
- 建议在额度快用完时安排批量操作
- 可以使用 `python3 gemini_manager.py report` 查看剩余额度

## 🔧 故障排除

### 常见问题

**Q: 修改后文件内容不变？**
A: 可能是 API 限制或网络问题，检查使用报告

**Q: 修改质量不理想？**
A: 尝试更具体的自定义指令

**Q: 批量处理中断了？**
A: 已处理的文件已保存，可以继续处理剩余文件

**Q: 如何恢复备份？**
A: 复制备份文件内容到原文件

### 获取帮助
```bash
# 查看详细使用说明
cat Gemini_书稿修改使用指南.md

# 检查系统状态
python3 gemini_api_manager.py report

# 测试 API 连接
python3 simple_test.py
```

## 📊 系统状态监控

```bash
# 实时监控使用情况
python3 gemini_monitor.py monitor

# 查看每日报告
python3 gemini_monitor.py report
```

---

## 🎊 开始使用！

你的 **Gemini 2.5-Flash 书稿修改系统** 已经完全就绪：

- ✅ **9个API keys** 全部正常
- ✅ **完整的编辑工具集**
- ✅ **智能速率控制**
- ✅ **自动备份系统**

现在你可以开始高效地修改你的书稿了！🚀

建议先用一个小文件测试，熟悉使用流程后再处理重要内容。