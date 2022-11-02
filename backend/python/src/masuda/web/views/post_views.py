from ast import Delete
from this import d
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.views import generic
from django.views.decorators.http import require_http_methods
from django.core import management
from django.contrib import messages
from django.db.models import Q, FilteredRelation
from django.conf import settings 

import re
import time
import datetime
import json
import subprocess
import logging

from masuda import const
from masudaapi.models import Post, HatenaUser, Progress, StopCommand, Delete_Post, Delete_Later_Check
from web.forms.post_forms import PostForm, SearchForm, FetchForm, SelectiveDeleteForm

class IndexView(generic.ListView):
    model = Post
    template_name = 'web/post/index.html'
    context_object_name = 'post_list'
    paginate_by = const.HATENA['PAGE_SIZE']
    ordering = '-posted_at'

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)

        user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
        queryset = queryset.filter(user=user)

        input = SearchForm(self.request.GET)
        if input.is_valid():
            keyword = input.cleaned_data.get('keyword')
            masuda_id = input.cleaned_data.get('masuda_id')
            bookmark_count_from = input.cleaned_data.get('bookmark_count_from')
            bookmark_count_to = input.cleaned_data.get('bookmark_count_to')
            response_count_from = input.cleaned_data.get('response_count_from')
            response_count_to = input.cleaned_data.get('response_count_to')
            posted_at_from = input.cleaned_data.get('posted_at_from')
            posted_at_to = input.cleaned_data.get('posted_at_to')
            may_be_deleted = input.cleaned_data.get('may_be_deleted')
            page_size = input.cleaned_data.get('page_size')
            space_masuda = input.cleaned_data.get('space_masuda')
            delete_later = input.cleaned_data.get('delete_later')

            if space_masuda:
                queryset = queryset.filter(title='', body=' ')
            elif keyword:
                keywords = re.split(' |　', keyword)
                for kw in keywords:
                    queryset = queryset.filter(Q(title__icontains=kw)|Q(body__icontains=kw))
            if masuda_id:
                queryset = queryset.filter(masuda_id=masuda_id)
            if bookmark_count_from is not None:
                queryset = queryset.filter(bookmark_count__gte=bookmark_count_from)
            if bookmark_count_to is not None:
                queryset = queryset.filter(bookmark_count__lte=bookmark_count_to)
            if response_count_from is not None:
                queryset = queryset.filter(response_count__gte=response_count_from)
            if response_count_to is not None:
                queryset = queryset.filter(response_count__lte=response_count_to)
            if posted_at_from:
                queryset = queryset.filter(posted_at__gte=posted_at_from)
            if posted_at_to:
                queryset = queryset.filter(posted_at__lte=posted_at_to)
            if page_size:
                self.paginate_by = page_size
            if may_be_deleted:
                queryset = queryset.filter(may_be_deleted=may_be_deleted)
            if delete_later:
                queryset = queryset.filter(delete_later_check__isnull=False, delete_later_check__checked=True)

        order_by = '-posted_at'
        sort_desc = self.request.GET.get('sort_desc')
        sort_asc = self.request.GET.get('sort_asc')
        if sort_desc in ['id', 'response_count', 'bookmark_count', 'posted_at']:
            order_by = '-' + sort_desc
        elif sort_asc in ['id', 'response_count', 'bookmark_count', 'posted_at']:
            order_by = sort_asc

        if sort_desc in ['posted_at', 'id'] or sort_asc in ['posted_at', 'id']:
            queryset = queryset.order_by(order_by)
        else:
            queryset = queryset.order_by(order_by, '-posted_at')
        queryset = queryset.select_related('delete_later_check')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['form'] = SearchForm(self.request.GET or None)
        context['fetch_form'] = FetchForm(self.request.GET or None)
        context['parameters'] = ''
        context['sort_directions'] = {'id': 'desc', 'posted_at': 'desc', 'bookmark_count': 'desc', 'response_count': 'desc'}
        context['sort_parameter'] = ''
        get_copy = self.request.GET.copy()
        sort_desc = get_copy.pop('sort_desc', ['']).pop()
        sort_asc = get_copy.pop('sort_asc', ['']).pop()
        parameters = get_copy.pop('page', True) and get_copy.urlencode()
        if parameters:
            context['parameters'] = '&' + parameters
        if sort_desc:
            context['sort_parameter'] = '&sort_desc=' + sort_desc
            if sort_desc in context['sort_directions'].keys():
                context['sort_directions'][sort_desc] = 'asc'
        if sort_asc:
            context['sort_parameter'] = '&sort_asc=' + sort_asc
            if sort_asc in context['sort_directions'].keys():
                context['sort_directions'][sort_asc] = 'desc'

        context['anond_url'] = const.HATENA['ANOND_URL']
        context['del_form'] = SelectiveDeleteForm(None)
        context['abbr_length'] = const.ABBREVIATION_LENGTH
        context['use_space_masuda'] = const.USE_SPACE_MASUDA
        
        return context

class DetailView(generic.DetailView):
    model = Post
    template_name = 'web/post/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['anond_url'] = const.HATENA['ANOND_URL']
        return context

def delete(request, pk):
    user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
    post = get_object_or_404(Post, pk=pk, user=user)
    params = {}
    if post.may_be_deleted:
        post.delete()
        params['result'] = 'success'
        params['message'] = f'Deleted id:{pk}({post.masuda_id} may have been deleted)'
        json_str = json.dumps(params, ensure_ascii=False, indent=2)
        return HttpResponse(json_str)

    # result = management.call_command('delete-masuda', post.id)
    try:
        process = subprocess.run(["python", 'manage.py', 'delete-masuda', str(post.id)], check=True, capture_output=True)
        if re.search(r'success', process.stdout.decode()):
            params['result'] = 'success'
            params['message'] = f'Deleted id:{pk}({post.masuda_id})'
        else:
            params['result'] = 'failure'
            params['message'] = f'Failed to delete id:{pk}({post.masuda_id})'
    except subprocess.CalledProcessError as e:
        params['result'] = 'failure'
        params['message'] = f'Failed to delete id:{pk}({post.masuda_id})'

    json_str = json.dumps(params, ensure_ascii=False, indent=2)
    return HttpResponse(json_str)

def space_masuda(request, pk):
    user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
    post = get_object_or_404(Post, pk=pk, user=user)
    params = {}
    # result = management.call_command('empty-masuda', post.id)
    try:
        process = subprocess.run(["python", 'manage.py', 'empty-masuda', str(post.id)], check=True, capture_output=True)
        if re.search(r'success', process.stdout.decode()):
            params['result'] = 'success'
            params['message'] = f'Emptied id:{pk}({post.masuda_id})'
        else:
            params['result'] = 'failure'
            params['message'] = f'Failed to empty id:{pk}({post.masuda_id})'
    except subprocess.CalledProcessError as e:
        params['result'] = 'failure'
        params['message'] = f'Failed to empty id:{pk}({post.masuda_id})'

    json_str = json.dumps(params, ensure_ascii=False, indent=2)
    return HttpResponse(json_str)

def reload(request, pk):
    user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
    post = get_object_or_404(Post, pk=pk, user=user)
    params = {}
    abbr_length = const.ABBREVIATION_LENGTH
    # result = management.call_command('empty-masuda', post.id)
    try:
        process = subprocess.run(["python", 'manage.py', 'reload-masuda', str(post.id)], check=True, capture_output=True)
        if re.search(r'success', process.stdout.decode()):
            params['result'] = 'success'
            params['message'] = f'Reloaded id:{pk}({post.masuda_id})'
            post = Post.objects.filter(id=pk).first()
            params['title'] = post.title[0:abbr_length - 1] + ('...' if len(post.title) > abbr_length else '')
            params['body'] = post.body[0:abbr_length - 1] + ('...' if len(post.body) > abbr_length else '')
            params['response_count'] = post.response_count
            params['bookmark_count'] = post.bookmark_count
        else:
            params['result'] = 'failure'
            params['message'] = f'Failed to reload id:{pk}({post.masuda_id})'
    except subprocess.CalledProcessError as e:
        params['result'] = 'failure'
        params['message'] = f'Failed to reload id:{pk}({post.masuda_id})'

    json_str = json.dumps(params, ensure_ascii=False, indent=2)
    return HttpResponse(json_str)

def selective_delete(request):
    params = {}
    user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
    # result = management.call_command('selective-delete-masuda')

    checks = Delete_Later_Check.objects.filter(post__user=user)
    if checks.count() == 0:
        params['result'] = 'failure'
        params['message'] = 'No posts to be deleted.'
        json_str = json.dumps(params, ensure_ascii=False, indent=2)
        return HttpResponse(json_str)

    progress = Progress.objects.create(
        user = user,
        total = 0,
        processed = 0,
        action = Progress.ACTIONS.DELETE,
        overview = '',
        status = Progress.STATUS.PENDING
    )
    subprocess.Popen(["python", 'manage.py', 'selective-delete-masuda', '--progress', str(progress.id)])

    statusList = [Progress.STATUS.PENDING, Progress.STATUS.PROCESSING]
    time.sleep(2)
    progress.refresh_from_db()
    # progress = Progress.objects.filter(action=Progress.ACTIONS.DELETE, status__in = statusList).order_by('-id').first()

    params['progress_id'] = progress.id
    json_str = json.dumps(params, ensure_ascii=False, indent=2)
    return HttpResponse(json_str)

def fetch(request):
    form = FetchForm(request.POST)
    params = {}
    if not form.is_valid():
        return HttpResponse(form.errors.as_json())

    page_from = form.cleaned_data.get('page_from')
    page_to = form.cleaned_data.get('page_to')
    # result = management.call_command('fetch-masuda', page_from, page_to)

    user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
    progress = Progress.objects.create(
        user = user,
        total = 0,
        processed = 0,
        action = Progress.ACTIONS.FETCH,
        overview = '',
        status = Progress.STATUS.PENDING
    )

    # logger = logging.getLogger(__name__)

    process = subprocess.Popen(["python", 'manage.py', 'fetch-masuda', str(page_from), str(page_to), '--progress', str(progress.id)])
    
    # statusList = [Progress.STATUS.PENDING, Progress.STATUS.PROCESSING]
    time.sleep(2)
    # logger.info('process.poll()')
    # logger.info(process.poll())
    # progress = Progress.objects.filter(action=Progress.ACTIONS.FETCH, status__in=statusList, user=user).order_by('-id').first()
    progress.refresh_from_db()

    # logger.info(process.poll())
    params['progress_id'] = progress.id
    json_str = json.dumps(params, ensure_ascii=False, indent=2)
    return HttpResponse(json_str)

def check_to_delete(request, pk, checked):
    user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
    post = get_object_or_404(Post, pk=pk, user=user)
    params = {}
    if checked == 1:
            Delete_Later_Check.objects.get_or_create(
                post=post,
            )
    else:
        Delete_Later_Check.objects.filter(post=post).delete()

    params['result'] = True
    json_str = json.dumps(params, ensure_ascii=False, indent=2)
    return HttpResponse(json_str)

def uncheck_all(request):
    user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
    Delete_Later_Check.objects.filter(user=user).delete()
    params = {}
    params['result'] = True
    json_str = json.dumps(params, ensure_ascii=False, indent=2)
    return HttpResponse(json_str)

def to_be_deleted_later(request):
    user = HatenaUser.objects.filter(hatena_id=const.HATENA["ID"]).first()
    delete_later_checks = Delete_Later_Check.objects.filter(post__user=user).select_related('post')
    data = [
        {
            'id': delete_later_check.post.id,
            'masuda_id': delete_later_check.post.masuda_id,
            'title': delete_later_check.post.title if delete_later_check.post.title.strip() != '' else delete_later_check.post.body[0:10] + ('...' if len(delete_later_check.post.body) > 10 else ''),
            'bookmark_count': delete_later_check.post.bookmark_count
        }
        for delete_later_check in delete_later_checks
    ]
    params = {}
    params['result'] = data
    json_str = json.dumps(params, ensure_ascii=False, indent=2)
    return HttpResponse(json_str)
