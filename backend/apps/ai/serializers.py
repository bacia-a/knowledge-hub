from rest_framework import serializers
from .models import AIAssistantSession, AIMessage

class AIMessageSerializer(serializers.ModelSerializer):
    """AI消息序列化器"""
    class Meta:
        model = AIMessage
        fields = ('id', 'content', 'is_user', 'created_at')

class AIAssistantSessionSerializer(serializers.ModelSerializer):
    """AI会话序列化器"""
    messages = AIMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AIAssistantSession
        fields = ('id', 'title', 'messages', 'message_count', 'created_at', 'updated_at')
    
    def get_message_count(self, obj):
        return obj.messages.count()

class OutlineRequestSerializer(serializers.Serializer):
    """大纲请求序列化器"""
    topic = serializers.CharField(max_length=200, required=True, label='主题')
    style = serializers.ChoiceField(
        choices=[('专业', '专业'), ('通俗', '通俗'), ('学术', '学术'), ('简洁', '简洁')],
        default='专业',
        label='风格'
    )

class ImproveRequestSerializer(serializers.Serializer):
    """优化请求序列化器"""
    content = serializers.CharField(required=True, label='内容')
    improve_type = serializers.ChoiceField(
        choices=[('grammar', '语法修正'), ('style', '风格优化'), ('expand', '内容扩展')],
        default='style',
        label='优化类型'
    )

class SummaryRequestSerializer(serializers.Serializer):
    """摘要请求序列化器"""
    content = serializers.CharField(required=True, label='内容')
    max_length = serializers.IntegerField(default=200, min_value=50, max_value=500, label='最大长度')