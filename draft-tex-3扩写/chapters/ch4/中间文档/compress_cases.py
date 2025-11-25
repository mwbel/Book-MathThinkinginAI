#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def compress_case_studies(file_path):
    """Compress the verbose case studies into concise versions."""

    # Read the file with UTF-8 encoding
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the start and end of the verbose content
    start_marker = "智能手机物体识别展现了三种思维的紧密协同"
    end_marker = r"\paragraph{案例二：大语言模型：语言智能的三层思维架构}"

    # Find the start position (after the concise case 1)
    start_pos = content.find(start_marker)
    if start_pos == -1:
        print("Could not find start marker")
        return False

    # Find the end of the first concise paragraph
    first_paragraph_end = content.find("等方面的平衡。", start_pos)
    if first_paragraph_end == -1:
        print("Could not find end of first paragraph")
        return False

    # Find the start of case 2
    case2_start = content.find("\\paragraph{案例二：大语言模型：语言智能的三层思维架构}")
    if case2_start == -1:
        print("Could not find case 2 start")
        return False

    # Content to keep: from start to end of first paragraph
    content_to_keep = content[:first_paragraph_end + 7]  # +7 to include "等方面的平衡。"

    # Add the new concise case 2
    new_case2 = """

\\paragraph{案例二：大语言模型}
大语言模型的成功体现了三种思维在大规模系统中的融合：\\textbf{数学思维}建立Transformer的数学基础，注意力机制$\\text{Attention}(Q,K,V) = \\text{softmax}(\\frac{QK^T}{\\sqrt{d_k}})V$体现了信息融合原理，概率建模为语言生成提供理论支撑；\\textbf{算法思维}实现自注意力的并行计算，设计梯度累积、混合精度训练等优化策略，创新预训练-微调范式；\\textbf{工程思维}通过分布式训练、模型量化、知识蒸馏等技术解决千亿参数模型的训练和服务挑战，确保系统的可扩展性和实际可用性。

\\paragraph{案例三：自动驾驶系统}
自动驾驶作为安全关键系统，更需要三种思维的深度整合：\\textbf{数学思维}运用贝叶斯推理融合多传感器信息，基于控制论设计车辆控制算法，利用博弈论处理多车交互场景；\\textbf{算法思维}开发SLAM、路径规划、目标检测等核心算法，在有限车载平台上实现实时感知与决策；\\textbf{工程思维}采用冗余设计、实时系统、安全验证等保障系统可靠性，通过分层解耦、容错机制等确保在复杂环境中的安全运行。三种思维共同构成了自动驾驶安全、高效、可靠的技术基础。

"""

    # Find the end of case 2 (look for the end of the verbose section)
    case2_end = content.find("工程思维层面：大规模系统的工程实现", case2_start)
    if case2_end == -1:
        print("Could not find case 2 end")
        return False

    # Find the end of the entire verbose section (before case 3)
    verbose_section_end = content.find("%\\paragraph{案例三：自动驾驶", case2_end)
    if verbose_section_end == -1:
        print("Could not find verbose section end")
        return False

    # Find the end of the entire commented section
    end_of_comments = content.find("功能安全标准（如ISO 26262）为系统设计提供了安全性指导。", verbose_section_end)
    if end_of_comments == -1:
        print("Could not find end of comments")
        return False

    # Get the rest of the content after the verbose section
    rest_of_content = content[end_of_comments + len("功能安全标准（如ISO 26262）为系统设计提供了安全性指导。"):]

    # Combine everything
    new_content = content_to_keep + new_case2 + rest_of_content

    # Write the result back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("Successfully compressed case studies!")
    return True

if __name__ == "__main__":
    file_path = "/Users/Min369/Desktop/书/书稿打磨/draft-tex-3扩写/chapters/ch4/4-Thinking.v1_polished_unified_expanded.tex"
    success = compress_case_studies(file_path)

    if success:
        print("✅ Case studies successfully compressed!")
    else:
        print("❌ Failed to compress case studies.")