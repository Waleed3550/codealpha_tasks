import os
import sys
import django

sys.path.append('D:\\E-commerance')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'technest.settings')
django.setup()

from products.models import Product
import random

products = list(Product.objects.filter(is_active=True))
if products:
    featured_products = random.sample(products, min(12, len(products)))
    for p in featured_products:
        p.is_featured = True
        p.save()
    print(f"Successfully marked {len(featured_products)} products as featured.")
else:
    print("No active products found.")
