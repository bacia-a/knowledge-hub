from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/remove-avatar/', views.remove_avatar, name='remove_avatar'),
]