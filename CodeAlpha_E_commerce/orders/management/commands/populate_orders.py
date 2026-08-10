import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from products.models import Product

User = get_user_model()

class Command(BaseCommand):
    help = "Generate realistic customers and orders"

    def handle(self, *args, **kwargs):
        Order.objects.all().delete()
        
        # 100 Customers
        first_names = ['John', 'Emma', 'Michael', 'Sophia', 'William', 'Olivia', 'James', 'Ava', 'Robert', 'Isabella', 'Ali', 'Fatima', 'Omar', 'Aisha']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Khan', 'Ahmed', 'Syed']
        
        customers = []
        for i in range(1, 101):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            username = f"{fn.lower()}{ln.lower()}{random.randint(100, 9999)}_{i}"
            email = f"{username}@example.com"
            user, created = User.objects.get_or_create(username=username, defaults={
                'first_name': fn, 'last_name': ln, 'email': email
            })
            if created:
                user.set_password('password123')
                user.save()
            customers.append(user)
            
        # 200 Orders
        statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
        products = list(Product.objects.all())
        
        if not products:
            self.stdout.write(self.style.ERROR("No products found! Run populate_products first."))
            return
            
        count = 0
        for i in range(1, 201):
            user = random.choice(customers)
            status = random.choice(statuses)
            # Match user requested 'Approved' to 'payment_status=approved' or 'status=confirmed'
            payment_status = 'approved' if status in ['processing', 'shipped', 'delivered', 'completed'] else 'pending'
            
            order = Order.objects.create(
                user=user,
                order_number=f"ORD-{random.randint(10000, 99999)}-{i}",
                email=user.email,
                full_name=f"{user.first_name} {user.last_name}",
                phone=f"+1-555-{random.randint(100,999)}-{random.randint(1000,9999)}",
                billing_address=f"{random.randint(100,9999)} Main St\nApt {random.randint(1, 100)}",
                shipping_address=f"{random.randint(100,9999)} Main St\nApt {random.randint(1, 100)}",
                city="New York",
                state="NY",
                postal_code="10001",
                payment_method="cod",
                payment_status=payment_status,
                status=status
            )
            
            subtotal = Decimal('0.00')
            # 1 to 4 items per order
            num_items = random.randint(1, 4)
            for _ in range(num_items):
                prod = random.choice(products)
                qty = random.randint(1, 3)
                unit_price = prod.price
                line_total = unit_price * qty
                subtotal += line_total
                
                OrderItem.objects.create(
                    order=order, product=prod, product_name=prod.name,
                    sku=prod.sku, quantity=qty, unit_price=unit_price, line_total=line_total
                )
                
            shipping = Decimal('10.00') if subtotal < Decimal('500.00') else Decimal('0.00')
            tax = subtotal * Decimal('0.08')
            order.subtotal = subtotal
            order.shipping_total = shipping
            order.tax_total = tax
            order.grand_total = subtotal + shipping + tax
            order.save()
            count += 1
            
        self.stdout.write(self.style.SUCCESS(f"Successfully generated 100 Customers and {count} Orders."))
