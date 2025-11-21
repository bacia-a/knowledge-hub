from django.conf import settings

class DeepSeekConfig:
    """DeepSeek配置"""
    API_KEY = settings.DEEPSEEK_API_KEY
    BASE_URL = "https://api.deepseek.com/v1"
    CHAT_MODEL = "deepseek-chat"
    DEFAULT_MAX_TOKENS = 2000
    TIMEOUT = 30