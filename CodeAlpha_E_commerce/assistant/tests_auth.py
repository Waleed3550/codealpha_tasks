import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from assistant.models import AISettings
from products.models import Brand, Category, Product

User = get_user_model()


class AssistantAuthFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        AISettings.load()
        self.category = Category.objects.create(name="Laptops", slug="laptops", is_active=True)
        self.brand = Brand.objects.create(name="TechBrand", slug="techbrand")
        self.product = Product.objects.create(
            category=self.category,
            brand=self.brand,
            name="CA-Tech Pro",
            slug="technest-pro",
            short_description="Powerful laptop",
            description="Powerful laptop for testing assistant auth.",
            price=Decimal("100.00"),
            sku="SKU-AI-AUTH",
            stock=5,
            is_active=True,
        )

    def test_guest_assistant_cart_request_prompts_login_and_saves_action(self):
        response = self.client.post(
            reverse("assistant:chat_api"),
            data=json.dumps({"message": f"Add {self.product.name} to my cart"}),
            content_type="application/json",
            HTTP_REFERER=self.product.get_absolute_url(),
        )

        payload = json.loads(response.content.decode("utf-8"))
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["login_required"])
        self.assertIn("Please log in", payload["assistant"]["content"])
        self.assertEqual(payload["assistant"]["metadata"]["pending_action"], "add_to_cart")

        session = self.client.session
        pending = session.get("technest_pending_shopping_action")
        self.assertIsNotNone(pending)
        self.assertEqual(pending["type"], "add_to_cart")
        self.assertEqual(pending["product_id"], self.product.id)

    def test_guest_wishlist_page_redirects_to_login(self):
        response = self.client.get(reverse("assistant:wishlist"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)
