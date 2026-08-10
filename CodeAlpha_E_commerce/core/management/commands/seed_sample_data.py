from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from products.models import Brand, Category, Product, ProductImage, ProductReview, ProductVariant


class Command(BaseCommand):
    help = "Seed CA-Tech Electronics with production-like sample catalog data."

    def handle(self, *args, **options):
        categories = [
            ("Laptops", "High-performance notebooks for work, gaming, and creation.", "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80"),
            ("Smartphones", "Flagship phones, foldables, and everyday mobile devices.", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=900&q=80"),
            ("Gaming", "Consoles, graphics power, headsets, and competitive gear.", "https://images.unsplash.com/photo-1593305841991-05c297ba4575?auto=format&fit=crop&w=900&q=80"),
            ("Displays", "Color-accurate monitors, ultrawides, and OLED panels.", "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=900&q=80"),
            ("Audio", "Premium headphones, earbuds, speakers, and microphones.", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80"),
            ("Accessories", "Keyboards, docks, chargers, storage, and protection.", "https://images.unsplash.com/photo-1527814050087-3793815479db?auto=format&fit=crop&w=900&q=80"),
        ]
        category_map = {}
        for name, description, image_url in categories:
            category, _ = Category.objects.update_or_create(slug=slugify(name), defaults={"name": name, "description": description, "image_url": image_url, "is_active": True})
            category_map[name] = category

        brand_names = ["Apple", "Samsung", "ASUS", "Dell", "Sony", "Logitech", "Lenovo", "Microsoft"]
        brand_map = {}
        for name in brand_names:
            brand, _ = Brand.objects.update_or_create(slug=slugify(name), defaults={"name": name, "description": f"{name} premium electronics and accessories.", "is_featured": True})
            brand_map[name] = brand

        products = [
            ("MacBook Pro 14 M3 Pro", "Apple", "Laptops", "Creator-class laptop with Liquid Retina XDR display and all-day battery.", "Built for demanding creative work, the MacBook Pro 14 combines high sustained performance, a premium display, studio-quality audio, and a refined aluminum design.", Decimal("1999.00"), Decimal("2199.00"), "TN-APP-MBP14", 14, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1000&q=80", {"CPU": "Apple M3 Pro", "Memory": "18GB", "Storage": "512GB SSD", "Display": "14.2-inch XDR"}),
            ("Galaxy S24 Ultra", "Samsung", "Smartphones", "AI-ready flagship phone with titanium frame and pro camera system.", "A premium Android flagship with a vivid AMOLED display, integrated stylus support, advanced zoom camera, and long software support.", Decimal("1199.00"), Decimal("1299.00"), "TN-SAM-S24U", 22, "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?auto=format&fit=crop&w=1000&q=80", {"Display": "6.8-inch AMOLED", "Storage": "256GB", "Camera": "200MP", "Battery": "5000mAh"}),
            ("ASUS ROG Zephyrus G14", "ASUS", "Gaming", "Compact gaming laptop with high-refresh OLED display.", "Portable gaming power for competitive play, streaming, and content creation with efficient cooling and premium materials.", Decimal("1599.00"), Decimal("1799.00"), "TN-ASU-G14", 9, "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=1000&q=80", {"GPU": "RTX 4070", "Display": "14-inch OLED", "Memory": "32GB", "Storage": "1TB SSD"}),
            ("Dell XPS 15", "Dell", "Laptops", "Premium Windows laptop with stunning InfinityEdge display.", "A refined productivity and creator laptop with powerful internals, precise keyboard feel, and an elegant machined chassis.", Decimal("1499.00"), Decimal("1699.00"), "TN-DEL-XPS15", 11, "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=1000&q=80", {"CPU": "Intel Core Ultra 7", "Memory": "16GB", "Storage": "1TB SSD", "Display": "15.6-inch OLED"}),
            ("Sony WH-1000XM5", "Sony", "Audio", "Industry-leading noise cancelling wireless headphones.", "Designed for travel, focus, and immersive listening with adaptive noise cancelling and lightweight comfort.", Decimal("349.00"), Decimal("399.00"), "TN-SON-XM5", 30, "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=1000&q=80", {"Battery": "30 hours", "Connectivity": "Bluetooth", "Charging": "USB-C", "ANC": "Adaptive"}),
            ("Logitech MX Mechanical", "Logitech", "Accessories", "Low-profile wireless mechanical keyboard for focused workflows.", "A quiet tactile keyboard with multi-device pairing, smart backlighting, and excellent battery life.", Decimal("169.00"), None, "TN-LOG-MXM", 42, "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=1000&q=80", {"Switches": "Tactile quiet", "Layout": "Full size", "Battery": "Up to 10 months", "Connection": "Bluetooth/USB"}),
            ("Samsung Odyssey OLED G8", "Samsung", "Displays", "Ultrawide OLED gaming monitor with vivid contrast.", "A premium display for immersive gaming and high-end desk setups with rich contrast and fast response.", Decimal("999.00"), Decimal("1199.00"), "TN-SAM-G8", 7, "https://images.unsplash.com/photo-1616588589676-62b3bd4ff6d2?auto=format&fit=crop&w=1000&q=80", {"Size": "34-inch", "Panel": "OLED", "Refresh": "175Hz", "Resolution": "3440x1440"}),
            ("Microsoft Surface Pro", "Microsoft", "Laptops", "Flexible tablet-laptop hybrid with premium pen support.", "A highly portable 2-in-1 for mobile productivity, note-taking, drawing, and everyday computing.", Decimal("1099.00"), None, "TN-MIC-SP", 18, "https://images.unsplash.com/photo-1585790050230-5dd28404ccb9?auto=format&fit=crop&w=1000&q=80", {"Display": "13-inch PixelSense", "Memory": "16GB", "Storage": "512GB", "Mode": "Tablet/Laptop"}),
            ("Lenovo Legion Go", "Lenovo", "Gaming", "Handheld Windows gaming system with detachable controllers.", "Portable PC gaming with a large high-refresh screen, ergonomic controls, and access to major game libraries.", Decimal("699.00"), Decimal("749.00"), "TN-LEN-GO", 15, "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?auto=format&fit=crop&w=1000&q=80", {"Display": "8.8-inch QHD", "Storage": "1TB", "Controls": "Detachable", "OS": "Windows"}),
        ]

        for index, data in enumerate(products):
            name, brand, category, short, description, price, compare, sku, stock, image, specs = data
            product, _ = Product.objects.update_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "slug": slugify(name),
                    "brand": brand_map[brand],
                    "category": category_map[category],
                    "short_description": short,
                    "description": description,
                    "price": price,
                    "compare_at_price": compare,
                    "stock": stock,
                    "is_featured": index < 6,
                    "is_active": True,
                    "specs": specs,
                    "rating": Decimal("4.80") if index < 4 else Decimal("4.60"),
                },
            )
            ProductImage.objects.update_or_create(product=product, sort_order=0, defaults={"image_url": image, "alt_text": name, "is_primary": True})
            ProductVariant.objects.update_or_create(product=product, name="Color", value="Graphite", defaults={"stock": max(1, stock // 2), "price_delta": Decimal("0.00")})
            ProductVariant.objects.update_or_create(product=product, name="Storage", value="1TB Upgrade", defaults={"stock": max(1, stock // 3), "price_delta": Decimal("180.00")})
            ProductReview.objects.update_or_create(
                product=product,
                customer_name="Verified CA-Tech Buyer",
                defaults={"rating": 5 if index < 5 else 4, "comment": f"{name} arrived quickly and matched the listed specifications.", "is_approved": True},
            )

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@technest.local", "AdminPass123!")
            self.stdout.write(self.style.WARNING("Created admin user: admin / AdminPass123! Change this password before deployment."))

        self.stdout.write(self.style.SUCCESS("CA-Tech sample data seeded successfully."))
