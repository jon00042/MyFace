from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('follow/<int:follow_user_id>', views.follow, name='follow'),
    path('followers_of/<int:follow_user_id>', views.followers_of, name='followers_of'),
    path('followings_of/<int:follow_user_id>', views.followings_of, name='followings_of'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('post', views.post, name='post'),
    path('search', views.search, name='search'),
    path('settings', views.settings, name='settings'),
    path('wall/<int:wall_user_id>', views.wall, name='wall'),
    path('unfollow/<int:unfollow_user_id>', views.unfollow, name='unfollow'),
]

