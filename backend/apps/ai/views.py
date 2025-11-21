from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import AIAssistantSession, AIMessage
from .services import deepseek_service
from .serializers import (
    AIAssistantSessionSerializer, 
    AIMessageSerializer,
    OutlineRequestSerializer,
    ImproveRequestSerializer,
    SummaryRequestSerializer
)

class AIAssistantViewSet(viewsets.ModelViewSet):
    """AI助手视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = AIAssistantSessionSerializer
    
    def get_queryset(self):
        return AIAssistantSession.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def chat(self, request, pk=None):
        """与AI对话"""
        session = self.get_object()
        message_content = request.data.get('message', '').strip()
        
        if not message_content:
            return Response({'error': '消息内容不能为空'}, status=400)
        
        try:
            with transaction.atomic():
                # 保存用户消息
                user_message = AIMessage.objects.create(
                    session=session,
                    content=message_content,
                    is_user=True
                )
                
                # 获取AI回复
                ai_response = deepseek_service.generate_content(message_content)
                
                # 保存AI回复
                ai_message = AIMessage.objects.create(
                    session=session,
                    content=ai_response,
                    is_user=False,
                    tokens_used=len(ai_response) // 4  # 简单估算token数
                )
                
                # 更新会话时间
                session.save()
            
            return Response({
                'user_message': AIMessageSerializer(user_message).data,
                'ai_message': AIMessageSerializer(ai_message).data
            })
            
        except Exception as e:
            return Response({'error': f'AI服务错误: {str(e)}'}, status=500)
    
    @action(detail=False, methods=['post'])
    def generate_outline(self, request):
        """生成文章大纲"""
        serializer = OutlineRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        topic = serializer.validated_data['topic']
        style = serializer.validated_data.get('style', '专业')
        
        try:
            outline = deepseek_service.generate_article_outline(topic, style)
            return Response(outline)
        except Exception as e:
            return Response({'error': f'生成大纲失败: {str(e)}'}, status=500)
    
    @action(detail=False, methods=['post'])
    def improve_article(self, request):
        """文章润色优化"""
        serializer = ImproveRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        content = serializer.validated_data['content']
        improve_type = serializer.validated_data.get('improve_type', 'style')
        
        try:
            improvement = deepseek_service.improve_writing(content, improve_type)
            return Response(improvement)
        except Exception as e:
            return Response({'error': f'文章优化失败: {str(e)}'}, status=500)
    
    @action(detail=False, methods=['post'])
    def generate_summary(self, request):
        """生成文章摘要"""
        serializer = SummaryRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        content = serializer.validated_data['content']
        max_length = serializer.validated_data.get('max_length', 200)
        
        try:
            summary = deepseek_service.generate_summary(content, max_length)
            return Response({'summary': summary})
        except Exception as e:
            return Response({'error': f'生成摘要失败: {str(e)}'}, status=500)
    
    @action(detail=False, methods=['post'])
    def generate_tags(self, request):
        """生成文章标签"""
        content = request.data.get('content', '').strip()
        count = request.data.get('count', 5)
        
        if not content:
            return Response({'error': '内容不能为空'}, status=400)
        
        try:
            tags = deepseek_service.generate_tags(content, count)
            return Response({'tags': tags})
        except Exception as e:
            return Response({'error': f'生成标签失败: {str(e)}'}, status=500)

class ArticleAIViewSet(viewsets.ViewSet):
    """文章AI功能视图集"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def auto_complete(self, request):
        """文章自动补全"""
        prompt = request.data.get('prompt', '')
        context = request.data.get('context', '')
        
        if not prompt:
            return Response({'error': '补全提示不能为空'}, status=400)
        
        full_prompt = f"上下文：{context}\n\n请继续写作：{prompt}"
        
        try:
            completion = deepseek_service.generate_content(full_prompt, max_tokens=500)
            return Response({'completion': completion})
        except Exception as e:
            return Response({'error': f'自动补全失败: {str(e)}'}, status=500)