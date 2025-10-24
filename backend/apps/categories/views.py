from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Category
from .serializers import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def articles(self, request, pk=None):
        category = self.get_object()
        articles = category.articles.all()
        
        # 使用简单的序列化，避免导入冲突
        article_data = []
        for article in articles:
            article_data.append({
                'id': article.id,
                'title': article.title,
                'summary': article.summary,
                'status': article.status,
                'created_at': article.created_at,
            })
        
        return Response({
            "category": category.name,
            "articles": article_data,
            "article_count": articles.count()
        })