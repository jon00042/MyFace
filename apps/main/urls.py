from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('post', views.post, name='post'),
    path('search', views.search, name='search'),
    path('settings', views.settings, name='settings'),
    path('wall/<int:wall_user_id>', views.wall, name='wall'),
]

