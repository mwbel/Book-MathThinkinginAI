现在，我需要向用户提供一份更新后的使用指南，特别说明 Mac 平台上的快捷键。

指南应该包括：

1. __明确指出快捷键已更新为 Mac 风格__。

2. __新添加的快捷键及其功能__：

   - `Cmd+Option+Shift+E`: 使用 `quick_edit.py` 进行通用扩写。
   - `Cmd+Option+R`: 使用 `quick_edit.py mtai-refine` 进&#x884C;__&#x5BF9;照式润色 (diff)__。
   - `Cmd+Option+D`: 使用 `quick_edit.py mtai-expand` 进&#x884C;__&#x6269;写 (diff 模式)__。

3. __如何使用这些快捷键__：选中文字，然后按下快捷键。结果会在 VS Code 终端中显示。

4. __重启 VS Code__：再次提醒用户重启 VS Code 使快捷键生效。

5. __diff 格式的输出__：解释 `mtai-refine` 和 `mtai-expand` 会输出 diff 格式，方便用户在 VS Code 中进行比较和应用更改。

Task Completed

我已经根据你的反馈，将 VS Code 快捷键修改为更符合 Mac 平台习惯的组合。

__请务必重启 VS Code__，以确保新的快捷键配置生效。

以下是你现在可用的 Mac 平台快捷键列表：

---

__📝 通用文本润色 (通过 `quick_edit.py polish`)__

- `Cmd+Option+P`：__学术风格润色__
- `Cmd+Option+L`：__课堂风格润色__
- `Cmd+Option+C`：__精炼文本__
- `Cmd+Option+Shift+E`：__扩写文本__ (新增)

---

__✍️ MTAI 专业书稿编辑 (通过 `quick_edit.py` 调用 MTAI 提示词)__

- `Cmd+Option+R`：__MTAI 对照式润色 (diff)__ (新增)

  - 功能：对选中的 LaTeX 文本进行轻度润色，目标是保持原意但提升表达质量，使其更接近通识 + 课堂讲解体。
  - 输出格式：会以 `diff` 视图显示原文和修改后的内容，方便你直接复制应用修改。

- `Cmd+Option+D`：__MTAI 扩写 (diff 模式)__ (新增)

  - 功能：对选中的 LaTeX 文本进行扩写（约 1.5–2 倍篇幅），对关键概念和结论提供更充分的解释，增加例子、类比或直观描述，同时保持课堂讲解体风格。
  - 输出格式：同样以 `diff` 视图显示原文和扩写后的内容。

---

__🔧 其他实用功能__

- `Cmd+Option+E`：__解释概念__
- `Cmd+Option+X`：__生成例子__
- `Cmd+Option+T`：__翻译中文__

---

__使用方法：__

1. 在 VS Code 编辑器中，__选中你想要处理的 LaTeX 文本__。
2. 按下相应的快捷键。
3. Gemini 模型处理后的结果会显示在 VS Code 的终端面板中。对于 `MTAI 对照式润色 (diff)` 和 `MTAI 扩写 (diff 模式)`，结果会以清晰的 `diff` 格式呈现，你可以直接从中复制修改后的内容。

希望这些新的 Mac 平台快捷方式能大大提高你的书稿修改效率！
