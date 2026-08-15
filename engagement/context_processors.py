from .models import Notification


def unread_notifications(request):
    if not request.user.is_authenticated:
        return {}

    return {
        "unread_notifications": Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).count()
    }