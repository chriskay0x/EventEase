from django.contrib import admin

from .models import Message, Notification, Review


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "sender",
        "recipient",
        "body",
        "read_at",
        "created_at",
    )
    search_fields = (
        "sender__username",
        "recipient__username",
        "body",
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "vendor",
        "rating",
        "comment",
        "created_at",
    )
    list_filter = ("rating",)
    search_fields = (
        "author__username",
        "vendor__username",
        "comment",
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "recipient",
        "kind",
        "message",
        "is_read",
        "created_at",
    )
    list_filter = (
        "kind",
        "read_at",
    )
    search_fields = (
        "recipient__username",
        "message",
    )

    actions = ("mark_read",)

    @admin.action(description="Mark selected notifications as read")
    def mark_read(self, request, queryset):
        for notification in queryset:
            notification.mark_read()