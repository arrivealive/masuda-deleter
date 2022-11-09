from django.urls import path

from . import views

app_name = 'dummy'
urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.IndexView.as_view(), name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('create/<int:count>', views.create, name='create'),
    path('bookmark', views.bookmark, name='bookmark'),
    path('save', views.save, name='save'),
    path('restore', views.restore, name='restore'),

    path('<int:masuda_id>', views.show, name='show'),
    path('<user_id>/', views.IndexView.as_view(), name='home'),
    path('<user_id>/edit', views.edit, name='edit'),
]