from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    article_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'color', 'article_count', 'created_at')
        read_only_fields = ('user', 'article_count')
    
    def get_article_count(self, obj):
        return obj.articles.count()
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)