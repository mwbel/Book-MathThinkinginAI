"""
LaTeX处理相关的数据模式
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class SectionType(str, Enum):
    """章节类型"""
    CHAPTER = "chapter"
    SECTION = "section"
    SUBSECTION = "subsection"
    SUBSUBSECTION = "subsubsection"

class Priority(str, Enum):
    """优先级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SuggestionType(str, Enum):
    """建议类型"""
    REMOVE_DUPLICATE = "remove_duplicate"
    ADD_TRANSITION = "add_transition"
    IMPROVE_FLOW = "improve_flow"
    REDUCE_REDUNDANCY = "reduce_redundancy"
    FIX_LOGIC = "fix_logic"

class LaTeXSection(BaseModel):
    """LaTeX章节"""
    id: str = Field(..., description="章节ID")
    type: SectionType = Field(..., description="章节类型")
    title: str = Field(..., description="章节标题")
    content: str = Field(..., description="章节内容")
    file: str = Field(..., description="文件名")
    children: Optional[List['LaTeXSection']] = Field(default=None, description="子章节")
    
    class Config:
        use_enum_values = True

class Location(BaseModel):
    """位置信息"""
    section_id: str = Field(..., description="章节ID")
    section_title: str = Field(..., description="章节标题")
    file: str = Field(..., description="文件名")
    paragraph: Optional[int] = Field(default=None, description="段落号")
    line: Optional[int] = Field(default=None, description="行号")

class Impact(BaseModel):
    """影响评估"""
    words_removed: int = Field(default=0, description="删除的字数")
    readability_improvement: float = Field(default=0.0, description="可读性改进度")
    logic_improvement: float = Field(default=0.0, description="逻辑改进度")

class OptimizationSuggestion(BaseModel):
    """优化建议"""
    id: str = Field(..., description="建议ID")
    type: SuggestionType = Field(..., description="建议类型")
    priority: Priority = Field(..., description="优先级")
    title: str = Field(..., description="建议标题")
    description: str = Field(..., description="建议描述")
    original_text: str = Field(..., description="原始文本")
    suggested_text: str = Field(..., description="建议文本")
    location: Location = Field(..., description="位置信息")
    impact: Impact = Field(..., description="影响评估")
    
    class Config:
        use_enum_values = True

class DuplicateContent(BaseModel):
    """重复内容"""
    id: str = Field(..., description="重复内容ID")
    similarity: float = Field(..., description="相似度")
    text1: str = Field(..., description="文本1")
    text2: str = Field(..., description="文本2")
    locations: List[Location] = Field(..., description="位置列表")

class LogicIssue(BaseModel):
    """逻辑问题"""
    id: str = Field(..., description="问题ID")
    type: str = Field(..., description="问题类型")
    severity: str = Field(..., description="严重程度")
    description: str = Field(..., description="问题描述")
    location: Location = Field(..., description="位置信息")

class Statistics(BaseModel):
    """统计信息"""
    total_sections: int = Field(..., description="总章节数")
    total_paragraphs: int = Field(..., description="总段落数")
    total_words: int = Field(..., description="总字数")
    duplicate_rate: float = Field(..., description="重复率")
    average_section_length: float = Field(..., description="平均章节长度")

class AnalysisResult(BaseModel):
    """分析结果"""
    duplicates: List[DuplicateContent] = Field(..., description="重复内容列表")
    logic_issues: List[LogicIssue] = Field(..., description="逻辑问题列表")
    statistics: Statistics = Field(..., description="统计信息")
    suggestions: List[OptimizationSuggestion] = Field(..., description="优化建议列表")

class ProjectAnalysisResponse(BaseModel):
    """项目分析响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    sections: List[LaTeXSection] = Field(..., description="章节列表")
    analysis: AnalysisResult = Field(..., description="分析结果")

class SuggestionApplicationRequest(BaseModel):
    """应用建议请求"""
    suggestion_id: str = Field(..., description="建议ID")
    file_path: str = Field(..., description="文件路径")
    original_text: str = Field(..., description="原始文本")
    suggested_text: str = Field(..., description="建议文本")

class SuggestionApplicationResponse(BaseModel):
    """应用建议响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    updated_content: Optional[str] = Field(default=None, description="更新后的内容")

class FileUploadRequest(BaseModel):
    """文件上传请求"""
    main_file: Optional[str] = Field(default=None, description="主文件名")

class DirectoryAnalysisRequest(BaseModel):
    """目录分析请求"""
    directory_path: str = Field(..., description="目录路径")

class ExportRequest(BaseModel):
    """导出请求"""
    project_path: str = Field(..., description="项目路径")
    output_path: str = Field(..., description="输出路径")
    include_suggestions: bool = Field(default=True, description="是否包含建议")

# 更新前向引用
LaTeXSection.model_rebuild()