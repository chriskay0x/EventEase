from django.contrib import admin

from .models import (
    DisputeDetail,
    Message,
    Notification,
    Review,
    BookingOversight,
    DisputeDetail,
    VerificationQueue,
)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "sender",
        "receiver",
        "subject",
        "is_read",
        "created_at",
    )

    search_fields = (
        "sender__username",
        "receiver__username",
        "subject",
        "content",
    )

    list_filter = (
        "is_read",
        "created_at",
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "reviewer",
        "rating",
        "comment",
        "created_at",
    )

    list_filter = (
        "rating",
        "created_at",
    )

    search_fields = (
        "reviewer__username",
        "comment",
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    search_fields = (
        "user__username",
        "title",
        "message",
    )

    actions = ("mark_read",)

    @admin.action(description="Mark selected notifications as read")
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)


@admin.register(BookingOversight)
class BookingOversightAdmin(admin.ModelAdmin):
    list_display = (
        "event_name",
        "client",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "event_name",
        "client__username",
    )


@admin.register(DisputeDetail)
class DisputeDetailAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "raised_by",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "raised_by__username",
    )


@admin.register(VerificationQueue)
class VerificationQueueAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "document_type",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "document_type",
        "created_at",
    )

    search_fields = (
        "user__username",
        "document_type",
    )