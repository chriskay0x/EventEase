import random
import string

from django.conf import settings
from django.db import models


def new_reference_code():
    suffix = "".join(random.choices(string.ascii_uppercase, k=2))
    return f"EE-{random.randint(1000, 9999)}-{suffix}"


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        DECLINED = "declined", "Declined"
        CANCELLED = "cancelled", "Cancelled"

    reference_code = models.CharField(max_length=20, unique=True, blank=True)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name="bookings")
    listing = models.ForeignKey("listings.VenueListing", on_delete=models.PROTECT,
                                related_name="bookings")
    event_date = models.DateField()
    event_start_time = models.TimeField(null=True, blank=True)
    event_end_time = models.TimeField(null=True, blank=True)
    guest_count = models.PositiveIntegerField()
    event_type = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices,
                              default=Status.PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference_code:
            self.reference_code = new_reference_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_code} ({self.status})"


class BookingItem(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="items")
    service = models.ForeignKey("listings.ServiceListing", on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.booking.reference_code}: {self.service_id} x{self.quantity}"


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        HELD = "held", "Held in escrow"
        RELEASED = "released", "Released"
        REFUNDED = "refunded", "Refunded"
        FAILED = "failed", "Failed"

    booking = models.OneToOneField(Booking, on_delete=models.PROTECT,
                                   related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices,
                              default=Status.PENDING)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    idempotency_key = models.CharField(max_length=64, unique=True, null=True, blank=True)
    escrow_release_date = models.DateField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.booking.reference_code} – {self.status}"