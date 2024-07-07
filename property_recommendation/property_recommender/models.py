from django.db import models
from django.utils import timezone
class Property(models.Model):
    # Define your property model fields here
    location = models.CharField(max_length=100)
    bedrooms = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        app_label = 'property_recommender'  # Specify the app label

    def __str__(self):
        return f"{self.location} - {self.bedrooms} bedrooms - ${self.price}"

class PropertySearch(models.Model):
    location = models.CharField(max_length=255)
    bedrooms = models.IntegerField()
    min_price = models.IntegerField()
    max_price = models.IntegerField()
    search_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.location} - {self.bedrooms} Bedrooms - ${self.min_price} to ${self.max_price}"

# models.py

class Property(models.Model):
    location = models.CharField(max_length=100)
    bedrooms = models.IntegerField()
    price = models.IntegerField()
    area = models.IntegerField(default=0)
    amenities = models.JSONField(default=list)

    def __str__(self):
        return f"{self.location} - {self.bedrooms} Bedrooms"
    # Define other fields as needed

