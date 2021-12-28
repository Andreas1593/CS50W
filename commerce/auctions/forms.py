from django.forms import widgets
from django.forms.widgets import Textarea
from auctions.models import Auction
from django.forms import ModelForm
from .models import *

class ListingForm(ModelForm):
    class Meta:
        model = Auction
        fields = ["title", "description", "category", "startBid", "image"]
        widgets = {
            "description": Textarea(attrs={'rows': 7, 'cols': 80}),
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]
        widgets = {
            "comment": Textarea(attrs={"class": None, 'rows': 5, 'cols': 32}),
        }
        labels = {
            "comment": "",
        }