from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from django.http import JsonResponse
import os
from datetime import datetime

from .models import Article
from .serializers import ArticleListSerializer, ArticleDetailSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        return ArticleDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'])
    def published(self, request):
        """获取已发布的文章"""
        articles = Article.objects.filter(author=request.user, status='published')
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def drafts(self, request):
        """获取草稿文章"""
        articles = Article.objects.filter(author=request.user, status='draft')
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """发布文章"""
        article = self.get_object()
        article.status = 'published'
        article.save()
        serializer = self.get_serializer(article)
        return Response(serializer.data)

# 修复：添加权限装饰器
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    """
    富文本编辑器图片上传
    """
    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'errno': 1,
                'message': '没有上传文件'
            }, status=400)
        
        image_file = request.FILES['image']
        
        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return JsonResponse({
                'errno': 1,
                'message': '不支持的文件类型，仅支持 JPEG、PNG、GIF、WebP'
            }, status=400)
        
        # 验证文件大小 (2MB)
        if image_file.size > 2 * 1024 * 1024:
            return JsonResponse({
                'errno': 1,
                'message': '文件大小不能超过2MB'
            }, status=400)
        
        # 生成安全的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        file_extension = os.path.splitext(image_file.name)[1].lower()
        safe_filename = f'editor_{timestamp}{file_extension}'
        
        # 创建用户目录
        user_dir = f'editor_images/{request.user.id}'
        if not os.path.exists(os.path.join('media', user_dir)):
            os.makedirs(os.path.join('media', user_dir), exist_ok=True)
        
        # 保存文件
        file_path = f'{user_dir}/{safe_filename}'
        filename = default_storage.save(file_path, image_file)
        
        # 生成完整的图片URL
        # 在开发环境中使用相对路径，在生产环境中使用完整URL
        if settings.DEBUG:
            # 开发环境：使用相对路径
            image_url = f'{settings.MEDIA_URL}{file_path}'
            if not image_url.startswith('/'):
                image_url = '/' + image_url
        else:
            # 生产环境：使用完整URL
            image_url = f'https://kb.devcook.cn{settings.MEDIA_URL}{file_path}'
        
        print(f"图片上传成功: {image_url}")  # 调试日志
        
        return JsonResponse({
            'errno': 0,
            'data': {
                'url': image_url,
                'alt': image_file.name,
                'href': image_url
            }
        })
        
    except Exception as e:
        print(f"图片上传错误: {str(e)}")
        return JsonResponse({
            'errno': 1,
            'message': f'上传失败: {str(e)}'
        }, status=500)
