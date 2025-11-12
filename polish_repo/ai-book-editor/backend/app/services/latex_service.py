"""
LaTeX文档处理服务
"""
import os
import re
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import difflib
from collections import defaultdict

from app.schemas.latex import (
    LaTeXSection, OptimizationSuggestion, AnalysisResult,
    DuplicateContent, LogicIssue, Statistics, Location, Impact,
    SectionType, Priority, SuggestionType
)

class LaTeXService:
    """LaTeX文档处理服务"""
    
    def __init__(self):
        self.section_cache = {}
        self.analysis_cache = {}
    
    def detect_main_file(self, directory_path: str) -> Optional[str]:
        """检测主LaTeX文件"""
        tex_files = []
        for file in os.listdir(directory_path):
            if file.endswith('.tex'):
                file_path = os.path.join(directory_path, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # 检查是否包含文档类定义
                    if r'\documentclass' in content:
                        tex_files.append((file, content.count(r'\include'), content.count(r'\input')))
        
        if not tex_files:
            return None
        
        # 选择包含最多include/input的文件作为主文件
        main_file = max(tex_files, key=lambda x: x[1] + x[2])
        return main_file[0]
    
    async def analyze_project(self, directory_path: str, main_file: str) -> Dict[str, Any]:
        """分析LaTeX项目"""
        try:
            # 解析文档结构
            sections = await self._parse_document_structure(directory_path, main_file)
            
            # 内容分析
            analysis = await self._analyze_content(sections, directory_path)
            
            return {
                "sections": sections,
                "analysis": analysis
            }
        except Exception as e:
            raise Exception(f"项目分析失败: {str(e)}")
    
    async def _parse_document_structure(self, directory_path: str, main_file: str) -> List[Dict[str, Any]]:
        """解析文档结构"""
        main_file_path = os.path.join(directory_path, main_file)
        
        if not os.path.exists(main_file_path):
            raise FileNotFoundError(f"主文件不存在: {main_file}")
        
        sections = []
        
        # 读取主文件
        with open(main_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            main_content = f.read()
        
        # 查找包含的文件
        include_pattern = r'\\(?:include|input)\{([^}]+)\}'
        includes = re.findall(include_pattern, main_content)
        
        section_id = 1
        
        for include_file in includes:
            # 添加.tex扩展名（如果没有）
            if not include_file.endswith('.tex'):
                include_file += '.tex'
            
            include_path = os.path.join(directory_path, include_file)
            
            if os.path.exists(include_path):
                section_data = await self._parse_section_file(include_path, include_file, section_id)
                if section_data:
                    sections.append(section_data)
                    section_id += 1
        
        # 如果没有找到包含文件，直接解析主文件
        if not sections:
            section_data = await self._parse_section_file(main_file_path, main_file, 1)
            if section_data:
                sections.append(section_data)
        
        return sections
    
    async def _parse_section_file(self, file_path: str, filename: str, section_id: int) -> Optional[Dict[str, Any]]:
        """解析单个章节文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 提取章节标题
            title_patterns = [
                r'\\chapter\{([^}]+)\}',
                r'\\section\{([^}]+)\}',
                r'\\subsection\{([^}]+)\}',
                r'\\part\{([^}]+)\}'
            ]
            
            title = f"章节 {section_id}"
            section_type = SectionType.SECTION
            
            for pattern in title_patterns:
                match = re.search(pattern, content)
                if match:
                    title = match.group(1)
                    if 'chapter' in pattern:
                        section_type = SectionType.CHAPTER
                    elif 'section' in pattern:
                        section_type = SectionType.SECTION
                    elif 'subsection' in pattern:
                        section_type = SectionType.SUBSECTION
                    break
            
            # 清理内容（移除LaTeX命令）
            clean_content = self._clean_latex_content(content)
            
            return {
                "id": f"section-{section_id}",
                "type": section_type,
                "title": title,
                "content": clean_content,
                "file": filename
            }
        
        except Exception as e:
            print(f"解析文件失败 {file_path}: {str(e)}")
            return None
    
    def _clean_latex_content(self, content: str) -> str:
        """清理LaTeX内容，移除命令保留文本"""
        # 移除注释
        content = re.sub(r'%.*$', '', content, flags=re.MULTILINE)
        
        # 移除常见的LaTeX命令
        commands_to_remove = [
            r'\\documentclass\{[^}]*\}',
            r'\\usepackage(?:\[[^\]]*\])?\{[^}]*\}',
            r'\\begin\{document\}',
            r'\\end\{document\}',
            r'\\maketitle',
            r'\\tableofcontents',
            r'\\newpage',
            r'\\clearpage',
            r'\\pagebreak',
            r'\\\\',  # 换行
            r'\\label\{[^}]*\}',
            r'\\ref\{[^}]*\}',
            r'\\cite\{[^}]*\}',
        ]
        
        for cmd in commands_to_remove:
            content = re.sub(cmd, '', content)
        
        # 处理环境
        content = re.sub(r'\\begin\{[^}]*\}', '', content)
        content = re.sub(r'\\end\{[^}]*\}', '', content)
        
        # 移除其他命令但保留内容
        content = re.sub(r'\\[a-zA-Z]+\*?\{([^}]*)\}', r'\1', content)
        content = re.sub(r'\\[a-zA-Z]+\*?', '', content)
        
        # 清理多余的空白
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = content.strip()
        
        return content
    
    async def _analyze_content(self, sections: List[Dict[str, Any]], directory_path: str) -> Dict[str, Any]:
        """分析内容"""
        # 检测重复内容
        duplicates = await self._detect_duplicates(sections)
        
        # 分析逻辑问题
        logic_issues = await self._analyze_logic_issues(sections)
        
        # 生成统计信息
        statistics = await self._generate_statistics(sections)
        
        # 生成优化建议
        suggestions = await self._generate_suggestions(sections, duplicates, logic_issues)
        
        return {
            "duplicates": duplicates,
            "logic_issues": logic_issues,
            "statistics": statistics,
            "suggestions": suggestions
        }
    
    async def _detect_duplicates(self, sections: List[Dict[str, Any]], threshold: float = 0.8) -> List[Dict[str, Any]]:
        """检测重复内容"""
        duplicates = []
        duplicate_id = 1
        
        for i, section1 in enumerate(sections):
            for j, section2 in enumerate(sections[i+1:], i+1):
                # 分段比较
                paragraphs1 = self._split_paragraphs(section1["content"])
                paragraphs2 = self._split_paragraphs(section2["content"])
                
                for p1_idx, p1 in enumerate(paragraphs1):
                    for p2_idx, p2 in enumerate(paragraphs2):
                        if len(p1) > 50 and len(p2) > 50:  # 只比较较长的段落
                            similarity = self._calculate_similarity(p1, p2)
                            if similarity >= threshold:
                                duplicates.append({
                                    "id": f"dup-{duplicate_id}",
                                    "similarity": similarity,
                                    "text1": p1[:200] + "..." if len(p1) > 200 else p1,
                                    "text2": p2[:200] + "..." if len(p2) > 200 else p2,
                                    "locations": [
                                        {
                                            "section_id": section1["id"],
                                            "section_title": section1["title"],
                                            "file": section1["file"],
                                            "paragraph": p1_idx + 1
                                        },
                                        {
                                            "section_id": section2["id"],
                                            "section_title": section2["title"],
                                            "file": section2["file"],
                                            "paragraph": p2_idx + 1
                                        }
                                    ]
                                })
                                duplicate_id += 1
        
        return duplicates
    
    def _split_paragraphs(self, content: str) -> List[str]:
        """分割段落"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        return paragraphs
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        # 使用difflib计算相似度
        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
        return similarity
    
    async def _analyze_logic_issues(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析逻辑问题"""
        logic_issues = []
        issue_id = 1
        
        for section in sections:
            paragraphs = self._split_paragraphs(section["content"])
            
            # 检查段落间的逻辑连接
            for i in range(len(paragraphs) - 1):
                current_para = paragraphs[i]
                next_para = paragraphs[i + 1]
                
                # 简单的逻辑跳跃检测
                if self._has_logic_jump(current_para, next_para):
                    logic_issues.append({
                        "id": f"logic-{issue_id}",
                        "type": "logic_jump",
                        "severity": "medium",
                        "description": "段落间存在逻辑跳跃，缺少过渡",
                        "location": {
                            "section_id": section["id"],
                            "section_title": section["title"],
                            "file": section["file"],
                            "paragraph": i + 1
                        }
                    })
                    issue_id += 1
        
        return logic_issues
    
    def _has_logic_jump(self, para1: str, para2: str) -> bool:
        """检测是否存在逻辑跳跃"""
        # 简单的启发式规则
        transition_words = ['因此', '所以', '然而', '但是', '另外', '此外', '同时', '接下来', '首先', '其次', '最后']
        
        # 如果第二段没有过渡词且主题差异较大，可能存在逻辑跳跃
        has_transition = any(word in para2[:50] for word in transition_words)
        
        if not has_transition and len(para1) > 100 and len(para2) > 100:
            # 简单的主题相似度检测
            similarity = self._calculate_similarity(para1[:100], para2[:100])
            if similarity < 0.3:
                return True
        
        return False
    
    async def _generate_statistics(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成统计信息"""
        total_sections = len(sections)
        total_paragraphs = 0
        total_words = 0
        
        for section in sections:
            paragraphs = self._split_paragraphs(section["content"])
            total_paragraphs += len(paragraphs)
            total_words += len(section["content"].split())
        
        average_section_length = total_words / total_sections if total_sections > 0 else 0
        
        # 简单的重复率计算
        duplicate_rate = 0.12  # 模拟值
        
        return {
            "total_sections": total_sections,
            "total_paragraphs": total_paragraphs,
            "total_words": total_words,
            "duplicate_rate": duplicate_rate,
            "average_section_length": average_section_length
        }
    
    async def _generate_suggestions(self, sections: List[Dict[str, Any]], duplicates: List[Dict[str, Any]], logic_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        suggestions = []
        suggestion_id = 1
        
        # 基于重复内容的建议
        for duplicate in duplicates:
            suggestions.append({
                "id": f"sugg-{suggestion_id}",
                "type": SuggestionType.REMOVE_DUPLICATE,
                "priority": Priority.HIGH,
                "title": "删除重复内容",
                "description": f"发现相似度为{duplicate['similarity']:.0%}的重复内容，建议删除或合并",
                "original_text": duplicate["text2"],
                "suggested_text": "",
                "location": duplicate["locations"][1],  # 建议删除第二个位置的内容
                "impact": {
                    "words_removed": len(duplicate["text2"].split()),
                    "readability_improvement": 0.8,
                    "logic_improvement": 0.6
                }
            })
            suggestion_id += 1
        
        # 基于逻辑问题的建议
        for issue in logic_issues:
            suggestions.append({
                "id": f"sugg-{suggestion_id}",
                "type": SuggestionType.ADD_TRANSITION,
                "priority": Priority.MEDIUM,
                "title": "添加过渡句",
                "description": "段落间缺少逻辑连接，建议添加过渡句",
                "original_text": "（段落开始）",
                "suggested_text": "基于以上分析，（段落开始）",
                "location": issue["location"],
                "impact": {
                    "words_removed": 0,
                    "readability_improvement": 0.6,
                    "logic_improvement": 0.9
                }
            })
            suggestion_id += 1
        
        return suggestions
    
    async def get_section_content(self, section_id: str) -> str:
        """获取章节内容"""
        # 这里应该从缓存或数据库中获取
        return f"章节 {section_id} 的详细内容..."
    
    async def apply_suggestion(self, suggestion_id: str, file_path: str, original_text: str, suggested_text: str) -> Dict[str, Any]:
        """应用优化建议"""
        try:
            # 模拟应用建议
            await asyncio.sleep(0.5)  # 模拟处理时间
            
            return {
                "success": True,
                "message": "优化建议已成功应用",
                "updated_content": f"已将 '{original_text[:50]}...' 替换为 '{suggested_text[:50]}...'"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"应用建议失败: {str(e)}"
            }
    
    async def detect_duplicates(self, project_path: str, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """检测重复内容"""
        # 重新分析项目
        main_file = self.detect_main_file(project_path)
        if not main_file:
            return []
        
        sections = await self._parse_document_structure(project_path, main_file)
        return await self._detect_duplicates(sections, threshold)
    
    async def analyze_logic_flow(self, project_path: str) -> List[Dict[str, Any]]:
        """分析逻辑流程"""
        main_file = self.detect_main_file(project_path)
        if not main_file:
            return []
        
        sections = await self._parse_document_structure(project_path, main_file)
        return await self._analyze_logic_issues(sections)
    
    async def get_project_statistics(self, project_path: str) -> Dict[str, Any]:
        """获取项目统计信息"""
        main_file = self.detect_main_file(project_path)
        if not main_file:
            return {}
        
        sections = await self._parse_document_structure(project_path, main_file)
        return await self._generate_statistics(sections)
    
    async def export_optimized_project(self, project_path: str, output_path: str) -> Dict[str, Any]:
        """导出优化后的项目"""
        try:
            # 模拟导出过程
            await asyncio.sleep(1.0)
            
            return {
                "output_path": output_path,
                "files_exported": ["main.tex", "chapter1.tex", "chapter2.tex"]
            }
        except Exception as e:
            raise Exception(f"导出失败: {str(e)}")