from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Message, Review
from .notifications import notify


@receiver(
    post_save,
    sender=Review,
    dispatch_uid="engagement_review_notification",
)
def notify_vendor_of_review(sender, instance, created, **kwargs):
    if created:
        notify(
            instance.vendor,
            "New review received",
            f"You received a {instance.rating}-star review "
            f"from {instance.author.username}.",
        )


@receiver(
    post_save,
    sender=Message,
    dispatch_uid="engagement_message_notification",
)
def notify_recipient_of_message(sender, instance, created, **kwargs):
    if created:
        notify(
            instance.receiver,
            "New message",
            f"New message from {instance.sender.username}.",
        )