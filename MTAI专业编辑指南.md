# 🎓 MTAI专业书稿编辑系统指南

## 📋 系统概述

基于你提供的专业级书稿编辑提示词，我们已经创建了一套完整的MTAI（Mathematical Thinking AI）专业编辑系统，专门为《人工智能的数学思维》书稿服务。

## 🚀 核心提示词系统

### 1. MTAI生成例子类比 (`mtai-examples`)

**用途**: 为抽象数学概念生成生活化的例子和类比

**特点**:
- 面向跨专业读者（文科、社会学等）
- 贴近日常生活场景（GPS导航、聚餐、社交媒体等）
- 结构化输出：例子描述 + 对应关系 + 适用位置建议

**使用示例**:
```bash
python3 quick_edit.py mtai-examples --concept "近似算法"
```

**输出结构**:
```
- 例子 1：
  1）例子描述：用于直接写入书稿的那种表述
  2）对应关系说明：原概念中的关键要素对应什么
  3）适用位置建议：引入/中间解释/小结回顾
```

### 2. MTAI对照式润色(diff) (`mtai-refine`)

**用途**: 对LaTeX文本进行轻度润色，生成diff视图

**核心约束**:
- 保持LaTeX结构不变（不删除\chapter、\section等）
- 保留所有标签和引用（\label、\ref等）
- 课堂讲解风格，温和理性
- 段落不超过7行，避免"显然"等压迫性词语
- 照顾数学基础一般的读者

**使用示例**:
```bash
python3 mtai_editor.py gen-examples --concept "NP完全问题"
```

### 3. MTAI扩写diff模式 (`mtai-expand`)

**用途**: 将文本扩写1.5-2倍，保持结构

**特别功能**:
- **智能itemize环境判断**: 自动判断列表项是否需要转换为完整段落
- 最小差异编辑：生成Git diff格式
- 块状LaTeX排版：禁止一行写完环境
- 行内数学公式：`~$...$请参考我之前撰写的提示词:`格式

**使用示例**:
```bash
python3 mtai_editor.py diff-expand --text "要扩写的LaTeX文本"
```

### 4. MTAI结构诊断 (`mtai-diagnose`)

**用途**: 分析章节结构，提供重构建议

**诊断维度**:
1. **核心问题与关键信息**: 概括整体目标
2. **现有结构优点**: 值得保留的部分
3. **结构性问题**: 小节过碎、顺序混乱、过渡缺失等
4. **重构建议**: 新的小节结构和过渡段建议

**使用示例**:
```bash
python3 mtai_editor.py struct-diagnose --file "chapter.tex"
```

### 5. MTAI选区diff编辑 (`mtai-edit`)

**用途**: 对选中LaTeX文本进行精确编辑，生成diff

**核心要求**:
- 最小差异编辑
- 只修改选区内容
- 智能判断itemize环境
- 保持课堂讲解风格
- 只输出diff，不输出额外说明

## 🛠️ 工具使用方式

### 方式1: MTAI专用工具
```bash
# 查看所有MTAI提示词
python3 mtai_editor.py list

# 生成例子
python3 mtai_editor.py gen-examples --concept "概念名"

# 结构诊断
python3 mtai_editor.py struct-diagnose --file "文件路径.tex"

# 扩写文本
python3 mtai_editor.py diff-expand --text "LaTeX文本"
```

### 方式2: 统一编辑工具
```bash
# 使用MTAI功能
python3 quick_edit.py mtai-examples --concept "NP完全问题"
python3 quick_edit.py mtai-refine --text "要润色的LaTeX"
python3 quick_edit.py mtai-expand --text "要扩写的LaTeX"
python3 quick_edit.py mtai-diagnose --file "章节文件.tex"
python3 quick_edit.py mtai-edit --text "选区LaTeX"
```

### 方式3: 快捷命令
```bash
# 生成例子
./gedit e "NP完全问题"  # 使用普通解释
python3 mtai_editor.py gen-examples -c "NP完全问题"  # 使用MTAI专业提示词
```

## 📊 MTAI vs 普通提示词对比

| 功能 | 普通提示词 | MTAI提示词 |
|------|------------|------------|
| **目标读者** | 通用读者 | 跨专业读者（文科、社会学等） |
| **数学基础** | 大学基础 | 大一上过高数水平 |
| **例子风格** | 技术性 | 生活化、贴近日常 |
| **输出结构** | 简单解释 | 结构化（描述+对应+建议） |
| **LaTeX处理** | 基础保持 | 专业级diff和结构保持 |
| **编辑风格** | 学术/课堂 | 课堂讲解+温和理性 |
| **智能判断** | 无 | itemize环境智能转换 |

## 💡 实际应用场景

### 场景1: 为抽象概念生成教学例子
```bash
# 传统方式
python3 quick_edit.py example --concept "近似算法"

# MTAI专业方式
python3 quick_edit.py mtai-examples --concept "近似算法"
```
**MTAI输出**: 包含GPS导航、聚餐选餐厅、社交媒体推荐3个生活化例子，每个都有详细的使用位置建议。

### 场景2: 书稿章节润色
```bash
# 处理一个包含itemize的段落
text = "\\begin{itemize}\\item 第一点\\item 第二点\\end{itemize}"
python3 quick_edit.py mtai-edit --text "$text"
```
**MTAI特性**: 自动判断列表项是否需要转换为流畅段落，提升可读性。

### 场景3: 章节结构优化
```bash
# 诊断整个章节的结构问题
python3 mtai_editor.py struct-diagnose --file "ch4/math-thinking.tex"
```
**MTAI输出**: 四维度结构分析 + 具体重构建议。

### 场景4: 扩写充实内容
```bash
# 将技术描述扩写为1.5-2倍
python3 quick_edit.py mtai-expand --text "复杂的技术描述"
```
**MTAI特性**: 保持LaTeX格式，添加生活化例子，确保教学效果。

## 🎯 专业特色功能

### 1. 智能itemize环境处理
MTAI系统会自动判断：
- **保留列表**: 独立要点、罗列事实、步骤说明
- **转为段落**: 逻辑连贯、可组织流畅叙述的内容

**判断标准**: 哪种方式更有助于跨专业读者理解和学习。

### 2. 严格的LaTeX结构保护
- 不删除`\chapter`、`\section`等结构命令
- 不修改`\label`、`\ref`、`\cite`等标签引用
- 保持环境内部的块状排版
- 行内数学公式使用`~$...请参考我之前撰写的提示词:`格式

### 3. 跨专业读者适配
- 数学基础假设：大一上过高数
- 包含社会学、教育学、文科等背景读者
- 避免使用"显然"、"不难发现"等压迫性词语
- 每段不超过7行，增强可读性

### 4. Diff格式编辑
所有修改都生成Git diff格式：
- `- 开头`: 删除的原内容
- `+ 开头`: 新增或修改的内容
- 便于在VSCode中审查和应用修改

## 📈 性能优化

### MTAI提示词优化
- 基于你的专业书稿编辑经验
- 符合《人工智能的数学思维》编辑手册
- 针对跨专业读者的认知特点
- 结构化输出便于直接使用

### API配置优化
- 9个API密钥，总日限额36,000次
- RPM 50，接近官方限制60
- 智能轮换和错误重试
- 支持长时间编辑任务

## 🚨 使用注意事项

### LaTeX文件处理
1. **备份原文件**: MTAI编辑前建议备份
2. **检查diff结果**: 仔细审查生成的修改
3. **逐步应用**: 分段应用diff修改
4. **验证编译**: 确保LaTeX编译无误

### 提示词选择
1. **概念解释**: 优先使用`mtai-examples`
2. **文本润色**: 使用`mtai-refine`生成diff
3. **内容扩充**: 使用`mtai-expand`智能扩写
4. **结构问题**: 使用`mtai-diagnose`诊断
5. **精确编辑**: 使用`mtai-edit`处理选区

### 读者适配
1. **数学术语**: 适当解释但保持准确性
2. **例子选择**: 贴近日常生活和技术场景
3. **语言风格**: 课堂讲解体，温和理性
4. **内容密度**: 平衡专业性和可读性

## 📋 快速命令参考

```bash
# MTAI核心功能
python3 mtai_editor.py list                           # 列出所有提示词
python3 mtai_editor.py gen-examples -c "概念名"        # 生成专业例子
python3 mtai_editor.py struct-diagnose -f "文件.tex"   # 结构诊断

# 统一编辑器中的MTAI功能
python3 quick_edit.py mtai-examples -c "近似算法"      # MTAI例子生成
python3 quick_edit.py mtai-refine -t "LaTeX文本"      # MTAI润色diff
python3 quick_edit.py mtai-expand -t "LaTeX文本"      # MTAI扩写diff
python3 quick_edit.py mtai-diagnose -f "章节.tex"     # MTAI结构诊断
python3 quick_edit.py mtai-edit -t "选区LaTeX"         # MTAI选区编辑

# 配套工具
python3 gemini_api_manager.py report                  # 查看API使用状态
python3 gemini_monitor.py monitor                     # 启动监控服务
```

---

🎓 **MTAI专业书稿编辑系统现已完全集成，为你的《人工智能的数学思维》提供专业级AI编辑支持！**