from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Posts")
    content = models.TextField(max_length=512, blank=False)
    datetime = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "creator": self.user.username,
            "content": self.content,
            "likes": Like.objects.filter(post=self).count(),
            "comments": Comment.objects.filter(post=self).count(),
            "datetime": self.datetime.strftime("%b %d %Y, %I:%M %p"),
        }

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="Likers")

    def serialize(self):
        return {
            "user": self.user.username,
        }

class Follow(models.Model):
    followee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Followers")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Followees")

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="Comments")
    comment = models.TextField(max_length=256, blank=False)