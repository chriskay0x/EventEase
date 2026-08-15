import hashlib
import hmac
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from . import paystack
from .models import Booking, Payment, Payout, Venue  # <-- Make sure Venue is here


# ---------- shared, idempotent success handler (verify AND webhook) ----------
def apply_success(reference, ps_data):
    with transaction.atomic():
        payment = Payment.objects.select_for_update().filter(reference=reference).first()
        if not payment or payment.status == Payment.Status.SUCCESS:
            return
        if ps_data.get("amount") != payment.amount_kobo:      # underpayment guard
            payment.status = Payment.Status.FAILED
            payment.paystack_data = ps_data
            payment.save()
            return
        payment.status = Payment.Status.SUCCESS
        payment.escrow_status = Payment.Escrow.HELD
        payment.paystack_data = ps_data
        payment.verified_at = timezone.now()
        payment.save()

        b = payment.booking
        b.status = Booking.Status.PAID
        b.save()
        Payout.objects.get_or_create(
            booking=b, vendor=b.venue.vendor,
            defaults=dict(
                description=b.venue.name,
                client_name=b.customer.get_full_name() or b.customer.email,
                amount_kobo=b.payout_kobo,
                status=Payout.Status.ESCROW,
            ),
        )


# ---------- A) issue reference before the popup opens ----------
@login_required
@require_POST
def pay_for_booking(request, booking_id):
    b = get_object_or_404(Booking, id=booking_id, customer=request.user)
    if b.status not in (Booking.Status.CONFIRMED, Booking.Status.PENDING_VENDOR):
        return JsonResponse({"error": "not payable"}, status=409)
    payment = Payment.objects.create(
        booking=b, amount_kobo=b.total_kobo, currency=b.venue.currency)
    return JsonResponse({
        "reference": payment.reference,
        "amount": b.total_kobo,
        "email": request.user.email,
        "publicKey": settings.PAYSTACK_PUBLIC_KEY,
        "currency": settings.PAYSTACK_CURRENCY,
    })


# ---------- B) verify (confirmation page calls this) ----------
@login_required
@require_GET
def verify_payment(request):
    reference = request.GET.get("reference")
    payment = Payment.objects.filter(reference=reference).select_related("booking").first()
    if not payment:
        return JsonResponse({"status": "unknown"}, status=404)
    if payment.status != Payment.Status.SUCCESS:
        data = paystack.verify_transaction(reference).get("data") or {}
        if data.get("status") == "success":
            apply_success(reference, data)
            payment.refresh_from_db()
    return JsonResponse({"status": payment.status, "bookingId": str(payment.booking_id)})


# ---------- C) webhook (safety net) ----------
@csrf_exempt
@require_POST
def paystack_webhook(request):
    sig = request.headers.get("x-paystack-signature", "")
    expected = hmac.new(settings.PAYSTACK_SECRET_KEY.encode(),
                        request.body, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return JsonResponse({"error": "bad signature"}, status=400)

    event = json.loads(request.body)
    etype, data = event.get("event"), event.get("data") or {}

    if etype == "charge.success":
        apply_success(data.get("reference"), data)
    elif etype == "charge.reversed":
        Payment.objects.filter(reference=data.get("reference")).update(
            status=Payment.Status.FAILED, escrow_status=Payment.Escrow.REFUNDED)
    elif etype == "transfer.success":
        Payout.objects.filter(transfer_code=data.get("transfer_code")).update(
            status=Payout.Status.PAID, paid_at=timezone.now())
    elif etype == "transfer.failed":
        Payout.objects.filter(transfer_code=data.get("transfer_code")).update(
            status=Payout.Status.ESCROW)
    return JsonResponse({"ok": True})


# ---------- D) escrow release → vendor bank ----------
@login_required
@require_POST
def release_payout(request, payout_id):
    payout = get_object_or_404(Payout, id=payout_id, vendor=request.user)
    if payout.status != Payout.Status.ESCROW:
        return JsonResponse({"error": "not releasable"}, status=409)

    profile = request.user.profile
    if not profile.recipient_code:
        rec = paystack.create_recipient(
            profile.payout_name, profile.account_number, profile.bank_code)
        profile.recipient_code = rec["data"]["recipient_code"]
        profile.save()

    t = paystack.transfer(profile.recipient_code, payout.amount_kobo,
                          f"Payout {payout.booking.number}")
    payout.transfer_code = t["data"]["transfer_code"]
    payout.status = Payout.Status.PROCESSING
    payout.save()
    return JsonResponse({"ok": True})   # flips to 'paid' on transfer.success webhook


# ---------- E) page-data endpoints ----------
@login_required
@require_GET
def my_bookings(request):
    qs = Booking.objects.filter(customer=request.user).select_related("venue")
    return JsonResponse({"bookings": [{
        "id": str(b.id), "number": b.number, "venue": b.venue.name,
        "image": b.venue.image_url, "status": b.status,
        "date": b.event_date.isoformat(), "guests": b.guests,
        "vendor": b.venue.vendor.get_full_name() or "Vendor",
        "total": b.total_kobo,
    } for b in qs]})


@login_required
@require_GET
def booking_detail(request, booking_id):
    b = get_object_or_404(
        Booking.objects.select_related("venue", "venue__vendor"), id=booking_id)
    return JsonResponse({
        "id": str(b.id), "number": b.number, "code": b.code, "status": b.status,
        "venue": b.venue.name, "address": b.venue.address, "image": b.venue.image_url,
        "event_type": b.event_type, "date": b.event_date.isoformat(), "guests": b.guests,
        "price": b.venue.price_kobo, "fee": b.fee_kobo, "discount": b.discount_kobo,
        "total": b.total_kobo,
        "vendor": {"name": b.venue.vendor.get_full_name(), "role": "Estate Manager"},
    })


@login_required
@require_GET
def vendor_requests(request):
    qs = Booking.objects.filter(venue__vendor=request.user).select_related("customer", "venue")
    pending = request.GET.get("status", "pending") == "pending"
    qs = (qs.filter(status=Booking.Status.PENDING_VENDOR) if pending
          else qs.exclude(status=Booking.Status.PENDING_VENDOR))
    return JsonResponse({"requests": [{
        "id": str(b.id), "customer": b.customer.get_full_name() or b.customer.email,
        "type": b.event_type, "location": b.venue.name,
        "date": b.event_date.isoformat(), "guests": b.guests,
        "payout": b.payout_kobo, "status": b.status,
        "requested_at": b.created_at.isoformat(),
    } for b in qs]})


@login_required
@require_POST
def vendor_request_action(request, booking_id, action):
    b = get_object_or_404(Booking, id=booking_id, venue__vendor=request.user)
    if action == "accept":
        b.status = Booking.Status.CONFIRMED
    elif action == "decline":
        b.status = Booking.Status.DECLINED
    else:
        return JsonResponse({"error": "bad action"}, status=400)
    b.save()
    return JsonResponse({"ok": True, "status": b.status})


@login_required
@require_GET
def vendor_finance(request):
    payouts = Payout.objects.filter(vendor=request.user)
    paid = payouts.filter(status=Payout.Status.PAID)
    escrowed = payouts.filter(status=Payout.Status.ESCROW)
    year = timezone.now().year

    ytd = paid.filter(paid_at__year=year).aggregate(s=Sum("amount_kobo"))["s"] or 0
    available = paid.aggregate(s=Sum("amount_kobo"))["s"] or 0
    escrow = escrowed.aggregate(s=Sum("amount_kobo"))["s"] or 0
    next_payout = escrowed.order_by("booking__event_date").first()

    months = (paid.annotate(m=TruncMonth("paid_at")).values("m")
              .annotate(s=Sum("amount_kobo")).order_by("m"))

    return JsonResponse({
        "ytd": ytd, "available": available, "escrow": escrow,
        "next_payout": next_payout and {
            "date": next_payout.booking.event_date.isoformat(),
            "amount": next_payout.amount_kobo},
        "chart": [{"month": r["m"].strftime("%b").upper(), "value": r["s"]} for r in months],
        "history": [{
            "date": (p.paid_at or p.booking.created_at).strftime("%b %d, %Y"),
            "description": p.description, "client": p.client_name,
            "status": p.status, "amount": p.amount_kobo,
        } for p in payouts.order_by("-booking__event_date")[:10]],
    })
    
    # add venue_id so REBOOK works from the frontend
# in my_bookings():  add  "venue_id": str(b.venue_id),   inside the dict
# in booking_detail(): add "venue_id": str(b.venue_id), inside the dict

@require_GET
def venues_list(request):
    qs = Venue.objects.select_related("vendor").all()
    return JsonResponse({"venues": [{
        "id": str(v.id), "name": v.name, "address": v.address,
        "image": v.image_url, "price": v.price_kobo,
        "vendor": v.vendor.get_full_name() or "Vendor",
    } for v in qs]})

@login_required
@require_POST
def create_booking(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        data = {}
    b = Booking.objects.create(
        customer=request.user, venue=venue,
        event_type=data.get("event_type", "Private Event"),
        event_date=data.get("date") or (timezone.now().date() + timezone.timedelta(days=30)),
        guests=int(data.get("guests", 50)),
        fee_kobo=venue.price_kobo * 8 // 100,
        status=Booking.Status.PENDING_VENDOR,
    )
    return JsonResponse({"id": str(b.id), "number": b.number}, status=201)

