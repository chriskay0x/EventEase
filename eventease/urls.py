"""
URL configuration for eventease project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'accounts/',
        include('accounts.urls', namespace='accounts')
    ),

    path(
        'engagement/',
        include('engagement.urls')
    ),

    path(
        '',
        RedirectView.as_view(
            url='/engagement/',
            permanent=False
        )
    ),
]