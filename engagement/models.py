from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Message(TimeStampedModel):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages_sent",
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages_received",
    )

    body = models.TextField(max_length=2000)

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender} → {self.recipient}"


class Review(TimeStampedModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_written",
    )

    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_received",
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )

    comment = models.TextField(
        blank=True,
        max_length=2000,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author} → {self.vendor} ({self.rating}★)"


class Notification(TimeStampedModel):
    class Kind(models.TextChoices):
        BOOKING_REQUESTED = "booking_requested", "Booking requested"
        BOOKING_CONFIRMED = "booking_confirmed", "Booking confirmed"
        BOOKING_DECLINED = "booking_declined", "Booking declined"
        PAYMENT_RELEASED = "payment_released", "Payment released"
        REVIEW_RECEIVED = "review_received", "New review received"
        MESSAGE_RECEIVED = "message_received", "New message received"
        SYSTEM = "system", "System"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    kind = models.CharField(
        max_length=30,
        choices=Kind.choices,
    )

    message = models.CharField(max_length=255)

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient} · {self.kind}"

    @property
    def is_read(self):
        return self.read_at is not None

    def mark_read(self):
        if not self.is_read:
            self.read_at = timezone.now()
            self.save(
                update_fields=[
                    "read_at",
                    "updated_at",
                ]
            )