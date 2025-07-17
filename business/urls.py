from django.urls import path
from business.views import FlashcardGenerateView, CatalogGenerateView

urlpatterns = [
    path('flashcards/', FlashcardGenerateView.as_view(), name='generate_flashcards'),
    path('catalog/', CatalogGenerateView.as_view(), name='generate_catalog'),
]