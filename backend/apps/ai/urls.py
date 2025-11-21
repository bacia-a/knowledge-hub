# apps/ai/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sessions', views.AIAssistantViewSet, basename='ai-session')

urlpatterns = [
    path('', include(router.urls)),
    
    # 单独注册action路由，确保路径正确
    path('generate_outline/', views.AIAssistantViewSet.as_view({'post': 'generate_outline'}), name='generate-outline'),
    path('improve_article/', views.AIAssistantViewSet.as_view({'post': 'improve_article'}), name='improve-article'),
    path('generate_summary/', views.AIAssistantViewSet.as_view({'post': 'generate_summary'}), name='generate-summary'),
    path('generate_tags/', views.AIAssistantViewSet.as_view({'post': 'generate_tags'}), name='generate-tags'),
    
    # 文章相关AI功能
    path('articles/auto_complete/', views.ArticleAIViewSet.as_view({'post': 'auto_complete'}), name='auto-complete'),
]