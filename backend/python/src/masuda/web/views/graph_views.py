from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.views import generic
from django.views.decorators.http import require_http_methods
from django.db.models import Q, FilteredRelation
from django.db.models import Sum, F, Func, Value, CharField, Count
from django.conf import settings 

import datetime
import logging

import matplotlib.pyplot as plt
import base64
from io import BytesIO

from masuda import const
from masudaapi.models import Post, HatenaUser
from masudaapi.lib import user_getter

def index(request):
    user = user_getter.get()
    fig = plt.figure(tight_layout=True, figsize=(10, 10))
    axes = fig.subplots(3, 1)
    # logger = logging.getLogger(__name__)
    # logger.info(axes[0])

    qs = Post.objects.filter(user=user).annotate(dt=Func(
        F('posted_at'),
        Value('%Y-%m-%d'),
        function='date_format',
        output_field=CharField()
    )).values('dt').annotate(sum_bookmark_count=Sum('bookmark_count')).order_by('dt')
    x = [datetime.datetime.strptime(x['dt'], '%Y-%m-%d') for x in qs]
    y = [y['sum_bookmark_count'] for y in qs]

    axes[0].bar(x, y, width=2)
    axes[0].set_title('Bookmarks per day')
    axes[0].set_xlabel('date')
    axes[0].set_ylabel('bookmarks')

    qs = Post.objects.filter(user=user, bookmark_count__gte=3).annotate(dt=Func(
        F('posted_at'),
        Value('%Y-%m-%d'),
        function='date_format',
        output_field=CharField()
    )).values('dt').annotate(hot_count=Count('bookmark_count')).order_by('dt')
    x = [datetime.datetime.strptime(x['dt'], '%Y-%m-%d') for x in qs]
    y = [y['hot_count'] for y in qs]

    axes[1].bar(x, y, width=2)
    axes[1].set_title('Count of hotentries (3 or more bookmarks) per day')
    axes[1].set_xlabel('date')
    axes[1].set_ylabel('count')

    from_tz = 'UTC'
    to_tz = settings.TIME_ZONE
    qs = Post.objects.filter(user=user, bookmark_count__gt=0).extra(
        {
            'hour': f"date_format(convert_tz(posted_at, '{from_tz}', '{to_tz}'), '%%H')"
        }
    ).values('hour').annotate(hour_count=Count('bookmark_count')).order_by('hour')

    items = {int(y['hour']): y['hour_count'] for y in qs}
    x = range(0, 24)
    y = [items[i] if i in items else 0 for i in x]

    axes[2].bar(x, y)
    axes[2].set_title('Count of bookmarked posts per hour')
    axes[2].set_xlabel('hour')
    axes[2].set_ylabel('count')

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.switch_backend("AGG")
    buffer.seek(0)
    img   = buffer.getvalue()
    chart = base64.b64encode(img)
    chart = chart.decode("utf-8")
    buffer.close()


    return render(request, 'web/graph/graph.html', {'chart':chart})
