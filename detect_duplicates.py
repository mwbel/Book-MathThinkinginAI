#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测LaTeX文档中重复段落的工具
包括被注释掉的内容
"""

import re
import sys
from collections import defaultdict

def normalize_text(text):
    """标准化文本，去除空白字符和格式差异"""
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 移除首尾空白
    text = text.strip()
    return text

def extract_paragraphs(content):
    """提取段落和注释内容"""
    paragraphs = []
    
    # 分割内容
    lines = content.split('\n')
    current_paragraph = []
    in_comment = False
    
    for line in lines:
        stripped = line.strip()
        
        # 检查是否是注释行
        if stripped.startswith('%'):
            # 处理注释内容
            comment_content = stripped[1:].strip()
            if comment_content:
                paragraphs.append({
                    'text': normalize_text(comment_content),
                    'original': line,
                    'type': 'comment',
                    'line_num': len(paragraphs) + 1
                })
        elif stripped:
            # 处理普通文本段落
            current_paragraph.append(stripped)
        elif current_paragraph:
            # 段落结束
            paragraph_text = ' '.join(current_paragraph)
            paragraphs.append({
                'text': normalize_text(paragraph_text),
                'original': '\n'.join(current_paragraph),
                'type': 'paragraph',
                'line_num': len(paragraphs) + 1
            })
            current_paragraph = []
    
    # 处理最后一个段落
    if current_paragraph:
        paragraph_text = ' '.join(current_paragraph)
        paragraphs.append({
            'text': normalize_text(paragraph_text),
            'original': '\n'.join(current_paragraph),
            'type': 'paragraph',
            'line_num': len(paragraphs) + 1
        })
    
    return paragraphs

def find_duplicates(paragraphs, min_length=20):
    """查找重复段落"""
    text_to_paragraphs = defaultdict(list)
    duplicates = []
    
    for i, para in enumerate(paragraphs):
        text = para['text']
        
        # 只检查长度足够的段落
        if len(text) >= min_length:
            text_to_paragraphs[text].append(i)
    
    # 找出有重复的文本
    for text, indices in text_to_paragraphs.items():
        if len(indices) > 1:
            duplicates.append({
                'text': text,
                'count': len(indices),
                'indices': indices,
                'type': paragraphs[indices[0]]['type']
            })
    
    return duplicates

def main():
    if len(sys.argv) != 2:
        print("用法: python detect_duplicates.py <文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        sys.exit(1)
    
    print(f"正在分析文件: {file_path}")
    print("=" * 60)
    
    # 提取段落
    paragraphs = extract_paragraphs(content)
    print(f"总共找到 {len(paragraphs)} 个段落和注释")
    
    # 查找重复
    duplicates = find_duplicates(paragraphs, min_length=15)
    
    print(f"\n找到 {len(duplicates)} 组重复内容:\n")
    
    for i, dup in enumerate(duplicates, 1):
        print(f"重复组 {i}:")
        print(f"  重复次数: {dup['count']}")
        print(f"  内容类型: {dup['type']}")
        print(f"  重复文本: {dup['text'][:100]}{'...' if len(dup['text']) > 100 else ''}")
        print(f"  出现位置: {dup['indices']}")
        print()
        
        # 显示原始内容
        for idx in dup['indices']:
            para = paragraphs[idx]
            print(f"    位置 {idx} ({para['type']}):")
            print(f"    {para['original']}")
            print()
        
        print("-" * 60)
    
    if not duplicates:
        print("未发现重复段落。")
    else:
        print(f"\n总结:")
        print(f"- 发现 {len(duplicates)} 组重复内容")
        total_redundant = sum(dup['count'] - 1 for dup in duplicates)
        print(f"- 总共 {total_redundant} 个重复实例")
        print("- 建议检查并删除重复内容以提高文档质量")

if __name__ == "__main__":
    main()
