#!/bin/bash
cd "/Users/Min369/Desktop/书/书稿打磨"
# 从剪贴板获取文本
TEXT=$(pbpaste)
echo "正在润色文本："
echo "$TEXT"
python3 quick_edit.py polish --text "$TEXT" --style lecture