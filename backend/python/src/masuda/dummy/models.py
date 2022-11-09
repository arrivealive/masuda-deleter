from django.db import models

class Post(models.Model):
    user_id = models.CharField(max_length=200)
    masuda_id = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    body = models.TextField()
    posted_at = models.DateTimeField()
    response_count = models.IntegerField(default=0)
    bookmark_count = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
