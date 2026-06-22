# 教材润色校对页面工具

本目录用于开发《人工智能的数学思维》教材润色校对页面的本地工具。

当前阶段实现两个能力：

- 读取 `.tex` 文件。
- 识别 `\chapter`、`\section`、`\subsection`、`\subsubsection`。
- 按空行切分正文段落。
- 将常见 LaTeX 环境作为不可拆分 block。
- 输出结构化 `review-data.json`。
- 可选读取一份润色后的 `.tex`，输出段落级 `pairs` 对照数据。
- 对每个 pair 标记 `unchanged`、`changed`、`added`、`removed`。
- 为 changed pair 输出 token 级 diff，供后续 HTML 校对页使用。
- 将 `compare-data.json` 渲染成可直接打开的静态 HTML 校对页。
- HTML 校对页支持按状态筛选，并可一键展开或收起词级差异。
- 可选导出标准 unified diff 文件 `changes.diff`。
- 可用一条命令生成 `compare-data.json`、`review.html`、`review-log.md`、`changes.diff`。
- 同时生成 `test.html`，用于在浏览器中自测校对页的渲染和交互。
- 可将带有“原文 / ChatGPT建议 / 修改后版本”的过程稿清洗为干净 `.tex` 校对稿。
- 可为干净校对稿生成 Typora / Overleaf 风格的 `render.html` 渲染预览页。
- 可选编译真实 LaTeX PDF 与 `.synctex.gz`，在四栏校对中用 SyncTeX 做 PDF 页面与源码行号的双向定位。

不做：

- 不修改原始 `.tex` 文件。
- 不生成润色稿。
- 不调用 LLM。
- 不依赖外部网页资源。
- 不做自动回写。
- 不覆盖输入 `.tex` 文件；清洗稿以新文件输出。
- 不在浏览器里直接改写 `.tex` 文件；源码栏临时编辑只影响当前页面的即时 HTML 预览，真实 PDF/SyncTeX 对应最近一次编译结果。

过程稿清洗示例：

```bash
python3 tools/review/clean_polished_tex.py \
  --input "draft-tex/chapters/12-语言中的智能：Transformer的意外胜利.v3_polished1.tex" \
  --output "draft-tex/chapters/12-语言中的智能：Transformer的意外胜利.v3_polished1_clean.tex"
```

如果输出文件已经存在，需要显式加 `--force` 才会覆盖。

推荐一键生成示例：

```bash
python3 tools/review/run_review.py \
  --source "draft-tex/chapters/12-语言中的智能：Transformer的意外胜利.v3_refined.tex" \
  --target "draft-tex/chapters/12-语言中的智能：Transformer的意外胜利.v3_polished1.tex" \
  --name "ch12" \
  --title "第12章 语言中的智能校对页" \
  --pretty
```

如果希望 `render.html` 的渲染栏使用真实 LaTeX PDF 页面，并启用 SyncTeX 定位，可以加：

```bash
python3 tools/review/run_review.py \
  --source "draft-tex/chapters/12-语言中的智能：Transformer的意外胜利.v3_refined.tex" \
  --target "draft-tex/chapters/12-语言中的智能：Transformer的意外胜利.v3_polished1_clean.tex" \
  --name "ch12-clean" \
  --title "第12章 清洗校对稿" \
  --pretty \
  --tex-root "draft-tex" \
  --build-pdf-preview
```

默认输出到 `tools/review/outputs/`：

- `ch12-compare-data.json`
- `ch12-review.html`
- `ch12-review-log.md`
- `ch12-changes.diff`
- `ch12-test.html`
- `ch12-render.html`

打开 `ch12-test.html` 后，可以直接运行自测，检查筛选按钮、差异展开/收起、章节导航、桌面宽度和移动宽度。
打开 `ch12-render.html` 后，可以在三种视图之间切换：

- `Typora 阅读`：只看修改稿渲染结果，适合连续通读。
- `双栏对照`：原文渲染与修改稿渲染并排，适合检查语言变化。
- `四栏校对`：原文源码 / 原文渲染 / 修改稿源码 / 修改稿渲染，适合检查源码结构与渲染结果是否一致。

页面顶部提供章节选择器。启动本地 HTTP 服务后，可以直接在浏览器里切换到任意章节，并分别选择 `原文版本` 与 `修改稿版本`；工具会自动生成该章节对应的 `review.html` 和 `render.html`，然后跳转到新页面。

目录和每个栏位都可以单独收起，四栏校对时可以先收起暂时不看的源码或渲染栏，给重点栏位留出空间。
四栏校对中的源码栏可以临时编辑，页面会即时刷新对应渲染结果；这些编辑只存在于浏览器页面内，不会自动写回 `.tex` 文件。
双栏对照和四栏校对中的渲染栏默认使用 PDF 阅读器式分页预览，页脚显示页码；源码编辑窗口高度与分页阅读窗口对齐，便于横向校对。
不加 `--build-pdf-preview` 时，分页预览是前端即时 HTML 预览，适合快速看结构，但不等同于真实 LaTeX 编译。
加 `--build-pdf-preview` 后，渲染栏改为真实 LaTeX PDF 的逐页 PNG，并写出同名 `.synctex.gz`；这时右键点击 PDF 页面会通过本地 SyncTeX 服务跳转到同侧源码栏行号，右键点击源码栏行号也可以跳回 PDF 页面位置。
源码栏使用不自动换行的代码视图和行号栏，定位时会同步滚动并高亮行号。
这一模式借鉴 TeXShop 的工作流：源码是编辑对象，PDF 是最近一次编译后的排版结果，SyncTeX 只负责二者之间的定位。浏览器源码栏里的临时编辑不会自动写回 `.tex`，也不会自动进入 PDF；点击 `重新编译 PDF` 时，工具会重新读取磁盘上的 `.tex` 文件并刷新 PDF 预览。
真实 PDF 渲染栏提供上一页、下一页、缩小和放大控制；PDF 页图按需加载，避免四栏页面一次性加载所有页面。

启动 SyncTeX 本地服务：

```bash
python3 tools/review/synctex_review_server.py \
  --root "tools/review/outputs" \
  --host 127.0.0.1 \
  --port 8766
```

然后打开：

```text
http://127.0.0.1:8766/ch12-clean-render.html
```

也可以直接使用脚本：

```bash
chmod +x tools/review/scripts/*.sh
```

只生成前端静态产物：

```bash
tools/review/scripts/build_review_frontend.sh
```

只启动本地 HTTP + SyncTeX 服务：

```bash
tools/review/scripts/start_review_backend.sh
```

一键先构建、再启动服务：

```bash
tools/review/scripts/start_review_all.sh
```

这三个脚本默认指向当前第 12 章清洗稿，也支持用位置参数覆盖：

```bash
tools/review/scripts/build_review_frontend.sh \
  "draft-tex/chapters/原文.tex" \
  "draft-tex/chapters/修改稿.tex" \
  "输出名前缀" \
  "页面标题"
```

服务脚本支持环境变量覆盖端口与根目录：

```bash
PORT=8767 STATIC_ROOT="tools/review/outputs" tools/review/scripts/start_review_backend.sh
```

服务启动后，页面顶部的 `重新编译 PDF` 按钮会调用本地服务重新生成当前预览页。修改了磁盘上的 `.tex` 文件后，可以直接点击该按钮刷新 PDF 和 SyncTeX 定位数据。

单文件解析示例：

```bash
python3 tools/review/build_review.py \
  --source "draft-tex/chapters/12-语言中的智能：Transformer的意外胜利.v3_refined.tex" \
  --output "tools/review/outputs/ch12-review-data.json"
```

双文件对照示例：

```bash
python3 tools/review/build_review.py \
  --source "draft-tex/chapters/12-语言中的智能：Transformer的意外胜利.v3_refined.tex" \
  --target "draft-tex/chapters/12-语言中的智能：Transformer的意外胜利.v3_polished1.tex" \
  --output "tools/review/outputs/ch12-compare-data.json" \
  --pretty
```

HTML 校对页生成示例：

```bash
python3 tools/review/render_review.py \
  --input "tools/review/outputs/ch12-compare-data.json" \
  --output "tools/review/outputs/ch12-review.html" \
  --log-output "tools/review/outputs/ch12-review-log.md" \
  --diff-output "tools/review/outputs/ch12-changes.diff" \
  --test-output "tools/review/outputs/ch12-test.html" \
  --title "第12章 语言中的智能校对页"
```

`--log-output` 会生成本次校对任务日志，记录输入文件、输出文件、对照统计、解析统计和本次任务边界。
`--diff-output` 会生成标准 unified diff，适合归档或交给熟悉 diff 的编辑复核。
`--test-output` 会生成前端测试面板，方便手动打开和自测。

单独生成渲染预览页示例：

```bash
python3 tools/review/render_tex_preview.py \
  --source "draft-tex/chapters/12-语言中的智能：Transformer的意外胜利.v3_polished1_clean.tex" \
  --original-source "draft-tex/chapters/12-语言中的智能：Transformer的意外胜利.v3_refined.tex" \
  --output "tools/review/outputs/ch12-clean-render.html" \
  --title "第12章 清洗校对稿"
```
