from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.

# Textchoice classes
class ServiceCategory(models.TextChoices):
    VENUE = 'venue', 'Venue'
    CATERING = 'catering', 'Catering'
    DJ = 'dj', 'DJ'

class AvailabilityStatus(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    BOOKED = 'booked', 'Booked'
    BLOCKED = 'blocked', 'Blocked'

class Venue(models.Model):
    Vendor = models.CharField(max_length= 1000)
    location = models.CharField(max_length=1000)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  # PostGIS PointField swap later
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    Venue_minguest = models.PositiveIntegerField(default=1)
    Venue_maxguest = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    Created_at = models.DateTimeField(auto_now_add=True)
    Updated_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    base_price = models.IntegerField(max_length=10)
    services = models.JSONField(default=list, blank=True)

class ServiceListing(models.Model):
    vendor = models.ForeignKey('accounts.VendorProfile', on_delete=models.CASCADE, related_name='services')
    category = models.CharField(max_length=20, choices=ServiceCategory.choices)
    description = models.TextField()
    pricing_model = models.CharField(max_length=50)

class Availability(models.Model):
    vendor = models.ForeignKey('accounts.VendorProfile', on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    status = models.CharField(max_length=15, choices=AvailabilityStatus.choices, default=AvailabilityStatus.AVAILABLE)

    class Meta:
        unique_together = ('vendor', 'date')
        
class Catering(models.Model):
    Caterer_name = models.CharField(max_length= 1000)
    location = models.CharField(max_length=1000)
    Catering_minguest = models.IntegerField(default=1)
    Catering_maxguest = models.IntegerField(default=2)
    Created_at = models.DateTimeField(auto_now_add=True)
    Updated_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    Base_price = models.IntegerField()

class DJ(models.Model):
    DJname = models.CharField(max_length= 1000)
    location = models.CharField(max_length=1000)
    Created_at = models.DateTimeField(auto_now_add=True)
    Updated_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    Base_price = models.IntegerField()
