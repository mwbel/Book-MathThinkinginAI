# 🎯 立即测试：像Cursor一样的逐行修改管理

## 现在就试试看！

### Step 1: 在VS Code中打开你的文件

1. **打开VS Code**
2. **打开文件**: `chapters/ch5/5-Tools.v1_polished_unified_expanded.tex`

### Step 2: 查看你的修改

你现在应该能看到：

**编辑器右侧的修改指示器：**
```
第56行: ━━━━━━━━ (红色删除线)
第57行: ++++++++++ (绿色新增线)
```

**源代码管理面板 (Ctrl+Shift+G)：**
```
📄 CHANGES
└─ 📝 5-Tools.v1_polished_unified_expanded.tex
   ├─ ➕ 1 insertion
   └─ ❌ 8 deletions
```

### Step 3: 逐行操作测试

**方法A: 鼠标点击 (最简单)**
1. **找到修改的行** (会有颜色高亮)
2. **看到行号的右边有小的 `+` 或 `-` 按钮**
3. **点击这些按钮来accept/reject**

**方法B: 右键菜单**
1. **选中修改的行**
2. **右键选择:**
   ```
   ├── 接受更改 (Accept Change)
   ├── 拒绝更改 (Reject Change)
   ├── 接受选区 (Accept Selection)
   └── 拒绝选区 (Reject Selection)
   ```

**方法C: 快捷键 (最高效)**
1. **选中要操作的行**
2. **按:**
   - `Ctrl+Alt+Enter` - 接受修改
   - `Ctrl+Alt+U` - 取消暂存
   - `Ctrl+Alt+Z` - 还原修改

### Step 4: 你应该看到的具体界面

**在编辑器中，你的修改看起来像这样：**

```tex
<<<<<<< HEAD                 // 这是原始版本
\subsection{导数与梯度}
=======
\subsection{导数与梯度：从基础概念到几何视角}  // 这是新版本
>>>>>>> 你的修改
```

**或者使用GitLens的内联显示：**
```tex
\subsection{导数与梯度：从基础概念到几何视角} | // ✨ 新增的标题
// ❌ 删除了: \subsection{导数与梯度}
// ❌ 删除了: \subsection{导数与梯度的几何视角}
```

### Step 5: 实际操作练习

**对你的当前文件尝试：**

1. **接受新标题**：
   - 找到 `\subsection{导数与梯度：从基础概念到几何视角}`
   - 点击右侧的 `+` 按钮

2. **拒绝旧标题**：
   - 找到删除线标记的 `\subsection{导数与梯度}`
   - 点击右侧的 `-` 按钮

3. **接受格式优化**：
   - 找到 `\textbf{梯度的几何意义}：`
   - 点击右侧的 `+` 按钮

### Step 6: 检查结果

**完成操作后，按 `Ctrl+Shift+G` 查看：**
```
📄 STAGED CHANGES  // 如果接受了修改
└─ 📝 5-Tools.v1_polished_unified_expanded.tex

📄 CHANGES         // 如果还有未处理的修改
└─ 📝 5-Tools.v1_polished_unified_expanded.tex
```

## 🎉 成功标志

如果你能看到以下任何一个界面，就说明配置成功了：

✅ **编辑器中的颜色高亮** (红色=删除，绿色=新增)
✅ **行号旁边的小按钮** (+ 或 -)
✅ **源代码管理面板中的修改列表**
✅ **右键菜单中的Git选项**

## 🚨 如果没有看到怎么办？

1. **重启VS Code** (确保配置生效)
2. **检查GitLens是否启用** (Ctrl+Shift+P → 输入 "GitLens")
3. **确保文件有修改** (如果没有Git差异，就看不到按钮)
4. **打开源代码管理面板** (Ctrl+Shift+G)

现在就试试看！你将获得完全类似Cursor的逐行修改管理体验。