from django.contrib import admin

from . import services
from .models import Booking, BookingItem, Payment


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("reference_code", "client", "listing", "event_date",
                    "status", "total_price")
    list_filter = ("status",)
    search_fields = ("reference_code", "client__username")
    actions = ["mark_completed"]

    @admin.action(description="Complete booking & release escrow")
    def mark_completed(self, request, queryset):
        for booking in queryset:
            services.complete_booking(booking)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "amount", "status", "escrow_release_date")
    list_filter = ("status",)
    actions = ["mark_refunded"]

    @admin.action(description="Refund payment (FR-20)")
    def mark_refunded(self, request, queryset):
        queryset.update(status=Payment.Status.REFUNDED)


admin.site.register(BookingItem)