from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ReviewForm
from .models import Message, Notification, Review


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def dashboard(request):
    user = request.user

    total_messages = Message.objects.filter(
        recipient=user
    ).count()

    total_reviews = Review.objects.filter(
        vendor=user
    ).count()

    average_rating = Review.objects.filter(
        vendor=user
    ).aggregate(
        average=Avg("rating")
    )["average"]

    total_notifications = Notification.objects.filter(
        recipient=user
    ).count()

    unread_notifications = Notification.objects.filter(
        recipient=user,
        read_at__isnull=True,
    ).count()

    recent_reviews = Review.objects.filter(
        vendor=user
    ).select_related("author")[:5]

    recent_messages = Message.objects.filter(
        recipient=user
    ).select_related("sender")[:5]

    context = {
        "total_messages": total_messages,
        "total_reviews": total_reviews,
        "average_rating": average_rating,
        "total_notifications": total_notifications,
        "unread_notifications": unread_notifications,
        "recent_reviews": recent_reviews,
        "recent_messages": recent_messages,
    }

    return render(
        request,
        "engagement/dashboard.html",
        context,
    )


# ============================================================
# MESSAGES
# ============================================================

@login_required
def message_list(request):
    received_messages = Message.objects.filter(
        recipient=request.user
    ).select_related("sender")

    sent_messages = Message.objects.filter(
        sender=request.user
    ).select_related("recipient")

    context = {
        "received_messages": received_messages,
        "sent_messages": sent_messages,
    }

    return render(
        request,
        "engagement/messages.html",
        context,
    )


@login_required
def message_create(request):
    User = get_user_model()

    if request.method == "POST":
        recipient_id = request.POST.get("recipient")
        body = request.POST.get("body", "").strip()

        recipient = get_object_or_404(
            User,
            pk=recipient_id,
        )

        if recipient == request.user:
            messages.error(
                request,
                "You cannot send a message to yourself.",
            )
            return redirect("engagement:message_create")

        if not body:
            messages.error(
                request,
                "Message cannot be empty.",
            )
            return redirect("engagement:message_create")

        Message.objects.create(
            sender=request.user,
            recipient=recipient,
            body=body,
        )

        messages.success(
            request,
            "Message sent successfully.",
        )

        return redirect("engagement:message_list")

    users = User.objects.exclude(
        pk=request.user.pk
    )

    return render(
        request,
        "engagement/message_form.html",
        {"users": users},
    )


# ============================================================
# REVIEWS
# ============================================================

@login_required
def review_list(request):
    reviews = Review.objects.filter(
        vendor=request.user
    ).select_related("author")

    average_rating = reviews.aggregate(
        average=Avg("rating")
    )["average"]

    return render(
        request,
        "engagement/reviews.html",
        {
            "reviews": reviews,
            "average_rating": average_rating,
        },
    )


@login_required
def review_create(request):
    User = get_user_model()

    if request.method == "POST":
        vendor_id = request.POST.get("vendor")
        vendor = get_object_or_404(
            User,
            pk=vendor_id,
        )

        if vendor == request.user:
            messages.error(
                request,
                "You cannot review yourself.",
            )
            return redirect("engagement:review_create")

        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.vendor = vendor
            review.save()

            messages.success(
                request,
                "Your review has been submitted.",
            )

            return redirect("engagement:review_list")

    else:
        form = ReviewForm()

    users = User.objects.exclude(
        pk=request.user.pk
    )

    return render(
        request,
        "engagement/review_form.html",
        {
            "form": form,
            "users": users,
        },
    )


# ============================================================
# NOTIFICATIONS
# ============================================================

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    )

    if request.GET.get("unread"):
        notifications = notifications.filter(
            read_at__isnull=True
        )

    paginator = Paginator(
        notifications,
        20,
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "engagement/notifications.html",
        {
            "page_obj": page_obj,
        },
    )


@login_required
@require_POST
def notification_mark_read(request, pk):
    notification = get_object_or_404(
        Notification,
        pk=pk,
        recipient=request.user,
    )

    notification.mark_read()

    return redirect(
        "engagement:notification_list"
    )


@login_required
@require_POST
def notification_mark_all_read(request):
    Notification.objects.filter(
        recipient=request.user,
        read_at__isnull=True,
    ).update(
        read_at=timezone.now()
    )

    messages.success(
        request,
        "All notifications marked as read.",
    )

    return redirect(
        "engagement:notification_list"
    )