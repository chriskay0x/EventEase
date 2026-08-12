from django.db.models import F, Sum
from rest_framework import permissions, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from . import services
from .models import Booking, Payment
from .serializers import BookingCreateSerializer, BookingDetailSerializer


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateSerializer
        return BookingDetailSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Booking.objects.select_related("listing", "payment")
        if getattr(user, "role", "") == "vendor":       # Booking Requests screen
            return qs.filter(listing__vendor=user)
        return qs.filter(client=user)                    # My Bookings screen

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            booking = serializer.save()
        except services.BookingError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response(BookingDetailSerializer(booking).data, status=201)

    def _require_vendor(self, request, booking):
        if getattr(request.user, "role", "") != "vendor" or \
                booking.listing.vendor_id != request.user.id:
            raise PermissionError("Not your listing.")

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        booking = self.get_object()
        try:
            self._require_vendor(request, booking)
            services.vendor_respond(booking, request.user, accept=True)
        except (PermissionError, services.BookingError) as exc:
            return Response({"error": str(exc)}, status=400)
        return Response({"status": booking.status})

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        booking = self.get_object()
        try:
            self._require_vendor(request, booking)
            services.vendor_respond(booking, request.user, accept=False)
        except (PermissionError, services.BookingError) as exc:
            return Response({"error": str(exc)}, status=400)
        return Response({"status": booking.status})

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        booking = self.get_object()
        try:
            self._require_vendor(request, booking)
            services.complete_booking(booking)
        except PermissionError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response({"status": booking.status, "payment": booking.payment.status})


@api_view(["GET"])
def earnings(request):
    """Financial Overview screen (FR-16)."""
    if getattr(request.user, "role", "") != "vendor":
        return Response({"detail": "Vendors only."}, status=403)

    payments = Payment.objects.filter(booking__listing__vendor=request.user)
    next_payout = (payments.filter(status=Payment.Status.HELD,
                                   escrow_release_date__isnull=False)
                   .order_by("escrow_release_date").first())

    return Response({
        "total_released": payments.filter(status=Payment.Status.RELEASED)
            .aggregate(t=Sum("amount"))["t"] or 0,
        "pending_escrow": payments.filter(status=Payment.Status.HELD)
            .aggregate(t=Sum("amount"))["t"] or 0,
        "next_payout": {"date": next_payout.escrow_release_date,
                        "estimated": next_payout.amount} if next_payout else None,
        "history": list(payments.select_related("booking")
                        .order_by("-created_at")
                        .values("id", "amount", "status", "created_at")
                        .annotate(booking_ref=F("booking__reference_code"))),
    })