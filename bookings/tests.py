from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.test import TestCase

from listings.models import Availability, VenueListing
from bookings import services
from bookings.models import Booking, Payment

User = get_user_model()


class BookingServiceTests(TestCase):
    """Business rules — the heart of Team 3."""

    def setUp(self):
        self.vendor = User.objects.create_user(
            username="vendor1", password="pass1234", role="vendor")
        self.client_user = User.objects.create_user(
            username="client1", password="pass1234", role="client")
        self.listing = VenueListing.objects.create(
            vendor=self.vendor, name="Grand Hall",
            min_guests=50, max_guests=300, base_price=1500)

    def test_booking_created_pending_with_payment(self):
        booking = services.create_booking(
            client=self.client_user, listing=self.listing,
            event_date=date(2026, 10, 24), guest_count=100)
        self.assertEqual(booking.status, Booking.Status.PENDING)
        self.assertTrue(booking.reference_code.startswith("EE-"))
        self.assertEqual(booking.total_price, 1500)
        self.assertEqual(booking.payment.status, Payment.Status.PENDING)

    def test_capacity_rejected(self):  # FR-03
        with self.assertRaises(services.BookingError):
            services.create_booking(
                client=self.client_user, listing=self.listing,
                event_date=date(2026, 10, 24), guest_count=9999)

    def test_double_booking_prevented(self):  # Concurrency NFR
        services.create_booking(
            client=self.client_user, listing=self.listing,
            event_date=date(2026, 10, 24), guest_count=100)
        with self.assertRaises(services.BookingError):
            services.create_booking(
                client=self.client_user, listing=self.listing,
                event_date=date(2026, 10, 24), guest_count=80)

    def test_vendor_accept_and_decline(self):  # FR-15
        b1 = services.create_booking(
            client=self.client_user, listing=self.listing,
            event_date=date(2026, 10, 24), guest_count=100)
        services.vendor_respond(b1, self.vendor, accept=True)
        self.assertEqual(b1.status, Booking.Status.CONFIRMED)

        b2 = services.create_booking(
            client=self.client_user, listing=self.listing,
            event_date=date(2026, 11, 1), guest_count=100)
        services.vendor_respond(b2, self.vendor, accept=False)
        self.assertEqual(b2.status, Booking.Status.DECLINED)
        availability = Availability.objects.get(
            vendor=self.vendor, date=date(2026, 11, 1))
        self.assertEqual(availability.status, "available")  # date freed again

    def test_complete_releases_escrow(self):  # FR-05
        booking = services.create_booking(
            client=self.client_user, listing=self.listing,
            event_date=date(2026, 10, 24), guest_count=100)
        services.complete_booking(booking)
        booking.payment.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.COMPLETED)
        self.assertEqual(booking.payment.status, Payment.Status.RELEASED)


class BookingAPITests(APITestCase):
    """The /api/v1/ endpoints the frontend will call."""

    def setUp(self):
        self.vendor = User.objects.create_user(
            username="vendor1", password="pass1234", role="vendor")
        self.client_user = User.objects.create_user(
            username="client1", password="pass1234", role="client")
        self.other_client = User.objects.create_user(
            username="client2", password="pass1234", role="client")
        self.listing = VenueListing.objects.create(
            vendor=self.vendor, name="Grand Hall",
            min_guests=50, max_guests=300, base_price=1500)

    def test_login_required(self):
        response = self.client.get("/api/v1/bookings/")
        self.assertIn(response.status_code, (401, 403))

    def test_client_can_create_booking(self):
        self.client.force_authenticate(self.client_user)
        response = self.client.post("/api/v1/bookings/", {
            "listing": self.listing.id,
            "event_date": "2026-10-24",
            "guest_count": 100,
            "event_type": "Corporate Retreat",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "pending")
        self.assertTrue(response.data["reference_code"].startswith("EE-"))

    def test_capacity_rejected_via_api(self):  # FR-03
        self.client.force_authenticate(self.client_user)
        response = self.client.post("/api/v1/bookings/", {
            "listing": self.listing.id,
            "event_date": "2026-10-24",
            "guest_count": 9999,
        }, format="json")
        self.assertEqual(response.status_code, 400)

    def test_client_sees_only_own_bookings(self):
        services.create_booking(
            client=self.client_user, listing=self.listing,
            event_date=date(2026, 10, 24), guest_count=100)
        self.client.force_authenticate(self.other_client)
        response = self.client.get("/api/v1/bookings/")
        self.assertEqual(len(response.data), 0)

    def test_vendor_sees_only_own_requests(self):  # Booking Requests screen
        services.create_booking(
            client=self.client_user, listing=self.listing,
            event_date=date(2026, 10, 24), guest_count=100)
        self.client.force_authenticate(self.vendor)
        response = self.client.get("/api/v1/bookings/")
        self.assertEqual(len(response.data), 1)

    def test_vendor_accept_endpoint(self):  # FR-15
        booking = services.create_booking(
            client=self.client_user, listing=self.listing,
            event_date=date(2026, 10, 24), guest_count=100)
        self.client.force_authenticate(self.vendor)
        response = self.client.post(f"/api/v1/bookings/{booking.id}/accept/")
        self.assertEqual(response.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CONFIRMED)
        