from django.conf import settings
from django.db import models

from products.models import Product, ProductVariant


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="carts")
    session_key = models.CharField(max_length=80, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["user", "session_key"], name="cart_cart_user_id_efbe4e_idx")]

    def __str__(self):
        return f"Cart #{self.pk}"

    @property
    def subtotal(self):
        return sum(item.line_total for item in self.items.select_related("product", "variant"))

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product", "variant")

    @property
    def unit_price(self):
        delta = self.variant.price_delta if self.variant else 0
        return self.product.price + delta

    @property
    def line_total(self):
        return self.unit_price * self.quantity
