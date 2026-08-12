from rest_framework import serializers

from listings.models import ServiceListing
from .models import Booking, BookingItem, Payment
from .services import create_booking


class BookingItemCreateSerializer(serializers.Serializer):
    service = serializers.PrimaryKeyRelatedField(queryset=ServiceListing.objects.all())
    quantity = serializers.IntegerField(min_value=1, default=1)


class BookingCreateSerializer(serializers.ModelSerializer):
    items = BookingItemCreateSerializer(many=True, required=False, default=list)

    class Meta:
        model = Booking
        fields = ["listing", "event_date", "event_start_time", "event_end_time",
                  "guest_count", "event_type", "note", "items"]

    def create(self, validated_data):
        items = validated_data.pop("items", [])
        return create_booking(client=self.context["request"].user,
                              items=items, **validated_data)


class BookingItemDetailSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.category", read_only=True)

    class Meta:
        model = BookingItem
        fields = ["id", "service", "service_name", "price", "quantity"]


class PaymentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["amount", "status", "escrow_release_date"]


class BookingDetailSerializer(serializers.ModelSerializer):
    items = BookingItemDetailSerializer(many=True, read_only=True)
    payment = PaymentSummarySerializer(read_only=True)
    listing_name = serializers.CharField(source="listing.name", read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "reference_code", "listing", "listing_name", "event_date",
                  "event_start_time", "event_end_time", "guest_count", "event_type",
                  "note", "status", "total_price", "items", "payment", "created_at"]