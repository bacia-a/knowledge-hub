#!/usr/bin/env python3
"""
图片上传功能测试脚本
用于验证图片上传和加载功能是否正常工作
"""

import os
import sys
import django

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 设置Django
django.setup()

from django.conf import settings

def test_media_config():
    """测试媒体文件配置"""
    print("=== 媒体文件配置测试 ===")
    print(f"DEBUG模式: {settings.DEBUG}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    # 检查media目录是否存在
    media_dir_exists = os.path.exists(settings.MEDIA_ROOT)
    print(f"MEDIA_ROOT目录存在: {media_dir_exists}")
    
    if media_dir_exists:
        # 列出media目录内容
        print(f"MEDIA_ROOT目录内容:")
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            level = root.replace(settings.MEDIA_ROOT, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")

def test_image_url_generation():
    """测试图片URL生成逻辑"""
    print("\n=== 图片URL生成测试 ===")
    
    # 模拟文件路径
    test_file_path = "editor_images/1/test_image.png"
    
    if settings.DEBUG:
        # 开发环境URL
        image_url = f'{settings.MEDIA_URL}{test_file_path}'
        if not image_url.startswith('/'):
            image_url = '/' + image_url
        print(f"开发环境图片URL: {image_url}")
    else:
        # 生产环境URL
        image_url = f'https://kb.devcook.cn{settings.MEDIA_URL}{test_file_path}'
        print(f"生产环境图片URL: {image_url}")

if __name__ == "__main__":
    print("图片上传功能诊断工具")
    print("=" * 50)
    
    try:
        test_media_config()
        test_image_url_generation()
        
        print("\n=== 建议 ===")
        if settings.DEBUG:
            print("1. 确保Django开发服务器正在运行: python manage.py runserver")
            print("2. 前端开发服务器应该使用代理配置")
            print("3. 检查浏览器控制台是否有CORS错误")
        else:
            print("1. 确保生产服务器正确配置了静态文件和媒体文件服务")
            print("2. 检查Nginx/Apache配置是否正确代理/media路径")
            
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
