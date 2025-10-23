from django.db import models

class Category(models.Model):
    """文章分类模型"""
    name = models.CharField(max_length=50, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    color = models.CharField(max_length=7, default='#409EFF', verbose_name='颜色')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='所属用户')  # 使用字符串引用
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'categories'
        verbose_name = '分类'
        verbose_name_plural = verbose_name
        unique_together = ['name', 'user']
        app_label = 'categories'  # 添加这一行

    def __str__(self):
        return self.name