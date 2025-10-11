import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from business.flashcard import FlashcardBusiness
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
        "text": "要学习的文本内容"
    }

    响应 (JSON):
    {
        "success": true,
        "cards": [
            {
                "question": "问题",
                "answer": "答案"
            }
        ]
    }
    """
    try:
        # 解析请求数据
        data = json.loads(request.body)
        text_content = data.get('text', '').strip()

        logger.info(f"收到文本闪卡生成请求，文本: {text_content}")

        # 验证输入
        if not text_content:
            logger.warning("文本内容为空")
            return JsonResponse({
                'success': False,
                'error': '请提供要学习的文本内容'
            }, status=400)

        # 调用业务层生成闪卡
        biz = FlashcardBusiness()
        result = biz.generate_flashcards_from_text(text_content)

        # 返回结果
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


@require_http_methods(["GET"])
def health_check(request):
    """
    健康检查接口
    """
    return JsonResponse({
        'status': 'ok',
        'service': 'ankigenix-backend'
    })
