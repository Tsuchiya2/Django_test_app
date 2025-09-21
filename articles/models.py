from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class Article(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="投稿者"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="タイトル"
    )
    content = models.TextField(
        verbose_name="内容"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新日時"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "記事"
        verbose_name_plural = "記事"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('articles:detail', kwargs={'pk': self.pk})
