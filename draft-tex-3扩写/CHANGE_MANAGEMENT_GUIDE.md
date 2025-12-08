# LaTeX单行修改管理指南

## 方法1：Git交互式添加（最推荐）

### 1.1 逐块审查修改
```bash
cd "/Users/Min369/Desktop/书/书稿打磨/draft-tex-3扩写"
git add -p chapters/ch5/5-Tools.v1_polished_unified_expanded.tex
```

**你会看到这样的交互界面：**
```
diff --git a/chapters/ch5/5-Tools.v1_polished_unified_expanded.tex b/chapters/ch5/5-Tools.v1_polished_unified_expanded.tex
index a8832ee..83291fc 100644
--- a/chapters/ch5/5-Tools.v1_polished_unified_expanded.tex
+++ b/chapters/ch5/5-Tools.v1_polished_unified_expanded.tex
@@ -56,7 +56,7 @@

 \vspace{0.5em}

-\subsection{导数与梯度}
+\subsection{导数与梯度：从基础概念到几何视角}
```

**选择操作：**
- `y` - **接受这个修改块**
- `n` - **拒绝这个修改块**
- `q` - 退出
- `a` - 接受这个及后续所有修改
- `d` - 拒绝这个及后续所有修改
- `s` - **拆分这个修改块为更小的块**
- `e` - 手动编辑这个修改块

### 1.2 拆分修改块进行精细控制
当遇到多个修改在一起的块时，按 `s` 可以拆分：

```bash
# 示例：合并两个小节的修改
git add -p chapters/ch5/5-Tools.v1_polished_unified_expanded.tex
# 看到:
- \subsection{导数与梯度}
- \subsection{导数与梯度的几何视角}
+ \subsection{导数与梯度：从基础概念到几何视角}

# 按 's' 拆分后，可以单独决定每个修改
```

## 方法2：使用VS Code的源代码管理

### 2.1 在VS Code中逐行审查
1. 打开源代码管理面板 (Ctrl+Shift+G)
2. 点击文件名查看修改
3. 每个修改旁边有操作按钮：
   - **"+"** - 接受修改
   - **"-"** - 拒绝修改

### 2.2 右键菜单操作
```plaintext
右键点击修改行 → 选择：
├── 接受更改 (Accept Change)
├── 拒绝更改 (Reject Change)
├── 接受所有更改 (Accept All Changes)
└── 拒绝所有更改 (Reject All Changes)
```

## 方法3：Git reset + 手动选择

### 3.1 查看所有修改
```bash
git diff chapters/ch5/5-Tools.v1_polished_unified_expanded.tex
```

### 3.2 选择性提交
```bash
# 方法A：使用交互式添加
git add -i chapters/ch5/5-Tools.v1_polished_unified_expanded.tex

# 方法B：手动编辑补丁
git diff chapters/ch5/5-Tools.v1_polished_unified_expanded.tex > changes.patch
# 编辑changes.patch，删除不想提交的修改
git apply changes.patch --whitespace=nowarn
```

## 实际操作示例

### 场景1：只接受标题修改，拒绝其他修改
```bash
# 1. 查看修改
git diff chapters/ch5/5-Tools.v1_polished_unified_expanded.tex

# 2. 交互式添加
git add -p chapters/ch5/5-Tools.v1_polished_unified_expanded.tex

# 3. 当看到标题修改时，按 'y' 接受
#    当看到其他修改时，按 'n' 拒绝

# 4. 提交接受的修改
git commit -m "优化小节标题：整合导数与梯度内容"
```

### 场景2：接受列表标题加粗，但保持原内容
```bash
# 使用git add -p时，如果看到这样的修改：
-梯度的几何意义：
+\textbf{梯度的几何意义}：

# 按 's' 拆分，然后单独选择接受加粗部分
```

### 场景3：临时保存部分修改
```bash
# 保存当前工作状态
git stash push -m "部分修改" chapters/ch5/5-Tools.v1_polished_unified_expanded.tex

# 只提交想接受的修改
git add chapters/ch5/5-Tools.v1_polished_unified_expanded.tex
git commit -m "提交部分修改"

# 恢复被stash的修改
git stash pop
```

## 高级技巧

### 使用Git的stage/unstage循环
```bash
# 1. 将所有修改添加到暂存区
git add chapters/ch5/5-Tools.v1_polished_unified_expanded.tex

# 2. 查看暂存的修改
git diff --cached chapters/ch5/5-Tools.v1_polished_unified_expanded.tex

# 3. 如果有不想提交的修改，将其移出暂存区
git reset -p chapters/ch5/5-Tools.v1_polished_unified_expanded.tex
# 用 'n' 拒绝不想提交的修改

# 4. 提交暂存区中的修改
git commit -m "提交选定的修改"
```

### 创建多个提交对应不同的修改
```bash
# 提交1：标题修改
git add -p chapters/ch5/5-Tools.v1_polished_unified_expanded.tex
# 只选择标题相关的修改
git commit -m "整合导数与梯度小节标题"

# 提交2：内容优化
git add -p chapters/ch5/5-Tools.v1_polished_unified_expanded.tex
# 选择内容优化相关的修改
git commit -m "优化列表标题格式和内容结构"
```

## 推荐工作流程

### 对于你的当前项目：
1. **第一步**：`git add -p chapters/ch5/5-Tools.v1_polished_unified_expanded.tex`
2. **第二步**：逐个审查修改块，使用 `s` 拆分复杂的修改
3. **第三步**：接受你想要的修改，拒绝不想要的
4. **第四步**：`git commit -m "描述接受的修改"`
5. **第五步**：对剩余修改重复上述过程

这样你就能完全控制每个修改的去留，实现真正的"单行修改管理"。