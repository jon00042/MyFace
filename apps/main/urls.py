from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('search_results', views.search_results, name='search_results'),
    path('settings', views.settings, name='settings'),
    path('wall', views.wall, name='wall'),
]

