
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:page_number>", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post_js, name="new_post"),
    path("edit_post/<int:postID>", views.edit_post, name="edit_post"),
    path("profile/<str:userData>", views.get_profile, name="get_profile_username"),
    path("profile/<str:userData>/<int:page_number>", views.get_profile, name="get_profile_username"),
    path("profile/<str:userData>/following", views.get_following_posts, name="get_following_posts"),
    path("profile/<str:userData>/following/<int:page_number>", views.get_following_posts, name="get_following_posts"),
    path("post/<int:postID>", views.load_post, name="load_post"),
    path("post/<int:postID>/<int:page_number>", views.load_post, name="load_post"),
    path("edit_post/<int:postID>", views.edit_post, name="edit_post")
]
