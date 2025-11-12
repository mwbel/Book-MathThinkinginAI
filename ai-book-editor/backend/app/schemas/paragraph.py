from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ParagraphType(str, Enum):
    """段落类型枚举"""
    TEXT = "TEXT"           # 普通文本段落
    TITLE = "TITLE"         # 标题段落
    EQUATION = "EQUATION"   # 公式段落
    FIGURE = "FIGURE"       # 图片段落
    TABLE = "TABLE"         # 表格段落
    LIST = "LIST"           # 列表段落
    CODE = "CODE"           # 代码段落
    QUOTE = "QUOTE"         # 引用段落
    FOOTNOTE = "FOOTNOTE"   # 脚注段落


class ParagraphBase(BaseModel):
    """段落基础模型"""
    paragraph_type: ParagraphType = Field(..., description="段落类型")
    order_index: int = Field(..., ge=0, description="段落在章节中的顺序")


class ParagraphCreate(ParagraphBase):
    """创建段落模型"""
    chapter_id: int = Field(..., description="所属章节ID")
    raw_content: str = Field(..., description="原始内容")
    processed_content: Optional[str] = Field(None, description="处理后内容")


class ParagraphUpdate(BaseModel):
    """更新段落模型"""
    paragraph_type: Optional[ParagraphType] = Field(None, description="段落类型")
    order_index: Optional[int] = Field(None, ge=0, description="段落顺序")
    processed_content: Optional[str] = Field(None, description="处理后内容")
    readability_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="可读性评分")


class ParagraphInDBBase(ParagraphBase):
    """数据库中的段落基础模型"""
    id: int
    chapter_id: int
    word_count: int = Field(default=0, description="字数统计")
    char_count: int = Field(default=0, description="字符数统计")
    readability_score: Optional[float] = Field(None, description="可读性评分")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Paragraph(ParagraphInDBBase):
    """段落响应模型"""
    pass


class ParagraphWithContent(Paragraph):
    """包含内容的段落模型"""
    content: Optional[str] = Field(None, description="段落内容")


class ParagraphInDB(ParagraphInDBBase):
    """数据库中的完整段落模型"""
    raw_content: str = Field(..., description="原始内容")
    processed_content: Optional[str] = Field(None, description="处理后内容")


class ParagraphStats(BaseModel):
    """段落统计信息"""
    paragraph_id: int
    paragraph_type: ParagraphType
    word_count: int
    char_count: int
    readability_score: Optional[float]
    created_at: datetime
    updated_at: datetime


class ParagraphAnalysis(BaseModel):
    """段落分析结果"""
    paragraph_id: int
    paragraph_type: ParagraphType
    word_count: int
    char_count: int
    readability_score: Optional[float]
    issues: List[str] = Field(default_factory=list, description="发现的问题")
    suggestions: List[str] = Field(default_factory=list, description="改进建议")


class ParagraphBatch(BaseModel):
    """批量段落操作"""
    paragraph_ids: List[int] = Field(..., description="段落ID列表")
    operation: str = Field(..., description="操作类型")
    parameters: Optional[dict] = Field(None, description="操作参数")