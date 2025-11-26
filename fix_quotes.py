#!/usr/bin/env python3
import os

# 处理特定的顽固文件
file_path = "/Users/Min369/Desktop/书/书稿打磨/draft-tex/chapters/9-AI的边界：图灵机、哥德尔与计算的极限.v3.tex"

with open(file_path, 'rb') as f:
    content = f.read()

# 将字节内容转换为字符串
content_str = content.decode('utf-8')

# 计算替换前的ASCII引号数量
ascii_quote_count = content_str.count(chr(34))
print(f"发现 {ascii_quote_count} 个ASCII直引号")

# 替换ASCII直引号为中文全角引号
content_str = content_str.replace(chr(34), '"')

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content_str)

print(f"已处理文件: {file_path}")

# 验证替换结果
with open(file_path, 'r', encoding='utf-8') as f:
    new_content = f.read()

remaining_quotes = new_content.count(chr(34))
print(f"剩余ASCII直引号: {remaining_quotes}")

if remaining_quotes == 0:
    print("✅ 所有ASCII直引号已成功替换！")
else:
    print("❌ 仍有ASCII直引号未替换")