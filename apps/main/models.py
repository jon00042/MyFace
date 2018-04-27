import pytz

from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ################################
    @property
    def local_created_at(self):
        tz = pytz.timezone('Asia/Hong_Kong')  ## TODO: use tz from browser!
        return self.created_at.astimezone(tz).strftime(r'%Y-%m-%d %H:%M:%S')

class Following(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ################################
    being_followed_user = models.ForeignKey(User, related_name='follows_me', on_delete=models.PROTECT)
    doing_the_following_user = models.ForeignKey(User, related_name='i_follow', on_delete=models.PROTECT)

class Post(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ################################
    post_user = models.ForeignKey(User, related_name='posted_by', on_delete=models.PROTECT)
    wall_user = models.ForeignKey(User, related_name='on_wall_of', on_delete=models.PROTECT)
    ################################
    @property
    def local_created_at(self):
        tz = pytz.timezone('Asia/Hong_Kong')  ## TODO: use tz from browser!
        return self.created_at.astimezone(tz).strftime(r'%Y-%m-%d %H:%M:%S')

class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ################################
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.PROTECT)
    ################################
    @property
    def local_created_at(self):
        tz = pytz.timezone('Asia/Hong_Kong')  ## TODO: use tz from browser!
        return self.created_at.astimezone(tz).strftime(r'%Y-%m-%d %H:%M:%S')

