from django.contrib import admin
from .models import Availability, ServiceListing, VenueListing

admin.site.register(VenueListing)
admin.site.register(ServiceListing)
admin.site.register(Availability)