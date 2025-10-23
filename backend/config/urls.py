from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    # 暂时注释掉有问题的路由
    # path('api/', include('categories.urls')),
    # path('api/', include('articles.urls')),
]