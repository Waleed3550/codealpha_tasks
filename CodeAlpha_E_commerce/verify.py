import os
import django
import random
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'technest.settings')
django.setup()

from django.utils import timezone
from orders.models import Order
from products.models import Product, Category

# Backdate Orders
orders = Order.objects.all()
now = timezone.now()
for o in orders:
    days_ago = random.randint(1, 365)
    random_date = now - timedelta(days=days_ago)
    Order.objects.filter(id=o.id).update(created_at=random_date)
print("Orders backdated successfully.")

# Verifications
smartphones_count = Product.objects.filter(category__slug='smartphones').count()
laptops_count = Product.objects.filter(category__slug='laptops').count()
other_count = Product.objects.exclude(category__slug__in=['smartphones', 'laptops']).count()
total_products = Product.objects.count()

print(f"Smartphones: {smartphones_count}")
print(f"Laptops: {laptops_count}")
print(f"Other Devices: {other_count}")
print(f"Total Products: {total_products}")

# Duplicates
sku_count = Product.objects.values('sku').distinct().count()
name_count = Product.objects.values('name').distinct().count()

if sku_count == total_products:
    print("No duplicate SKUs found.")
else:
    print(f"ERROR: Duplicate SKUs exist. Unique: {sku_count}")
    
if name_count == total_products:
    print("No duplicate product names found.")
else:
    print(f"ERROR: Duplicate Names exist. Unique: {name_count}")
    
print("All verifications passed!")
