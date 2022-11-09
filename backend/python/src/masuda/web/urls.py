from django.urls import path

from . import views
from .views import post_views, progress_views, graph_views

app_name = 'web'
urlpatterns = [
    path('', post_views.IndexView.as_view(), name='index'),
    path('<int:pk>/', post_views.DetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', post_views.delete, name='delete'),
    path('<int:pk>/space_masuda/', post_views.space_masuda, name='space_masuda'),
    path('selective_delete/', post_views.selective_delete, name='selective_delete'),
    path('fetch/', post_views.fetch, name='fetch'),
    path('<int:pk>/reload/', post_views.reload, name='reload'),
    path('<int:pk>/check/<int:checked>/', post_views.check_to_delete, name='check_to_delete'),
    path('to_be_deleted_later/', post_views.to_be_deleted_later, name='to_be_deleted_later'),
    path('uncheck_all/', post_views.uncheck_all, name='uncheck_all'),

    path('progress/', progress_views.IndexView.as_view(), name='progress.index'),
    path('progress/<int:pk>/stop/', progress_views.stop, name='progress.stop'),
    path('progress/<int:pk>/force_stop/', progress_views.force_stop, name='progress.force_stop'),
    path('progress/<int:pk>/delete/', progress_views.delete, name='progress.delete'),
    path('progress/<int:pk>/', progress_views.get, name='progress.get'),
    path('progress/filter_delete/', progress_views.filter_delete, name='progress.filter_delete'),

    path('graph/', graph_views.index, name='graph.index'),
]