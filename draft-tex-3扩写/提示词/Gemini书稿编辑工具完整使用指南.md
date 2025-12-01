# 🛠️ Gemini书稿编辑工具完整使用指南

## 📋 工具概览

### 核心工具分类

| 工具类型 | 主要文件 | 功能描述 | 适用场景 |
|----------|----------|----------|----------|
| **基础编辑工具** | `quick_edit.py` | 通用书稿编辑 | 日常润色、概念解释、翻译 |
| **MTAI专业工具** | `mtai_editor.py` | 专业级书稿编辑 | 跨专业读者适配、结构优化 |
| **超级快捷命令** | `gedit` | 命令行快捷操作 | 快速处理单行文本 |
| **提示词管理** | `prompt_manager.py` | 提示词管理 | 自定义提示词模板 |
| **API管理** | `gemini_api_manager.py` | API状态监控 | 配额管理、密钥轮换 |

---

## 🚀 一、基础编辑工具 (`quick_edit.py`)

### 基本使用方法
```bash
cd "/Users/Min369/Desktop/书/书稿打磨"
python3 quick_edit.py <命令> [选项]
```

### 主要命令

#### 1. 文本润色类
```bash
# 学术风格润色
python3 quick_edit.py polish --style academic --text "要润色的文本"

# 课堂讲解风格润色
python3 quick_edit.py polish --style lecture --text "要润色的文本"

# 精炼文本
python3 quick_edit.py polish --style concise --text "要精炼的文本"

# 详细扩写
python3 quick_edit.py polish --style expand --text "要扩写的文本"
```

#### 2. 数学内容处理
```bash
# 解释数学概念
python3 quick_edit.py explain --concept "旅行商问题"

# 生成例子
python3 quick_edit.py example --concept "动态规划"

# 改进公式解释
python3 quick_edit.py formula --formula "T(n) = O(n!)" --context "时间复杂度分析"

# 检查数学严谨性
python3 quick_edit.py check --text "要检查的数学文本"
```

#### 3. 翻译和语言处理
```bash
# 英译中
python3 quick_edit.py translate --text "英文文本"

# 交互式对话
python3 quick_edit.py interactive
```

#### 4. 文件处理
```bash
# 处理整个文件
python3 quick_edit.py polish --style academic --file "chapters/ch4/file.tex"

# 保存结果到新文件
python3 quick_edit.py polish --style academic --text "文本" --output "result.tex"
```

---

## 🎓 二、MTAI专业工具 (`mtai_editor.py`)

### 专业级书稿编辑，符合《人工智能的数学思维》编辑标准

#### 主要命令
```bash
cd "/Users/Min369/Desktop/书/书稿打磨"
python3 mtai_editor.py <命令> [选项]
```

#### 1. MTAI专业功能
```bash
# 查看所有MTAI提示词
python3 mtai_editor.py list

# 生成专业例子（面向跨专业读者）
python3 mtai_editor.py gen-examples --concept "近似算法"

# 对照式润色（生成diff视图）
python3 mtai_editor.py refine-diff --text "LaTeX文本"

# 智能扩写（1.5-2倍，判断itemize环境）
python3 mtai_editor.py diff-expand --text "LaTeX文本"

# 章节结构诊断
python3 mtai_editor.py struct-diagnose --file "章节文件.tex"

# 选区精确编辑（diff模式）
python3 mtai_editor.py diff-selection --text "选区LaTeX"
```

#### 2. MTAI特色功能

**智能itemize环境判断**：
- 自动判断列表项是否需要转换为流畅段落
- 标准：提升跨专业读者的可读性和学习效果

**严格LaTeX保护**：
- 不删除`\chapter`、`\section`等结构命令
- 保持所有`\label`、`\ref`引用
- 块状环境排版，禁止一行写完

**跨专业读者适配**：
- 数学基础：大一上过高数水平
- 避免压迫性词汇（"显然"、"不难发现"）
- 每段不超过7行，课堂讲解风格

---

## ⚡ 三、超级快捷命令 (`gedit`)

### 最快的文本处理方式

#### 基本用法
```bash
cd "/Users/Min369/Desktop/书/书稿打磨"
./gedit <命令> "文本"
```

#### 快捷命令对照表

| 快捷命令 | 完整命令 | 功能 | 示例 |
|----------|----------|------|------|
| `./gedit p "文本"` | `python3 quick_edit.py polish --style academic` | 学术润色 | `./gedit p "旅行商问题"` |
| `./gedit l "文本"` | `python3 quick_edit.py polish --style lecture` | 课堂润色 | `./gedit l "复杂概念"` |
| `./gedit c "文本"` | `python3 quick_edit.py polish --style concise` | 精炼文本 | `./gedit c "冗长描述"` |
| `./gedit e "概念"` | `python3 quick_edit.py explain --concept` | 解释概念 | `./gedit e "NP完全"` |
| `./gedit x "概念"` | `python3 quick_edit.py example --concept` | 生成例子 | `./gedit x "动态规划"` |
| `./gedit t "文本"` | `python3 quick_edit.py translate --text` | 翻译中文 | `./gedit t "英文文本"` |
| `./gedit k "文本"` | `python3 quick_edit.py check --text` | 检查严谨性 | `./gedit k "数学定义"` |
| `./gedit i` | `python3 quick_edit.py interactive` | 交互模式 | `./gedit i` |
| `./gedit h` | 帮助信息 | 显示帮助 | `./gedit h` |

#### 实际使用示例
```bash
# 快速学术润色
./gedit p "旅行商问题是classical的NP完全问题"

# 快速概念解释
./gedit e "近似算法理论"

# 快速生成例子
./gedit x "贪心算法"

# 进入交互模式
./gedit i
```

---

## ⌨️ 四、VS Code快捷键配置

### 已配置的快捷键

#### 文本编辑快捷键（选中文本后使用）

| 快捷键 | 功能 | 对应命令 |
|--------|------|----------|
| **Ctrl+Alt+P** | 学术风格润色 | `quick_edit.py polish --style academic` |
| **Ctrl+Alt+L** | 课堂风格润色 | `quick_edit.py polish --style lecture` |
| **Ctrl+Alt+C** | 精炼文本 | `quick_edit.py polish --style concise` |
| **Ctrl+Alt+E** | 解释概念 | `quick_edit.py explain --concept` |
| **Ctrl+Alt+X** | 生成例子 | `quick_edit.py example --concept` |
| **Ctrl+Alt+T** | 翻译中文 | `quick_edit.py translate --text` |

#### VS Code任务面板（Ctrl+Shift+P → Tasks）

| 任务名称 | 功能 | 使用场景 |
|----------|------|----------|
| 润色文本 (学术风格) | 学术润色 | 严格学术写作 |
| 润色文本 (课堂风格) | 课堂润色 | 教学化表达 |
| 精炼文本 | 内容精炼 | 删除冗余表达 |
| 解释概念 | 概念解释 | 详细定义和例子 |
| 生成例子 | 例证生成 | 具体应用场景 |
| 翻译中文 | 英译中 | 中文化表达 |
| 检查严谨性 | 数学检查 | 逻辑验证 |

#### 快捷键使用方法

1. **选中文本**：在VS Code中选中要处理的文本
2. **按下快捷键**：使用对应的组合键
3. **查看结果**：在终端窗口查看处理结果

```bash
# 使用示例：
1. 在VS Code中选中："旅行商问题是classical的NP完全问题"
2. 按下 Ctrl+Alt+P
3. 在终端查看学术润色结果
```

### 快捷键配置文件位置

- **用户快捷键**: `~/.vscode/keybindings.json`
- **工作区任务**: `./.vscode/tasks.json`

---

## 📖 五、实际操作示例

### 场景1：快速润色一段文本

#### 方法1：VS Code快捷键
1. 在VS Code中打开书稿文件
2. 选中要润色的文本
3. 按 **Ctrl+Alt+P**（学术润色）或 **Ctrl+Alt+L**（课堂润色）
4. 在终端查看结果

#### 方法2：命令行
```bash
# 使用基础工具
python3 quick_edit.py polish --style academic --text "旅行商问题是一个classical的NP完全问题"

# 使用快捷命令
./gedit p "旅行商问题是一个classical的NP完全问题"
```

#### 方法3：MTAI专业润色
```bash
# 使用MTAI专业工具
python3 mtai_editor.py refine-diff --text "旅行商问题是classical的NP完全问题"
```

### 场景2：为抽象概念生成例子

#### 方法1：普通例子生成
```bash
python3 quick_edit.py example --concept "近似算法"
```

#### 方法2：MTAI专业例子（推荐用于书稿）
```bash
python3 mtai_editor.py gen-examples --concept "近似算法"
```
**输出特点**：
- 3个生活化例子（GPS导航、聚餐、社交媒体）
- 对应关系说明
- 适用位置建议（引入/解释/小结）

### 场景3：处理LaTeX文件

#### 润色整个章节
```bash
# 学术风格润色并保存到新文件
python3 quick_edit.py polish --style academic \
  --file "chapters/ch4/4-Thinking.tex" \
  --output "chapters/ch4/4-Thinking_polished.tex"
```

#### MTAI结构诊断
```bash
# 诊断章节结构问题
python3 mtai_editor.py struct-diagnose --file "chapters/ch4/4-Thinking.tex"
```

#### MTAI智能扩写
```bash
# 扩写选中的LaTeX段落（自动判断itemize环境）
python3 quick_edit.py mtai-expand --text "要扩写的LaTeX段落"
```

### 场景4：交互式编辑

```bash
# 进入交互模式
python3 quick_edit.py interactive

# 或使用快捷命令
./gedit i
```

**交互模式特点**：
- 多轮对话
- 保持上下文
- 适合复杂编辑任务

### 场景5：批量处理

#### 检查数学严谨性
```bash
# 检查文件中的数学表述
python3 quick_edit.py check --file "chapters/ch4/math-section.tex"
```

#### 生成章节习题
```bash
# 为主题生成习题
python3 quick_edit.py exercise --concept "动态规划"
```

---

## 🔧 六、提示词管理

### 查看和管理提示词

```bash
# 查看所有可用提示词
python3 quick_edit.py prompts --list-prompts

# 查看特定类别提示词
python3 prompt_manager.py list --category polish

# 搜索提示词
python3 prompt_manager.py search --keyword "例子"
```

### 添加自定义提示词

```bash
# 添加书稿专用提示词
python3 prompt_manager.py add \
  --name "我的书稿润色" \
  --template "请以《数学思维与AI》风格润色以下文本：{text}" \
  --description "专用于书稿的润色提示词"

# 使用自定义提示词
python3 quick_edit.py custom --prompt-name "我的书稿润色" --text "要处理的文本"
```

---

## 📊 七、API状态监控

### 查看API使用情况
```bash
# 查看详细使用报告
python3 gemini_api_manager.py report

# 测试所有API密钥
python3 gemini_api_manager.py test

# 查看当前可用密钥
python3 gemini_api_manager.py current
```

### 启动监控服务
```bash
# 启动长期监控
python3 gemini_monitor.py monitor

# 一次性状态检查
python3 gemini_monitor.py check

# 生成每日报告
python3 gemini_monitor.py report
```

---

## 🚨 八、故障排除指南

### 常见问题及解决方案

#### 1. API密钥问题
**问题**: 提示"没有可用的API密钥"
```bash
# 解决方案：检查配置
python3 gemini_api_manager.py test

# 解决方案：查看配额
python3 gemini_api_manager.py report
```

#### 2. LaTeX编译错误
**问题**: 编辑后的LaTeX无法编译
```bash
# 解决方案：使用MTAI工具（更严格的结构保护）
python3 quick_edit.py mtai-refine --text "有问题的LaTeX"

# 解决方案：检查diff修改，只应用安全的部分
```

#### 3. 快捷键不工作
**问题**: VS Code快捷键无响应
```bash
# 检查配置文件
cat ~/.vscode/keybindings.json
cat ./.vscode/tasks.json

# 重新配置快捷键
python3 setup_vs_code_shortcuts.py
```

#### 4. 输出质量不佳
**问题**: AI输出不符合书稿要求
```bash
# 解决方案：使用MTAI专业工具
python3 mtai_editor.py gen-examples --concept "概念名"

# 解决方案：尝试不同风格
python3 quick_edit.py polish --style lecture --text "文本"

# 解决方案：添加自定义提示词
python3 prompt_manager.py add --name "专用风格" --template "你的模板"
```

#### 5. 内存或性能问题
**问题**: 处理大文件时出错
```bash
# 解决方案：分块处理
python3 quick_edit.py polish --file "file_part1.tex" --output "part1_done.tex"
python3 quick_edit.py polish --file "file_part2.tex" --output "part2_done.tex"

# 解决方案：检查API使用量
python3 gemini_api_manager.py report
```

### 调试技巧

#### 1. 启用详细日志
```python
# 在Python脚本中添加
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2. 测试单个功能
```bash
# 测试API连接
python3 gemini_api_manager.py test

# 测试简单文本处理
./gedit p "测试文本"

# 测试MTAI功能
python3 mtai_editor.py gen-examples -c "算法"
```

#### 3. 分步验证
1. 先用短文本测试功能
2. 确认输出质量满意
3. 再处理长文本或整个文件

### 配置文件检查

#### 重要文件位置
```
/Users/Min369/Desktop/书/书稿打磨/
├── gemini_config.json          # API配置
├── prompts.json               # 基础提示词
├── mtai_prompts.json          # MTAI专业提示词
├── quick_edit.py              # 主要编辑工具
├── mtai_editor.py             # MTAI专业工具
├── gedit                      # 超级快捷命令
├── gemini_usage.json          # 使用统计
└── .vscode/
    ├── tasks.json             # VS Code任务
    └── keybindings.json       # 用户快捷键
```

#### 检查配置完整性
```bash
# 检查主要配置文件
ls -la *.json *.py

# 验证配置文件格式
python3 -c "import json; print('gemini_config:', json.load(open('gemini_config.json'))['model_info'])"
python3 -c "import json; print('prompts:', len(json.load(open('prompts.json'))['categories']))"
```

---

## 📋 九、最佳实践建议

### 1. 日常使用流程
1. **写作阶段**: 使用交互模式 (`./gedit i`)
2. **润色阶段**: 使用VS Code快捷键或 `./gedit p`
3. **概念解释**: 使用MTAI专业工具 (`mtai_editor.py gen-examples`)
4. **结构优化**: 使用MTAI结构诊断 (`mtai_editor.py struct-diagnose`)
5. **最终检查**: 使用严谨性检查 (`./gedit k`)

### 2. 团队协作
- 统一使用MTAI专业提示词保证风格一致性
- 使用diff格式便于协作和版本控制
- 定期检查API使用量避免配额耗尽

### 3. 质量控制
- 重要内容人工审核AI输出
- 分步应用修改，逐步验证
- 定期备份原始文件

### 4. 性能优化
- 合理设置日限额避免API限制
- 使用监控服务及时发现问题
- 批量操作时注意控制频率

---

## 🎯 十、快速开始指南

### 新用户5分钟上手

1. **测试基本功能**：
   ```bash
   cd "/Users/Min369/Desktop/书/书稿打磨"
   ./gedit p "测试文本"
   ```

2. **体验VS Code快捷键**：
   - 在VS Code中选中文本
   - 按 `Ctrl+Alt+P`
   - 查看终端结果

3. **尝试MTAI专业功能**：
   ```bash
   python3 mtai_editor.py gen-examples --concept "算法复杂度"
   ```

4. **检查系统状态**：
   ```bash
   python3 gemini_api_manager.py report
   ```

### 核心快捷键速查表

| 操作 | 快捷键 | 命令 |
|------|--------|------|
| **学术润色** | `Ctrl+Alt+P` | `./gedit p "文本"` |
| **课堂润色** | `Ctrl+Alt+L` | `./gedit l "文本"` |
| **精炼文本** | `Ctrl+Alt+C` | `./gedit c "文本"` |
| **解释概念** | `Ctrl+Alt+E` | `./gedit e "概念"` |
| **生成例子** | `Ctrl+Alt+X` | `./gedit x "概念"` |
| **翻译中文** | `Ctrl+Alt+T` | `./gedit t "文本"` |
| **检查严谨性** | `Ctrl+Alt+K` | `./gedit k "文本"` |
| **交互模式** | - | `./gedit i` |
| **查看帮助** | - | `./gedit h` |

### MTAI专业功能速查表

| 功能 | 命令 | 适用场景 |
|------|------|----------|
| **生成专业例子** | `python3 mtai_editor.py gen-examples -c "概念"` | 跨专业读者教学 |
| **对照式润色** | `python3 mtai_editor.py refine-diff -t "文本"` | LaTeX文本润色 |
| **智能扩写** | `python3 mtai_editor.py diff-expand -t "文本"` | 内容扩充 |
| **结构诊断** | `python3 mtai_editor.py struct-diagnose -f "文件"` | 章节结构优化 |
| **精确编辑** | `python3 mtai_editor.py diff-selection -t "文本"` | 选区编辑 |

---

## 📞 技术支持

如果遇到问题，请按以下顺序排查：

1. **查看故障排除指南**（第八章）
2. **检查API状态**：`python3 gemini_api_manager.py test`
3. **验证配置文件**：确保所有JSON文件格式正确
4. **尝试简单功能**：用短文本测试基本功能
5. **查看日志**：启用详细日志模式

**记住**：
- 日常快速编辑：使用 **VS Code快捷键** 或 **./gedit** 命令
- 专业书稿编辑：使用 **MTAI工具** (`mtai_editor.py`)
- 复杂任务：使用 **交互模式** (`./gedit i`)
- 监控状态：使用 **API管理工具** (`gemini_api_manager.py`)

现在你已经完全掌握了这套强大的Gemini书稿编辑工具系统！🎉

---

*最后更新: 2025年11月26日*