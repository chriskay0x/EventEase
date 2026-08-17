from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings

# Create your models here.

# Textchoice classes
class ServiceCategory(models.TextChoices):
    VENUE = 'venue', 'Venue'
    CATERING = 'catering', 'Catering'
    DJ = 'dj', 'DJ'


class VenueListing(models.Model):
    Vendor = models.CharField(max_length= 1000)
    location = models.CharField(max_length=1000)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  # PostGIS PointField swap later
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    Venue_minguest = models.PositiveIntegerField(default=1)
    Venue_maxguest = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    Created_at = models.DateTimeField(auto_now_add=True)
    Updated_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    base_price = models.IntegerField()
    services = models.JSONField(default=list, blank=True)

class ServiceListing(models.Model):
    vendor = models.ForeignKey('accounts.VendorProfile', on_delete=models.CASCADE, related_name='services')
    category = models.CharField(max_length=20, choices=ServiceCategory.choices)
    description = models.TextField()
    pricing_model = models.CharField(max_length=50)


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


class Listing(models.Model):

    CATEGORY_CHOICES = [
        ("wedding", "Wedding Venue"),
        ("conference", "Conference Centre"),
        ("party", "Party / Event Hall"),
        ("outdoor", "Outdoor Venue"),
        ("studio", "Studio"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("live", "Live"),
        ("hidden", "Hidden"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings"
    )

    name = models.CharField(max_length=200)

    description = models.TextField()

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    location = models.CharField(max_length=200)

    capacity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to="listings/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name

class AvailabilityStatus(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    BOOKED = 'booked', 'Booked'
    BLOCKED = 'blocked', 'Blocked'

class Availability(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="availability"
    )

    date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=AvailabilityStatus.choices,
        default=AvailabilityStatus.AVAILABLE
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "date"],
                name="unique_listing_availability_date"
            )
        ]
        def __str__(self):
            return f"{self.listing.name} - {self.date} - {self.status}"
    # vendor = models.ForeignKey('accounts.VendorProfile', on_delete=models.CASCADE, related_name='availability')
    # date = models.DateField()
    # status = models.CharField(max_length=15, choices=AvailabilityStatus.choices, default=AvailabilityStatus.AVAILABLE)

    # class Meta:
    #     unique_together = ('vendor', 'date')
        
