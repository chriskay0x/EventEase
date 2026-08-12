from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('get-started/', views.get_started_view, name='get_started'),
    path('signup/', views.register_client_view, name='signup'),
    path('vendor-signup/', views.register_vendor_view, name='vendor_signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]