import json
import logging
import requests
from typing import Dict, List, Optional
from django.conf import settings
from .config import DeepSeekConfig
import time

logger = logging.getLogger(__name__)

class DeepSeekService:
    """DeepSeek AI服务"""
    
    def __init__(self):
        self.api_key = DeepSeekConfig.API_KEY
        self.base_url = DeepSeekConfig.BASE_URL
        self.model = DeepSeekConfig.CHAT_MODEL
        self.timeout = 60  # 增加超时时间到60秒
        self.max_retries = 3  # 最大重试次数
    
    def generate_content(self, prompt: str, max_tokens: int = None) -> str:
        """生成内容 - 增加重试机制"""
        if not self.api_key:
            raise Exception("DeepSeek API Key未配置")
        
        max_tokens = max_tokens or DeepSeekConfig.DEFAULT_MAX_TOKENS
        
        # 重试机制
        for attempt in range(self.max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                    "stream": False
                }
                
                logger.info(f"尝试调用DeepSeek API (第{attempt + 1}次)...")
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("DeepSeek API调用成功")
                    return result["choices"][0]["message"]["content"]
                else:
                    error_msg = f"DeepSeek API错误: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    
                    # 如果是服务器错误，重试
                    if response.status_code >= 500:
                        if attempt < self.max_retries - 1:
                            wait_time = 2 ** attempt  # 指数退避
                            logger.info(f"等待 {wait_time} 秒后重试...")
                            time.sleep(wait_time)
                            continue
                    
                    raise Exception(error_msg)
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"API请求超时，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    error_msg = "DeepSeek API请求超时，请检查网络连接或稍后重试"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"网络连接错误，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    error_msg = "网络连接错误，请检查网络设置"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
            except Exception as e:
                error_msg = f"DeepSeek服务错误: {str(e)}"
                logger.error(error_msg)
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(error_msg)
        
        # 所有重试都失败
        raise Exception("DeepSeek服务暂时不可用，请稍后重试")
    
    def generate_article_outline(self, topic: str, style: str = "专业") -> Dict:
        """生成文章大纲"""
        prompt = f"""请为主题"{topic}"生成一个{style}风格的文章大纲。

要求：
1. 包含清晰的章节结构（3-5个主要章节）
2. 每个章节要有3-5个具体的内容要点
3. 适合技术文档的格式
4. 包含引言和总结部分
5. 返回严格的JSON格式

JSON格式示例：
{{
    "title": "文章标题",
    "sections": [
        {{
            "title": "章节标题", 
            "points": ["要点1", "要点2", "要点3"]
        }}
    ]
}}

请直接返回JSON，不要其他文字。"""
        
        try:
            result = self.generate_content(prompt)
            # 提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # 如果无法解析JSON，返回默认结构
                return self._create_default_outline(topic)
        except Exception as e:
            logger.error(f"生成大纲失败: {e}")
            return self._create_default_outline(topic)
    
    def _create_default_outline(self, topic: str) -> Dict:
        """创建默认大纲"""
        return {
            "title": f"{topic}",
            "sections": [
                {
                    "title": "引言",
                    "points": ["背景介绍", "问题陈述", "目标意义"]
                },
                {
                    "title": "核心内容",
                    "points": ["关键概念", "技术原理", "实施步骤"]
                },
                {
                    "title": "实践应用",
                    "points": ["使用场景", "最佳实践", "注意事项"]
                },
                {
                    "title": "总结",
                    "points": ["内容回顾", "核心价值", "未来展望"]
                }
            ]
        }
    
    def improve_writing(self, content: str, improve_type: str = "style") -> Dict:
        """文章润色优化"""
        improve_prompts = {
            "grammar": f"""请修正以下内容的语法错误和拼写错误，保持原意不变：

{content}

要求：
1. 只修正错误，不要改变内容结构
2. 保持专业的技术文档风格
3. 直接返回修正后的内容""",

            "style": f"""请优化以下内容的写作风格，使其更加专业、流畅：

{content}

要求：
1. 保持核心内容不变
2. 优化句子结构和表达方式
3. 提升技术文档的专业性和可读性
4. 直接返回优化后的内容""",

            "expand": f"""请扩展以下内容，增加技术细节和深度：

{content}

要求：
1. 保持原文主旨和技术准确性
2. 增加相关的技术细节和实际例子
3. 扩展后的内容应该是原文的1.5-2倍长度
4. 直接返回扩展后的内容"""
        }
        
        prompt = improve_prompts.get(improve_type, improve_prompts["style"])
        
        try:
            improved_content = self.generate_content(prompt, max_tokens=4000)
            
            return {
                "improved_content": improved_content,
                "suggestions": self._generate_writing_suggestions(content),
                "overall_rating": self._rate_writing_quality(content),
                "provider": "deepseek"
            }
        except Exception as e:
            logger.error(f"文章优化失败: {e}")
            return {
                "improved_content": content,
                "suggestions": ["AI服务暂时不可用"],
                "overall_rating": "N/A",
                "provider": "deepseek"
            }
    
    def _generate_writing_suggestions(self, content: str) -> List[str]:
        """生成写作建议"""
        if len(content) < 50:
            return ["内容较短，建议扩展更多技术细节"]
        
        prompt = f"""请为以下技术内容提供3条具体的写作改进建议：

{content[:800]}

要求：
1. 针对技术文档的特点提出建议
2. 每条建议要具体可行
3. 用中文返回，用分号分隔
4. 不要编号，直接返回建议内容"""
        
        try:
            suggestions = self.generate_content(prompt, max_tokens=500)
            return [s.strip() for s in suggestions.split(";") if s.strip()][:3]
        except:
            return [
                "建议：优化技术术语的使用一致性",
                "建议：增加具体的代码或配置示例", 
                "建议：改善段落之间的逻辑衔接"
            ]
    
    def _rate_writing_quality(self, content: str) -> str:
        """评估写作质量"""
        if len(content) < 50:
            return "内容过短"
        
        prompt = f"""请从技术文档的角度评估以下内容的写作质量（满分10分）：

{content[:500]}

要求：
1. 从专业性、清晰度、逻辑性等方面评估
2. 只返回分数数字
3. 不要其他文字"""
        
        try:
            rating = self.generate_content(prompt, max_tokens=10)
            # 提取数字
            import re
            numbers = re.findall(r'\d+', rating)
            if numbers:
                score = min(10, max(1, int(numbers[0])))
                return f"{score}/10"
        except:
            pass
        
        return "8/10"  # 默认评分
    
    def generate_summary(self, content: str, max_length: int = 200) -> str:
        """生成文章摘要"""
        if len(content) < 100:
            return content
        
        prompt = f"""请为以下技术文章生成一个简洁的摘要，长度不超过{max_length}字：

{content[:3000]}

要求：
1. 抓住技术核心观点和关键信息
2. 突出技术要点和实践价值
3. 语言精炼，逻辑清晰
4. 直接返回摘要内容"""
        
        try:
            summary = self.generate_content(prompt, max_tokens=300)
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            return summary
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return content[:max_length] + ("..." if len(content) > max_length else "")
    
    def generate_tags(self, content: str, count: int = 5) -> List[str]:
        """生成文章标签"""
        if len(content) < 50:
            return ["技术", "文档"]
        
        prompt = f"""根据以下技术内容，生成{count}个相关的技术标签：

{content[:1500]}

要求：
1. 标签要体现技术关键词
2. 每个标签2-4个汉字
3. 用中文逗号分隔返回
4. 不要其他文字"""
        
        try:
            result = self.generate_content(prompt, max_tokens=100)
            tags = [tag.strip() for tag in result.split("，") if tag.strip()]
            unique_tags = list(dict.fromkeys(tags))[:count]
            return unique_tags if unique_tags else ["技术", "开发", "文档", "实践"]
        except:
            return ["技术", "开发", "文档", "实践", "总结"]

# 全局DeepSeek服务实例
deepseek_service = DeepSeekService()