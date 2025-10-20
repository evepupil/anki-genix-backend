"""
闪卡生成路由

对应前端API路径:
- POST /api/flashcards/generate/text/
- POST /api/flashcards/generate/file/
- POST /api/flashcards/generate/url/
- POST /api/flashcards/generate/text/section/
- POST /api/flashcards/generate/file/section/
"""
import os
import json
import tempfile
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from api.models import (
    FlashcardTextRequest, FlashcardURLRequest, FlashcardTextSectionRequest,
    FlashcardResponse, FlashcardItem
)
from business.flashcard import FlashcardBusiness
from business.task_manager import TaskManager
from business.database.catalog_db import CatalogDB
from utils.logger import get_logger

logger = get_logger(name="api.routes.flashcard")
router = APIRouter()


@router.post("/generate/text/", response_model=FlashcardResponse)
async def generate_flashcards_from_text(request: FlashcardTextRequest):
    """
    API接口：根据文本生成闪卡

    请求方法: POST
    请求体 (JSON):
    {
        "task_id": "任务ID（必填）",
        "text": "要学习的文本内容",
        "card_number": 10,  # 可选，不提供则由AI智能决定数量
        "lang": "zh"  # 可选，默认中文
    }

    响应 (JSON):
    {
        "success": true,
        "cards": [
            {
                "question": "问题",
                "answer": "答案"
            }
        ],
        "count": 10
    }
    """
    try:
        logger.info(f"收到文本闪卡生成请求，task_id={request.task_id}, 文本长度: {len(request.text)}, 数量: {request.card_number or '智能'}, 语言: {request.lang}")

        # 1. 验证 task_id 是否提供
        if not request.task_id:
            logger.warning("task_id未提供")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': 'task_id为必填参数'}
            )

        # 2. 验证任务是否存在且合法
        task_mgr = TaskManager()
        validation = task_mgr.validate_task(
            task_id=request.task_id,
            expected_task_type="text"  # 验证输入类型为 text
        )

        if not validation['valid']:
            logger.warning(f"任务验证失败: {validation['error']}")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': validation['error']}
            )

        # 3. 验证文本内容
        if not request.text:
            logger.warning("文本内容为空")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': '请提供要学习的文本内容'}
            )

        # 4. 验证文本长度是否与任务信息表一致
        task = validation['task']
        input_data = task.get('input_data', {})
        expected_text = input_data.get('text')

        if expected_text is not None:
            expected_text_length = len(expected_text)
            actual_text_length = len(request.text)
            if actual_text_length != expected_text_length:
                logger.warning(f"文本长度不匹配: 期望={expected_text_length}, 实际={actual_text_length}")
                return JSONResponse(
                    status_code=400,
                    content={
                        'success': False,
                        'error': f'文本内容长度不匹配，期望: {expected_text_length}, 实际: {actual_text_length}'
                    }
                )

        # 5. 调用业务层生成闪卡（会自动更新任务状态）
        biz = FlashcardBusiness()
        result = biz.generate_flashcards_from_text(request.text, request.card_number, request.lang, request.task_id)

        # 6. 返回结果
        if result['success']:
            logger.info(f"成功生成 {len(result['cards'])} 张闪卡")
            return FlashcardResponse(
                success=True,
                cards=[FlashcardItem(**card) for card in result['cards']],
                count=len(result['cards'])
            )
        else:
            logger.error(f"闪卡生成失败: {result.get('error')}")
            return JSONResponse(
                status_code=500,
                content={'success': False, 'error': result.get('error', '生成闪卡失败')}
            )

    except Exception as e:
        logger.error(f"API处理异常: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': '服务器内部错误'}
        )


@router.post("/generate/file/", response_model=FlashcardResponse)
async def generate_flashcards_from_file(
    task_id: str = Form(...),
    file: UploadFile = File(...),
    card_number: Optional[int] = Form(None),
    lang: str = Form("zh")
):
    """
    API接口：根据上传的文件生成闪卡

    请求方法: POST
    Content-Type: multipart/form-data
    请求体:
    - task_id: 任务ID（必填）
    - file: 上传的文件（支持PDF、DOC、DOCX、TXT、MD等）
    - card_number: 卡片数量（可选，不提供则由AI智能决定数量）
    - lang: 语言（可选，默认中文）

    响应 (JSON):
    {
        "success": true,
        "cards": [
            {
                "question": "问题",
                "answer": "答案"
            }
        ],
        "count": 10
    }
    """
    try:
        file_name = file.filename
        logger.info(f"收到文件闪卡生成请求，task_id={task_id}, 文件名: {file_name}, 数量: {card_number or '智能'}, 语言: {lang}")

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
            expected_task_type="file"  # 验证输入类型为 file
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
            # 7. 调用业务层生成闪卡（会自动更新任务状态）
            biz = FlashcardBusiness()
            result = biz.generate_flashcards_from_file(temp_file_path, card_number, lang, task_id)

            # 8. 返回结果
            if result['success']:
                logger.info(f"成功生成 {len(result['cards'])} 张闪卡")
                return FlashcardResponse(
                    success=True,
                    cards=[FlashcardItem(**card) for card in result['cards']],
                    count=len(result['cards']),
                    file_name=file_name
                )
            else:
                logger.error(f"闪卡生成失败: {result.get('error')}")
                return JSONResponse(
                    status_code=500,
                    content={'success': False, 'error': result.get('error', '生成闪卡失败')}
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


@router.post("/generate/url/", response_model=FlashcardResponse)
async def generate_flashcards_from_url(request: FlashcardURLRequest):
    """
    API接口：根据URL爬取网页内容并生成闪卡

    请求方法: POST
    请求体 (JSON):
    {
        "task_id": "任务ID（必填）",
        "url": "https://example.com/article",
        "card_number": 10,  # 可选，不提供则由AI智能决定数量
        "lang": "zh"  # 可选，默认中文
    }

    响应 (JSON):
    {
        "success": true,
        "cards": [
            {
                "question": "问题",
                "answer": "答案"
            }
        ],
        "count": 10,
        "url": "https://example.com/article",
        "crawled_length": 5000
    }
    """
    try:
        logger.info(f"收到URL闪卡生成请求，task_id={request.task_id}, URL: {request.url}, 数量: {request.card_number or '智能'}, 语言: {request.lang}")

        # 1. 验证 task_id 是否提供
        if not request.task_id:
            logger.warning("task_id未提供")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': 'task_id为必填参数'}
            )

        # 2. 验证任务是否存在且合法
        task_mgr = TaskManager()
        validation = task_mgr.validate_task(
            task_id=request.task_id,
            expected_task_type="web"  # 验证输入类型为 web
        )

        if not validation['valid']:
            logger.warning(f"任务验证失败: {validation['error']}")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': validation['error']}
            )

        # 3. 验证URL
        if not request.url:
            logger.warning("URL为空")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': '请提供有效的URL地址'}
            )

        # 4. 验证URL是否与任务信息表一致
        task = validation['task']
        input_data = task.get('input_data', {})
        expected_url = input_data.get('web_url')

        if expected_url is not None and request.url != expected_url:
            logger.warning(f"URL不匹配: 期望={expected_url}, 实际={request.url}")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': f'URL不匹配，期望: {expected_url}, 实际: {request.url}'}
            )

        # 5. 验证card_number参数（如果提供了的话）
        if request.card_number is not None:
            if request.card_number <= 0 or request.card_number > 50:
                logger.warning(f"闪卡数量不合理: {request.card_number}")
                return JSONResponse(
                    status_code=400,
                    content={'success': False, 'error': '闪卡数量必须在1-50之间'}
                )

        # 6. 调用业务层生成闪卡
        biz = FlashcardBusiness()
        result = biz.generate_flashcards_from_url(request.url, request.card_number, request.lang)

        # 7. 返回结果
        if result['success']:
            logger.info(f"成功从URL生成 {len(result['cards'])} 张闪卡")
            return FlashcardResponse(
                success=True,
                cards=[FlashcardItem(**card) for card in result['cards']],
                count=len(result['cards']),
                url=result.get('url'),
                crawled_length=result.get('crawled_length')
            )
        else:
            logger.error(f"闪卡生成失败: {result.get('error')}")
            return JSONResponse(
                status_code=500,
                content={'success': False, 'error': result.get('error', '生成闪卡失败')}
            )

    except Exception as e:
        logger.error(f"API处理异常: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': '服务器内部错误'}
        )


@router.post("/generate/text/section/", response_model=FlashcardResponse)
async def generate_flashcards_from_text_section(request: FlashcardTextSectionRequest):
    """
    API接口：根据文本内容和指定章节生成闪卡

    请求方法: POST
    请求体 (JSON):
    {
        "text": "完整的学习材料文本内容",
        "section_title": "第三章：Python数据类型",
        "card_number": 10,  # 可选，不提供则由AI智能决定数量
        "lang": "zh"  # 可选，默认中文
    }

    响应 (JSON):
    {
        "success": true,
        "cards": [
            {
                "question": "问题",
                "answer": "答案"
            }
        ],
        "count": 10,
        "section_title": "第三章：Python数据类型"
    }
    """
    try:
        logger.info(f"收到文本章节闪卡生成请求，章节: {request.section_title}, 文本长度: {len(request.text)}, 数量: {request.card_number or '智能'}, 语言: {request.lang}")

        # 验证输入
        if not request.text:
            logger.warning("文本内容为空")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': '请提供学习材料文本内容'}
            )

        if not request.section_title:
            logger.warning("章节标题为空")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': '请提供章节标题'}
            )

        # 调用业务层生成闪卡
        biz = FlashcardBusiness()
        result = biz.generate_flashcards_from_text_section(request.text, request.section_title, request.card_number, request.lang)

        # 返回结果
        if result['success']:
            logger.info(f"成功生成 {len(result['cards'])} 张闪卡 - 章节: {request.section_title}")
            return FlashcardResponse(
                success=True,
                cards=[FlashcardItem(**card) for card in result['cards']],
                count=len(result['cards']),
                section_title=result.get('section_title')
            )
        else:
            logger.error(f"闪卡生成失败: {result.get('error')}")
            return JSONResponse(
                status_code=500,
                content={'success': False, 'error': result.get('error', '生成闪卡失败')}
            )

    except Exception as e:
        logger.error(f"API处理异常: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': '服务器内部错误'}
        )


@router.post("/generate/file/section/", response_model=FlashcardResponse)
async def generate_flashcards_from_file_section(
    task_id: str = Form(...),
    file: UploadFile = File(...),
    chapter_ids: str = Form("[]"),
    card_number: Optional[int] = Form(None),
    lang: str = Form("zh")
):
    """
    API接口：根据上传文件和指定章节ID列表生成闪卡

    请求方法: POST
    Content-Type: multipart/form-data
    请求体:
    - task_id: 任务ID（必填）
    - file: 上传的文件（支持PDF、DOC、DOCX、TXT、MD等）
    - chapter_ids: 章节ID列表（JSON字符串格式）
    - card_number: 卡片数量（可选，不提供则由AI智能决定数量）
    - lang: 语言（可选，默认中文）

    响应 (JSON):
    {
        "success": true,
        "cards": [
            {
                "question": "问题",
                "answer": "答案"
            }
        ],
        "count": 10,
        "section_results": [
            {
                "section_title": "第三章：Python数据类型",
                "cards": [{"question": "问题", "answer": "答案"}],
                "count": 5
            }
        ],
        "file_name": "example.pdf"
    }
    """
    try:
        file_name = file.filename

        # 解析章节ID列表
        try:
            chapter_ids_list = json.loads(chapter_ids)
            if not isinstance(chapter_ids_list, list):
                chapter_ids_list = []
        except json.JSONDecodeError:
            logger.warning("章节ID列表格式错误")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': '章节ID列表格式错误'}
            )

        logger.info(f"收到文件章节闪卡生成请求，task_id={task_id}, 文件名: {file_name}, 章节ID: {chapter_ids_list}, 数量: {card_number or '智能'}, 语言: {lang}")

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
            expected_task_type="file"
        )

        if not validation['valid']:
            logger.warning(f"任务验证失败: {validation['error']}")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': validation['error']}
            )

        # 4. 验证任务状态必须是 catalog_ready（已生成大纲，等待用户选择章节）
        task = validation['task']
        current_status = task.get('status')
        if current_status != 'catalog_ready':
            logger.warning(f"任务状态不正确: 期望=catalog_ready, 实际={current_status}")
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': f'任务状态不正确，期望: catalog_ready, 实际: {current_status}'}
            )

        # 5. 验证文件名是否与任务信息表一致
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

        # 6. 验证章节ID列表
        if not chapter_ids_list:
            logger.warning("章节ID列表为空")
            task_mgr.update_status(task_id, 'failed')
            return JSONResponse(
                status_code=400,
                content={'success': False, 'error': '请提供章节ID列表'}
            )

        # 7. 更新大纲信息表中的选中章节ID列表 (在验证合法后立即更新)
        try:
            catalog_db = CatalogDB()
            update_result = catalog_db.update_selected_sections(task_id, chapter_ids_list)

            if update_result.get('success'):
                logger.info(f"成功更新选中章节ID到大纲表: task_id={task_id}, 选中ID数量: {len(chapter_ids_list)}")
            else:
                logger.warning(f"更新选中章节ID到大纲表失败: {update_result.get('error')}")
        except Exception as update_error:
            logger.error(f"更新选中章节ID到大纲表时发生异常: {str(update_error)}", exc_info=True)

        # 8. 文件大小限制（10MB）
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

        # 9. 保存文件到临时目录
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, file_name)

        with open(temp_file_path, 'wb') as destination:
            destination.write(file_content)

        logger.info(f"文件已保存至临时路径: {temp_file_path}")

        try:
            # 10. 调用业务层生成闪卡（会自动更新任务状态）
            biz = FlashcardBusiness()
            result = biz.generate_flashcards_from_file_section_by_ids(temp_file_path, chapter_ids_list, card_number, lang, task_id)

            # 11. 返回结果
            if result['success']:
                logger.info(f"成功生成 {len(result['cards'])} 张闪卡 - 文件: {file_name}, 章节ID数量: {len(chapter_ids_list)}")
                return FlashcardResponse(
                    success=True,
                    cards=[FlashcardItem(**card) for card in result['cards']],
                    count=len(result['cards']),
                    section_results=result.get('section_results', []),
                    file_name=result.get('file_name', file_name)
                )
            else:
                logger.error(f"闪卡生成失败: {result.get('error')}")
                return JSONResponse(
                    status_code=500,
                    content={'success': False, 'error': result.get('error', '生成闪卡失败')}
                )

        finally:
            # 12. 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.debug(f"已删除临时文件: {temp_file_path}")

    except Exception as e:
        logger.error(f"API处理异常: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': '服务器内部错误'}
        )
