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
    
    # Verification Fields
    verification_document = models.FileField(upload_to='vendor_documents/', blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name or self.user.email