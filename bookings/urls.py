from django.http import Http404
from django.shortcuts import render
from django.urls import path
from . import views

# Your exact list of pages
PAGES = {
    "confirmed", 
    "payment_failed", 
    "payment", 
    "review_pay", 
    "booking_detail",
    "my_bookings", 
    "review_bookings", 
    "vendor_requests", 
    "earnings",
    "discover",    # <-- Added
    "messages"     # <-- Added
}

def page(request, name):
    if name not in PAGES:
        raise Http404(f"Page '{name}' not found in PAGES list.")
    return render(request, f"bookings/{name}.html")

urlpatterns = [
    # 1. Frontend Template Routes
    path("<str:name>.html", page, name="page"),
    
    # 2. Backend API Routes (Payment & Verification)
    path("api/bookings/<uuid:booking_id>/pay", views.pay_for_booking),
    path("api/payments/verify", views.verify_payment),
    path("api/webhooks/paystack", views.paystack_webhook),
    
    # 3. Customer Endpoints
    path("api/me/bookings", views.my_bookings),
    path("api/bookings/<uuid:booking_id>", views.booking_detail),
    
    # 4. Vendor Endpoints
    path("api/vendor/requests", views.vendor_requests),
    path("api/vendor/requests/<uuid:booking_id>/<str:action>", views.vendor_request_action),
    path("api/vendor/payouts/<int:payout_id>/release", views.release_payout),
    path("api/vendor/finance", views.vendor_finance),  # <-- Notice the comma here!

    # 5. NEW: Venues & Booking Creation (for Discover page & Rebook button)
    path("api/venues", views.venues_list),
    path("api/venues/<uuid:venue_id>/book", views.create_booking),
]