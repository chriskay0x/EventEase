from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView
from django.db.models import FloatField, ExpressionWrapper
from django.db.models.functions import ACos, Cos, Radians, Sin, Greatest, Least
from .models import VenueListing, Availability, AvailabilityStatus
from .forms import VenueSearchForm

class VenueBrowseView(ListView):
    model = VenueListing
    template_name = 'listings/browse.html'
    context_object_name = 'venues'
    paginate_by = 12

    def get_queryset(self):
        queryset = VenueListing.objects.all()
        # Bind GET parameters to form for validation
        self.form = VenueSearchForm(self.request.GET)

        if self.form.is_valid():
            data = self.form.cleaned_data

            # 1. Capacity Validation Filter (FR-13)
            guests = data.get('guest_count')
            if guests is not None:
                queryset = queryset.filter(min_guests__lte=guests, max_guests__gte=guests)

            # 2. Availability Filter
            event_date = data.get('event_date')
            if event_date:
                unavailable_vendors = Availability.objects.filter(
                    date=event_date, 
                    status__in=[AvailabilityStatus.BOOKED, AvailabilityStatus.BLOCKED]
                ).values_list('vendor_id', flat=True)
                queryset = queryset.exclude(vendor_id__in=unavailable_vendors)

            # 3. Geolocation Radius Filter
            lat = data.get('lat')
            lng = data.get('lng')
            radius = data.get('radius_km') or 25.0

            if lat is not None and lng is not None:
                cos_expression = Least(1.0, Greatest(-1.0, 
                    Cos(Radians(lat)) * Cos(Radians('latitude')) *
                    Cos(Radians('longitude') - Radians(lng)) +
                    Sin(Radians(lat)) * Sin(Radians('latitude'))
                ))

                distance_expr = ExpressionWrapper(
                    6371 * ACos(cos_expression),
                    output_field=FloatField()
                )
                queryset = queryset.annotate(distance=distance_expr).filter(distance__lte=radius).order_by('distance')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass form back to template to keep search inputs populated
        context['form'] = self.form
        return context

def homepage(request):
    return render(request, 'listings/homepage.html')

def browse(request):
    return render(request, 'browse.html')

def calendar(request):
    return render(request, 'calendar.html')

def create_listing(request):
    return render(request, 'create_listing.html')

def my_listings(request):
    return render(request, 'my_listings.html')

def service_detail(request):
    return render(request, 'service_detail.html')

def venue_detail(request):
    return render(request, 'listings/venue_detail.html')