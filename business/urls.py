from django.urls import path
from business.views import FlashcardGenerateView

urlpatterns = [
    path('flashcards/', FlashcardGenerateView.as_view(), name='generate_flashcards'),
] 