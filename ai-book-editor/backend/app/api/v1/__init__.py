"""
API v1 路由配置
"""
from fastapi import APIRouter

from app.api.v1.endpoints import latex, symbols

api_router = APIRouter()

# 包含各个端点路由
api_router.include_router(latex.router, prefix="/latex", tags=["latex"])
api_router.include_router(symbols.router, prefix="/symbols", tags=["symbols"])