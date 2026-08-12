from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from django.db.models import FloatField, ExpressionWrapper
from django.db.models.functions import ACos, Cos, Radians, Sin, Greatest, Least
from .models import VenueListing, Availability, AvailabilityStatus
from .serializers import VenueListingSerializer, BookingSearchQuerySerializer

class VenueSearchAPIView(generics.ListAPIView):
    serializer_class = VenueListingSerializer

    def get_queryset(self):
        queryset = VenueListing.objects.all()

        # 1. Validate query params using the imported serializer
        query_serializer = BookingSearchQuerySerializer(data=self.request.query_params)
        if not query_serializer.is_valid():
            raise ValidationError(query_serializer.errors)

        params = query_serializer.validated_data

        # 2. Capacity Validation Filter (FR-13)
        guests = params.get('guest_count')
        if guests is not None:
            queryset = queryset.filter(min_guests__lte=guests, max_guests__gte=guests)

        # 3. Availability Filter
        event_date = params.get('event_date')
        if event_date:
            unavailable_vendors = Availability.objects.filter(
                date=event_date, 
                status__in=[AvailabilityStatus.BOOKED, AvailabilityStatus.BLOCKED]
            ).values_list('vendor_id', flat=True)
            queryset = queryset.exclude(vendor_id__in=unavailable_vendors)

        # 4. Geolocation Radius Filter
        lat = params.get('lat')
        lng = params.get('lng')
        radius = params.get('radius_km', 25.0)

        if lat is not None and lng is not None:
            # Clamp inner calculation strictly within [-1.0, 1.0] to prevent ACos crashes
            cos_expression = Least(1.0, Greatest(-1.0, 
                Cos(Radians(lat)) * Cos(Radians('latitude')) *
                Cos(Radians('longitude') - Radians(lng)) +
                Sin(Radians(lat)) * Sin(Radians('latitude'))
            ))

            distance_expr = ExpressionWrapper(
                6371 * ACos(cos_expression),
                output_field=FloatField()
            )
            queryset = queryset.annotate(distance=distance_expr).filter(distance__lte=radius)

        return queryset