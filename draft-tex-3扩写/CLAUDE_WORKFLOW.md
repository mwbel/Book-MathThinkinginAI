# Claude Code + GLM-4.6 书稿写作工作流程

## 配置说明

当前已配置使用 Claude Code + GLM-4.6 模型进行书稿写作和润色。

## 核心命令

### 1. 润色命令
- `/refine` - 选择润色模式（推荐新手使用）
- `/examples` - 直接生成例子/类比
- `/diff` - 对照式LaTeX文本润色
- `/expand` - 深度扩展解释

### 2. 辅助命令
- `/help` - 显示命令帮助
- `/clear` - 清除上下文

## 工作流程建议

### 方式A：渐进式润色
1. 使用 `/diff` 进行轻度润色，保持结构
2. 使用 `/examples` 为抽象概念添加例子
3. 使用 `/expand` 对关键概念深入解释

### 方式B：目标导向润色
1. 直接使用 `/refine` 选择合适的模式
2. 根据需要组合使用不同命令

## 版本控制集成

### 修改前
```bash
git status  # 查看当前状态
git diff    # 查看已有修改
```

### 修改后
```bash
git add <filename>
git commit -m "描述修改内容"
```

### 如果需要撤销
```bash
git checkout -- <filename>  # 撤销未提交的修改
```

## 切换配置

### 切换到 Claude + GLM-4.6
```bash
cd .continue
cp config-claude.json config.json
```

### 切换回原配置
```bash
cd .continue
cp config-gemini-backup.json config.json
```

## 最佳实践

1. **分段处理**：将长文档分成小段处理，效果更好
2. **编译验证**：修改后使用 `xelatex` 编译验证
3. **渐进提交**：每完成一个段落就提交一次
4. **备份重要版本**：对重大修改创建分支或标签

## 文件结构

- `AImath.v6.tex` - 主文件
- `chapters/ch5/5-Tools.v1_polished_unified_expanded.tex` - 当前工作文件
- `.continue/config.json` - 当前配置文件
- `.continue/config-gemini-backup.json` - Gemini配置备份
- `.continue/config-claude.json` - Claude配置文件

现在可以开始使用 `/refine` 或其他命令进行书稿润色了！