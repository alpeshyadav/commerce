from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

from django.db.models.deletion import CASCADE



class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    description = models.TextField()
    bid = models.FloatField()
    url = models.CharField(max_length=1000, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=50)
    created_at = models.DateField(auto_now_add=True)
    cat = models.ForeignKey(Category, related_name='listings', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return f"{self.title} ${self.bid}"

class AllBids(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user_bid = models.FloatField()

    def __str__(self) -> str:
        return f"user: {self.user}, bid: {self.user_bid}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user_comment = models.TextField()

    def __str__(self) -> str:
        return f"User {self.user} commented"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE)
    in_watchlist = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"User {self.user}, {self.listing_id}: {self.in_watchlist}"