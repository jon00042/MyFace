from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Post(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ################################
    post_user = models.ForeignKey(User, related_name='posted_by', on_delete=models.PROTECT)
    wall_user = models.ForeignKey(User, related_name='on_wall_of', on_delete=models.PROTECT)
