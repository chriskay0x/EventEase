from django.db import transaction
from django.utils import timezone

from .models import Booking, Payment


class BookingError(Exception):
    """Business-rule violation → HTTP 400."""


def create_booking(*, client, listing, event_date, guest_count,
                   event_type="", note="", event_start_time=None,
                   event_end_time=None, items=None):
    # FR-03: reject if guest count outside capacity
    if not (listing.min_guests <= guest_count <= listing.max_guests):
        raise BookingError(
            f"{listing.name} hosts {listing.min_guests}–{listing.max_guests} guests."
        )

    from listings.models import Availability

    with transaction.atomic():
        # Concurrency NFR: row-level lock prevents double-booking
        availability = (
            Availability.objects.select_for_update()
            .filter(vendor=listing.vendor, date=event_date)
            .first()
        )
        if availability is None:
            availability = Availability.objects.create(
                vendor=listing.vendor, date=event_date, status="available"
            )
        if availability.status != "available":
            raise BookingError("This date is already booked or blocked.")

        booking = listing.bookings.create(
            client=client,
            event_date=event_date,
            event_start_time=event_start_time,
            event_end_time=event_end_time,
            guest_count=guest_count,
            event_type=event_type,
            note=note,
        )

        total = listing.base_price
        for item in items or []:
            service, qty = item["service"], item["quantity"]
            booking.items.create(service=service, price=service.price, quantity=qty)
            total += service.price * qty

        booking.total_price = total
        booking.save(update_fields=["total_price"])
        Payment.objects.create(booking=booking, amount=total)   # FR-05 escrow

        availability.status = "booked"                          # FR-14 auto-lock
        availability.save(update_fields=["status"])

    return booking


def vendor_respond(booking, vendor, accept: bool):
    """Vendor Accept/Decline (FR-15)."""
    if booking.listing.vendor_id != vendor.id:
        raise PermissionError("Not your listing.")
    if booking.status != Booking.Status.PENDING:
        raise BookingError("This request was already handled.")

    booking.status = Booking.Status.CONFIRMED if accept else Booking.Status.DECLINED
    booking.save(update_fields=["status"])

    if not accept:  # free the date again
        from listings.models import Availability
        Availability.objects.filter(
            vendor=vendor, date=booking.event_date, status="booked"
        ).update(status="available")
    return booking


def complete_booking(booking):
    """Event done → release escrow to vendor."""
    booking.status = Booking.Status.COMPLETED
    booking.save(update_fields=["status"])
    payment = booking.payment
    payment.status = Payment.Status.RELEASED
    payment.released_at = timezone.now()
    payment.save(update_fields=["status", "released_at"])
    return booking