from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from datetime import datetime
from django.db.models import Avg, Max, Min, Sum, Q

from . models import User, Category, Listing, Bid
from . forms import ListingForm, BidForm

def index(request):
    if request.user.is_authenticated:
        listings = Listing.objects.all().filter(Q(listing_open=True) | Q(listing_winner=request.user))
    else:
        listings = Listing.objects.all().filter(Q(listing_open=True))    
    return render(request, "auctions/index.html", {
       'listings' : listings,
    })

@login_required
def create_view(request):
    if request.method == 'POST': 
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save()
            listing.listing_owner = request.user
            listing.save()
        return redirect('index') 
         
    else: 
        form = ListingForm() 
        return render(request, 'auctions/createform.html', {'form' : form}) 


@login_required
def categories(request):
    categories = Category.objects.all()
    print(categories)
    return render(request, "auctions/categories.html", {
        'categories' : categories
        })


@login_required
def category(request, cat_id):  
    listings = Listing.objects.all().filter(
        Q(cat_id=cat_id),
        (Q(listing_open=True) | Q(listing_winner=request.user))
    )
    category = Category.objects.get(id=cat_id)
    return render(request, "auctions/categorylist.html", {
        'listings' : listings,
        'category' : category,
        })

@login_required
def close(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if listing.listing_owner == request.user and listing.listing_open == True:
        
        bid_max = Bid.objects.all().filter(listing_id=listing_id).aggregate(Max('user_bid'))
        print('bid_max : ', bid_max)
        winner_bid = bid_max['user_bid__max']
        print('winner_bid: :', winner_bid)


        bid=Bid.objects.all().get(user_bid=winner_bid)
        if bid != None:
            listing.listing_winner=bid.user
        
        print('listing_id:', bid.user)
        listing.listing_open =False
        listing.listing_final_price = winner_bid 
        listing.save()


    return redirect('listing', listing_id=listing_id)
 

def listing_view(request, listing_id):
    in_wl = False #is in 
    owner = False #is owner of the listing
    can_close = False # the owner can close the auction
    you_are_on_top = False
    try:
        listing = Listing.objects.get(pk=listing_id)
           
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")

    listing=Listing.objects.get(pk=listing_id)
    print('listing: ',listing)
    print('listing.listing_owner: ', listing.listing_owner)
    
    category = Category.objects.get(cat_name=listing.cat_id)
    print('category: ', category.cat_name)
    
    if listing.listing_owner == request.user and listing.listing_open == True:
        owner = True
        can_close = True
    
    print('owner: ', owner)
    print('can_close: ', can_close)

    starting_price = listing.starting_price
    print("Sarting Price: ", starting_price)

    bid_max = Bid.objects.all().filter(listing_id=listing_id).aggregate(Max('user_bid'))
    print('bid_max: ', bid_max)

    if (bid_max['user_bid__max'] == None):
        highest_bid = starting_price
    else:
        highest_bid=bid_max['user_bid__max']
    
    print('highest bid: ', highest_bid)
    
    your_actual_max = Bid.objects.all().filter(listing_id=listing_id, user=request.user).aggregate(Max('user_bid'))
    print('your_actual_max: ', your_actual_max)
    
    your_max_bid = your_actual_max['user_bid__max']
    if your_max_bid == None:
        your_max_bid = 0
    print('your max bid:', your_max_bid)

    if your_max_bid == highest_bid:
        you_are_on_top = True

    bid_count = Bid.objects.all().filter(listing_id=listing_id).count()
    print('bid count: ', bid_count)

    message =''

    if request.method == 'POST': 
            bform = BidForm(request.POST, request.FILES)

            if bform.is_valid(): 
                b = bform.save(commit=False)
                b.bid_at = datetime.now()
                b.listing_id = Listing.objects.get(pk=listing_id)
                b.user=request.user
                b.bid_status =True
                if highest_bid > b.user_bid:
                    b.save()
                    highest_bid = b.user_bid
                    you_are_on_top = True
                    bid_count = bid_count + 1
                    bform = BidForm()
                    return render(request,'auctions/listing.html', {
                        "listing": listing,
                        "bid_count": bid_count,
                        "highest_bid": highest_bid,
                        "in_wl" : in_wl,
                        "bform" : bform,
                        "message" : message,
                        "owner": owner,
                        "can_close" : can_close,
                        "category" : category.cat_name,
                        # "user_comments" : user_comments,
                        "you_are_on_top" : you_are_on_top,
                        }) 
                else:
                    message = str('{0:.2g}'. format(b.user_bid)) + ' is higher than highest bid. Pleases bid lower'
                    bform = BidForm()
                    return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "bid_count": bid_count,
                        "highest_bid": highest_bid,
                        "in_wl" : in_wl,
                        "bform" : bform,
                        "message" : message,
                        "owner": owner,
                        "can_close" : can_close,
                        "category" : category.cat_name,
                        "you_are_on_top" : you_are_on_top,
                    })
    else:
        listing = Listing.objects.get(pk=listing_id)
        if listing.listing_open == True and listing.listing_owner != request.user:
            bform = BidForm()
        else:
            bform = '' 
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "bid_count": bid_count,
            "highest_bid": highest_bid,
            "in_wl" : in_wl,
            "bform" : bform,
            "message" : message,
            "owner": owner,
            "can_close" : can_close,
            "category" : category.cat_name,
            # "user_comments" : user_comments,
            "you_are_on_top" : you_are_on_top,
            })


def success(request): 
    return HttpResponse('successfully uploaded') 


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
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":

        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.last_name = last_name
            user.first_name = first_name
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")