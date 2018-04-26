from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('settings', views.settings, name='settings'),

    path('post', views.post, name='post'),
    path('wall/<int:wall_user_id>', views.wall, name='wall'),

    path('follow/<int:follow_user_id>', views.follow, name='follow'),
    path('unfollow/<int:unfollow_user_id>', views.unfollow, name='unfollow'),

    path('search', views.search, name='search'),
    path('followers_of/<int:followed_user_id>', views.followers_of, name='followers_of'),
    path('followings_of/<int:following_user_id>', views.followings_of, name='followings_of'),
]

