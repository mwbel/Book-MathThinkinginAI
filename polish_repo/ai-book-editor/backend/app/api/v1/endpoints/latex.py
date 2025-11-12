"""
LaTeX文档处理API端点
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
import os
import tempfile
import shutil
from pathlib import Path

from app.services.latex_service import LaTeXService
from app.schemas.latex import (
    LaTeXSection,
    OptimizationSuggestion,
    AnalysisResult,
    ProjectAnalysisResponse,
    SuggestionApplicationRequest,
    SuggestionApplicationResponse
)

router = APIRouter()
latex_service = LaTeXService()

@router.post("/upload", response_model=ProjectAnalysisResponse)
async def upload_latex_project(
    files: List[UploadFile] = File(...),
    main_file: Optional[str] = None
):
    """
    上传LaTeX项目文件并进行分析
    """
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        # 保存上传的文件
        uploaded_files = []
        for file in files:
            if not file.filename.endswith(('.tex', '.bib')):
                continue
                
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, 'wb') as f:
                content = await file.read()
                f.write(content)
            uploaded_files.append(file.filename)
        
        if not uploaded_files:
            raise HTTPException(status_code=400, detail="没有找到有效的LaTeX文件")
        
        # 如果没有指定主文件，尝试自动检测
        if not main_file:
            main_file = latex_service.detect_main_file(temp_dir)
        
        # 分析项目
        result = await latex_service.analyze_project(temp_dir, main_file)
        
        # 清理临时文件
        shutil.rmtree(temp_dir)
        
        return ProjectAnalysisResponse(
            success=True,
            message="项目分析完成",
            sections=result["sections"],
            analysis=result["analysis"]
        )
        
    except Exception as e:
        # 清理临时文件
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@router.post("/analyze-directory")
async def analyze_directory(directory_path: str):
    """
    分析指定目录中的LaTeX项目
    """
    try:
        if not os.path.exists(directory_path):
            raise HTTPException(status_code=404, detail="目录不存在")
        
        # 检测主文件
        main_file = latex_service.detect_main_file(directory_path)
        if not main_file:
            raise HTTPException(status_code=400, detail="未找到主LaTeX文件")
        
        # 分析项目
        result = await latex_service.analyze_project(directory_path, main_file)
        
        return ProjectAnalysisResponse(
            success=True,
            message="项目分析完成",
            sections=result["sections"],
            analysis=result["analysis"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@router.get("/sections/{section_id}")
async def get_section_content(section_id: str):
    """
    获取特定章节的详细内容
    """
    try:
        content = await latex_service.get_section_content(section_id)
        return {"section_id": section_id, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取章节内容失败: {str(e)}")

@router.post("/suggestions/apply", response_model=SuggestionApplicationResponse)
async def apply_suggestion(request: SuggestionApplicationRequest):
    """
    应用优化建议
    """
    try:
        result = await latex_service.apply_suggestion(
            request.suggestion_id,
            request.file_path,
            request.original_text,
            request.suggested_text
        )
        
        return SuggestionApplicationResponse(
            success=result["success"],
            message=result["message"],
            updated_content=result.get("updated_content")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"应用建议失败: {str(e)}")

@router.get("/duplicates")
async def detect_duplicates(project_path: str, threshold: float = 0.8):
    """
    检测重复内容
    """
    try:
        duplicates = await latex_service.detect_duplicates(project_path, threshold)
        return {"duplicates": duplicates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测重复内容失败: {str(e)}")

@router.get("/logic-analysis")
async def analyze_logic_flow(project_path: str):
    """
    分析逻辑流程
    """
    try:
        logic_issues = await latex_service.analyze_logic_flow(project_path)
        return {"logic_issues": logic_issues}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"逻辑分析失败: {str(e)}")

@router.get("/statistics")
async def get_project_statistics(project_path: str):
    """
    获取项目统计信息
    """
    try:
        stats = await latex_service.get_project_statistics(project_path)
        return {"statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.post("/export")
async def export_optimized_project(project_path: str, output_path: str):
    """
    导出优化后的项目
    """
    try:
        result = await latex_service.export_optimized_project(project_path, output_path)
        return {"success": True, "output_path": result["output_path"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

@router.get("/health")
async def health_check():
    """
    健康检查
    """
    return {"status": "healthy", "service": "latex-processor"}