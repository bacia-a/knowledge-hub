from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Category
from .serializers import CategorySerializer
from apps.articles.serializers import ArticleListSerializer
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
        from articles.serializers import ArticleListSerializer
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)