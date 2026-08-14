from django.contrib import admin
from .models import User, VendorProfile

@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'city', 'category', 'verification_status', 'created_at')
    list_filter = ('verification_status', 'category')
    search_fields = ('business_name', 'user__email', 'city')
    actions = ['approve_vendor', 'reject_vendor']

    @admin.action(description='Approve selected vendors')
    def approve_vendor(self, request, queryset):
        queryset.update(verification_status=VendorProfile.VerificationStatus.VERIFIED)

    @admin.action(description='Reject selected vendors')
    def reject_vendor(self, request, queryset):
        queryset.update(verification_status=VendorProfile.VerificationStatus.REJECTED)