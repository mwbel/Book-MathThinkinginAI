# 解决 \textbf{} 加粗文字高度不一致问题

## 问题原因

`\textbf{}` 加粗后的文字比未加粗文字更高，主要原因包括：

1. **字体度量差异**：加粗字体（如 `FZHei-B01` 方正黑体）与正文字体（如 `FZShuSong-Z01` 方正书宋）的字形设计不同，ascender（上升部分）高度可能不同。

2. **行高计算**：LaTeX 的行高（`\baselinestretch=1.2`）基于正文字体计算，没有考虑加粗字体的实际高度。

3. **字体设计差异**：黑体与书宋的字形高度在设计上可能略有不同。

## 解决方案

### ✅ 方案0：全局重定义 `\textbf`（已实施，推荐）

**已在 `AImath.v6.tex` 中实施**，无需修改任何现有代码！

在主文档的导言区添加：

```latex
% --- 修复 \textbf{} 加粗文字高度不一致问题 ---
% 重新定义 \textbf 命令，自动添加 \strut 以统一行高
\let\oldtextbf\textbf
\renewcommand{\textbf}[1]{\strut\oldtextbf{#1}\strut}
```

**优点**：
- ✅ 无需修改任何现有代码
- ✅ 全局生效，所有 `\textbf{}` 自动统一行高
- ✅ 保持代码风格一致

### 方案1：使用 `\strut` 统一行高（手动方式）

在加粗文字前后添加 `\strut`，确保行高一致：

```latex
\strut\textbf{数学思维}\strut 奠定理论基础
```

或者创建一个便捷命令：

```latex
\newcommand{\bftext}[1]{\strut\textbf{#1}\strut}
```

使用方式：
```latex
\bftext{数学思维} 奠定理论基础
```

### 方案2：调整行间距（全局方案）

在文档导言区添加：

```latex
% 确保加粗文字不影响行高
\setlength{\lineskip}{0pt}
\setlength{\lineskiplimit}{0pt}
```

### 方案3：使用 `\smash` 命令（不推荐，可能影响可读性）

```latex
\smash{\textbf{数学思维}} 奠定理论基础
```

注意：这会消除加粗文字的垂直空间，可能导致文字重叠。

### 方案4：自定义加粗命令（最佳实践）

在 `elegantbook.cls` 或文档导言区添加：

```latex
% 统一高度的加粗命令
\newcommand{\bftext}[1]{%
  \begingroup
  \setlength{\lineskip}{0pt}%
  \textbf{#1}%
  \endgroup
}
```

或者更完善的版本：

```latex
% 带行高控制的加粗命令
\newcommand{\bftext}[1]{%
  \strut\textbf{#1}\strut
}
```

### 方案5：检查字体配置（根本解决）

如果问题严重，可以考虑：

1. **统一字体族**：确保加粗和常规字体来自同一字体族，度量更一致。

2. **调整字体配置**：在 `elegantbook.cls` 中，可以尝试：

```latex
\setCJKmainfont[
  BoldFont={FZHei-B01},
  BoldFontFeatures={SizeFeatures={Size={-},VerticalMetrics={*}}}
]{FZShuSong-Z01}
```

## 推荐做法

**建议使用方案1或方案4**，创建一个统一的加粗命令：

```latex
\newcommand{\bftext}[1]{\strut\textbf{#1}\strut}
```

然后在文档中统一使用 `\bftext{}` 替代 `\textbf{}`，这样可以：
- 保持行高一致
- 代码更清晰
- 便于后续统一调整

## 批量替换

如果需要批量替换文档中的 `\textbf{}` 为 `\bftext{}`，可以使用：

```bash
# 在项目根目录执行
find . -name "*.tex" -type f -exec sed -i '' 's/\\textbf{\([^}]*\)}/\\bftext{\1}/g' {} \;
```

注意：执行前请备份文件！
