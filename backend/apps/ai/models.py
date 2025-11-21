from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AIAssistantSession(models.Model):
    """AI助手会话"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    title = models.CharField(max_length=200, verbose_name='会话标题')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'ai_sessions'
        verbose_name = 'AI会话'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class AIMessage(models.Model):
    """AI消息"""
    session = models.ForeignKey(AIAssistantSession, on_delete=models.CASCADE, 
                               related_name='messages', verbose_name='会话')
    content = models.TextField(verbose_name='消息内容')
    is_user = models.BooleanField(default=True, verbose_name='是否用户消息')
    tokens_used = models.IntegerField(default=0, verbose_name='使用token数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'ai_messages'
        verbose_name = 'AI消息'
        verbose_name_plural = verbose_name
        ordering = ['created_at']
