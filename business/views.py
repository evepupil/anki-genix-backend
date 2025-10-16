import json
import os
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from business.flashcard import FlashcardBusiness
from business.catalog import CatalogService
from utils.logger import get_logger

logger = get_logger(name="api.views")


@csrf_exempt
@require_http_methods(["POST"])
def generate_flashcards_from_text(request):
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
        # 解析请求数据
        data = json.loads(request.body)
        task_id = data.get('task_id', '').strip()
        text_content = data.get('text', '').strip()
        card_number = data.get('card_number', None)  # 可选，None表示智能模式
        lang = data.get('lang', 'zh')

        logger.info(f"收到文本闪卡生成请求，task_id={task_id}, 文本长度: {len(text_content)}, 数量: {card_number or '智能'}, 语言: {lang}")

        # 1. 验证 task_id 是否提供
        if not task_id:
            logger.warning("task_id未提供")
            return JsonResponse({
                'success': False,
                'error': 'task_id为必填参数'
            }, status=400)

        # 2. 验证任务是否存在且合法
        from business.task_manager import TaskManager
        task_mgr = TaskManager()

        validation = task_mgr.validate_task(
            task_id=task_id,
            expected_task_type="text"  # 验证输入类型为 text
        )

        if not validation['valid']:
            logger.warning(f"任务验证失败: {validation['error']}")
            return JsonResponse({
                'success': False,
                'error': validation['error']
            }, status=400)

        # 3. 验证文本内容
        if not text_content:
            logger.warning("文本内容为空")
            return JsonResponse({
                'success': False,
                'error': '请提供要学习的文本内容'
            }, status=400)

        # 4. 验证文本长度是否与任务信息表一致
        task = validation['task']
        input_data = task.get('input_data', {})
        expected_text = input_data.get('text')

        if expected_text is not None:
            expected_text_length = len(expected_text)
            actual_text_length = len(text_content)
            if actual_text_length != expected_text_length:
                logger.warning(f"文本长度不匹配: 期望={expected_text_length}, 实际={actual_text_length}")
                return JsonResponse({
                    'success': False,
                    'error': f'文本内容长度不匹配，期望: {expected_text_length}, 实际: {actual_text_length}'
                }, status=400)

        # 4. 调用业务层生成闪卡（会自动更新任务状态）
        biz = FlashcardBusiness()
        result = biz.generate_flashcards_from_text(text_content, card_number, lang, task_id)

        # 5. 返回结果
        if result['success']:
            logger.info(f"成功生成 {len(result['cards'])} 张闪卡")
            return JsonResponse({
                'success': True,
                'cards': result['cards'],
                'count': len(result['cards'])
            })
        else:
            logger.error(f"闪卡生成失败: {result.get('error')}")
            return JsonResponse({
                'success': False,
                'error': result.get('error', '生成闪卡失败')
            }, status=500)

    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        }, status=400)

    except Exception as e:
        logger.error(f"API处理异常: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_flashcards_from_file(request):
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
        # 1. 验证 task_id
        task_id = request.POST.get('task_id', '').strip()
        if not task_id:
            logger.warning("task_id未提供")
            return JsonResponse({
                'success': False,
                'error': 'task_id为必填参数'
            }, status=400)

        # 2. 检查是否有文件上传
        if 'file' not in request.FILES:
            logger.warning("未找到上传的文件")
            return JsonResponse({
                'success': False,
                'error': '请上传文件'
            }, status=400)

        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        card_number = request.POST.get('card_number', None)  # 可选，None表示智能模式
        if card_number is not None:
            try:
                card_number = int(card_number)
            except (ValueError, TypeError):
                card_number = None
        lang = request.POST.get('lang', 'zh')

        logger.info(f"收到文件闪卡生成请求，task_id={task_id}, 文件名: {file_name}, 大小: {uploaded_file.size} bytes, 数量: {card_number or '智能'}, 语言: {lang}")

        # 3. 验证任务是否存在且合法
        from business.task_manager import TaskManager
        task_mgr = TaskManager()

        validation = task_mgr.validate_task(
            task_id=task_id,
            expected_task_type="file"  # 验证输入类型为 file
        )

        if not validation['valid']:
            logger.warning(f"任务验证失败: {validation['error']}")
            return JsonResponse({
                'success': False,
                'error': validation['error']
            }, status=400)

        # 4. 验证文件名是否与任务信息表一致
        task = validation['task']
        input_data = task.get('input_data', {})
        file_info = input_data.get('file', {})
        expected_file_name = file_info.get('name')

        if expected_file_name is not None and file_name != expected_file_name:
            logger.warning(f"文件名不匹配: 期望={expected_file_name}, 实际={file_name}")
            return JsonResponse({
                'success': False,
                'error': f'文件名不匹配，期望: {expected_file_name}, 实际: {file_name}'
            }, status=400)

        # 5. 文件大小限制（10MB）
        max_size = 10 * 1024 * 1024
        if uploaded_file.size > max_size:
            logger.warning(f"文件过大: {uploaded_file.size} bytes")
            task_mgr.update_status(task_id, 'failed')
            return JsonResponse({
                'success': False,
                'error': f'文件大小不能超过 {max_size // (1024*1024)}MB'
            }, status=400)

        # 6. 保存文件到临时目录
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, file_name)

        with open(temp_file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        logger.info(f"文件已保存至临时路径: {temp_file_path}")

        try:
            # 7. 调用业务层生成闪卡（会自动更新任务状态）
            biz = FlashcardBusiness()
            result = biz.generate_flashcards_from_file(temp_file_path, card_number, lang, task_id)

            # 8. 返回结果
            if result['success']:
                logger.info(f"成功生成 {len(result['cards'])} 张闪卡")
                return JsonResponse({
                    'success': True,
                    'cards': result['cards'],
                    'count': len(result['cards']),
                    'file_name': file_name
                })
            else:
                logger.error(f"闪卡生成失败: {result.get('error')}")
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', '生成闪卡失败')
                }, status=500)

        finally:
            # 9. 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.debug(f"已删除临时文件: {temp_file_path}")

    except Exception as e:
        logger.error(f"API处理异常: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_flashcards_from_url(request):
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
        # 解析请求数据
        data = json.loads(request.body)
        task_id = data.get('task_id', '').strip()
        url = data.get('url', '').strip()
        card_number = data.get('card_number', None)  # 可选，None表示智能模式
        lang = data.get('lang', 'zh')

        logger.info(f"收到URL闪卡生成请求，task_id={task_id}, URL: {url}, 数量: {card_number or '智能'}, 语言: {lang}")

        # 1. 验证 task_id 是否提供
        if not task_id:
            logger.warning("task_id未提供")
            return JsonResponse({
                'success': False,
                'error': 'task_id为必填参数'
            }, status=400)

        # 2. 验证任务是否存在且合法
        from business.task_manager import TaskManager
        task_mgr = TaskManager()

        validation = task_mgr.validate_task(
            task_id=task_id,
            expected_task_type="web"  # 验证输入类型为 web
        )

        if not validation['valid']:
            logger.warning(f"任务验证失败: {validation['error']}")
            return JsonResponse({
                'success': False,
                'error': validation['error']
            }, status=400)

        # 3. 验证URL
        if not url:
            logger.warning("URL为空")
            return JsonResponse({
                'success': False,
                'error': '请提供有效的URL地址'
            }, status=400)

        # 4. 验证URL是否与任务信息表一致
        task = validation['task']
        input_data = task.get('input_data', {})
        expected_url = input_data.get('web_url')

        if expected_url is not None and url != expected_url:
            logger.warning(f"URL不匹配: 期望={expected_url}, 实际={url}")
            return JsonResponse({
                'success': False,
                'error': f'URL不匹配，期望: {expected_url}, 实际: {url}'
            }, status=400)

        # 5. 验证card_number参数（如果提供了的话）
        if card_number is not None:
            try:
                card_number = int(card_number)
                if card_number <= 0 or card_number > 50:
                    logger.warning(f"闪卡数量不合理: {card_number}")
                    return JsonResponse({
                        'success': False,
                        'error': '闪卡数量必须在1-50之间'
                    }, status=400)
            except (ValueError, TypeError):
                logger.warning(f"闪卡数量格式错误: {card_number}")
                return JsonResponse({
                    'success': False,
                    'error': '闪卡数量必须是有效的整数'
                }, status=400)

        # 6. 调用业务层生成闪卡
        biz = FlashcardBusiness()
        result = biz.generate_flashcards_from_url(url, card_number, lang)

        # 7. 返回结果
        if result['success']:
            logger.info(f"成功从URL生成 {len(result['cards'])} 张闪卡")
            return JsonResponse({
                'success': True,
                'cards': result['cards'],
                'count': len(result['cards']),
                'url': result.get('url'),
                'crawled_length': result.get('crawled_length')
            })
        else:
            logger.error(f"闪卡生成失败: {result.get('error')}")
            return JsonResponse({
                'success': False,
                'error': result.get('error', '生成闪卡失败')
            }, status=500)

    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        }, status=400)

    except Exception as e:
        logger.error(f"API处理异常: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)


@require_http_methods(["GET"])
def health_check(request):
    """
    健康检查接口
    """
    return JsonResponse({
        'status': 'ok',
        'service': 'ankigenix-backend'
    })


# ============ 章节闪卡生成接口 ============

@csrf_exempt
@require_http_methods(["POST"])
def generate_flashcards_from_text_section(request):
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
        # 解析请求数据
        data = json.loads(request.body)
        text_content = data.get('text', '').strip()
        section_title = data.get('section_title', '').strip()
        card_number = data.get('card_number', None)  # 可选，None表示智能模式
        lang = data.get('lang', 'zh')

        logger.info(f"收到文本章节闪卡生成请求，章节: {section_title}, 文本长度: {len(text_content)}, 数量: {card_number or '智能'}, 语言: {lang}")

        # 验证输入
        if not text_content:
            logger.warning("文本内容为空")
            return JsonResponse({
                'success': False,
                'error': '请提供学习材料文本内容'
            }, status=400)

        if not section_title:
            logger.warning("章节标题为空")
            return JsonResponse({
                'success': False,
                'error': '请提供章节标题'
            }, status=400)

        # 调用业务层生成闪卡
        biz = FlashcardBusiness()
        result = biz.generate_flashcards_from_text_section(text_content, section_title, card_number, lang)

        # 返回结果
        if result['success']:
            logger.info(f"成功生成 {len(result['cards'])} 张闪卡 - 章节: {section_title}")
            return JsonResponse({
                'success': True,
                'cards': result['cards'],
                'count': len(result['cards']),
                'section_title': result.get('section_title')
            })
        else:
            logger.error(f"闪卡生成失败: {result.get('error')}")
            return JsonResponse({
                'success': False,
                'error': result.get('error', '生成闪卡失败')
            }, status=500)

    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        }, status=400)

    except Exception as e:
        logger.error(f"API处理异常: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_flashcards_from_file_section(request):
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
        # 1. 验证 task_id
        task_id = request.POST.get('task_id', '').strip()
        if not task_id:
            logger.warning("task_id未提供")
            return JsonResponse({
                'success': False,
                'error': 'task_id为必填参数'
            }, status=400)

        # 2. 检查是否有文件上传
        if 'file' not in request.FILES:
            logger.warning("未找到上传的文件")
            return JsonResponse({
                'success': False,
                'error': '请上传文件'
            }, status=400)

        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        chapter_ids = request.POST.get('chapter_ids', '[]')
        card_number = request.POST.get('card_number', None)  # 可选，None表示智能模式
        if card_number is not None:
            try:
                card_number = int(card_number)
            except (ValueError, TypeError):
                card_number = None
        lang = request.POST.get('lang', 'zh')

        # 解析章节ID列表
        try:
            chapter_ids = json.loads(chapter_ids)
            if not isinstance(chapter_ids, list):
                chapter_ids = []
        except json.JSONDecodeError:
            logger.warning("章节ID列表格式错误")
            return JsonResponse({
                'success': False,
                'error': '章节ID列表格式错误'
            }, status=400)

        logger.info(f"收到文件章节闪卡生成请求，task_id={task_id}, 文件名: {file_name}, 章节ID: {chapter_ids}, 大小: {uploaded_file.size} bytes, 数量: {card_number or '智能'}, 语言: {lang}")

        # 3. 验证任务是否存在且合法
        from business.task_manager import TaskManager
        task_mgr = TaskManager()

        validation = task_mgr.validate_task(
            task_id=task_id,
            expected_task_type="file"
        )

        if not validation['valid']:
            logger.warning(f"任务验证失败: {validation['error']}")
            return JsonResponse({
                'success': False,
                'error': validation['error']
            }, status=400)

        # 4. 验证任务状态必须是 catalog_ready（已生成大纲，等待用户选择章节）
        task = validation['task']
        current_status = task.get('status')
        if current_status != 'catalog_ready':
            logger.warning(f"任务状态不正确: 期望=catalog_ready, 实际={current_status}")
            return JsonResponse({
                'success': False,
                'error': f'任务状态不正确，期望: catalog_ready, 实际: {current_status}'
            }, status=400)

        # 5. 验证文件名是否与任务信息表一致
        input_data = task.get('input_data', {})
        file_info = input_data.get('file', {})
        expected_file_name = file_info.get('name')

        if expected_file_name is not None and file_name != expected_file_name:
            logger.warning(f"文件名不匹配: 期望={expected_file_name}, 实际={file_name}")
            task_mgr.update_status(task_id, 'failed')
            return JsonResponse({
                'success': False,
                'error': f'文件名不匹配，期望: {expected_file_name}, 实际: {file_name}'
            }, status=400)

        # 6. 验证章节ID列表
        if not chapter_ids:
            logger.warning("章节ID列表为空")
            task_mgr.update_status(task_id, 'failed')
            return JsonResponse({
                'success': False,
                'error': '请提供章节ID列表'
            }, status=400)

        # 7. 更新大纲信息表中的选中章节ID列表 (在验证合法后立即更新)
        try:
            from business.database.catalog_db import CatalogDB
            catalog_db = CatalogDB()
            update_result = catalog_db.update_selected_sections(task_id, chapter_ids)
            
            if update_result.get('success'):
                logger.info(f"成功更新选中章节ID到大纲表: task_id={task_id}, 选中ID数量: {len(chapter_ids)}")
            else:
                logger.warning(f"更新选中章节ID到大纲表失败: {update_result.get('error')}")
        except Exception as update_error:
            logger.error(f"更新选中章节ID到大纲表时发生异常: {str(update_error)}", exc_info=True)

        # 8. 文件大小限制（10MB）
        max_size = 10 * 1024 * 1024
        if uploaded_file.size > max_size:
            logger.warning(f"文件过大: {uploaded_file.size} bytes")
            task_mgr.update_status(task_id, 'failed')
            return JsonResponse({
                'success': False,
                'error': f'文件大小不能超过 {max_size // (1024*1024)}MB'
            }, status=400)

        # 9. 保存文件到临时目录
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, file_name)

        with open(temp_file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        logger.info(f"文件已保存至临时路径: {temp_file_path}")

        try:
            # 10. 调用业务层生成闪卡（会自动更新任务状态）
            # 需要更新业务层方法以支持章节ID
            biz = FlashcardBusiness()
            result = biz.generate_flashcards_from_file_section_by_ids(temp_file_path, chapter_ids, card_number, lang, task_id)

            # 11. 返回结果
            if result['success']:
                logger.info(f"成功生成 {len(result['cards'])} 张闪卡 - 文件: {file_name}, 章节ID数量: {len(chapter_ids)}")
                return JsonResponse({
                    'success': True,
                    'cards': result['cards'],
                    'count': len(result['cards']),
                    'section_results': result.get('section_results', []),
                    'file_name': result.get('file_name', file_name)
                })
            else:
                logger.error(f"闪卡生成失败: {result.get('error')}")
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', '生成闪卡失败')
                }, status=500)

        finally:
            # 12. 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.debug(f"已删除临时文件: {temp_file_path}")

    except Exception as e:
        logger.error(f"API处理异常: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)


# ============ 大纲生成接口 ============

@csrf_exempt
@require_http_methods(["POST"])
def analyze_catalog_from_topic(request):
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
        # 解析请求数据
        data = json.loads(request.body)
        topic = data.get('topic', '').strip()
        lang = data.get('lang', 'zh')

        logger.info(f"收到话题大纲生成请求，话题: {topic}, 语言: {lang}")

        # 验证输入
        if not topic:
            logger.warning("话题为空")
            return JsonResponse({
                'success': False,
                'error': '请提供学习主题'
            }, status=400)

        # 调用业务层生成大纲
        catalog_service = CatalogService()
        catalog = catalog_service.analyze_catalog_from_topic(topic, lang)

        # 返回结果
        logger.info(f"成功生成大纲 - 话题: {topic}")
        return JsonResponse({
            'success': True,
            'catalog': catalog
        })

    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        }, status=400)

    except Exception as e:
        logger.error(f"API处理异常: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def analyze_catalog_from_text(request):
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
        # 解析请求数据
        data = json.loads(request.body)
        text_content = data.get('text', '').strip()
        lang = data.get('lang', 'zh')

        logger.info(f"收到文本大纲生成请求，文本长度: {len(text_content)}, 语言: {lang}")

        # 验证输入
        if not text_content:
            logger.warning("文本内容为空")
            return JsonResponse({
                'success': False,
                'error': '请提供文本内容'
            }, status=400)

        # 调用业务层生成大纲
        catalog_service = CatalogService()
        catalog = catalog_service.analyze_catalog_from_text(text_content, lang)

        # 返回结果
        logger.info(f"成功生成大纲 - 文本长度: {len(text_content)}")
        return JsonResponse({
            'success': True,
            'catalog': catalog
        })

    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        }, status=400)

    except Exception as e:
        logger.error(f"API处理异常: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def analyze_catalog_from_file(request):
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
        # 1. 验证 task_id
        task_id = request.POST.get('task_id', '').strip()
        if not task_id:
            logger.warning("task_id未提供")
            return JsonResponse({
                'success': False,
                'error': 'task_id为必填参数'
            }, status=400)

        # 2. 检查是否有文件上传
        if 'file' not in request.FILES:
            logger.warning("未找到上传的文件")
            return JsonResponse({
                'success': False,
                'error': '请上传文件'
            }, status=400)

        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        lang = request.POST.get('lang', 'zh')

        logger.info(f"收到文件大纲生成请求，task_id={task_id}, 文件名: {file_name}, 大小: {uploaded_file.size} bytes, 语言: {lang}")

        # 3. 验证任务是否存在且合法
        from business.task_manager import TaskManager
        task_mgr = TaskManager()

        validation = task_mgr.validate_task(
            task_id=task_id,
            expected_task_type="file",
            expected_workflow_type="extract_catalog"
        )

        if not validation['valid']:
            logger.warning(f"任务验证失败: {validation['error']}")
            return JsonResponse({
                'success': False,
                'error': validation['error']
            }, status=400)

        # 4. 验证文件名是否与任务信息表一致
        task = validation['task']
        input_data = task.get('input_data', {})
        file_info = input_data.get('file', {})
        expected_file_name = file_info.get('name')

        if expected_file_name is not None and file_name != expected_file_name:
            logger.warning(f"文件名不匹配: 期望={expected_file_name}, 实际={file_name}")
            task_mgr.update_status(task_id, 'failed')
            return JsonResponse({
                'success': False,
                'error': f'文件名不匹配，期望: {expected_file_name}, 实际: {file_name}'
            }, status=400)

        # 5. 文件大小限制（10MB）
        max_size = 10 * 1024 * 1024
        if uploaded_file.size > max_size:
            logger.warning(f"文件过大: {uploaded_file.size} bytes")
            task_mgr.update_status(task_id, 'failed')
            return JsonResponse({
                'success': False,
                'error': f'文件大小不能超过 {max_size // (1024*1024)}MB'
            }, status=400)

        # 6. 保存文件到临时目录
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, file_name)

        with open(temp_file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        logger.info(f"文件已保存至临时路径: {temp_file_path}")

        try:
            # 7. 调用业务层生成大纲（会自动更新任务状态）
            catalog_service = CatalogService()
            catalog = catalog_service.analyze_catalog_from_file(temp_file_path, lang, task_id)

            # 8. 返回结果
            logger.info(f"成功生成大纲 - 文件: {file_name}")
            return JsonResponse({
                'success': True,
                'catalog': catalog,
                'file_name': file_name
            })

        finally:
            # 9. 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.debug(f"已删除临时文件: {temp_file_path}")

    except Exception as e:
        logger.error(f"API处理异常: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)


# ============ 导出接口 ============

@csrf_exempt
@require_http_methods(["GET"])
def export_flashcards(request):
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
        # 获取请求参数
        task_id = request.GET.get('task_id', '').strip()
        export_format = request.GET.get('format', 'apkg').strip().lower()
        deck_name = request.GET.get('deck_name', '').strip()

        logger.info(f"收到导出请求: task_id={task_id}, format={export_format}, deck_name={deck_name or '默认'}")

        # 验证 task_id
        if not task_id:
            logger.warning("task_id未提供")
            return JsonResponse({
                'success': False,
                'error': 'task_id为必填参数'
            }, status=400)

        # 调用导出业务逻辑
        from business.export import ExportBusiness
        export_biz = ExportBusiness()
        result = export_biz.export_task_flashcards(
            task_id=task_id,
            export_format=export_format,
            deck_name=deck_name if deck_name else None
        )

        if not result['success']:
            logger.error(f"导出失败: {result.get('error')}")
            return JsonResponse({
                'success': False,
                'error': result.get('error', '导出失败')
            }, status=500)

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
        from django.http import HttpResponse
        response = HttpResponse(file_content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        response['Content-Length'] = len(file_content)

        logger.info(f"成功导出闪卡: task_id={task_id}, format={export_format}, size={len(file_content)} bytes")
        return response

    except Exception as e:
        logger.error(f"导出API处理异常: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)
