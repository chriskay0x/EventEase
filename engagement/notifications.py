from .models import Notification


def notify(user, title, message):
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
    )