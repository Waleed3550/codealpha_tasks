import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from cart.models import Cart
from products.models import Brand, Category, Product

User = get_user_model()


class CartAuthFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_one = User.objects.create_user(
            username="user_one",
            email="one@example.com",
            password="password123",
        )
        self.user_two = User.objects.create_user(
            username="user_two",
            email="two@example.com",
            password="password123",
        )
        self.category = Category.objects.create(name="Laptops", slug="laptops", is_active=True)
        self.brand = Brand.objects.create(name="TechBrand", slug="techbrand")
        self.product = Product.objects.create(
            category=self.category,
            brand=self.brand,
            name="CA-Tech Pro",
            slug="technest-pro",
            short_description="Powerful laptop",
            description="Powerful laptop for testing cart auth.",
            price=Decimal("100.00"),
            sku="SKU-CART-AUTH",
            stock=5,
            is_active=True,
        )

    def test_guest_add_to_cart_redirects_to_login_and_replays_after_login(self):
        response = self.client.post(
            reverse("cart:add", args=[self.product.id]),
            {"quantity": 1},
            HTTP_REFERER=self.product.get_absolute_url(),
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

        login_response = self.client.post(
            reverse("accounts:login"),
            {"username": self.user_one.username, "password": "password123"},
        )
        self.assertEqual(login_response.status_code, 302)
        self.assertTrue(Cart.objects.filter(user=self.user_one).exists())
        cart = Cart.objects.get(user=self.user_one)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().product, self.product)

    def test_guest_ajax_add_to_cart_returns_login_payload(self):
        response = self.client.post(
            reverse("cart:add", args=[self.product.id]),
            {"quantity": 1},
            HTTP_REFERER=self.product.get_absolute_url(),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        payload = json.loads(response.content.decode("utf-8"))
        self.assertFalse(payload["ok"])
        self.assertTrue(payload["login_required"])
        self.assertIn(reverse("accounts:login"), payload["login_url"])

    def test_each_user_has_independent_cart(self):
        self.client.force_login(self.user_one)
        self.client.post(reverse("cart:add", args=[self.product.id]), {"quantity": 1})
        self.client.logout()

        self.client.force_login(self.user_two)
        self.client.post(reverse("cart:add", args=[self.product.id]), {"quantity": 1})

        self.assertEqual(Cart.objects.count(), 2)
        self.assertEqual(Cart.objects.get(user=self.user_one).items.count(), 1)
        self.assertEqual(Cart.objects.get(user=self.user_two).items.count(), 1)
