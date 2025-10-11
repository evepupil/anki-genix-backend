from django.urls import path
from business import views

urlpatterns = [
    # 健康检查
    path('health/', views.health_check, name='health_check'),

    # 文本生成闪卡
    path('flashcards/generate/text/', views.generate_flashcards_from_text, name='generate_flashcards_from_text'),
]
