from .models import Availability, AvailabilityStatus

def lock_vendor_date(vendor_id, date):
    """Called by Team 3 (Bookings) to auto-lock dates upon booking creation."""
    availability, created = Availability.objects.get_or_create(
        vendor_id=vendor_id,
        date=date,
        defaults={'status': AvailabilityStatus.BOOKED}
    )
    if not created:
        if availability.status == AvailabilityStatus.BOOKED:
            raise ValueError("Date is already booked.")
        availability.status = AvailabilityStatus.BOOKED
        availability.save()
    return availability