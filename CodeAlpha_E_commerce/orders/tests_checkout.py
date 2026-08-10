from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from cart.models import Cart, CartItem
from orders.models import Order
from products.models import Brand, Category, Product

User = get_user_model()


class CheckoutFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="checkout_user",
            email="checkout@example.com",
            password="password123",
            first_name="Checkout",
            last_name="User",
        )
        self.category = Category.objects.create(name="Laptops", slug="laptops", is_active=True)
        self.brand = Brand.objects.create(name="TechBrand", slug="techbrand")
        self.product = Product.objects.create(
            category=self.category,
            brand=self.brand,
            name="CA-Tech Pro",
            slug="technest-pro",
            short_description="Powerful laptop",
            description="Powerful laptop for testing checkout.",
            price=Decimal("100.00"),
            sku="SKU-TECHNEST-PRO",
            stock=5,
            is_active=True,
        )
        self.client.force_login(self.user)

    def _prepare_cart(self, quantity=1):
        session = self.client.session
        session.save()
        cart = Cart.objects.create(user=self.user, session_key=session.session_key)
        CartItem.objects.create(cart=cart, product=self.product, quantity=quantity)
        return cart

    def test_cod_checkout_creates_order_without_duplicate_payment_method(self):
        self._prepare_cart()
        response = self.client.post(
            reverse("orders:checkout"),
            {
                "full_name": "Checkout User",
                "email": "checkout@example.com",
                "phone": "+1-555-000-0000",
                "billing_address": "123 Main St",
                "shipping_address": "123 Main St",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "United States",
                "notes": "",
                "payment_method": "cod",
            },
        )
        self.assertRedirects(response, reverse("orders:confirmation", args=[Order.objects.latest("created_at").order_number]))

        order = Order.objects.latest("created_at")
        self.assertEqual(order.payment_method, "cod")
        self.assertEqual(order.payment_status, Order.PAYMENT_PENDING)
        self.assertEqual(order.status, Order.PENDING)
        self.assertEqual(order.payment_gateway, "")
        self.assertEqual(order.transaction_id, "")
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 4)

    def test_card_checkout_redirects_to_payment_page(self):
        self._prepare_cart()
        response = self.client.post(
            reverse("orders:checkout"),
            {
                "full_name": "Checkout User",
                "email": "checkout@example.com",
                "phone": "+1-555-000-0000",
                "billing_address": "123 Main St",
                "shipping_address": "123 Main St",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "United States",
                "notes": "",
                "payment_method": "card",
            },
        )
        order = Order.objects.latest("created_at")
        self.assertRedirects(response, reverse("orders:payment", args=[order.order_number]))
        self.assertEqual(order.payment_method, "card")
        self.assertEqual(order.payment_status, Order.PAYMENT_PENDING)
        self.assertEqual(order.status, Order.PENDING)

    def test_checkout_rejects_out_of_stock_items(self):
        self.product.stock = 0
        self.product.save(update_fields=["stock"])
        self._prepare_cart()
        response = self.client.post(
            reverse("orders:checkout"),
            {
                "full_name": "Checkout User",
                "email": "checkout@example.com",
                "phone": "+1-555-000-0000",
                "billing_address": "123 Main St",
                "shipping_address": "123 Main St",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "United States",
                "notes": "",
                "payment_method": "cod",
            },
        )
        self.assertRedirects(response, reverse("cart:detail"))
        self.assertFalse(Order.objects.exists())

    def test_guest_checkout_redirects_to_login(self):
        self.client.logout()
        response = self.client.post(
            reverse("orders:checkout"),
            {
                "full_name": "Guest Buyer",
                "email": "guest@example.com",
                "phone": "+1-555-000-1111",
                "billing_address": "456 Guest Ave",
                "shipping_address": "456 Guest Ave",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "United States",
                "notes": "",
                "payment_method": "cod",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)
        self.assertIn("next=", response.url)
        self.assertFalse(Order.objects.exists())
