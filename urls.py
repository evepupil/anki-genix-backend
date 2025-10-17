from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    """健康检查端点，用于 fly.io 和其他监控服务"""
    return JsonResponse({'status': 'healthy', 'service': 'anki-genix-backend'})

urlpatterns = [
    path('api/health', health_check, name='health_check'),
    path('api/', include('business.urls')),
] 