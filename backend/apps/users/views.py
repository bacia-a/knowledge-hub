from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.conf import settings
from django.core.files.storage import default_storage
import os
from datetime import datetime
from .serializers import UserRegistrationSerializer, UserSerializer, UserUpdateSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """用户注册"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'user': UserSerializer(user).data,
            'message': '用户注册成功'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """用户登录"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': '必须提供用户名和密码'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': '登录成功'
            })
        else:
            return Response({'error': '用户账户已被禁用'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': '用户名或密码错误'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """用户退出"""
    return Response({'message': '退出登录成功'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """获取用户信息"""
    serializer = UserSerializer(request.user, context={'request': request})
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """更新用户基本信息"""
    user = request.user
    serializer = UserUpdateSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'user': serializer.data,
            'message': '个人信息更新成功'
        })
    return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    """上传用户头像"""
    try:
        if 'avatar' not in request.FILES:
            return Response({'error': '没有上传文件'}, status=400)
        
        avatar_file = request.FILES['avatar']
        
        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if avatar_file.content_type not in allowed_types:
            return Response({'error': '不支持的文件类型'}, status=400)
        
        # 验证文件大小 (2MB)
        if avatar_file.size > 2 * 1024 * 1024:
            return Response({'error': '文件大小不能超过2MB'}, status=400)
        
        # 生成安全的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        file_extension = os.path.splitext(avatar_file.name)[1].lower()
        safe_filename = f'avatar_{timestamp}{file_extension}'
        
        # 创建用户目录
        user_dir = f'avatars/{request.user.id}'
        if not os.path.exists(os.path.join('media', user_dir)):
            os.makedirs(os.path.join('media', user_dir), exist_ok=True)
        
        # 保存文件
        file_path = f'{user_dir}/{safe_filename}'
        filename = default_storage.save(file_path, avatar_file)
        
        # 删除旧头像
        if request.user.avatar:
            old_avatar_path = request.user.avatar.path
            if os.path.exists(old_avatar_path):
                os.remove(old_avatar_path)
        
        # 更新用户头像
        request.user.avatar = file_path
        request.user.save()
        
        # 生成头像URL
        if settings.DEBUG:
            avatar_url = f'{settings.MEDIA_URL}{file_path}'
            if not avatar_url.startswith('/'):
                avatar_url = '/' + avatar_url
        else:
            avatar_url = f'https://kb.devcook.cn{settings.MEDIA_URL}{file_path}'
        
        return Response({
            'avatar_url': avatar_url,
            'message': '头像上传成功'
        })
        
    except Exception as e:
        return Response({'error': f'上传失败: {str(e)}'}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """修改密码"""
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not old_password or not new_password:
        return Response({'error': '必须提供旧密码和新密码'}, status=400)
    
    if not user.check_password(old_password):
        return Response({'error': '旧密码错误'}, status=400)
    
    if len(new_password) < 6:
        return Response({'error': '新密码长度不能少于6位'}, status=400)
    
    user.set_password(new_password)
    user.save()
    
    return Response({'message': '密码修改成功'})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_avatar(request):
    """移除头像"""
    try:
        user = request.user
        if user.avatar:
            # 删除物理文件
            avatar_path = user.avatar.path
            if os.path.exists(avatar_path):
                os.remove(avatar_path)
            
            # 清除数据库记录
            user.avatar = None
            user.save()
        
        return Response({'message': '头像移除成功'})
    except Exception as e:
        return Response({'error': f'移除失败: {str(e)}'}, status=500)