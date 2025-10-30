from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from django.http import JsonResponse
import os
from datetime import datetime

from .models import Article
from .serializers import ArticleListSerializer, ArticleDetailSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # 类级别的权限设置

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

# 独立的图片上传视图函数
@api_view(['POST'])
def upload_image(request):
    """
    富文本编辑器图片上传
    """
    # 手动检查认证，因为这是独立视图函数
    if not request.user.is_authenticated:
        return JsonResponse({
            'errno': 1,
            'message': '未认证用户'
        }, status=401)
    
    if 'image' not in request.FILES:
        return JsonResponse({
            'errno': 1,
            'message': '没有上传文件'
        })
    
    image_file = request.FILES['image']
    
    # 验证文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if image_file.content_type not in allowed_types:
        return JsonResponse({
            'errno': 1,
            'message': '不支持的文件类型'
        })
    
    # 验证文件大小 (2MB)
    if image_file.size > 2 * 1024 * 1024:
        return JsonResponse({
            'errno': 1,
            'message': '文件大小不能超过2MB'
        })
    
    # 生成安全的文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_extension = os.path.splitext(image_file.name)[1]
    safe_filename = f'{timestamp}{file_extension}'
    
    # 保存文件
    file_path = f'editor_images/{request.user.id}/{safe_filename}'
    filename = default_storage.save(file_path, image_file)
    file_url = default_storage.url(filename)
    
    # 构建完整的URL
    full_url = request.build_absolute_uri(file_url)
    
    return JsonResponse({
        'errno': 0,
        'data': {
            'url': full_url,
            'alt': image_file.name,
            'href': full_url
        }
    })