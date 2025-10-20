"""
FastAPI应用主入口

AnkiGenix Backend - AI驱动的Anki闪卡生成服务
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import flashcard, catalog, export, health

# 创建FastAPI应用
app = FastAPI(
    title="AnkiGenix API",
    description="AI驱动的Anki闪卡生成服务",
    version="2.0.0"
)

# CORS配置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:3003",
    "https://ankigenix.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "accept",
        "accept-encoding",
        "authorization",
        "content-type",
        "dnt",
        "origin",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
    ],
)

# 注册路由
app.include_router(flashcard.router, prefix="/api/flashcards", tags=["flashcards"])
app.include_router(catalog.router, prefix="/api/catalog", tags=["catalog"])
app.include_router(export.router, prefix="/api/flashcards", tags=["export"])
app.include_router(health.router, prefix="/api", tags=["health"])


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    import traceback
    from utils.logger import get_logger

    logger = get_logger(name="api.exception")
    logger.error(f"全局异常: {str(exc)}", exc_info=True)
    logger.error(f"异常详情: {traceback.format_exc()}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "服务器内部错误"
        }
    )


import os

if __name__ == "__main__":
    import uvicorn
    
    # 生产环境配置
    uvicorn.run(
        "main:app",  # 字符串形式
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False,  # 生产环境关闭热重载
        workers=int(os.getenv("WORKERS", "1")),  # 根据环境变量调整
        log_level="info"
    )
