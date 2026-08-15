import random, string, uuid
from django.conf import settings
from django.db import models
from django.utils import timezone

LETTERS = "ABCDEFGHJKMNPQRSTUVWXYZ"
new_number    = lambda: f"EV-{random.randint(1000, 9999)}"                 # EV-9824
new_code      = lambda: f"{new_number()}-{random.choice(string.ascii_uppercase[:8])}"  # EV-9824-A
new_reference = lambda: (f"EE-{random.randint(1000, 9999)}-"
                         + "".join(random.choices(LETTERS, k=2)))          # EE-1024-GV

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[("customer","customer"),("vendor","vendor")], default="customer")
    payout_name    = models.CharField(max_length=120, blank=True)
    bank_code      = models.CharField(max_length=10, blank=True)   # fetch list from GET /bank
    account_number = models.CharField(max_length=10, blank=True)
    recipient_code = models.CharField(max_length=64, blank=True)  # cached Paystack recipient

class Venue(models.Model):
    vendor    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="venues")
    name      = models.CharField(max_length=120)
    address   = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    price_kobo = models.BigIntegerField()
    currency   = models.CharField(max_length=3, default="NGN")

class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING_VENDOR = "pending_vendor"; CONFIRMED = "confirmed"; PAID = "paid"
        COMPLETED = "completed"; CANCELLED = "cancelled"; DECLINED = "declined"
    id       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number   = models.CharField(max_length=10, unique=True, default=new_number)
    code     = models.CharField(max_length=14, unique=True, default=new_code)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    venue    = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="bookings")
    event_type = models.CharField(max_length=60, default="Wedding Reception")
    event_date = models.DateField()
    guests     = models.PositiveIntegerField()
    fee_kobo      = models.BigIntegerField(default=0)   # platform fee line
    discount_kobo = models.BigIntegerField(default=0)
    status   = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_VENDOR)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_kobo(self):  return self.venue.price_kobo + self.fee_kobo - self.discount_kobo
    @property
    def payout_kobo(self): return self.venue.price_kobo - self.discount_kobo  # vendor share

class Payment(models.Model):
    class Status(models.TextChoices):   PENDING="pending"; SUCCESS="success"; FAILED="failed"
    class Escrow(models.TextChoices):   NONE="none"; HELD="held"; RELEASED="released"; REFUNDED="refunded"
    booking   = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    reference = models.CharField(max_length=64, unique=True, default=new_reference)
    amount_kobo = models.BigIntegerField()
    currency    = models.CharField(max_length=3, default="NGN")
    status        = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    escrow_status = models.CharField(max_length=10, choices=Escrow.choices, default=Escrow.NONE)
    paystack_data = models.JSONField(null=True, blank=True)
    verified_at   = models.DateTimeField(null=True, blank=True)

class Payout(models.Model):   # drives the vendor "Payout History" table
    class Status(models.TextChoices): PAID="paid"; ESCROW="escrow"; PROCESSING="processing"; DEDUCTED="deducted"
    vendor   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payouts")
    booking  = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payouts")
    description = models.CharField(max_length=120)
    client_name = models.CharField(max_length=120, blank=True)
    amount_kobo = models.BigIntegerField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ESCROW)
    transfer_code = models.CharField(max_length=64, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)