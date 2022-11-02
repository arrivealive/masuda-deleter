from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views import generic
from faker import Faker
import logging
from datetime import datetime 
from django.utils import timezone
from dateutil import tz
from masuda import const
from dummy.models import Post
import re
import json
import urllib.parse
from django.core import management
import os
from django.conf import settings
# Create your views here.

def index(request):
    user = None
    if request.user.is_authenticated:
        user = request.user
        logger = logging.getLogger(__name__)
        logger.info(user)

    return render(request, 'dummy/top.html', {'user': user})

class IndexView(generic.ListView):
    model = Post
    template_name = 'dummy/index.html'
    context_object_name = 'post_list'
    paginate_by = const.HATENA['PAGE_SIZE']
    ordering = '-posted_at'

    def get(self, *args, **kwargs):
        if 'user_id' in kwargs:
            if not self.request.user.is_authenticated:
                return redirect('dummy:index')
            if self.request.user.username != kwargs['user_id']:
                return redirect('dummy:index')

        logger = logging.getLogger(__name__)
        logger.info( self.request)

        return super(IndexView, self).get(self.request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        # logger = logging.getLogger(__name__)
        # logger.info(self.kwargs)

        if 'user_id' in self.kwargs:
            if self.request.user.is_authenticated and self.request.user.username == self.kwargs['user_id']:
                queryset = queryset.filter(user_id=self.kwargs['user_id'])

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        user = None
        if self.request.user.is_authenticated:
            user = self.request.user

        context['user'] = user
        logger = logging.getLogger(__name__)
        # logger.info(user)
        # logger.info(self.kwargs)
        day_list = {}
        for post in context['post_list']:
            posted_at = convert_time_to_jst(post.posted_at)
            datekey = datetime.strftime(posted_at, '%Y%m%d')
            if datekey not in day_list:
                day_list[datekey] = {'date': datetime.strftime(posted_at, '%Y-%m-%d'), 'posts': []}
            # post.lines = list(map(lambda x: '<p>' + x + '</p>', re.split(r'\n', post.body)))
            post.lines = re.split(r'\n', post.body)
            day_list[datekey]['posts'].append(post)
        context['day_list'] = day_list
        context['my'] = 'user_id' in self.kwargs
        
        # context['now'] = datetime.strftime(post.posted_at.astimezone(tz.gettz('Asia/Tokyo')), '%Y%m%d %H:%M')
        return context

def login(request):
    if (request.method == 'POST'):
        username = request.POST['key']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('dummy:index')
    return render(request, 'dummy/login.html')

def logout(request):
    auth_logout(request)
    return redirect('dummy:index')

def show(request, masuda_id):
    post = Post.objects.filter(masuda_id=masuda_id).first()
    if post:
        post.lines = re.split(r'\n', post.body)
    user = None
    if request.user.is_authenticated:
        user = request.user
    return render(request, 'dummy/show.html', {'post': post, 'user': user})

def edit(request, user_id):
    if not request.user.is_authenticated:
        return redirect('dummy:index')
    if request.user.username != user_id:
        return redirect('dummy:index')
    
    logger = logging.getLogger(__name__)
    post = None
    # logger.info(request.GET)
    if request.method == 'POST':
        title = request.POST['title']
        body = request.POST['body']
        id = request.POST['id']
        if id:
            post = Post.objects.filter(masuda_id=id).first()
            if 'delete' in request.POST:
                post.delete()
                return redirect('dummy:index')
        else:
            post = Post()
            now = datetime.now()
            post.posted_at = now
            post.user_id = user_id
            id = datetime.strftime(now, '%Y%m%d%H%M%S')
            post.masuda_id = id
        post.title = title
        post.body = body
        post.save()
        return redirect('dummy:show', masuda_id=id)

    # logger = logging.getLogger(__name__)
    # logger.info(request.GET)
    if 'id' in request.GET:
        id = request.GET['id']
        post = Post.objects.filter(masuda_id=id).first()
    
    if post:
        post.date = datetime.strftime(post.posted_at, '%Y-%m-%d')
    else:
        post = Post()
        post.date = datetime.strftime(datetime.now(), '%Y-%m-%d')
    
    return render(request, 'dummy/edit.html', {'post': post, 'user': request.user})


def create(request, count):
    user_id = ''
    if request.user.is_authenticated:
        user = request.user
        user_id = user.username 
    fake = Faker('ja_JP')
    for i in range(count):
        posted_at = fake.date_time_between(datetime.strptime('2001-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
        masuda_id = datetime.strftime(posted_at, '%Y%m%d%H%M%S')
        Post.objects.create(
            user_id=user_id,
            masuda_id=masuda_id,
            title=fake.sentence(),
            body=fake.text(),
            posted_at=timezone.make_aware(posted_at),
            response_count=fake.pyint(0, 100),
            bookmark_count=fake.pyint(0, 3000)
        )

    return HttpResponse("created")

def bookmark(request):
    urls = request.GET.getlist('url', None)
    ids = [re.search(r'([\d]{14,})\/?$', urllib.parse.unquote(url)).group(1) for url in urls]
    posts = Post.objects.filter(masuda_id__in=ids)
    bookmarks = {}
    for url, masuda_id in zip(urls, ids):
        bc = 0
        for post in posts:
            if post.masuda_id == masuda_id:
                bc = post.bookmark_count
                break
        bookmarks[url] = bc
    result = json.dumps(bookmarks)
    return HttpResponse(result)

def restore(request):
    path = os.path.join(settings.BASE_DIR, 'dummy/files/dummy.json')
    management.call_command('loaddata', path)
    return HttpResponse('restored')

def save(request):
    path = os.path.join(settings.BASE_DIR, 'dummy/files/dummy.json')
    with open(path, 'w') as f:
        management.call_command('dumpdata', 'dummy', stdout=f)
    return HttpResponse('saved')

def convert_time_to_jst(dt:datetime):
    jst = tz.gettz('Asia/Tokyo')
    return dt.astimezone(jst)
