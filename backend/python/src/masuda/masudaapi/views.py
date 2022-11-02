from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters

from .models import HatenaUser, Post
from .serializer import HatenaUserSerializer, PostSerializer


class HatenaUserViewSet(viewsets.ModelViewSet):
    queryset = HatenaUser.objects.all()
    serializer_class = HatenaUserSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer