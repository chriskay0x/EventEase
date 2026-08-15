from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),

    path(
        "booking-oversite/",
        views.booking_oversite,
        name="booking_oversite"
    ),

    path(
        "client-review/",
        views.client_review,
        name="client_review"
    ),

    path(
        "dispute-detail/",
        views.dispute_detail,
        name="dispute_detail"
    ),

    path(
        "review/",
        views.review,
        name="review"
    ),

    path(
    "system-overview/",
    views.system_overview,
    name="system_overview"
    ),

    path(
        "verification-queue/",
        views.verification_queue,
        name="verification_queue"
    ),
]