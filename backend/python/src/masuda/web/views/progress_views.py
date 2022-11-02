
from django.http import HttpResponse, Http404
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings

import os
import re
from zoneinfo import ZoneInfo
import json
import logging
import psutil

from web.forms.progress_forms import FilterDeleteForm

from masuda import const
from masudaapi.models import Post, HatenaUser, Progress, StopCommand, Delete_Post

class IndexView(generic.ListView):
    model = Progress
    template_name = 'web/progress/index.html'
    context_object_name = 'progress_list'
    paginate_by = const.HATENA['PAGE_SIZE']
    ordering = '-id'
    
    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
        queryset = queryset.filter(user=user)
        queryset = queryset.prefetch_related('delete_posts')
        queryset = queryset.prefetch_related('stop_commands')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['del_form'] = FilterDeleteForm(None)
        return context

@require_http_methods(['POST'])
def stop(request, pk):
    user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
    progress = get_object_or_404(Progress, pk=pk, user=user)
    stop_command = StopCommand()
    stop_command.progress = progress
    stop_command.save()
    messages.add_message(request, messages.SUCCESS, f'ID:{pk} に停止を要求しました。')
    return redirect('web:progress.index')


@require_http_methods(['POST'])
def force_stop(request, pk):
    user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
    progress = get_object_or_404(Progress, pk=pk, user=user)
    try:
        if not progress.pid:
            raise FileNotFoundError
        pid = int(progress.pid)
        action = Progress.ACTIONS(progress.action).name
        pidfile_path = progress.pidfile
        with open(pidfile_path, 'r') as f:
            pidfile_pid = int(f.read())
            if pidfile_pid != pid:
                # logger = logging.getLogger(__name__)
                # logger.info(int(pidfile_pid), pid)
                progress.status = Progress.STATUS.STOPPED
                progress.memo = 'Force stopped (pid is not compatible).'
                progress.save()
                messages.add_message(request, messages.WARNING, f'ID:{pk} を強制停止しました。(PIDが一致しません)')
                return redirect('web:progress.index')
    except (FileNotFoundError, TypeError):
        progress.status = Progress.STATUS.STOPPED
        progress.memo = 'Force stopped (pid file not found).'
        progress.save()

        messages.add_message(request, messages.WARNING, f'ID:{pk} を強制停止しました。(PIDファイルが見つかりません)')
        return redirect('web:progress.index')

    if action == 'DELETE_ONE':
        prefix = 'delete'
    elif action == 'DELETE':
        prefix = 'selective-delete'
    else:
        prefix = action.lower()
    script_name = prefix + '-masuda'

    process = None
    for proc in psutil.process_iter(['pid', 'cmdline']):
        if script_name in proc.cmdline() and proc.pid == pid:
            process = proc
            break
    
    if not process:
        messages.add_message(request, messages.WARNING, '動作中のプロセスが見つかりません。')
        return redirect('web:progress.index')

    for cp in process.children(recursive=True):
        cp.terminate()
    process.terminate()
    progress.status = Progress.STATUS.STOPPED
    progress.memo = 'Force stopped.'
    progress.save()

    if os.path.isfile(pidfile_path):
        os.remove(pidfile_path)

    messages.add_message(request, messages.SUCCESS, f'ID:{pk} を強制停止しました。')
    return redirect('web:progress.index')


def get(request, pk):
    params = {}
    user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
    progress = Progress.objects.filter(id=pk, user=user).prefetch_related('delete_posts').first()
    if progress:
        params['total'] = progress.total
        params['processed'] = progress.processed
        params['start'] = progress.created_at.astimezone(ZoneInfo('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')
        params['action'] = Progress.ACTIONS(progress.action).label
        params['overview'] = progress.overview
        params['status'] = progress.status
        params['status_label'] = Progress.STATUS(progress.status).label
        params['status_name'] = Progress.STATUS(progress.status).name
        params['memo'] = progress.memo
        # logger = logging.getLogger(__name__)
        # logger.info(progress.delete_posts.values_list('post_id', flat=True))
        delete_post_ids = [post_id for post_id in progress.delete_posts.values_list('post_id', flat=True) if post_id]
        if len(delete_post_ids) > 0:
            params['delete_posts'] = delete_post_ids
        
    json_str = json.dumps(params, ensure_ascii=False, indent=2)
    return HttpResponse(json_str)

def delete(request, pk):
    user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
    progress = get_object_or_404(Progress, pk=pk, user=user)
    progress.delete()
    messages.add_message(request, messages.SUCCESS, f'ID:{pk} を削除しました。')
    return redirect('web:progress.index')

def filter_delete(request):
    params = {}
    form = FilterDeleteForm(request.POST)
    if not form.is_valid():
        params['error'] = form.errors
        result = form.errors
        return render(request, 'web/progress/test.html', {'result': result,})
    
    status = form.cleaned_data.get('status')
    user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
    Progress.objects.filter(status__in=status, user=user).delete()
    messages.add_message(request, messages.SUCCESS, '、'.join([Progress.STATUS(int(state)).label for state in status]) + 'を削除しました。')
    return redirect('web:progress.index')
