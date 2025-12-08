# 🚀 立即可用的逐行修改管理指南

## 🎯 快速解决方案（重启VS Code后立即生效）

### 方法1：右键菜单（最简单可靠）

1. **选中你选中的行** (`\subsection{导数与梯度}`)
2. **右键点击** → 在菜单中找到：
   ```
   ┌─────────────────────────────┐
   │ 复制(Copy)                  │
   │ 粘贴(Paste)                  │
   │ ─────────────────────────── │
   │ Git相关操作：                │
   │ ✅ Stage Change (暂存更改)   │
   │ ❌ Unstage Change (取消暂存) │
   │ 🗑️ Discard Changes (放弃更改)│
   └─────────────────────────────┘
   ```

### 方法2：源代码管理面板（最直观）

1. **按 `Ctrl+Shift+G`** 打开Git面板
2. **点击文件名** `5-Tools.v1_polished_unified_expanded.tex`
3. **你会看到：**
   ```
   📄 CHANGES
   └─ 📝 5-Tools.v1_polished_unified_expanded.tex
      ├─ 📝 Modified: 3 additions, 8 deletions
      │  ├─ ➕ \subsection{导数与梯度：从基础概念到几何视角}
      │  ├─ ❌ \subsection{导数与梯度}
      │  └─ ➕ \textbf{梯度的几何意义}：
   └─ 📝 [✅ Stage All Changes] [🗑️ Discard All Changes]
   ```

### 方法3：命令面板（最灵活）

1. **选中要处理的行**
2. **按 `Ctrl+Shift+P`**
3. **输入以下命令之一：**
   - `Git: Stage` → 暂存选中的修改
   - `Git: Unstage` → 取消暂存选中的修改
   - `Git: Discard Changes` → 放弃选中的修改

### 方法4：内联点击按钮（最类似Cursor）

1. **确保修改是可见的**（应该有颜色高亮）
2. **在行号旁边寻找小图标：**
   - 红色 `~` 或 `-` → 删除的内容
   - 绿色 `+` 或 `▶` → 新增的内容
3. **点击这些图标来操作**

## 🔧 如果看不到修改的解决方法

### 检查1：修改是否可见
```bash
# 在终端中运行确认有修改
cd "/Users/Min369/Desktop/书/书稿打磨/draft-tex-3扩写"
git diff chapters/ch5/5-Tools.v1_polished_unified_expanded.tex
```

### 检查2：VS Code设置
1. **重启VS Code**（重要！）
2. **按 `Ctrl+,` 打开设置**
3. **搜索 "git decorators"**
4. **确保 "Diff Decorators" 已启用**

### 检查3：切换显示模式
1. **按 `Ctrl+Shift+P`**
2. **输入 "Toggle Inline Diff"**
3. **按回车切换模式**

## 🎮 针对你当前的修改

### 你的具体修改内容：
1. **第56行**: `\subsection{导数与梯度：从基础概念到几何视角}` ✅ **新标题**
2. **删除**: `\subsection{导数与梯度}` ❌ **旧标题1**
3. **删除**: `\subsection{导数与梯度的几何视角}` ❌ **旧标题2**
4. **格式优化**: `\textbf{梯度的几何意义}：` ✅ **加粗标题**

### 建议操作：
1. **接受新标题** ✅
2. **删除旧标题** ✅
3. **接受格式优化** ✅

## 🚀 立即行动步骤

### 第一步：重启VS Code
```bash
# 完全退出VS Code，然后重新打开
```

### 第二步：打开文件
1. **打开VS Code**
2. **打开文件**: `chapters/ch5/5-Tools.v1_polished_unified_expanded.tex`

### 第三步：查看修改
- **你应该看到红色和绿色的高亮**
- **在行号旁边有小的图标**

### 第四步：逐行操作
1. **选中第56行的修改**
2. **右键 → "Stage Change"**
3. **对其他修改重复此操作**

## 💡 终极解决方案

如果以上方法都不行，使用命令行：

```bash
# 1. 交互式添加（最精确控制）
cd "/Users/Min369/Desktop/书/书稿打磨/draft-tex-3扩写"
git add -p chapters/ch5/5-Tools.v1_polished_unified_expanded.tex

# 2. 按y接受，按n拒绝每个修改块
# 3. 按s拆分复杂修改
```

## 🎯 预期效果

配置成功后，你应该看到：
- ✅ **编辑器中的颜色高亮**
- ✅ **行号旁边的操作图标**
- ✅ **右键菜单中的Git选项**
- ✅ **源代码管理面板中的修改列表**

现在就重启VS Code试试看！