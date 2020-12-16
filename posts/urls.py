from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # раздел администратора
    path('admin/',
         admin.site.urls,
         name='admin'),
    path('group/<slug:slug>/',
         views.group_post,
         name='group_post'),
    path('new/',
         views.new_post,
         name='new_post'),
    path("follow/",
         views.follow_index,
         name="follow_index"),
    path("<str:username>/follow/",
         views.profile_follow,
         name="profile_follow"),
    path("<str:username>/unfollow/",
         views.profile_unfollow,
         name="profile_unfollow"),
    # Профайл пользователя
    path('<str:username>/',
         views.profile,
         name='profile'),
    # Просмотр записи
    path('<str:username>/<int:post_id>/',
         views.post_view,
         name='post'),
    path('<str:username>/<int:post_id>/edit/',
         views.post_edit,
         name='post_edit'),
    path("<str:username>/<int:post_id>/comment",
         views.add_comment,
         name="add_comment"),
    path("<str:username>/<int:post_id>/like/",
         views.post_like,
         name="post_like"),
    path("<str:username>/<int:post_id>/deletelike/",
         views.post_delete_like,
         name="post_delete_like"),
    ]

