from decimal import Decimal

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ("products", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order_number", models.CharField(max_length=24, unique=True)),
                ("email", models.EmailField(max_length=254)),
                ("full_name", models.CharField(max_length=160)),
                ("phone", models.CharField(max_length=24)),
                ("billing_address", models.TextField()),
                ("shipping_address", models.TextField()),
                ("city", models.CharField(max_length=80)),
                ("state", models.CharField(max_length=80)),
                ("postal_code", models.CharField(max_length=20)),
                ("country", models.CharField(default="United States", max_length=80)),
                ("payment_method", models.CharField(choices=[("cod", "Cash on Delivery")], default="cod", max_length=20)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("processing", "Processing"), ("shipped", "Shipped"), ("delivered", "Delivered"), ("cancelled", "Cancelled")], default="pending", max_length=20)),
                ("subtotal", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("shipping_total", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("tax_total", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("grand_total", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_name", models.CharField(max_length=180)),
                ("sku", models.CharField(max_length=64)),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("line_total", models.DecimalField(decimal_places=2, max_digits=10)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="orders.order")),
                ("product", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="products.product")),
                ("variant", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="products.productvariant")),
            ],
        ),
    ]
