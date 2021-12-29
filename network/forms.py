from django.forms.widgets import Textarea
from django.forms import ModelForm
from .models import *

class NewPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["content"]
        widgets = {
            "content": Textarea(attrs={"class": "form-control",
            "placeholder": "Type your message here..."}),
        }
        labels = {
            "content": "",
        }

class NewCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]
        widgets = {
            "comment": Textarea(attrs={"class": "form-control",
            "placeholder": "Type your comment here..."}),
        }
        labels = {
            "comment": "",
        }