import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from network.forms import NewCommentForm, NewPostForm

from .models import *


def index(request):

    try:
        user = User.objects.get(username=request.user)
    except:
        user = None

    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            form = form.cleaned_data
            content = form["content"]
        post = Post(user=user, content=content)
        post.save()

        return HttpResponseRedirect(reverse("index"))

    else:
        # Show recent posts first
        posts = list(reversed(Post.objects.all()))

        # Get list of all posts the user liked
        # Required to pre-configure the like-button
        likedPosts = getLikedPosts(posts, user)

        # Show 10 posts per page
        page_obj = create_paginator(request, posts)

        return render(request, "network/index.html", {
            "form": NewPostForm(),
            "page_obj": page_obj,
            "likedPosts": likedPosts,
            "commentForm": NewCommentForm(),
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


def profile(request, username):
    
    try:
        user = User.objects.get(username=request.user)
    except:
        user = None

    # Check if the profile's user exists
    try:
        followee = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "network/notFound.html")
    # Set visiting user to None if not logged in
    try:
        follower = User.objects.get(username=request.user)
    except:
        follower = None
    # Check if the visiting user is following the profile's user
    try:
        follow = Follow.objects.get(followee=followee, follower=follower)
    except:
        follow = None

    if request.method == "GET":

        # The profile's user
        profileUser = User.objects.get(username=username)

        # Hide follow button on one's own profile or if not logged in
        if followee == follower or not follower:
            followButton = None
        elif follow:
            followButton = "Unfollow"
        else:
            followButton = "Follow"

        # Show recent posts first
        posts = list(reversed(Post.objects.filter(user=profileUser)))

        # Get list of all posts the user liked
        likedPosts = getLikedPosts(posts, user)

        # Show 10 posts per page
        page_obj = create_paginator(request, posts)

        return render(request, "network/profile.html", {
            "profileUser": profileUser,
            "followButton": followButton,
            "page_obj": page_obj,
            "likedPosts": likedPosts,
        })

    # Follow button was clicked
    else:
        if follow:
            follow.delete()

        else:
            follow = Follow(followee=followee, follower=follower)
            follow.save()
            print(follow)

        return HttpResponseRedirect(reverse("profile", kwargs={"username": username}))


@login_required(login_url="login")
def following(request):

    user = User.objects.get(username=request.user)
    # All followees as Follow objects
    follows = user.Followees.all()
    # All followees as User objects
    followees = User.objects.filter(Followers__in=follows)

    # Show recent posts first
    posts = list(reversed(Post.objects.filter(user__in=followees)))

    # Get list of all posts the user liked
    likedPosts = getLikedPosts(posts, user)

    # Show 10 posts per page
    page_obj = create_paginator(request, posts)

    return render(request, "network/following.html", {
        "page_obj": page_obj,
        "likedPosts": likedPosts,
    })


@csrf_exempt
def post(request, id):

    # Query for requested post
    try:
        # Making sure only the creator can edit the post
        post = Post.objects.get(id=id, user=request.user)
    except:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Return post content
    if request.method == "GET":
        return JsonResponse(post.serialize())

    # Update post content
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("content") is not None:
            post.content = data["content"]
        post.save()
        return HttpResponse(status=204)

    # Post must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


@csrf_exempt
def likes(request, id):

    # Query for requested post
    try:
        post = Post.objects.get(id=id)
    except:
        return JsonResponse({"error": "Post not found."}, status=404)

    likes = Like.objects.filter(post=post).all()

    # Return likes on that post
    if request.method == "GET":
        return JsonResponse([like.serialize() for like in likes], safe=False)
        
    # Update likes
    elif request.method == "POST":
        like = Like(user=request.user, post=post)
        like.save()
        return HttpResponse(status=204)
    
    elif request.method == "DELETE":
        try:
            like = Like.objects.get(user=request.user, post=post)
            like.delete()
        # Shouldn't be the case - a user can like every post only once
        except:
            likes = Like.objects.filter(user=request.user, post=post).all()
            likes.delete()
        return HttpResponse(status=204)

    # Post must be via GET, POST or DELETE
    else:
        return JsonResponse({
            "error": "GET, POST or DELETE request required."
        }, status=400)


# API for the number of likes on a post
# Was added later in addition to the "likes"-route
def _likeCounter(request, id):

    # Query for requested post
    try:
        post = Post.objects.get(id=id)
    except:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method == "GET":
        return render(request, "network/partials/_likeCounter.html", {
            "post": post,
        })


@csrf_exempt
def _comments(request, id):

    # Query for requested post
    try:
        post = Post.objects.get(id=id)
    except:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method == "POST":

        data = json.loads(request.body)
        if data.get("comment") is not None:
            comment = data["comment"]
        newComment = Comment(user=request.user, post=post, comment=comment)
        print(newComment)
        print("Hi")
        newComment.save()

        return HttpResponse(status=204)

    else:
        comments = Comment.objects.filter(post=post)
        return render(request, "network/partials/_comments.html", {
            "comments": comments,
        })
    

# Distribute posts over multiple pages
def create_paginator(request, posts):

    # Show 10 posts per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


# Create a list of all posts the user liked
def getLikedPosts(posts, user):

    likedPosts =[]
    for post in posts:
        for like in post.Likers.all():
            if like.user == user:
                likedPosts.append(like.post)
    return likedPosts