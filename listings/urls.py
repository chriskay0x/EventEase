from django.urls import path
from . import views
app_name = 'listings'

urlpatterns = [
    path('', views.homepage, name = 'home'),
    path('browse', views.browse, name = 'browse'),
    path('calendar', views.calendar, name = 'calendar'),
    path('create_listing/', views.create_listing, name = 'create_listing'),
    path('my_listings', views.my_listings, name = 'my_listings'),
    path('service_detail', views.service_detail, name = 'service_detail'),
    path('venue_detail', views.venue_detail, name = 'venue_detail'),
]