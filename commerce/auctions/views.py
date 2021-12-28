from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models.expressions import F
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max
from random import randrange

from .models import *
from .forms import *


def index(request):
    listings = Auction.objects.all()
    try:
        return render(request, "auctions/index.html", {
            "listings": listings,
        })
    except:
        return render(request, "auctions/index.html")


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password.",
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match.",
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken.",
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="login")
def createListing(request):

    # Collect all data and save new listing
    if request.method == "POST":

        user = User.objects.get(username=request.user)

        listingID = randrange(9999)
        # Generate new random product ID if that one already exists
        while listingID in Auction.objects.filter(listingID=listingID):
                listingID = randrange(9999)

        form = ListingForm(request.POST)
        if form.is_valid():
            form = form.cleaned_data
            title = form["title"]
            description = form["description"]
            category = form["category"]
            image = form["image"]
            startBid = form["startBid"]

        listing = Auction(user=user, listingID=listingID, title=title, description=description,
                          category=category, image=image, startBid=startBid, currentBid=None)
        listing.save()

        return HttpResponseRedirect(reverse("productPage", args=(listingID,)))

    else:
        return render(request, "auctions/createListing.html", {
            "form": ListingForm(),
        })


def productPage(request, listingID):
    user = request.user
    listing = Auction.objects.get(listingID=listingID)
    if user.is_authenticated:
        # Empty if listing isn't on the user's watchlist
        onWatchlist = user.Watchlist.filter(listing=listing)
    else:
        onWatchlist = None
    currentBid = listing.currentBid
    # Set currently highest bid to 0 if it's None
    if not currentBid:
        currentBid = 0
    comments = listing.Comments.all()

    if request.method == "POST":
        # 'Add to Watchlist' button was clicked
        if request.POST.get("addWatchlist"):
            addWatchlist = Watchlist(user=user, listing=listing)
            addWatchlist.save()

        # 'Remove from Watchlist' button was clicked
        elif request.POST.get("rmvWatchlist"):
            onWatchlist.delete()

        # 'Close Listing' button was clicked
        elif request.POST.get("close"):

            # Winner is the user with the highest current bid
            if currentBid:
                listing.winner = Bid.objects.get(listing=listing, bid=currentBid).user
            else:
                listing.winner = None

            listing.closed = True
            listing.save()
            return render(request, "auctions/productPage.html", {
                "listing": listing,
                "onWatchlist": onWatchlist,
                "comments": comments,
                "commentForm": CommentForm(),
            })

        # 'Place Bid' button was clicked
        elif request.POST.get("placeBid"):
            bid = float(request.POST.get("bid"))
            startBid = listing.startBid

            # Placed bid is lower than start bid
            if bid < startBid:
                return render(request, "auctions/productPage.html", {
                    "listing": listing,
                    "onWatchlist": onWatchlist,
                    "error": "Bid must be higher than start bid.",
                    "comments": comments,
                    "commentForm": CommentForm(),
                })

            # Placed bid is lower than existing bids
            elif bid < currentBid:
                return render(request, "auctions/productPage.html", {
                    "listing": listing,
                    "onWatchlist": onWatchlist,
                    "error": "Bid must be higher than current bid.",
                    "comments": comments,
                    "commentForm": CommentForm(),
                })

            # Save placed bid
            else:
                newBid = Bid(user=user, bid=bid, listing=listing)
                newBid.save()
                # Update new current bid
                listing.currentBid = bid
                listing.save()
                return HttpResponseRedirect(reverse("productPage", args=(listingID,)))

        # 'Post Comment' button was clicked
        else:
            comment = request.POST["comment"]
            newComment = Comment(user=user, listing=listing, comment=comment)
            newComment.save()
            return HttpResponseRedirect(reverse("productPage", args=(listingID,)))

        return HttpResponseRedirect(reverse("productPage", args=(listingID,)))

    else:
        return render(request, "auctions/productPage.html", {
            "listing": listing,
            "onWatchlist": onWatchlist,
            "comments": comments,
            "commentForm": CommentForm(),
        })


@login_required(login_url="login")
def watchlist_view(request):
    user = request.user
    watchlists = user.Watchlist.all()
    print(watchlists)
    return render(request, "auctions/watchlist.html", {
        "watchlists": watchlists,
    })


def categories_view(request):
    return render(request, "auctions/categories.html", {
        "categories": CATEGORIES,
    })


def categories_listings(request, category):
    listings = Auction.objects.filter(category=category)
    return render(request, "auctions/categories_listings.html", {
        "listings": listings,
        "category": category,
    })