# LaTeX 修订跟踪实用指南

## 方法1：使用 changes 包（已配置）

### 1. 基本命令

#### 显示/隐藏修订
```latex
% 在导言区修改：
\usepackage[draft]{changes}  % 显示所有修订
\usepackage[final]{changes}  % 隐藏所有修订（当前设置）
```

#### 修订命令
```latex
% 添加内容
\added[id=作者,comment=说明]{新增文本}

% 删除内容
\deleted[id=作者,comment=说明]{删除的文本}

% 替换内容
\replaced[id=作者,comment=说明]{新文本}{旧文本}

% 添加注释
\note[id=作者,comment=这是注释]{注释文本}
```

### 2. 实际使用示例

#### 标记我们的刚才修改
```latex
% 原文：
\subsection{导数与梯度}

% 修改后：
\added[id=claude,comment=整合两个小节]{\subsection{导数与梯度：从基础概念到几何视角}}

% 删除重复内容
\deleted[id=claude,comment=删除重复的小节标题]
{\subsection{导数与梯度的几何视角}}

% 优化列表标题
\replaced[id=claude,comment=加粗标题]{\textbf{梯度的几何意义}：}{梯度的几何意义：}
```

### 3. 接受/拒绝修订的方法

#### 方法A：批量处理
```latex
% 接受所有修订
\acceptAllChanges

% 拒绝所有修订
\rejectAllChanges
```

#### 方法B：手动逐个处理
```latex
% 接受特定修订：将修订命令替换为正式内容
\accept{正式内容}

% 拒绝修订：删除修订命令
\reject{}  % 内容完全消失
```

#### 方法C：最终清理
1. 将 `\usepackage[draft]{changes}` 改为 `\usepackage[final]{changes}`
2. 逐个检查修订，手动决定保留还是删除
3. 清理所有修订标记

## 方法2：简单注释法

### 1. 使用颜色和注释
```latex
\usepackage{xcolor}
\usepackage{soul}

% 定义修订命令
\newcommand{\newtext}[1]{\textcolor{green}{#1}}
\newcommand{\deltext}[1]{\textcolor{red}{\sout{#1}}}
\newcommand{\revtext}[2]{\deltext{#2} \newtext{#1}}
```

### 2. 使用
```latex
% 新增内容
\newtext{这是新增的内容}

% 删除内容
\deltext{这是要删除的内容}

% 替换内容
\revtext{新内容}{旧内容}
```

## 方法3：Git + 手动标记

### 1. Git工作流
```bash
# 查看修改
git diff

# 创建修订分支
git checkout -b revision-chapter5

# 提交修订
git add .
git commit -m "第五章修订：导数与梯度部分"

# 合并修订
git checkout main
git merge revision-chapter5
```

### 2. 在文档中使用注释
```latex
% REV: 2024-12-06 整合导数与梯度小节
% TODO: 需要检查数学公式的准确性
% FIXME: 这里需要添加例子
```

## 推荐工作流程

### 阶段1：标记修订
1. 使用 `\usepackage[draft]{changes}` 显示修订
2. 用 `\added`、`\deleted`、`\replaced` 标记所有修改
3. 添加清晰的注释说明修改原因

### 阶段2：审阅修订
1. 编译文档查看修订效果
2. 逐个检查每个修订的合理性
3. 决定接受或拒绝每个修订

### 阶段3：最终化
1. 将 `\usepackage[draft]{changes}` 改为 `\usepackage[final]{changes}`
2. 手动清理接受的修订（移除修订标记）
3. 删除拒绝的修订
4. 最终编译检查

## 当前状态

你的文档已经配置了 changes 包，当前设置为 `final` 模式（隐藏修订）。

要开始使用修订跟踪：

1. 将第53行改为：`\usepackage[draft]{changes}`
2. 开始使用修订命令标记修改
3. 完成后再改回 `final` 模式