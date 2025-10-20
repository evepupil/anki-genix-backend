"""
健康检查路由

对应前端API路径:
- GET /api/health
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    健康检查接口
    用于 fly.io 和其他监控服务
    """
    return JSONResponse(
        content={
            'status': 'ok',
            'service': 'ankigenix-backend'
        }
    )
