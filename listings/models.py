from django.conf import settings
from django.db import models


class VenueListing(models.Model):
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name="venue_listings")
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    min_guests = models.PositiveIntegerField(default=1)
    max_guests = models.PositiveIntegerField(default=100)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amenities = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ServiceListing(models.Model):
    class Category(models.TextChoices):
        CATERING = "catering", "Catering"
        DECOR = "decor", "Decor"
        DJ = "dj", "DJ / Entertainment"
        MC = "mc", "MC"
        USHER = "usher", "Usher"

    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name="service_listings")
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.get_category_display()} – {self.vendor.username}"


class Availability(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        BOOKED = "booked", "Booked"
        BLOCKED = "blocked", "Blocked"

    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name="availability")
    date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices,
                              default=Status.AVAILABLE)

    class Meta:
        unique_together = [("vendor", "date")]

    def __str__(self):
        return f"{self.vendor.username} {self.date} ({self.status})"