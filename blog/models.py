from distutils.command.upload import upload
from email.policy import default
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


STATUS = (
    (0,"Draft"),
    (1,"Publish")
)

class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    thumbnail = models.ImageField(upload_to='thumbnails', default='NULL.png')
    author = models.ForeignKey(User, on_delete = models.CASCADE, related_name='blog_posts')
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices = STATUS, default=0)
    likes = models.ManyToManyField(User, related_name='blog_likes')
    class Meta:
        ordering = ['-created_on']

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("post_detail", kwargs={"slug": str(self.slug)})

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    commented_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['commented_on']
    
    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.commented_on)


class ProfileInfo(models.Model):
    user = models.OneToOneField(User, null=True, on_delete = models.CASCADE)
    bio = models.TextField()
    display_picture = models.ImageField(upload_to='profiles', default='profiles/NULL.png')
    website_url = models.CharField(max_length=200, null=True)
    facebook_url = models.CharField(max_length=200, null=True)
    twitter_url = models.CharField(max_length=200, null=True)
    youtube_url = models.CharField(max_length=200, null=True)
    linkedin_url = models.CharField(max_length=200, null=True)
    def __str__(self):
        return str(self.user)

# Create your models here.
