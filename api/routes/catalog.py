"""
大纲分析路由

对应前端API路径:
- POST /api/catalog/topic/
- POST /api/catalog/text/
- POST /api/catalog/file/
"""
import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from api.models import CatalogTopicRequest, CatalogTextRequest, CatalogResponse
from business.catalog import CatalogService
from business.task_manager import TaskManager
from utils.logger import get_logger

logger = get_logger(name="api.routes.catalog")
router = APIRouter()


@router.post("/topic/", response_model=CatalogResponse)
async def analyze_catalog_from_topic(request: CatalogTopicRequest):
    """
    API接口：基于话题生成知识大纲

    请求方法: POST
    请求体 (JSON):
    {
        "topic": "学习主题，如'Python编程基础'",
        "lang": "zh"  # 可选，默认中文 (zh/en/ja)
    }

    响应 (JSON):
    {
        "success": true,
        "catalog": [
            {
                "chapter": "章节名称",
                "description": "章节描述",
                "sections": [
                    {
                        "section": "小节名称",
                        "description": "小节描述",
                        "subsections": [
                            {"subsection": "子小节名称", "description": "子小节描述"}
                        ]
                    }
                ]
            }
        ]
    }
    """
    try:
        logger.info(f"收到话题大纲生成请求，话题: {request.topic}, 语言: {request.lang}")

        # 验证输入
        if not request.topic:
            logger.warning("话题为空")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': '请提供学习主题'}
            )

        # 调用业务层生成大纲
        catalog_service = CatalogService()
        catalog = catalog_service.analyze_catalog_from_topic(request.topic, request.lang)

        # 返回结果
        logger.info(f"成功生成大纲 - 话题: {request.topic}")
        return CatalogResponse(
            success=True,
            catalog=catalog
        )

    except Exception as e:
        logger.error(f"API处理异常: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': '服务器内部错误'}
        )


@router.post("/text/", response_model=CatalogResponse)
async def analyze_catalog_from_text(request: CatalogTextRequest):
    """
    API接口：基于文本内容生成知识大纲

    请求方法: POST
    请求体 (JSON):
    {
        "text": "完整的文本内容",
        "lang": "zh"  # 可选，默认中文 (zh/en/ja)
    }

    响应 (JSON):
    {
        "success": true,
        "catalog": [
            {
                "chapter": "章节名称",
                "description": "章节描述",
                "sections": [...]
            }
        ]
    }
    """
    try:
        logger.info(f"收到文本大纲生成请求，文本长度: {len(request.text)}, 语言: {request.lang}")

        # 验证输入
        if not request.text:
            logger.warning("文本内容为空")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': '请提供文本内容'}
            )

        # 调用业务层生成大纲
        catalog_service = CatalogService()
        catalog = catalog_service.analyze_catalog_from_text(request.text, request.lang)

        # 返回结果
        logger.info(f"成功生成大纲 - 文本长度: {len(request.text)}")
        return CatalogResponse(
            success=True,
            catalog=catalog
        )

    except Exception as e:
        logger.error(f"API处理异常: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': '服务器内部错误'}
        )


@router.post("/file/", response_model=CatalogResponse)
async def analyze_catalog_from_file(
    task_id: str = Form(...),
    file: UploadFile = File(...),
    lang: str = Form("zh")
):
    """
    API接口：基于上传文件生成知识大纲

    请求方法: POST
    Content-Type: multipart/form-data
    请求体:
    - task_id: 任务ID（必填）
    - file: 上传的文件
    - lang: 语言 (可选，默认zh)

    响应 (JSON):
    {
        "success": true,
        "catalog": [
            {
                "id": "1",
                "chapter": "第一章 概述",
                "description": "本章介绍基本概念和框架",
                "sections": [
                    {
                        "id": "1.1",
                        "section": "1.1 背景知识",
                        "description": "介绍相关背景和历史",
                        "subsections": [
                            {
                                "id": "1.1.1",
                                "subsection": "1.1.1 历史发展",
                                "description": "详细介绍发展历程"
                            }
                        ]
                    }
                ]
            }
        ],
        "file_name": "example.pdf"
    }

    注意: catalog中的每个章节、小节、子小节都包含唯一的id字段，
    前端可直接使用这些id进行章节选择操作
    """
    try:
        file_name = file.filename
        logger.info(f"收到文件大纲生成请求，task_id={task_id}, 文件名: {file_name}, 语言: {lang}")

        # 1. 验证 task_id
        if not task_id:
            logger.warning("task_id未提供")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': 'task_id为必填参数'}
            )

        # 2. 检查是否有文件上传
        if not file:
            logger.warning("未找到上传的文件")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': '请上传文件'}
            )

        # 3. 验证任务是否存在且合法
        task_mgr = TaskManager()
        validation = task_mgr.validate_task(
            task_id=task_id,
            expected_task_type="file",
            expected_workflow_type="extract_catalog"
        )

        if not validation['valid']:
            logger.warning(f"任务验证失败: {validation['error']}")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': validation['error']}
            )

        # 4. 验证文件名是否与任务信息表一致
        task = validation['task']
        input_data = task.get('input_data', {})
        file_info = input_data.get('file', {})
        expected_file_name = file_info.get('name')

        if expected_file_name is not None and file_name != expected_file_name:
            logger.warning(f"文件名不匹配: 期望={expected_file_name}, 实际={file_name}")
            task_mgr.update_status(task_id, 'failed')
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': f'文件名不匹配，期望: {expected_file_name}, 实际: {file_name}'}
            )

        # 5. 文件大小限制（10MB）
        file_content = await file.read()
        file_size = len(file_content)
        max_size = 10 * 1024 * 1024
        if file_size > max_size:
            logger.warning(f"文件过大: {file_size} bytes")
            task_mgr.update_status(task_id, 'failed')
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': f'文件大小不能超过 {max_size // (1024*1024)}MB'}
            )

        # 6. 保存文件到临时目录
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, file_name)

        with open(temp_file_path, 'wb') as destination:
            destination.write(file_content)

        logger.info(f"文件已保存至临时路径: {temp_file_path}")

        try:
            # 7. 调用业务层生成大纲（会自动更新任务状态）
            catalog_service = CatalogService()
            catalog = catalog_service.analyze_catalog_from_file(temp_file_path, lang, task_id)

            # 8. 返回结果
            logger.info(f"成功生成大纲 - 文件: {file_name}")
            return CatalogResponse(
                success=True,
                catalog=catalog,
                file_name=file_name
            )

        finally:
            # 9. 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.debug(f"已删除临时文件: {temp_file_path}")

    except Exception as e:
        logger.error(f"API处理异常: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': '服务器内部错误'}
        )
