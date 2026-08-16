from django.urls import path
from . import views

urlpatterns = [
    path(
        'reviews/submit/<int:booking_id>/',
        views.submit_review,
        name='submit_review'
    ),

    path(
        'admin/overview/',
        views.admin_overview,
        name='admin_overview'
    ),

    path(
        'admin/platform-overview/',
        views.platform_overview,
        name='platform_overview'
    ),

    path(
        'admin/verification-queue/',
        views.verification_queue,
        name='verification_queue'
    ),

    path(
        'admin/verification-queue/<int:vendor_id>/approve/',
        views.approve_vendor,
        name='approve_vendor'
    ),

    path(
        'admin/verification-queue/<int:vendor_id>/reject/',
        views.reject_vendor,
        name='reject_vendor'
    ),

    path(
        'admin/booking-oversight/',
        views.booking_oversight,
        name='booking_oversight'
    ),

    path(
        'admin/disputes/<int:booking_id>/',
        views.dispute_detail,
        name='dispute_detail'
    ),

    path(
        'admin/disputes/<int:booking_id>/resolve/',
        views.resolve_dispute,
        name='resolve_dispute'
    ),

    path(
        'admin/disputes/<int:booking_id>/refund/',
        views.issue_refund,
        name='issue_refund'
    ),

    path(
        'admin/disputes/<int:booking_id>/note/',
        views.add_internal_note,
        name='add_internal_note'
    ),

    path('admin/client-reviews/', views.client_reviews, name='client_reviews'),

    path('admin/booking-oversight/<int:booking_id>/flag/', views.flag_booking, name='flag_booking'),

    path('coming-soon/<str:feature_name>/', views.coming_soon, name='coming_soon'),
    
    path('admin/send-bulk-reminder/', views.send_bulk_reminder, name='send_bulk_reminder'),
    
    path('admin/export-report/', views.export_report, name='export_report'),
]