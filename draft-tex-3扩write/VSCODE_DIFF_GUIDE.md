# VS Code逐行修改管理指南 - 像Cursor一样的体验

## 🎯 目标：实现Cursor式的逐行accept/reject功能

### 方法1：VS Code内建功能 + GitLens（推荐）

#### 1.1 安装和配置

**Step 1: 安装GitLens扩展**
1. 打开VS Code
2. 按 `Ctrl+Shift+X` 打开扩展面板
3. 搜索 `GitLens`
4. 点击安装（作者：GitKraken）

**Step 2: 启用内联差异显示**
- 已为你配置了 `.vscode/settings.json`
- 重启VS Code使配置生效

#### 1.2 使用方法

**查看修改的3种方式：**

1. **源代码管理面板（Ctrl+Shift+G）**
   ```
   📁 chapters/ch5/5-Tools.v1_polished_unified_expanded.tex
   ├─ ➕ \subsection{导数与梯度：从基础概念到几何视角}
   ├─ ❌ \subsection{导数与梯度}
   ├─ ❌ \subsection{导数与梯度的几何视角}
   └─ ➕ \textbf{梯度的几何意义}：
   ```

2. **编辑器内联显示**
   - 左侧：删除的内容（红色）
   - 右侧：新增的内容（绿色）
   - 每行都有操作按钮

3. **GitLens注释视图**
   ```tex
   \subsection{导数与梯度：从基础概念到几何视角}  // ✨ 新增
   // ❌ 删除: \subsection{导数与梯度}
   // ❌ 删除: \subsection{导数与梯度的几何视角}
   ```

#### 1.3 逐行操作快捷键

**已配置的快捷键：**
- `Ctrl+Alt+Enter` - 接受选中的修改行
- `Ctrl+Alt+U` - 取消暂存选中的修改行
- `Ctrl+Alt+Z` - 还原选中的修改行

**鼠标操作：**
1. **选中修改的行或代码块**
2. **右键菜单** → 选择Git操作：
   ```
   ├── 接受更改 (Accept Change)
   ├── 拒绝更改 (Reject Change)
   ├── 接受选区 (Accept Selection)
   ├── 拒绝选区 (Reject Selection)
   └── 暂存更改 (Stage Changes)
   ```

#### 1.4 实际操作演示

**对于你的当前文件：**

1. **打开文件**：`chapters/ch5/5-Tools.v1_polished_unified_expanded.tex`

2. **你会看到类似这样的界面：**
   ```tex
   - \subsection{导数与梯度}                     | ✅ 拒绝
   + \subsection{导数与梯度：从基础概念到几何视角} | ✅ 接受

   - \subsection{导数与梯度的几何视角}            | ✅ 拒绝

   - 梯度的几何意义：                           | ✅ 拒绝
   + \textbf{梯度的几何意义}：                 | ✅ 接受
   ```

3. **操作方式：**
   - **鼠标点击**：点击每行右侧的 `+` 或 `-` 按钮
   - **键盘快捷键**：选中行后按 `Ctrl+Alt+Enter`
   - **右键菜单**：选中后右键选择操作

### 方法2：使用专门的Git GUI工具

#### 2.1 GitKraken（可视化Git客户端）

**安装：**
```bash
# macOS使用Homebrew安装
brew install --cask gitkraken

# 或从官网下载：https://www.gitkraken.com/
```

**使用：**
1. 打开GitKraken
2. 打开你的项目文件夹
3. 在修改视图中逐行accept/reject

#### 2.2 Sublime Merge

**安装：**
```bash
# macOS使用Homebrew安装
brew install --cask sublime-merge
```

**特点：**
- 专门为逐行diff设计
- 类似Cursor的界面
- 支持LaTeX文件高亮

### 方法3：专业级解决方案

#### 3.1 Meld（可视化diff工具）

**安装：**
```bash
# macOS使用Homebrew安装
brew install meld
```

**配置VS Code使用Meld：**
```json
{
    "git.diffTool": "meld",
    "git.enableSmartCommit": true,
    "git.autofetch": true
}
```

#### 3.2 VS Code + Git Lens + 扩展组合

**推荐扩展组合：**
1. **GitLens** - 必装
2. **Git History** - 查看修改历史
3. **Git Blame** - 查看每行修改者
4. **Git Indicators** - 更直观的修改指示器

## 🚀 快速开始指南

### 立即体验：

1. **在VS Code中打开你的项目**
2. **安装GitLens扩展**
3. **重启VS Code**
4. **打开** `chapters/ch5/5-Tools.v1_polished_unified_expanded.tex`
5. **按 `Ctrl+Shift+G` 打开源代码管理面板**

### 你将看到：

**源代码管理面板：**
```
📄 CHANGES (1)
├─ 📝 5-Tools.v1_polished_unified_expanded.tex
│  ├─ ➕ \subsection{导数与梯度：从基础概念到几何视角}
│  ├─ ❌ \subsection{导数与梯度}
│  ├─ ❌ \subsection{导数与梯度的几何视角}
│  ├─ ➕ \textbf{梯度的几何意义}：
│  └─ ➕ \textbf{在AI应用中的实践价值}：
```

**编辑器内联视图：**
- 绿色高亮：新增内容（带+按钮）
- 红色高亮：删除内容（带-按钮）
- 每行都可单独点击accept/reject

### 操作流程：

1. **查看修改**：打开文件即可看到所有修改
2. **逐行决策**：
   - 点 `+` 接受新增
   - 点 `-` 接受删除
   - 右键选择更多操作
3. **暂存决定**：`Ctrl+Alt+Enter` 暂存选中的修改
4. **提交结果**：`Ctrl+Shift+G` → 输入提交信息 → `Ctrl+Enter`

## 📋 最佳实践

### 工作流程建议：

1. **先看整体**：在源代码管理面板概览所有修改
2. **逐行审查**：在编辑器中逐行决定去留
3. **分批提交**：相关修改一起提交
4. **及时提交**：每完成一个审查就提交

### 快捷键记忆：

- `Ctrl+Shift+G` - 打开Git面板
- `Ctrl+Alt+Enter` - 接受选中的修改
- `Ctrl+Alt+U` - 取消暂存
- `Ctrl+Alt+Z` - 还原修改

这样你就能获得完全类似Cursor的逐行修改管理体验！现在就可以试试看效果如何。