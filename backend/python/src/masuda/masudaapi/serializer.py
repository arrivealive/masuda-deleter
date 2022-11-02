# coding: utf-8
from .models import HatenaUser, Post
from rest_framework import serializers

class HatenaUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = HatenaUser
        fields = ('id', 'hatena_id')


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title', 'body', 'posted_at', 'masuda_id')