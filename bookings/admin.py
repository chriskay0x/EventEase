from django.contrib import admin
from .models import Profile, Venue, Booking, Payment, Payout

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__email', 'user__username')

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    # Added 'display_price_naira' to the list so it shows on the main list page
    list_display = ('name', 'vendor', 'price_kobo', 'display_price_naira', 'currency')
    list_filter = ('currency',)
    search_fields = ('name', 'address', 'vendor__email')

    # This creates a custom read-only column that translates kobo to Naira
    @admin.display(description='Price (Naira)')
    def display_price_naira(self, obj):
        naira = obj.price_kobo / 100
        return f"₦{naira:,.2f}"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('number', 'code', 'customer', 'venue', 'status', 'event_date')
    list_filter = ('status', 'event_type')
    search_fields = ('number', 'code', 'customer__email')
    readonly_fields = ('id', 'created_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'booking', 'amount_kobo', 'status', 'escrow_status')
    list_filter = ('status', 'escrow_status')
    search_fields = ('reference', 'booking__number')
    readonly_fields = ('id', 'verified_at')

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'booking', 'amount_kobo', 'status')
    list_filter = ('status',)
    search_fields = ('vendor__email', 'booking__number')