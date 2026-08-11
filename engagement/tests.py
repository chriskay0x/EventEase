from django.contrib import admin
from django.test import SimpleTestCase
from django.urls import reverse

from engagement.admin import MessageAdmin, ReviewAdmin
from engagement.models import Message, Review


class LandingPageTests(SimpleTestCase):
    def test_landing_page_renders_successfully(self):
        response = self.client.get(reverse('landing'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EventEase')


class AdminConfigurationTests(SimpleTestCase):
    def test_review_admin_list_display_references_existing_fields(self):
        admin_instance = ReviewAdmin(model=Review, admin_site=admin.site)

        for field_name in admin_instance.list_display:
            self.assertTrue(
                hasattr(Review, field_name)
                or hasattr(admin_instance, field_name)
                or callable(getattr(admin_instance, field_name, None)),
            )

    def test_message_admin_list_display_references_existing_fields(self):
        admin_instance = MessageAdmin(model=Message, admin_site=admin.site)

        for field_name in admin_instance.list_display:
            self.assertTrue(
                hasattr(Message, field_name)
                or hasattr(admin_instance, field_name)
                or callable(getattr(admin_instance, field_name, None)),
            )
