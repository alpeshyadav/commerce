from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError, reset_queries
from django.db.models import Max, expressions
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import AllBids, Category, Comment, User, Listing, Watchlist


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {'listings': listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if request.POST.get('next'):
                return redirect(request.POST.get('next'))

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
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='/login/')
def addcategory(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        cat = Category(name=name)
        cat.save()
        return HttpResponseRedirect(reverse(create))
    return render(request, 'auctions/addcategory.html')

@login_required(login_url='/login/')
def create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        bid = request.POST.get('bid')
        categories = request.POST.get('categories')
        url = request.POST.get('url')
        created_by = request.user.username
        print(categories, Category(name=categories))
        listing = Listing(title=title, description=description, bid=bid, cat= Category.objects.get(name=categories), url=url, created_by=created_by)
        listing.save()
        return redirect('/')

    categories = Category.objects.all()
    return render(request, 'auctions/create.html', {'categories': categories})

@login_required(login_url='/login/')
def listing(request, id):
    print('reacheddddddd')
    listing = Listing.objects.get(id=id)
    print('erorrrrrrrrrrrrr')
    bidsofar = AllBids.objects.filter(listing_id=id).count()
    user = User.objects.get(username=request.user.username)
    is_it = Watchlist.objects.filter(listing_id=listing, user=user)
    in_watchlist = False
    try:
        in_watchlist = is_it[0].in_watchlist
    except:
        pass
    comments = {}
    print(listing, 'eheeeeeeeeee')
    flag = False
    if listing.created_by == request.user.username:
        flag = True
    try:
        comments = Comment.objects.filter(listing_id=id)
    except:
        pass

    return render(request, 'auctions/listing.html', {'listing':listing, 'comments':comments, 'bidsofar':bidsofar, 'flag':flag, 'in_watchlist':in_watchlist})

@login_required(login_url='/login/')
def addcomment(request):
    if request.method == "POST":
        listing_id = request.POST.get('listing_id')
        user_comment = request.POST.get('comment')
        user = request.user.username

        print(listing_id, user_comment, user)
        print(Comment.objects.filter(user=User.objects.get(username=user)))
        print(2)
        id = Listing.objects.get(id=listing_id)
        if len(Comment.objects.filter(user=User.objects.get(username=user),
        listing_id=listing_id)):
            print('updateeeeeeee')
            Comment.objects.filter(listing_id=id).update(user_comment=user_comment)

        else:
            print('adddddddddddddd')
            comment = Comment(listing_id=id, user_comment=user_comment, user=User.objects.get(username=user))
            comment.save()

        return redirect(f'/listing/{listing_id}')

@login_required(login_url='/login/')
def addbid(request):
    listing_id = request.POST.get('listing_id')
    bid = request.POST.get('bid')
    listing = Listing.objects.get(id=listing_id)
    # print(listing_id, bid)

    former_bid = listing.bid

    bidsofar = AllBids.objects.filter(listing_id=listing_id).count()

    if bidsofar == 0:
        addbid = AllBids(user=User.objects.get(username=request.user.username), user_bid=bid, listing_id=Listing.objects.get(id=listing_id))
        addbid.save()

        return redirect(f'/listing/{listing_id}')

    if int(bid) > int(former_bid):
        addbid = AllBids(user=User.objects.get(username=request.user.username), user_bid=bid, listing_id=Listing.objects.get(id=listing_id))
        addbid.save()

        Listing.objects.filter(id=listing_id).update(bid=bid)
        messages.add_message(request, messages.INFO, 'Bid placed Successfully')

    else:
         messages.add_message(request, messages.INFO, 'Bid must be greater than previous bid value')

    return redirect(f'/listing/{listing_id}')

@login_required(login_url='/login/')
def closebid(request):
    id = request.POST.get('listing_id')
    Listing.objects.filter(id=id).update(is_active=False)
    return redirect('/')

def listall(request):
    listings = Listing.objects.all()
    maxbids = AllBids.objects.values('listing_id').annotate(Max('user_bid'))
    allbids = {}

    for bid in maxbids:
        # print(bid)
        allbids[bid['listing_id']] = [AllBids.objects.get(user_bid = bid['user_bid__max']).user, bid['user_bid__max']]
    print(allbids)
    return render(request, "auctions/listall.html", {'listings': listings, 'allbids':allbids})

@login_required(login_url='/login/')
def watchlist(request):
    if request.method == 'POST':
        listing_id = request.POST.get('listing_id')
        user = request.user.username
        id = Listing.objects.get(id=listing_id)
        user = User.objects.get(username=user)
        is_it = Watchlist.objects.filter(listing_id=id, user=user)
        if len(is_it):
            is_it.update(in_watchlist = not is_it[0].in_watchlist)
            # print(is_it[0].in_watchlist)
        else:
            Watchlist(listing_id=id, user=user).save()

        return redirect(f'/listing/{listing_id}')

    user = request.user.username
    watchlist = Watchlist.objects.filter(user=User.objects.get(username=user), in_watchlist=True)
    listings = []
    for item in watchlist:
        listings.append(item.listing_id)
    print(listings)
    return render(request, 'auctions/watchlist.html', {'listings':listings})


def category(request, category_type=None):
    if category_type is None:
        category = Category.objects.all()
        print(category)
        # for _ in listings:
        #     print(_)
        return render(request, 'auctions/category.html', {'category':category})
    listings = Listing.objects.filter(cat=Category.objects.get(name=category_type))

    return render(request, 'auctions/index.html', {'listings':listings})