# from django.urls import path
# from . import views

# urlpatterns = [
#     # Map http://127.0.0.1:8000/engagement/ directly to your dashboard view
#     path('', views.dashboard, name='dashboard'), 
    
#     path('dashboard/', views.dashboard, name='dashboard'),
#     path('messages/', views.message_list, name='message_list'),
#     path('messages/send/', views.message_create, name='message_create'),
#     path('reviews/', views.review_list, name='review_list'),
#     path('reviews/create/', views.review_create, name='review_create'),
#     path('notifications/', views.notification_list, name='notification_list'),
#     path('notifications/<int:pk>/read/', views.notification_mark_read, name='notification_mark_read'),
#     path('notifications/read-all/', views.notification_mark_all_read, name='notification_mark_all_read'),
# ] 


from django.urls import path
from . import views

# 1. ADD THIS LINE: Required for the 'engagement:' namespace to work
app_name = "engagement" 

urlpatterns = [
    # Map http://127.0.0.1:8000/engagement/ directly to your dashboard view
    path('', views.dashboard, name='dashboard'), 
    
    # 2. REMOVED duplicate: You already have '' mapping to dashboard above.
    # Having two paths with name='dashboard' causes reverse() conflicts.
    
    path('messages/', views.message_list, name='message_list'),
    path('messages/send/', views.message_create, name='message_create'),
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/create/', views.review_create, name='review_create'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/read-all/', views.notification_mark_all_read, name='notification_mark_all_read'),
]