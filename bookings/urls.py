from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("bookings", views.BookingViewSet, basename="booking")

urlpatterns = [
    path("", include(router.urls)),
    path("vendors/earnings/", views.earnings, name="vendor-earnings"),
]