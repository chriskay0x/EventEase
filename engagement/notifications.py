from .models import Notification


def notify(recipient, kind, message):
    return Notification.objects.create(
        recipient=recipient,
        kind=kind,
        message=message,
    )