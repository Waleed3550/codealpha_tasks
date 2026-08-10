from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from orders.models import Order

User = get_user_model()


class PaymentFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="password123",
            first_name="Test",
            last_name="Buyer",
        )
        self.base_kwargs = {
            "user": self.user,
            "email": self.user.email,
            "full_name": "Test Buyer",
            "phone": "+1-555-123-4567",
            "billing_address": "123 Main St",
            "shipping_address": "123 Main St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "subtotal": Decimal("100.00"),
            "shipping_total": Decimal("19.00"),
            "tax_total": Decimal("8.25"),
            "grand_total": Decimal("127.25"),
        }
        self.order_pk = Order.objects.create(
            order_number="TN-PK123",
            payment_method="card",
            **self.base_kwargs,
            country="Pakistan",
        )
        self.order_in = Order.objects.create(
            order_number="TN-IN123",
            payment_method="card",
            **self.base_kwargs,
            country="India",
        )
        self.order_us = Order.objects.create(
            order_number="TN-US123",
            payment_method="card",
            **self.base_kwargs,
            country="United States",
        )
        self.client.force_login(self.user)

    def test_payment_methods_display_correctly(self):
        response_pk = self.client.get(reverse("orders:payment", args=[self.order_pk.order_number]))
        self.assertContains(response_pk, "JazzCash")
        self.assertContains(response_pk, "EasyPaisa")
        self.assertContains(response_pk, "Bank Transfer")
        self.assertNotContains(response_pk, "UPI")
        self.assertNotContains(response_pk, "Stripe")

        response_in = self.client.get(reverse("orders:payment", args=[self.order_in.order_number]))
        self.assertContains(response_in, "UPI")
        self.assertContains(response_in, "PhonePe")
        self.assertContains(response_in, "Paytm")
        self.assertNotContains(response_in, "JazzCash")
        self.assertNotContains(response_in, "Stripe")

        response_us = self.client.get(reverse("orders:payment", args=[self.order_us.order_number]))
        self.assertContains(response_us, 'value="stripe"')
        self.assertContains(response_us, 'value="paypal"')
        self.assertNotContains(response_us, "JazzCash")
        self.assertNotContains(response_us, "UPI")

    def test_online_payment_success_persists_transaction_metadata(self):
        response = self.client.post(
            reverse("orders:payment", args=[self.order_us.order_number]),
            {"action": "pay", "gateway": "stripe"},
        )
        self.assertRedirects(response, reverse("orders:confirmation", args=[self.order_us.order_number]))

        self.order_us.refresh_from_db()
        self.assertEqual(self.order_us.payment_status, Order.PAYMENT_APPROVED)
        self.assertEqual(self.order_us.status, Order.CONFIRMED)
        self.assertEqual(self.order_us.payment_gateway, "stripe")
        self.assertTrue(self.order_us.transaction_id.startswith("TXN-"))

    def test_online_payment_fail_cancels_order(self):
        response = self.client.post(
            reverse("orders:payment", args=[self.order_in.order_number]),
            {"action": "fail", "gateway": "upi"},
        )
        self.assertRedirects(response, reverse("orders:payment", args=[self.order_in.order_number]))

        self.order_in.refresh_from_db()
        self.assertEqual(self.order_in.payment_status, Order.PAYMENT_REJECTED)
        self.assertEqual(self.order_in.status, Order.CANCELLED)

    def test_guest_payment_redirects_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("orders:payment", args=[self.order_us.order_number]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)
