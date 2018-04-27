from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('settings', views.settings, name='settings'),

    path('add_post', views.add_post, name='add_post'),
    path('del_post/<int:post_id>', views.del_post, name='del_post'),
    path('add_comment/<int:post_id>', views.add_comment, name='add_comment'),
    path('del_comment/<int:comment_id>', views.del_comment, name='del_comment'),
    path('wall/<int:wall_user_id>', views.wall, name='wall'),

    path('follow/<int:follow_user_id>', views.follow, name='follow'),
    path('unfollow/<int:unfollow_user_id>', views.unfollow, name='unfollow'),

    path('search', views.search, name='search'),
    path('followers_of/<int:followed_user_id>', views.followers_of, name='followers_of'),
    path('followings_of/<int:following_user_id>', views.followings_of, name='followings_of'),
]

