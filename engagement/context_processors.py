from .models import Notification


def unread_notifications(request):
    if not request.user.is_authenticated:
        return {}

    return {
        "unread_notifications": Notification.objects.filter(
            recipient=request.user,
            read_at__isnull=True,
        ).count()
    }