from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q
from pyrsistent import v
from .models import User, Post, PostImage, UserForm, PostForm, PostImageForm
import json
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token

@csrf_exempt
@requires_csrf_token
def index(request, page_number=1):
    #Slicing is in the documentation, but I found said doc page thanks to https://stackoverflow.com/a/6574038
    #Thanks to https://stackoverflow.com/a/739799 for pointing out how to use Complex lookout for OR logic operator
    if request.method == "PUT":
        return change_like_status(request)
    else:
        posts = Post.objects.filter(Q(replies_to = 0) | Q(replies_to = None)).order_by('-timestamp')
        posts_dict = paginate_posts(request.user.id, posts, page_number)
        post_form = PostForm()
        return render(request, "network/home.html", {
            "posts": posts_dict["posts"],
            "has_previous": posts_dict["has_previous"],
            "has_next": posts_dict["has_next"],
            "page_number": page_number,
            "post_form":post_form
        })

def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@csrf_exempt
@requires_csrf_token
@login_required(login_url="login")
def new_post_js(request):
    if request.method == "POST":
        data = json.loads(request.body)
        postForm = PostForm(data)
        if postForm.is_valid():
            newPostForm = postForm.save(commit=False)
            if len(newPostForm.text.strip()) > 0:
                newPostForm.userID = request.user
                newPostForm.save()
                post = Post.objects.filter(id=newPostForm.id).values()
                post_get = Post.objects.get(id=newPostForm.id) #needed for timestamp unfortunately
                timestamp = post_get.timestamp.strftime("%B %d, %Y, %I:%M %p")
                user = User.objects.filter(id=newPostForm.userID.id).values("profile_image_URL", "username", "public_name")
                return JsonResponse({
                    "message":"Post saved!",
                    "posted":True,
                    "post":list(post),
                    "timestamp":timestamp,
                    "user":list(user)
                }, status=200)
            else:
                return JsonResponse({
                    "message":"Form is not valid",
                    "form": newPostForm,
                    "posted":False
                }, status=200)
        else:
            return JsonResponse({
                "message":"Form is not valid",
                "form": newPostForm,
                "posted":False
            }, status=200)
    else:
        return JsonResponse({
            "message":"Action not permitted",
            "posted":False
        }, status=403)

@csrf_exempt
@requires_csrf_token
@login_required(login_url="login")
def edit_post(request, postID):
    try:
        post = Post.objects.get(id=postID)
        if request.method == "POST":
            data = json.loads(request.body)
            if post.userID == request.user:
                postForm = PostForm(data)
                if postForm.is_valid():
                    postFormText = postForm.cleaned_data['text']
                    if post.text != postFormText:
                        post.text = postForm.cleaned_data['text']
                        post.edited = True
                        post.save()
                        return JsonResponse(data={
                            "text": post.text,
                            "timestamp":post.timestamp.strftime("%B %d, %Y, %I:%M %p"),
                            "edited":True
                        }, status=200)
        return JsonResponse(data={
            "message":"Action not permitted",
            "edited":False
        }, status=403)
    except Post.DoesNotExist:
        return JsonResponse(data={
            "message":"Post does not exist anymore.",
            "edited":False
        }, status=404)

@csrf_exempt
@requires_csrf_token
def get_profile(request, userData, page_number=1):
    if request.method == "PUT":
        return change_follow_status(request, userData)
    else:
        try:
            #probably not necessary anymore, since I've narrowed down possibilities
            #I'm only leaving it for now to showcase that it is possible to have two paths.
            if isinstance(userData, int):
                user = User.objects.get(id=userData)
            elif isinstance(userData, str):
                user = User.objects.get(username=userData)
            else:
                return HttpResponse(status=403)
            #if request.method == "POST": #Not gonna be used anymore, went to PUT instead.
            #        return follow_user(request, userData)
            #else:
            follower_count = 0
            user.followers.all()
            if user.followers.exists():
                follower_count = user.followers.count()
            following_count = 0
            if user.follows.exists():
                following_count = user.follows.count()
            rq_user_is_following = False
            posts = Post.objects.filter(userID=user).order_by('-timestamp')
            posts_dict = paginate_posts(request.user.id, posts, page_number)
            if request.user.is_authenticated and user.followers.filter(id=request.user.id).exists():
                rq_user_is_following = True #Thanks to https://stackoverflow.com/a/16723038 for showing me how to check in Many-to-Many
            return render(request, "network/profile.html", {
                "user":user,
                "follower_count":follower_count,
                "following_count":following_count,
                "rq_user_is_following": rq_user_is_following,
                "posts": posts_dict["posts"],
                "has_next": posts_dict["has_next"],
                "has_previous":posts_dict["has_previous"],
                "page_number":page_number
            })
        except User.DoesNotExist:
            return index_message(request, "User does not exist")

@csrf_exempt
@requires_csrf_token
@login_required(login_url="login")
def change_like_status(request):
    try:
        data = json.loads(request.body)
        if data.get("postID") is not None:
            postID = data["postID"]
            post = Post.objects.get(id = postID)
            likes = post.likes.count()
            liked = False
            if post.likes.filter(id=request.user.id).exists():
                post.likes.remove(request.user)
                liked = False
                likes -= 1
            else:
                post.likes.add(request.user)
                likes += 1
                liked = True
            return JsonResponse(data={
                "liked":liked,
                "like_count":likes
            }, status=200)
        else:
            return JsonResponse(data={
                "message":"Post was not provided",
            }, status=404)
    except Post.DoesNotExist or User.DoesNotExist:
        return JsonResponse(data={
            "message":"Post does not exist anymore",
        }, status=404)

@csrf_exempt
@requires_csrf_token
@login_required(login_url="login")
def change_follow_status(request, userID):
    try:
        user = User.objects.get(id=userID)
        if user == request.user:
            return JsonResponse({
                "message":"You cannot follow yourself"
            }, 403)
        follower_count = user.followers.count()
        follows = False
        if user.followers.filter(id=request.user.id).exists():
            user.followers.remove(request.user)
            follower_count -= 1
        else:
            user.followers.add(request.user)
            follows=True
            follower_count += 1
        return JsonResponse({
            "follows":follows,
            "follower_count":follower_count
        }, status=200)            
    except User.DoesNotExist:
        return index_message(request, "User does not exist.")

def index_message(request, message):
    posts = Post.objects.filter(parent_post = 0).order_by('-timestamp')
    posts_dict = paginate_posts(request.user.id, posts, 1)
    post_form = PostForm()
    return render(request, "network/home.html", {
        "message":message,
        "posts": posts_dict["posts"],
        "post_form":post_form,
        "has_previous": False,
        "has_next": posts_dict["has_next"],
        "page_number": 1
    })

def load_post(request, postID, page_number=1):
    try:
        post = Post.objects.get(id=postID)
        replies = Post.objects.filter(replies_to=post)
        post_likes = get_likes(request.user.id, [post])
        replies_dict = paginate_posts(request.user.id, replies, page_number)
        return render(request, "network/post.html", {
            "ogpost":list(post_likes),
            "posts":replies_dict["posts"],
            "has_previous":replies_dict["has_previous"],
            "has_next":replies_dict["has_next"],
            "page_number":page_number
        })
    except Post.DoesNotExist:
        return index_message(request, "Post does not exist anymore")

@login_required(login_url="login")
def get_following_posts(request, userData, page_number=1):
    try:
        user = User.objects.get(username=userData)
        posts = Post.objects.filter(userID__in=user.follows.all()).order_by('-timestamp')
        post_dict = paginate_posts(request.user.id, posts, page_number)
        return render(request, "network/following.html", {
            "user":user,
            "posts":post_dict["posts"],
            "has_previous":post_dict["has_previous"],
            "has_next":post_dict["has_next"],
            "page_number":page_number,
        })
    except User.DoesNotExist:
        return HttpResponse(status=404)
    pass

def paginate_posts(userID, posts, page_number):
    postPaginator = Paginator(posts, 10)
    postPage = postPaginator.page(page_number)
    post_likes = get_likes(userID, postPage)
    post_dict = {
        "posts": post_likes,
        "has_next": postPage.has_next(),
        "has_previous": postPage.has_previous(),
        "page_number": page_number
    }
    return post_dict

def get_likes(userID, posts):
    likes = []
    user_liked = []
    for post in posts:
        likes.append(post.likes.count())
        if (post.likes.filter(id=userID).exists()):
            user_liked.append(True)
        else:
            user_liked.append(False)
    return zip(posts, likes, user_liked)


