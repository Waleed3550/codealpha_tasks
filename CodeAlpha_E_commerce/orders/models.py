from decimal import Decimal
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from products.models import Product, ProductVariant


class Order(models.Model):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PAYMENT_PENDING = "pending"
    PAYMENT_APPROVED = "approved"
    PAYMENT_REJECTED = "rejected"
    PAYMENT_REFUNDED = "refunded"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (CONFIRMED, "Confirmed"),
        (PROCESSING, "Processing"),
        (SHIPPED, "Shipped"),
        (DELIVERED, "Delivered"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, "Pending"),
        (PAYMENT_APPROVED, "Approved"),
        (PAYMENT_REJECTED, "Rejected"),
        (PAYMENT_REFUNDED, "Refunded"),
    ]
    PAYMENT_CHOICES = [("cod", "Cash on Delivery"), ("card", "Online Payment")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    order_number = models.CharField(max_length=24, unique=True)
    email = models.EmailField()
    full_name = models.CharField(max_length=160)
    phone = models.CharField(max_length=24)
    billing_address = models.TextField()
    shipping_address = models.TextField()
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=80, default="United States")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="cod")
    payment_gateway = models.CharField(max_length=32, blank=True, default="")
    transaction_id = models.CharField(max_length=64, blank=True, default="", db_index=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    shipping_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    tax_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    converted_currency = models.CharField(max_length=10, blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    visitor_country = models.CharField(max_length=80, blank=True, null=True)
    visitor_language = models.CharField(max_length=20, blank=True, null=True)
    visitor_timezone = models.CharField(max_length=80, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.order_number

    def get_absolute_url(self):
        return reverse("orders:detail", kwargs={"order_number": self.order_number})

    @property
    def estimated_delivery_date(self):
        if self.status in {self.DELIVERED, self.COMPLETED, self.CANCELLED}:
            return None
        return timezone.localdate(self.created_at) + timedelta(days=5)

    @property
    def timeline(self):
        return [
            ("pending", "Order Placed", self.created_at),
            ("confirmed", "Payment Received", self.updated_at if self.payment_status == self.PAYMENT_APPROVED else None),
            ("confirmed", "Confirmed", self.updated_at if self.status in {self.CONFIRMED, self.PROCESSING, self.SHIPPED, self.DELIVERED, self.COMPLETED} else None),
            ("processing", "Processing", self.updated_at if self.status in {self.PROCESSING, self.SHIPPED, self.DELIVERED, self.COMPLETED} else None),
            ("shipped", "Shipped", self.updated_at if self.status in {self.SHIPPED, self.DELIVERED, self.COMPLETED} else None),
            ("delivered", "Delivered", self.updated_at if self.status in {self.DELIVERED, self.COMPLETED} else None),
            ("completed", "Completed", self.updated_at if self.status == self.COMPLETED else None),
            ("cancelled", "Cancelled", self.updated_at if self.status == self.CANCELLED else None),
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=180)
    sku = models.CharField(max_length=64)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=140)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

class OrderEvent(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"{self.order.order_number} - {self.title}"

class PaymentTransaction(Order):
    class Meta:
        proxy = True
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Management"
