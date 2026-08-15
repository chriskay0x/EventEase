from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "client", "Client"
        VENDOR = "vendor", "Vendor"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CLIENT)
    phone = models.CharField(max_length=20, blank=True)
    verified = models.BooleanField(default=False)


# class VendorProfile(TimeStampedModel):
#     class VerificationStatus(models.TextChoices):
#         PENDING = "pending", "Pending"
#         APPROVED = "approved", "Approved"
#         REJECTED = "rejected", "Rejected"

#     class Category(models.TextChoices):
#         VENUE = "venue", "Venue"
#         CATERING = "catering", "Catering"
#         DJ = "dj", "DJ / Entertainment"

#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vendor_profile")
#     business_name = models.CharField(max_length=255)
#     category = models.CharField(max_length=20, choices=Category.choices)
#     verification_status = models.CharField(max_length=10, choices=VerificationStatus.choices, default=VerificationStatus.PENDING)
#     verification_document = models.FileField(upload_to="vendor_verification/", blank=True, null=True)
    
    
class VendorProfile(models.Model):
    class VerificationStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING = 'pending', 'Pending Approval'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'
        
    class Category(models.TextChoices):
        VENUE = "venue", "Venue"
        CATERING = "catering", "Catering"
        DJ = "dj", "DJ / Entertainment"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=255)
    legal_business_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    
    # Extended Profile & Social
    bio = models.TextField(blank=True, null=True, help_text="Business Description")
    avatar = models.ImageField(upload_to='vendor_avatars/', blank=True, null=True)
    instagram_handle = models.CharField(max_length=100, blank=True, null=True)
    website_url = models.URLField(max_length=255, blank=True, null=True)

    # Notification & Security Preferences
    email_notifications = models.BooleanField(default=True)
    sms_alerts = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    
    # Verification Fields
    verification_document = models.FileField(upload_to='vendor_documents/', blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name or self.user.email
    
    
    
class BookingRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='booking_requests')
    client_name = models.CharField(max_length=150)
    client_initials = models.CharField(max_length=5, blank=True)
    event_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.client_initials and self.client_name:
            parts = self.client_name.strip().split()
            self.client_initials = "".join([p[0].upper() for p in parts[:2]])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_name} - {self.event_date} ({self.status})"


class VendorActivity(models.Model):
    class ActivityType(models.TextChoices):
        REVIEW = 'review', 'Review'
        SURGE = 'surge', 'Surge'
        SYSTEM = 'system', 'System'

    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='activities')
    title = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices, default=ActivityType.SYSTEM)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vendor.business_name}: {self.title}"