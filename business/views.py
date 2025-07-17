from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from business.flashcard import FlashcardBusiness

class FlashcardGenerateView(APIView):
    """
    POST /api/flashcards/
    请求参数: {card_type, topic, number, lang}
    返回: 闪卡列表
    """
    def post(self, request):
        card_type = request.data.get('card_type')
        topic = request.data.get('topic')
        number = request.data.get('number', 10)
        lang = request.data.get('lang', 'zh')
        if not card_type or not topic:
            return Response({'error': 'card_type和topic为必填项'}, status=status.HTTP_400_BAD_REQUEST)
        biz = FlashcardBusiness()
        try:
            cards = biz.generate_flashcards(card_type, topic, number, lang)
            return Response(cards, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CatalogGenerateView(APIView):
    """
    POST /api/catalog/
    请求参数: {topic, lang}
    返回: 结构化目录列表
    """
    def post(self, request):
        topic = request.data.get('topic')
        lang = request.data.get('lang', 'zh')

        if not topic:
            return Response({'error': 'topic为必填项'}, status=status.HTTP_400_BAD_REQUEST)

        biz = FlashcardBusiness()
        try:
            catalog = biz.analyze_catalog(topic, lang)
            return Response({
                'topic': topic,
                'lang': lang,
                'catalog': catalog
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)