
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user/<str:username>", views.profile, name="profile"),
    path("following", views.following, name="following"),

    # API Routes
    path("posts/<int:id>", views.post, name="post"),
    path("likes/<int:id>", views.likes, name="likes"),
    path("_likeCounter/<int:id>", views._likeCounter, name="_likeCounter"),
    path("_comments/<int:id>", views._comments, name="_comments"),
]
