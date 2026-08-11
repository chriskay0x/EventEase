from django.contrib import admin
from .models import Review, Message


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('comment',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp')
