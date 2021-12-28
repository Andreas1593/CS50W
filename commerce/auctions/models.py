from django.contrib.auth.models import AbstractUser
from django.db import models


CATEGORIES = (
    ('Appliances', 'Appliances'),
    ('Books', 'Books'),
    ('Clothing', 'Clothing'),
    ('Electronics', 'Electronics'),
    ('Furniture', 'Furniture'),
    ('Toys', 'Toys'),
)

class User(AbstractUser):
    pass

class Auction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Listings")
    listingID = models.IntegerField()
    title = models.CharField(max_length=32)
    description = models.TextField(max_length=256)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    image = models.URLField(max_length=512, blank=True)
    startBid = models.DecimalField(max_digits=6, decimal_places=2)
    currentBid = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    created = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)
    winner = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name="WonAuctions", null=True, default=None)

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Bids")
    bid = models.DecimalField(max_digits=6, decimal_places=2)
    listing = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="Bids")

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Comments")
    listing = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="Comments")
    comment = models.TextField(max_length=512, blank=False)
    date = models.DateTimeField(auto_now_add=True)

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Watchlist")
    listing = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="Watchlists")