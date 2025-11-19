太好了！我把你刚给的“写作风格与语气提示词”完整融入，做成**落地可执行**的打磨工作流 + 可直接粘贴到 ChatGPT/Trae 的模板，并按你要求固定“**对照式修改**”输出格式（原文 + `% ChatGPT建议:` + 修改版）。时间表也为你排到**11月15日**。

# 工作流（到 11/15 的执行版）

**每日循环（两段微修 + 一章统修）**

1. **微修·上午**（20–40 段，≤4页）
   - 在 VS Code/TeXShop 中选中片段 → 用【模板A】跑“对照式修改”。
   - 只合并你认可的段落到 `chXX_*.v(N+1).tex`。
   - 立即 `xelatex` 编译，修掉 Overfull/未定义命令。
2. **微修·下午**（同上）
3. **统修·晚上**（跨段衔接与风格统一）
   - 用【模板B】对整章做“风格一致化 + 思维引导化 + 逻辑连贯”。
   - 检查“导览 + 你将收获 + 各节末学习回扣”是否齐全、口径一致。

**时间安排**

- 11/04–11/09：优先处理“读者路径关键章”（绪论/AI史、机器学习、深度学习入门）。
- 11/10–11/12：联动章节的一致化（术语、引语、图表体例）。
- 11/13–11/14：整书通读一次（逻辑跳跃、口径、学习目标回扣）。
- 11/15：导出提交版（清理 `% ChatGPT建议` 注释，统一参考文献、目录、图表编号）。

------

| 模板              | 用途                     | 使用频率        | 输出形式                      | 目标                   |
| ----------------- | ------------------------ | --------------- | ----------------------------- | ---------------------- |
| **A｜对照式修改** | 处理局部段落（2 – 4 页） | 每天多次        | 原文 → % ChatGPT建议 → 修改后 | 修“语气 + 逻辑 + 温度” |
| **B｜整章一致化** | 统修全章                 | 每章定稿前 1 次 | 原文 → % ChatGPT建议 → 修改后 | 修“风格 + 结构 + 衔接” |

## 🧭 工作节奏建议

- **上午** ：模板 A （精修 2–4 页）
- **下午** ：编译 + 人工采纳
- **晚上** ：模板 B （整章统一）
- **每 3 天** ：跨章风格检查
- 

# 模板A｜对照式修改（章节片段用）

> 直接粘到 ChatGPT/Trae；**保证输出：原文 → `% ChatGPT建议:` → 修改后版本**。
>  适用：你一次选 2–4 页进行“精修”。

```
你是一位专业教材编辑与人工智能教育专家。我们现在处于“成熟草稿的优化阶段”，目标不是重写，而是把每一段成熟文本打磨成“像一堂结构清晰、语气自然、行文有温度的深度课”。


【必守】
- 只做“对照式修改”：输出顺序固定为
  ① 原文段落
  ② % ChatGPT建议:（≤2句，说明修改动机）
  ③ 修改后版本（保留 LaTeX 结构与命令，不改标签/引用）
- 每段 ≤ 7 行；删除机械重复；添加必要过渡句与思维引导句。
- 语气基准：理性、温和、启发式；像老师在黑板前讲解。
- 调整语气，使理性与温度并存；让读者在阅读中能“跟着作者思考”，而不是被动接受。

- 思维节奏：“数学思维 → 算法思维 → 工程思维”。
- 每个小节末，补 1–2 句“学习呼应/思维回顾”，回扣导览中的学习目标。

【编辑时的思考框架】
- 逻辑线：段首承接，段尾收束（问题→推理→结论）。
- 语气：少被动语态；适度使用“我们/可以看到/换句话说”。
- 阅读流：技术句（原理）与叙事句（意义）交替。
- 启发性：关键概念后加一句引导思考。
- 禁用：空洞口号、居高临下的“显然/不难发现”。

✳️ 编辑语气模板（Editing Tone）
像一位有耐心的老师在板书讲解， 既准确、又有节奏， 既不压迫、也不飘浮。
✅ 句式参考：
* “从另一角度看，这一结果并非偶然。”
* “这正体现了数学思维的力量：把抽象概念转化为可计算结构。”
* “如果我们把注意力从算法转向背后的假设，会发现……”
* “这一思路在后来的深度学习中被以新的形式延续。”
❌ 避免：
* “综上所述，我们不难发现……”（太报告式）
* “显然，可以看出……”（太高姿态）
* “AI 改变了世界。”（空洞）

【输出格式示例】
% 原文
<粘贴原段落>

% ChatGPT建议: 语气偏报告式；段间缺过渡，补一句承上启下；压缩长句。
% 修改后版本
<改写后的段落（LaTeX命令保留，≤7行）>
```

------

# 模板B｜整章一致化（风格+逻辑+引导）

> 用在每晚的“统修”；**会做跨段衔接**、统一“导览/你将收获/节末回扣”。

```
你是《人工智能的数学思维》的教材编辑顾问。请对整章做“风格一致化 + 思维引导化 + 逻辑连贯性”润色。

【任务】
1) 不改章节结构与学术信息；只修复逻辑跳跃与风格不统一。
2) 统一语气：理性而有温度，像课堂讲解；减少被动语态。调整语气，使理性与启发并存；
3) 强化结构密度：每节 4-6 段，每段 ≤ 7 行；段与段有自然过渡。
4) 在需要处添加“承上启下”与“启发性提问”。
6) 保持“本章导览 + 你将收获”模板，口径与术语统一（首次中英并列）。

【思维标尺（编辑时请内化）】
- 目的：让读者“跟着作者思考”，而不是被动接受。
- 节奏：理论先行 → 实证验证 → 工程落地（螺旋规律）。
- 语句：先结论后解释；长句拆分；逻辑标志词“因此/由此/换言之”。

【输出格式】
按小节逐段输出：原文 → % ChatGPT建议: → 修改后版本
若有跨段重排，请先给 3 行“调整理由”，再给修改后文本。

✳️ 自检清单（Before You Save）
☑ 内容完整：没有删掉必要的学术要素；
☑ 衔接顺畅：每段都有“呼吸点”；
☑ 语气一致：不在同章内跳变“报告语 ↔ 对话语”；
☑ 有启发句：至少 1–2 个“引导思考”句；
☑ 结尾闭环：呼应章节导览或“你将收获”；
☑ LaTeX 安全：命令未被破坏、格式未变。

✳️ 输出基准示例（成品参考）
人工智能的发展既是一场技术演进，也是一种思维的自我迭代。
每一次算法的诞生，背后都有一个问题被重新表述的过程。
这正是数学思维与工程思维交汇之处：前者追求可解性，后者追求可实现性。
思维回顾：
从问题的抽象表达到可实现算法的设计，AI 的历史告诉我们——
“理解”始终比“计算”更深一步。
```

------

# 语气与风格指令（已融入模板，单列备查）

**🎯 目标定位（Purpose）**
 你不是在重写章节，而是在优化成熟草稿：

1. 保留原有结构与学术信息；
2. 修复逻辑跳跃与风格不统一；
3. 调整语气，让理性与温度并存；
4. 让读者“跟着作者思考”。

**✳️ 工作思路（How to Think While Editing）**

- 逻辑线：问题—推理—结论；段首承上启下。
- 语气：理性但温和；适度“我们/可以看到/换句话说”。
- 结构密度：一章一气；每段≤7行。
- 风格统一：数学 → 算法 → 工程。
- 阅读流：技术句（原理）× 叙事句（意义）交替。
- 启发性：关键处加 1 句引导思考。
- 结尾闭环：每节末回扣“你将收获”。

**✅ 句式参考**

- “从另一角度看，这一结果并非偶然。”
- “这正体现了数学思维的力量：把抽象概念转化为可计算结构。”
- “如果我们把注意力从算法转向背后的假设，会发现……”
- “这一思路在后来的深度学习中被以新的形式延续。”

**❌ 避免**

- “综上所述/显然/AI 改变了世界”等空洞/高姿态表达。

------

# 自检清单（保存前 6 条）

-  **内容完整**：学术信息未丢失；LaTeX 命令/标签不破坏
-  **衔接顺畅**：每段有呼吸点；段间有过渡
-  **语气一致**：课堂讲述感，非“报告体”
-  **启发句**：每节至少 1–2 句引导思考
-  **闭环**：节末回扣“你将收获”
-  **版面**：每段≤7行；修掉 Overfull/Undefined

------

# 快用片段（你可复制到章节开头做“编辑指令注释”）

```
% === Editing Guardrails (for ChatGPT/Trae) ===
% 不改结构与命令；原文→% ChatGPT建议→修改后版本；每段≤7行；
% 语气：理性、温和、启发式；“数学→算法→工程”；
% 关键处加过渡句与启发句；节末加“学习呼应”。
```

------

# 编译与版本建议

- TeXShop：引擎设为 `xelatexmk`；主控 `main.tex`
- 终端一键：

```
latexmk -xelatex -interaction=nonstopmode -synctex=1 -outdir=outputs tex/main.tex
```

- Git：每次模型出“对照式”稿，单独 commit 到 `reviews/`；人工采纳后再提交到 `chapters/`。





===

非常好的问题——你现在已经进入**教材打磨工程的核心阶段**。
 由于《人工智能的数学思维》是基于 LaTeX（`elegantbook.cls`） 的正式出版物，
 同时又结合了大模型（ChatGPT + Trae）进行“学术化 + 教学化”优化，
 我们要的不是“AI 自动改写”，而是一个 **可复用、可控、可追溯的编辑工作流**。

下面给你一个完整的、针对你实际项目量身设计的
 🧩 **《书稿打磨AI工作流（ChatGPT + Trae + LaTeX）》**。

------

## 🚀 一、总体设计目标

> **目标**：用大模型协同完成 *逻辑优化 + 语气统一 + 跨章一致性*，
>  让《人工智能的数学思维》达到正式教材出版级的结构与语体标准。

**核心原则：**

1. **保持结构完整**：不破坏 LaTeX 命令，不修改章节结构。
2. **强化思维引导**：让学生“看见思维的过程”，而不仅是结论。
3. **确保版本可控**：所有修改均以“对照式版本”保存，支持回溯与合并。
4. **分阶段协作**：写作 → 精修 → 全书一致化 → 排版验收。

------

## 🧱 二、整体流程总览

| 阶段                     | 主要目标                                 | 工具                     | 输出                     |
| ------------------------ | ---------------------------------------- | ------------------------ | ------------------------ |
| **阶段 1**：结构检查     | 明确章节结构、LaTeX 命令统一             | VS Code + LaTeX Workshop | `章节结构清单.xlsx`      |
| **阶段 2**：章节级优化   | 每章单独润色（逻辑、语气、教学导向）     | ChatGPT + Trae           | `xxx_refined.tex`        |
| **阶段 3**：跨章一致化   | 统一语气、术语、风格                     | ChatGPT 批量审校         | `merged_vX.tex`          |
| **阶段 4**：全书连贯审读 | 检查衔接、标题层级、引用与导览一致性     | ChatGPT 或 Claude        | `AI_Math_full_review.md` |
| **阶段 5**：出版级排版   | elegantbook 样式微调、页眉页脚、图表统一 | LaTeX 本地编译           | `final.pdf`              |

------

## 🧩 三、章节级工作流（主干）

每一章（例如 `3-History-computer.v1.tex`）都经历以下 6 步：

| 步骤                     | 操作                                                         | 工具           | 输出                            |
| ------------------------ | ------------------------------------------------------------ | -------------- | ------------------------------- |
| **1. 提取草稿**          | 复制 `.tex` 纯文本，删除编译残留                             | VS Code        | `chapter.v1.tex`                |
| **2. 结构扫描**          | 检查章节命令层级（chapter/section/subsection）与 introduction 环境 | VS Code        | `chapter.structure.txt`         |
| **3. 模型润色（阶段1）** | 使用 *Trae 提示词：“章节写作提示词”* 优化语气与逻辑          | Trae           | `chapter.v1_refined.tex`        |
| **4. 模型精修（阶段2）** | 使用 *“章节润色提示词”* 进行“对照式修改稿”                   | ChatGPT        | `chapter.v1_refined_review.tex` |
| **5. 审校与确认**        | 手动检查引号、公式、LaTeX 环境闭合、编号一致性               | LaTeX Workshop | `chapter.v2_final.tex`          |
| **6. 提交版本库**        | 将每章的最终版推送到 Git                                     | GitHub / Gitea | `commit: ch3 refined`           |

> 💡 建议：每章用版本号追踪。
>  如：`3-History-computer.v1.tex` → `v1_refined` → `v2_final`
>  同时保留 `% ChatGPT建议:` 注释，方便回溯修改逻辑。

------

## 🧭 四、Trae 与 ChatGPT 的分工策略

| 模型                          | 角色定位           | 适用场景                         | 产出风格                                          |
| ----------------------------- | ------------------ | -------------------------------- | ------------------------------------------------- |
| **Trae**                      | “结构级写作专家”   | 初稿扩写、段落逻辑修复           | 保持章节逻辑完整；自动识别 LaTeX 环境；偏学术温和 |
| **ChatGPT (GPT-5)**           | “语言与思维优化师” | 二次润色、风格统一、添加教学引导 | 语气温和启发；保持书面感；兼顾理性与温度          |
| **Claude Sonnet 4.1（可选）** | “语气检查员”       | 跨章风格一致化                   | 抓风格不一致句；优化跨章用词                      |

> ✅ 流程顺序：
>  **Trae 扩写/整理 → ChatGPT 精修 → Claude 一致化（可选）**

------

## 🧩 五、LaTeX 文件结构建议

```
AI_Math/
│
├── main.tex                  # 主文件
├── preamble.tex              # 统一导言区
├── elegantbook.cls           # 自定义类
│
├── chapters/
│   ├── 1-Intro.v2_final.tex
│   ├── 2-MathThinking.v2_final.tex
│   ├── 3-History-computer.v2_final.tex
│   ├── 4-ML-Foundations.v2_final.tex
│   └── ...
│
├── prompts/
│   ├── 章节写作提示词.md
│   ├── 章节润色提示词.md
│   ├── 草稿优化阶段提示词.md   ← 当前模板
│
├── scripts/
│   ├── merge_all_tex.py       # 自动合并章节
│   ├── tex_diff.py            # 对比版本差异
│
└── outputs/
    ├── AI_Math_v1.pdf
    ├── AI_Math_v2_review.pdf
    └── AI_Math_final.pdf
```

------

## 🔄 六、自动化辅助（可选）

| 工具                       | 用途                     | 说明                                   |
| -------------------------- | ------------------------ | -------------------------------------- |
| **Trae Workspace**         | 按章节生成并管理版本     | 每次保存即同步版本号                   |
| **VS Code LaTeX Workshop** | 编译、语法高亮、错误捕获 | 建议设置自动保存 `.synctex`            |
| **Git + GitHub**           | 版本与协作控制           | `commit: refine(chapter3): tone+logic` |
| **diff2html**              | 可视化比较修改           | 显示 ChatGPT 修改建议与原稿差异        |
| **Python 脚本**            | 自动合并章节             | 统一 `\input{}` 路径与编号校验         |

------

## 🧩 七、质量评估与审读节奏

| 层级     | 审核周期       | 审核重点                             |
| -------- | -------------- | ------------------------------------ |
| 章节内审 | 每完成 1 章    | 逻辑与语气一致性                     |
| 跨章审读 | 每 3–4 章      | 用词、风格、符号统一                 |
| 全书复审 | 完成后         | 前后概念呼应（如“数学思维”定义一致） |
| 教学审校 | 教师或专家试读 | 学习目标可操作性、语言平易度         |

------

## 📘 八、推荐版本命名与文件策略

| 文件名示例                                  | 含义               |
| ------------------------------------------- | ------------------ |
| `ch3_HistoryComputer_v1.tex`                | 原稿               |
| `ch3_HistoryComputer_v1_refined.tex`        | Trae 扩写版        |
| `ch3_HistoryComputer_v1_refined_review.tex` | ChatGPT 对照修改稿 |
| `ch3_HistoryComputer_v2_final.tex`          | 定稿（提交出版前） |

每个 `.tex` 文件头建议加上：

```tex
% --- 《人工智能的数学思维》章节编辑信息 ---
% 章节：第3章 智能，成于计算机
% 状态：v2_final（2025-11-04）
% 修改阶段：Trae结构优化 + ChatGPT润色整合
% 风格模板：书面、启发式、理性温和
% --------------------------------------------
```

------

## 💬 九、实际工作节奏建议

| 周次    | 任务                                          | 工具       |
| ------- | --------------------------------------------- | ---------- |
| 第1周   | 建立项目目录、检查 LaTeX 结构、导入提示词模板 | VS Code    |
| 第2–4周 | 每周完成 2–3 章的结构整理 + Trae 优化         | Trae       |
| 第5–7周 | ChatGPT 精修、风格统一                        | ChatGPT    |
| 第8周   | 全书交叉校对 + 编译测试 + 生成 PDF 预览       | LaTeX      |
| 第9周   | 专家外审与版面定稿                            | PDF 校对版 |

------

## ✅ 最终目标

> 一本文理兼容、理性温暖的 AI 教材，
>  在“数学思维—算法思维—工程思维”的逻辑中，
>  让学生不仅“学会AI”，更“理解智能背后的理性与取舍”。

------

是否希望我帮你生成对应的
 **「执行清单模板（Excel/Markdown版）」**，
 列出每章的状态、当前模型、任务负责人和完成进度？
 （可以直接作为团队协作/自查用）



===



太好了，你在 Mac 上用 **TeXShop** 编译，这里把前面的整体工作流补充为**Mac + TeXShop 定制版**，一步到位可用。

# Mac + TeXShop 最佳实践补充

## 1) 基础环境（一次性）

- 安装 **MacTeX**（包含 TeXShop、latexmk、biber、makeglossaries 等）。
- 字体建议安装：
  - Noto/Source Han 系列（思源宋体/黑体）：更适合 XeLaTeX。
- 代码着色（若用 `minted`）：`pip3 install Pygments`（或 `brew install pygments`）。

## 2) 工程约定（放在仓库根目录）

**主控文件**：`main.tex`（只 `\input{chapters/...}`）
 **统一导言**：`preamble.tex`（含 `elegantbook.cls` 相关设置、字体、宏定义）
 **章节**：`chapters/*.tex`（每章一个）
 **版本标记**：每章头部加编辑注释（日期/版本/模型）

在每个章节文件开头放置（方便单章编译 & 根文件统一）：

```tex
% !TEX root = ../main.tex
% !TEX encoding = UTF-8
```

在 `main.tex` 开头放置编译指令（建议 XeLaTeX + biber）：

```tex
% !TEX TS-program = xelatexmk
% !BIB TS-program = biber
% !TEX encoding = UTF-8
```

## 3) XeLaTeX + CJK 字体模板（推荐）

在 `preamble.tex` 或类文件加载后加入：

```tex
\usepackage{fontspec}
\usepackage{xeCJK}
\setmainfont{Times New Roman}
\setsansfont{Helvetica Neue}
\setmonofont{Menlo}
\setCJKmainfont{Source Han Serif SC}
\setCJKsansfont{Source Han Sans SC}
\setCJKmonofont{Source Han Mono SC}
% 数学：保持 amsmath + unicode-math（如需）
% \usepackage{unicode-math}
% \setmathfont{TeX Gyre Termes Math}
```

> 若使用 `elegantbook.cls` 自带的 CJK 方案，以上字体段可适当精简，保持一致即可。

## 4) TeXShop：设置 latexmk 引擎（建议）

TeXShop 自带 latexmk 引擎，建议启用 **XeLaTeX 驱动**，这样一次点击即可跑：`xelatex → biber → xelatex ×2 → 索引/术语`。

### 新建引擎（可选但强烈推荐）

1. 打开：`~/Library/TeXShop/Engines/`

2. 新建文件 `xelatexmk.engine`，内容：

   ```bash
   #!/bin/zsh
   latexmk -xelatex -halt-on-error -file-line-error -synctex=1 "$1"
   ```

3. 赋可执行权限：

   ```bash
   chmod +x ~/Library/TeXShop/Engines/xelatexmk.engine
   ```

4. 之后在 TeXShop 顶部下拉选择引擎：`xelatexmk`。

### 如果使用 minted

- 需要允许 `-shell-escape`：在引擎中加入：

  ```bash
  latexmk -xelatex -halt-on-error -file-line-error -synctex=1 -shell-escape "$1"
  ```

- 章节中使用：

  ```tex
  \usepackage[outputdir=build]{minted} % 可选独立输出
  ```

## 5) BibLaTeX + biber（推荐）

- 导言区：

  ```tex
  \usepackage[backend=biber,style=gb7714-2015]{biblatex} % 或者 numeric/authoryear
  \addbibresource{refs.bib}
  ```

- TeXShop 菜单：`Typeset` 只需点一次（由 latexmk 调 biber）。

## 6) 索引/术语（如有）

- 术语：

  ```tex
  \usepackage[acronym]{glossaries}
  \makeglossaries
  ```

- `latexmk` 会自动调用 `makeglossaries`（大多数 MacTeX 预设已支持）。如果未触发，可在引擎中追加 `-gg` 强制全构建。

## 7) SyncTeX（跳转定位）

- `-synctex=1` 已在引擎开启。TeXShop 左右联动：源 ↔ PDF 双向跳转。

## 8) ElegantBook 相关（与你当前需求贴合）

你之前已经把**“结构导览 introduction 环境 + 你将收获”**做成两块；如果需要**缩紧“本章摘要/导览”边距**（不改全局风格），可在 `preamble.tex` 定义两个轻量环境，**不破坏类文件**：

```tex
% 轻量缩进盒：用于导览/摘要
\newenvironment{tightsummary}{%
  \par\begingroup
  \setlength{\leftskip}{1em}%
  \setlength{\rightskip}{1em}%
  \small
}{\par\endgroup}

% 用法：
% \begin{tightsummary}
%   这里放“本章导览”或“你将收获”的列表内容
% \end{tightsummary}
```

如果你坚持复用 `introduction` 的视觉样式，只想**局部收紧**，可以包一层：

```tex
\begin{adjustwidth}{1em}{1em} % 需要 \usepackage{changepage}
  \begin{introduction}
    \item ...
  \end{introduction}
\end{adjustwidth}
```

> 这不会修改类文件，也不会影响其他章节。你之前遇到“不能传参数进去”，就用外层 `adjustwidth` 解决。

## 9) 章节“对照式修改稿”的最省心做法（配合 TeXShop）

- 每章维持三份：
   `chN.v1.tex`（原稿）
   `chN.v1_refined.tex`（Trae/ChatGPT改写）
   `chN.v1_review.tex`（对照式：原文+% ChatGPT建议+修改版）
- `main.tex` 只 `\input{..._final.tex}`；对照稿只在审读时单独编译查看。

## 10) 常见错误与快速修复

- **Undefined control sequence**：通常是宏/包加载顺序或忘记 `\usepackage{...}`。回到 `preamble.tex` 统一加。
- **CJK 乱码或问号**：确认 `xelatex`、`UTF-8`、字体存在。
- **biber 报错**：删除 `*.bbl *.bcf` 后重编；或 `latexmk -C` 清理再编。
- **minted 报错**：未加 `-shell-escape`；或 Pygments 未安装。
- **Overfull/Underfull**：在导览/摘要局部使用 `\small` 或 `\raggedright`；必要时 `\sloppy`（尽量少用）。

## 11) VS Code 并存（可选）

如果你偶尔想用 VS Code 进行模型交互和多文件浏览，但保持 TeXShop 编译：

- VS Code 负责**写作与版本管理**；TeXShop 负责**一键编译**。
- VS Code 设置 `latex-workshop.latex.outDir = build`，不和 TeXShop 冲突即可。
- 两边都能用 SyncTeX（VS Code 要装 LaTeX Workshop）。

------

# 小清单（可打印）

-  安装 MacTeX（含 TeXShop/latexmk/biber）
-  安装 CJK 字体（思源/Noto），确认 XeLaTeX 可用
-  `preamble.tex` 统一字体与宏包（fontspec/xeCJK）
-  `xelatexmk.engine` 建好并选为默认引擎
-  `main.tex` 顶部三行 `% !TEX` 指令就位
-  章节文件头加 `% !TEX root = ../main.tex`
-  对照式版本保存策略（v1 / v1_refined / v1_review / v2_final）
-  “本章导览/你将收获”使用 `adjustwidth` 或 `tightsummary` 收紧边距
-  `biblatex+biber` 串好；若有 minted，则启用 `-shell-escape`
-  编译异常优先看 `.log` 的第一处 “!” 和 `l.xxx` 行号

------

需要的话，我可以基于你现有的 `elegantbook.cls` 和一段示例章节，直接给出**可拷贝即用的 `preamble.tex`** 与 **`xelatexmk.engine`** 成套模板（包含 CJK 字体、biblatex、minted 可开关）。

## 💡 推荐组合工作流（适合你目前状态）

> 🧱 当前阶段：草稿优化与润色
>  🖥 平台：Mac + TeXShop 编译 + VS Code 编辑
>  🤖 模型：ChatGPT 网页 / Trae 桌面端