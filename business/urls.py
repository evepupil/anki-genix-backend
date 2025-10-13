from django.urls import path
from business import views

urlpatterns = [
    # 健康检查
    path('health/', views.health_check, name='health_check'),

    # 闪卡生成接口
    path('flashcards/generate/text/', views.generate_flashcards_from_text, name='generate_flashcards_from_text'),
    path('flashcards/generate/file/', views.generate_flashcards_from_file, name='generate_flashcards_from_file'),
    path('flashcards/generate/url/', views.generate_flashcards_from_url, name='generate_flashcards_from_url'),

    # 章节闪卡生成接口
    path('flashcards/generate/text/section/', views.generate_flashcards_from_text_section, name='generate_flashcards_from_text_section'),
    path('flashcards/generate/file/section/', views.generate_flashcards_from_file_section, name='generate_flashcards_from_file_section'),

    # 大纲生成接口
    path('catalog/topic/', views.analyze_catalog_from_topic, name='analyze_catalog_from_topic'),
    path('catalog/text/', views.analyze_catalog_from_text, name='analyze_catalog_from_text'),
    path('catalog/file/', views.analyze_catalog_from_file, name='analyze_catalog_from_file'),
]
