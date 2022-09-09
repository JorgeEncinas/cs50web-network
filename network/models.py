from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms
from django.utils.translation import gettext_lazy as gtlazy


class User(AbstractUser):
    public_name = models.CharField(max_length=100)
    profile_image_URL = models.URLField()
    follows = models.ManyToManyField('self', related_name="followers", symmetrical=False, null=True, blank=True)

class PostImage(models.Model):
    postID = models.ForeignKey('Post', related_name="post_images", on_delete=models.CASCADE)
    image_URL = models.URLField()

    def serialize(self):
        return {
            "postID":self.postID,
            "image_URL":self.image_URL
        }

class Post(models.Model):
    userID = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_posts")
    text = models.TextField(max_length=280)
    likes = models.ManyToManyField(User, related_name="user_likes")
    #likes = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="liked_post")
    #likes = models.ForeignKey(Like, on_delete=models.DO_NOTHING, related_name="liked_post")
    replies_to = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name="children_reply", null=True)
    timestamp = models.DateTimeField(auto_now=True)
    edited = models.BooleanField(default=False)

    def serialize(self):
        return {
            "id":self.id,
            "userID":self.userID,
            "text":self.text,
            "likes":self.likes.count(),
            "replies_to":self.replies_to,
            "timestamp":self.timestamp,
            "edited":self.edited
        }

class UserForm(forms.ModelForm):
    confirm_password = forms.CharField(label="Confirm your Password")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username',
            'public_name', 'password', 'profile_image_URL'
        ]
        labels = {
            'first_name': gtlazy('Input your First Name'),
            'last_name': gtlazy('Input your Last Name'),
            'email': gtlazy('Input an e-mail to link with your account'),
            'username': gtlazy('Choose a username. This cannot be changed frequently'),
            'public_name': gtlazy('Choose a public name. This can be changed easily'),
            'password': gtlazy('Create a password for your account'),
            'profile_image_URL':gtlazy('Confirm your password')
        }

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields=['text']
        exclude = ['userID', 'likes', 'replies_to']
        labels = {
            'text': 'What are you thinking?'
        }

class PostImageForm(forms.ModelForm):

    class Meta:
        model = PostImage
        fields = ['image_URL']