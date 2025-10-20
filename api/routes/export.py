"""
导出路由

对应前端API路径:
- GET /api/flashcards/export/
"""
import os
from fastapi import APIRouter, Query
from fastapi.responses import Response, JSONResponse
from business.export import ExportBusiness
from utils.logger import get_logger

logger = get_logger(name="api.routes.export")
router = APIRouter()


@router.get("/export/")
async def export_flashcards(
    task_id: str = Query(..., description="任务ID（必填）"),
    format: str = Query("apkg", description="导出格式，'csv' 或 'apkg'（可选，默认 'apkg'）"),
    deck_name: str = Query("", description="牌组名称（仅用于 apkg 格式，可选）")
):
    """
    API接口：导出闪卡为 CSV 或 APKG 格式

    请求方法: GET
    请求参数:
    - task_id: 任务ID（必填）
    - format: 导出格式，'csv' 或 'apkg'（可选，默认 'apkg'）
    - deck_name: 牌组名称（仅用于 apkg 格式，可选）

    响应:
    - 成功: 返回文件下载流
    - 失败: 返回 JSON 错误信息
    """
    try:
        export_format = format.strip().lower()
        deck_name_clean = deck_name.strip() if deck_name else None

        logger.info(f"收到导出请求: task_id={task_id}, format={export_format}, deck_name={deck_name_clean or '默认'}")

        # 验证 task_id
        if not task_id:
            logger.warning("task_id未提供")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': 'task_id为必填参数'}
            )

        # 调用导出业务逻辑
        export_biz = ExportBusiness()
        result = export_biz.export_task_flashcards(
            task_id=task_id,
            export_format=export_format,
            deck_name=deck_name_clean
        )

        if not result['success']:
            logger.error(f"导出失败: {result.get('error')}")
            return JSONResponse(
                status_code=500,
                content={'success': False, 'error': result.get('error', '导出失败')}
            )

        # 读取文件并返回
        file_path = result['file_path']
        file_name = result['file_name']

        # 根据格式设置 Content-Type
        content_type = 'application/octet-stream'
        if export_format == 'csv':
            content_type = 'text/csv; charset=utf-8'
        elif export_format == 'apkg':
            content_type = 'application/zip'

        # 读取文件内容
        with open(file_path, 'rb') as f:
            file_content = f.read()

        # 删除临时文件
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"已删除临时导出文件: {file_path}")

        # 返回文件响应
        logger.info(f"成功导出闪卡: task_id={task_id}, format={export_format}, size={len(file_content)} bytes")

        return Response(
            content=file_content,
            media_type=content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{file_name}"',
                'Content-Length': str(len(file_content))
            }
        )

    except Exception as e:
        logger.error(f"导出API处理异常: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': '服务器内部错误'}
        )
