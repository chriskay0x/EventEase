from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.generic import ListView
from django.db.models import FloatField, ExpressionWrapper
from django.db.models.functions import ACos, Cos, Radians, Sin, Greatest, Least
from .models import VenueListing, Availability, AvailabilityStatus, Listing
# from django.contrib.auth.decorators import login_required

# class VenueBrowseView(ListView):
#     model = VenueListing
#     template_name = 'listings/browse.html'
#     context_object_name = 'venues'
#     paginate_by = 12

#     def get_queryset(self):
#         queryset = VenueListing.objects.all()
#         # Bind GET parameters to form for validation
#         self.form = VenueSearchForm(self.request.GET)

#         if self.form.is_valid():
#             data = self.form.cleaned_data

#             # 1. Capacity Validation Filter (FR-13)
#             guests = data.get('guest_count')
#             if guests is not None:
#                 queryset = queryset.filter(min_guests__lte=guests, max_guests__gte=guests)

#             # 2. Availability Filter
#             event_date = data.get('event_date')
#             if event_date:
#                 unavailable_vendors = Availability.objects.filter(
#                     date=event_date, 
#                     status__in=[AvailabilityStatus.BOOKED, AvailabilityStatus.BLOCKED]
#                 ).values_list('vendor_id', flat=True)
#                 queryset = queryset.exclude(vendor_id__in=unavailable_vendors)

#             # 3. Geolocation Radius Filter
#             lat = data.get('lat')
#             lng = data.get('lng')
#             radius = data.get('radius_km') or 25.0

#             if lat is not None and lng is not None:
#                 cos_expression = Least(1.0, Greatest(-1.0, 
#                     Cos(Radians(lat)) * Cos(Radians('latitude')) *
#                     Cos(Radians('longitude') - Radians(lng)) +
#                     Sin(Radians(lat)) * Sin(Radians('latitude'))
#                 ))

#                 distance_expr = ExpressionWrapper(
#                     6371 * ACos(cos_expression),
#                     output_field=FloatField()
#                 )
#                 queryset = queryset.annotate(distance=distance_expr).filter(distance__lte=radius).order_by('distance')

#         return queryset

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Pass form back to template to keep search inputs populated
#         context['form'] = self.form
#         return context

def homepage(request):
    return render(request, 'listings/homepage.html')

# def browse(request):

#     listings = Listing.objects.filter(
#         status="live"
#     )

#     search = request.GET.get("search")

#     if search:
#         listings = listings.filter(
#             name__icontains=search
#         )

#     return render(
#         request,
#         "listings/browse.html",
#         {
#             "listings": listings
#         }
#     )

def browse(request):
    listings = Listing.objects.filter(
        status="live"
    )

    # SEARCH
    # -----------------------------

    search = request.GET.get("search")

    if search:

        listings = listings.filter(
            name__icontains=search
        )

    # LOCATION
    # -----------------------------

    location = request.GET.get("location")

    if location:

        listings = listings.filter(
            location__icontains=location
        )

    # CATEGORY
    # -----------------------------

    category = request.GET.get("category")

    if category:

        listings = listings.filter(
            category=category
        )

    # CAPACITY
    # -----------------------------

    capacity = request.GET.get("capacity")

    if capacity:

        listings = listings.filter(
            capacity__gte=capacity
        )

    # PRICE
    # -----------------------------

    price = request.GET.get("price")

    if price == "1":

        listings = listings.filter(
            price__lt=100000
        )

    elif price == "2":

        listings = listings.filter(
            price__gte=100000,
            price__lt=250000
            )

    elif price == "3":

        listings = listings.filter(
            price__gte=250000,
            price__lt=500000
        )
    elif price == "4":
        listings = listings.filter(
            price__gte=500000
        )

    # SORT
    # -----------------------------

    sort = request.GET.get("sort")

    if sort == "price_low":

        listings = listings.order_by("price")

    elif sort == "price_high":

        listings = listings.order_by("-price")

    elif sort == "capacity":

        listings = listings.order_by("-capacity")

    else:

        listings = listings.order_by("-created_at")


    return render(
        request,
        "listings/browse.html",
        {
            "listings": listings
        }
    )


# @login_required
def calendar(request, listing_id):

    listing = get_object_or_404(
        Listing,id=listing_id,
        owner=request.user)

    availability = Availability.objects.filter(
        listing=listing
    ).order_by("date")

    return render(
        request,
        "listings/calendar.html",
        {
            "listing": listing,
            "availability": availability,
        }
    )
# def calendar(request):
#     return render(request, 'listings/calendar.html')
    # return render(request, 'listings/calendar.html',{"listings":listings})

def create_listing(request):
    return render(request, 'listings/create_listing.html')

def my_listings(request):
    return render(request, 'listings/my_listings.html')

def service_detail(request):
    return render(request, 'listings/service_detail.html')

def venue_detail(request):
    return render(request, 'listings/venue_detail.html')