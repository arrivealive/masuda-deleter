from django.db import models
from django.utils import timezone
from enum import Enum

# Create your models here.

class HatenaUser(models.Model):
    hatena_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['hatena_id'],
                name='unique_hatenauser_hatena_id'
            )
        ]

class Post(models.Model):
    user = models.ForeignKey(HatenaUser, on_delete=models.CASCADE)
    masuda_id = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    body = models.TextField()
    posted_at = models.DateTimeField()
    response_count = models.IntegerField(default=0)
    bookmark_count = models.IntegerField(blank=True, null=True)
    may_be_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['masuda_id'],
                name='unique_post_hatena_id'
            )
        ]

class Progress(models.Model):
    class STATUS(models.IntegerChoices):
        PENDING = (0, '処理待ち')
        PROCESSING = (1, '処理中')
        PROCESSED = (2, '処理済み')
        STOPPED = (3, '停止')
        ERROR = (9, 'エラー')

    class ACTIONS(models.IntegerChoices):
        FETCH = (1, '取り込み')
        DELETE_ONE = (2, '削除')
        EMPTY = (3, 'Space masuda')
        DELETE = (4, '選択削除')
        RELOAD = (5, '再読み込み')

    user = models.ForeignKey(HatenaUser, on_delete=models.CASCADE, blank=True, null=True)
    total = models.IntegerField(default=0)
    processed = models.IntegerField(default=0)
    action = models.SmallIntegerField(default=0, choices=ACTIONS.choices)
    overview = models.CharField(max_length=200, blank=True, null=True)
    memo = models.TextField(blank=True, null=True)
    status = models.SmallIntegerField(default=0, choices=STATUS.choices)
    pid = models.CharField(max_length=100, blank=True, null=True)
    pidfile = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_status(self):
        return self.STATUS(self.status).label

    def get_action(self):
        return self.ACTIONS(self.action).label

class StopCommand(models.Model):
    progress = models.ForeignKey(Progress, on_delete=models.CASCADE, related_name='stop_commands')
    is_executed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Delete_Post(models.Model):
    user = models.ForeignKey(HatenaUser, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, related_name='delete_posts')
    masuda_id = models.CharField(max_length=200)
    progress = models.ForeignKey(Progress, on_delete=models.CASCADE, null=True, related_name='delete_posts')
    is_executed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Delete_Later_Check(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='delete_later_check')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)