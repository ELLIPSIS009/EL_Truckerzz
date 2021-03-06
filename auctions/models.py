from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    pass


class Category(models.Model):
    cat_name = models.CharField(max_length=64)
    cat_desc = models.CharField(max_length=64)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.cat_name}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    listing_desc = models.TextField()
    listing_img = models.ImageField(upload_to='listing_images', default=None, blank=True, null=True)
    cat_id = models.ForeignKey(Category, default = 1, on_delete=models.CASCADE)
    starting_price = models.DecimalField(decimal_places=2, max_digits=10, default = 0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    listing_open = models.BooleanField(default=True)
    listing_owner = models.ForeignKey(User, null=True , on_delete=models.CASCADE, related_name='owner')
    listing_winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='winner')
    listing_final_price = models.DecimalField(decimal_places=2, max_digits=10, default = 0) 

    def __str__(self):
        return f"title: {self.title} category: {self.cat_id}"


class Bid(models.Model):
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_bid = models.DecimalField(decimal_places=2, max_digits=10)
    bid_at = models.DateTimeField(auto_now_add=True)
    bid_status = models.BooleanField(default= True)

    def __str__(self):
        return f"listing_id: {self.listing_id} user: {self.user} bid: {self.user_bid}"
