# engagement/views.py

from django.shortcuts import render, get_object_or_404, redirect

from .models import Message, Review, Notification, BookingOversight, DisputeDetail, VerificationQueue
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Review


def dashboard(request):
    """Engagement dashboard."""
    total_messages = Message.objects.count()
    total_reviews = Review.objects.count()
    total_notifications = Notification.objects.count()

    unread_notifications = Notification.objects.filter(
        is_read=False
    ).count()

    recent_messages = Message.objects.order_by("-created_at")[:5]
    recent_reviews = Review.objects.order_by("-created_at")[:5]

    average_rating = 0

    if total_reviews > 0:
        ratings = Review.objects.values_list("rating", flat=True)
        average_rating = sum(ratings) / total_reviews

    context = {
        "total_messages": total_messages,
        "total_reviews": total_reviews,
        "total_notifications": total_notifications,
        "unread_notifications": unread_notifications,
        "average_rating": round(average_rating, 1),
        "recent_messages": recent_messages,
        "recent_reviews": recent_reviews,
    }

    return render(request, "engagement/dashboard.html", context)


def booking_oversite(request):
    """Booking oversight page."""
    return render(request, "engagement/booking_oversite.html")


def client_review(request):
    """Client reviews page."""
    reviews = Review.objects.all().order_by("-created_at")

    context = {
        "reviews": reviews,
    }

    return render(request, "engagement/client_review.html", context)


def dispute_detail(request):
    """Dispute details page."""
    return render(request, "engagement/dispute_detail.html")


# @login_required
def review(request):
    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment", "").strip()

        if rating and comment:
            Review.objects.create(
                reviewer=request.user,
                rating=int(rating),
                comment=comment,
            )

            return render(
                request,
                "engagement/review.html",
                {
                    "submitted": True,
                    "rating": int(rating),
                    "comment": comment,
                },
            )

    return render(request, "engagement/review.html")


def system_overview(request):
    """System overview page."""
    context = {
        "total_messages": Message.objects.count(),
        "total_reviews": Review.objects.count(),
        "total_notifications": Notification.objects.count(),
    }

    return render(request, "engagement/system_overview.html", context)


def verification_queue(request):
    """Verification queue page."""
    return render(request, "engagement/verification_queue.html")