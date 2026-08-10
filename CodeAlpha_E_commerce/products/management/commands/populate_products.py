import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Product, Category, Brand, ProductImage

class Command(BaseCommand):
    help = "Populate database with 300 unique products"

    def handle(self, *args, **kwargs):
        # Product.objects.all().delete()
        
        smartphone_brands = ['Apple', 'Samsung', 'Google Pixel', 'Xiaomi', 'OnePlus', 'Oppo', 'Vivo', 'Realme', 'Nothing', 'Motorola', 'Huawei', 'Honor', 'Nokia', 'Sony']
        laptop_brands = ['Apple', 'Dell', 'HP', 'Lenovo', 'ASUS', 'Acer', 'MSI', 'Razer', 'Microsoft Surface', 'Samsung', 'LG', 'Huawei', 'Gigabyte']
        other_device_types = ['Tablet', 'Smart Watch', 'Wireless Earbuds', 'Headphones', 'Bluetooth Speaker', 'Gaming Controller', 'Gaming Mouse', 'Gaming Keyboard', 'Monitor', 'Printer', 'Router', 'Webcam', 'Microphone', 'Power Bank', 'Charger', 'SSD', 'HDD', 'USB Flash Drive', 'Memory Card', 'Smart Home Device']
        
        all_brands = set(smartphone_brands + laptop_brands + ['Sony', 'Logitech', 'Razer', 'Corsair', 'Bose', 'Jabra', 'Seagate', 'Western Digital', 'Kingston', 'SanDisk', 'TP-Link', 'Netgear'])
        
        db_brands = {}
        for b in all_brands:
            try:
                obj = Brand.objects.get(slug=slugify(b))
            except Brand.DoesNotExist:
                obj = Brand.objects.create(name=b, slug=slugify(b))
            db_brands[b] = obj
            
        smartphones_cat, _ = Category.objects.get_or_create(name='Smartphones', slug='smartphones')
        laptops_cat, _ = Category.objects.get_or_create(name='Laptops', slug='laptops')
        acc_cat, _ = Category.objects.get_or_create(name='Accessories', slug='accessories')
        audio_cat, _ = Category.objects.get_or_create(name='Audio', slug='audio')
        display_cat, _ = Category.objects.get_or_create(name='Displays', slug='displays')
        gaming_cat, _ = Category.objects.get_or_create(name='Gaming', slug='gaming')

        count = 0
        Product.objects.all().delete() # Start fresh to maintain exact constraints
        
        # 100 Smartphones
        def _add_media_and_reviews(product):
            num_images = random.randint(3, 5)
            for i in range(num_images):
                img_url = f"https://picsum.photos/seed/{product.slug}-{i}/800/800"
                ProductImage.objects.create(
                    product=product, image_url=img_url, alt_text=f"{product.name} View {i+1}",
                    is_primary=(i==0), sort_order=i
                )
            num_reviews = random.randint(1, 4)
            for _ in range(num_reviews):
                from products.models import ProductReview
                ProductReview.objects.create(
                    product=product, customer_name=f"Customer {random.randint(100,999)}",
                    rating=random.randint(4, 5), comment="Great product! Highly recommended.",
                    is_approved=True
                )

        for i in range(1, 101):
            brand_name = random.choice(smartphone_brands)
            brand = db_brands[brand_name]
            
            # Realistic naming
            storage = random.choice(['128GB', '256GB', '512GB', '1TB'])
            color = random.choice(['Phantom Black', 'Titanium Gray', 'Space Black', 'Midnight', 'Starlight', 'Alpine Green', 'Cosmic Grey'])
            
            if brand_name == "Apple":
                name = f"Apple iPhone {random.randint(13, 15)} {random.choice(['Pro', 'Pro Max', 'Plus', ''])} {storage} - {color}"
            elif brand_name == "Samsung":
                name = f"Samsung Galaxy {random.choice(['S22', 'S23', 'S24', 'Z Fold5', 'Z Flip5'])} {random.choice(['Ultra', 'Plus', ''])} {storage} {color}"
            elif brand_name == "Google Pixel":
                name = f"Google Pixel {random.randint(6, 8)} {random.choice(['Pro', 'a', ''])} {storage} {color}"
            else:
                name = f"{brand.name} {random.choice(['X', 'Z', 'Pro', 'Elite', 'Ultra'])} {random.randint(10, 50)} 5G {storage} {color}"
                
            # Fallback for strict uniqueness constraint
            model_code = f" (Model {random.randint(1000, 9999)}{random.choice(['A','B','X','U'])})"
            name += model_code

            if Product.objects.filter(slug=slugify(name)).exists():
                name += f" - Var {i}"
                
            price = Decimal(random.randint(400, 1500) * 100)
            compare_price = price + Decimal(random.randint(50, 200) * 100) if random.random() > 0.5 else None
            specs = {
                "Processor": random.choice(["Snapdragon 8 Gen 3", "Snapdragon 8 Gen 2", "A17 Pro", "A16 Bionic", "Dimensity 9300", "Exynos 2400", "Tensor G3"]),
                "RAM": f"{random.choice([4, 6, 8, 12, 16])}GB",
                "Storage": storage,
                "Display": f"{random.choice(['6.1', '6.4', '6.7', '6.8'])}-inch Super AMOLED, 120Hz",
                "Battery": f"{random.choice([4000, 4500, 5000, 6000])}mAh",
                "Camera": f"{random.choice([12, 48, 50, 108, 200])}MP Main + {random.choice([12, 50])}MP Ultrawide",
                "Operating System": random.choice(["Android 14", "Android 13", "iOS 17", "iOS 16"]),
                "Connectivity": random.choice(["5G, Wi-Fi 6E, Bluetooth 5.3", "5G, Wi-Fi 7, Bluetooth 5.4"])
            }
            sku = f"PHN-{i}-{random.randint(1000,9999)}"
            while Product.objects.filter(sku=sku).exists():
                sku = f"PHN-{i}-{random.randint(1000,99999)}"
                
            p = Product.objects.create(
                category=smartphones_cat, brand=brand, name=name, slug=slugify(name),
                short_description="A premium smartphone.", description="A very premium smartphone with excellent features.",
                price=price, compare_at_price=compare_price, sku=sku,
                stock=random.randint(10, 150), rating=Decimal(f"{random.uniform(3.5, 5.0):.2f}"), specs=specs,
                warranty=random.choice(["1 Year Limited Warranty", "2 Year Manufacturer Warranty"])
            )
            _add_media_and_reviews(p)
            count += 1
            
        # 100 Laptops
        for i in range(101, 201):
            brand_name = random.choice(laptop_brands)
            brand = db_brands[brand_name]
            
            processor = random.choice(["Intel Core i5", "Intel Core i7", "Intel Core i9", "AMD Ryzen 7", "AMD Ryzen 9", "M2", "M3 Max"])
            ram = f"{random.choice([8, 16, 32, 64])}GB"
            
            if brand_name == "Apple":
                name = f"Apple MacBook {random.choice(['Air', 'Pro'])} {random.choice(['13-inch', '14-inch', '16-inch'])} {processor} {ram}"
            elif brand_name == "Dell":
                name = f"Dell {random.choice(['XPS 13', 'XPS 15', 'XPS 17', 'Inspiron 16', 'Alienware m16'])} {processor} {ram}"
            elif brand_name == "HP":
                name = f"HP {random.choice(['Spectre x360', 'Envy 16', 'Omen 17', 'Pavilion Plus'])} {processor} {ram}"
            elif brand_name == "Lenovo":
                name = f"Lenovo {random.choice(['ThinkPad X1 Carbon', 'Legion Pro 7i', 'Yoga 9i', 'IdeaPad Slim 7'])} {processor} {ram}"
            elif brand_name == "ASUS":
                name = f"ASUS {random.choice(['ROG Zephyrus G14', 'Zenbook 14 OLED', 'TUF Gaming A15', 'Vivobook Pro 15'])} {processor} {ram}"
            else:
                name = f"{brand.name} {random.choice(['Studio', 'Creator', 'Gaming', 'Business'])} {random.randint(13, 17)} {processor} {ram}"

            model_code = f" ({random.choice(['Late', 'Early', 'Mid'])} 202{random.randint(2,4)} - #{random.randint(1000, 9999)})"
            name += model_code

            if Product.objects.filter(slug=slugify(name)).exists():
                name += f" - Var {i}"
                
            price = Decimal(random.randint(800, 3500) * 100)
            compare_price = price + Decimal(random.randint(100, 500) * 100) if random.random() > 0.5 else None
            specs = {
                "Processor": processor,
                "RAM": f"{ram} DDR5",
                "Storage": f"{random.choice([256, 512, 1024, 2048, 4096])}GB NVMe SSD",
                "Graphics Card": random.choice(["Intel Iris Xe", "NVIDIA RTX 4050", "NVIDIA RTX 4070", "NVIDIA RTX 4090", "AMD Radeon RX 7600S", "Apple Integrated 14-core GPU"]),
                "Display": f"{random.choice(['13.3', '14', '15.6', '16', '17.3'])}-inch 4K UHD OLED",
                "Battery": f"{random.choice([50, 70, 90, 99])}Whr",
                "Operating System": random.choice(["Windows 11 Home", "Windows 11 Pro", "macOS Sonoma", "Ubuntu Linux"]),
                "Ports": random.choice(["2x Thunderbolt 4, 1x HDMI 2.1, 1x USB-A", "3x USB-C, SD Card Reader, Audio Jack"]),
                "Weight": f"{round(random.uniform(1.2, 2.5), 1)} kg"
            }
            sku = f"LAP-{i}-{random.randint(1000,9999)}"
            while Product.objects.filter(sku=sku).exists():
                sku = f"LAP-{i}-{random.randint(1000,99999)}"
                
            p = Product.objects.create(
                category=laptops_cat, brand=brand, name=name, slug=slugify(name),
                short_description="A powerful laptop.", description="High performance laptop for professionals.",
                price=price, compare_at_price=compare_price, sku=sku,
                stock=random.randint(5, 100), rating=Decimal(f"{random.uniform(4.0, 5.0):.2f}"), specs=specs,
                warranty=random.choice(["1 Year Limited Warranty", "3 Year Manufacturer Warranty"])
            )
            _add_media_and_reviews(p)
            count += 1

        # 100 Other Devices
        cats = [acc_cat, audio_cat, display_cat, gaming_cat]
        for i in range(201, 301):
            dev_type = random.choice(other_device_types)
            brand = random.choice(list(db_brands.values()))
            
            if "Monitor" in dev_type:
                name = f"{brand.name} {random.choice(['UltraSharp', 'Odyssey', 'ProDisplay', 'TUF'])} {random.choice(['27', '32', '34'])}-inch 4K {dev_type}"
            elif "Earbuds" in dev_type or "Headphones" in dev_type:
                name = f"{brand.name} {random.choice(['QuietComfort', 'AirPods', 'Galaxy Buds', 'FreeBuds', 'Elite'])} {random.choice(['Pro', 'Max', 'Ultra', 'Active'])} {dev_type}"
            elif "Router" in dev_type:
                name = f"{brand.name} {random.choice(['Nighthawk', 'Archer', 'Orbi', 'Deco'])} AX{random.randint(1800, 11000)} Wi-Fi {random.choice(['6', '6E', '7'])} {dev_type}"
            elif "Gaming Mouse" in dev_type or "Gaming Keyboard" in dev_type:
                name = f"{brand.name} {random.choice(['DeathAdder', 'BlackWidow', 'G Pro X', 'K70', 'Basilisk'])} Wireless {dev_type}"
            elif "Smart Watch" in dev_type:
                name = f"{brand.name} {random.choice(['Watch Series 9', 'Galaxy Watch 6', 'Pixel Watch 2', 'Venu 3'])} {random.choice(['41mm', '45mm', '47mm'])}"
            elif "Drive" in dev_type or "SSD" in dev_type or "HDD" in dev_type or "Memory" in dev_type:
                name = f"{brand.name} {random.choice(['Extreme Pro', 'Evo 990', 'Black SN850X', 'BarraCuda'])} {random.choice(['1TB', '2TB', '4TB'])} {dev_type}"
            else:
                name = f"{brand.name} {random.choice(['Premium', 'Advanced', 'Elite', 'Pro'])} {dev_type} {random.choice(['Gen 2', 'V2', 'Max'])}"

            model_code = f" ({random.randint(100, 999)}{random.choice(['X','Z','A'])}-{i})"
            name += model_code

            if Product.objects.filter(slug=slugify(name)).exists():
                name += f" - Var {i}"
                
            price = Decimal(random.randint(50, 800) * 100)
            compare_price = price + Decimal(random.randint(20, 100) * 100) if random.random() > 0.5 else None
            cat = random.choice(cats)
            
            # Dynamic realistic specs based on dev_type
            if "Monitor" in dev_type:
                specs = {"Display Size": random.choice(["24-inch", "27-inch", "32-inch", "34-inch Ultrawide"]), "Resolution": random.choice(["1080p", "1440p", "4K"]), "Refresh Rate": random.choice(["60Hz", "144Hz", "240Hz"])}
            elif "Earbuds" in dev_type or "Headphones" in dev_type:
                specs = {"Connectivity": "Bluetooth 5.3", "Battery Life": random.choice(["20 hours", "30 hours", "40 hours"]), "Active Noise Cancellation": random.choice(["Yes", "No"])}
            elif "Drive" in dev_type or "SSD" in dev_type or "HDD" in dev_type or "Memory" in dev_type:
                specs = {"Capacity": random.choice(["256GB", "512GB", "1TB", "2TB", "4TB"]), "Interface": random.choice(["USB 3.2", "NVMe PCIe 4.0", "SATA III"])}
            elif "Router" in dev_type:
                specs = {"Wi-Fi Standard": random.choice(["Wi-Fi 6", "Wi-Fi 6E", "Wi-Fi 7"]), "Speed": random.choice(["AX1800", "AX3000", "AXE5400", "BE19000"])}
            else:
                specs = {"Compatibility": "Universal", "Color": random.choice(["Black", "White", "Silver", "Space Gray"]), "Material": "Premium Aluminum/Plastic"}
                
            sku = f"OTH-{i}-{random.randint(1000,9999)}"
            while Product.objects.filter(sku=sku).exists():
                sku = f"OTH-{i}-{random.randint(1000,99999)}"
                
            p = Product.objects.create(
                category=cat, brand=brand, name=name, slug=slugify(name),
                short_description=f"A useful {dev_type.lower()}.", description=f"High quality {dev_type.lower()}.",
                price=price, compare_at_price=compare_price, sku=sku,
                stock=random.randint(20, 300), rating=Decimal(f"{random.uniform(3.8, 5.0):.2f}"), specs=specs,
                warranty=random.choice(["6 Months Warranty", "1 Year Manufacturer Warranty", "Lifetime Warranty"])
            )
            _add_media_and_reviews(p)
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully populated {count} unique products with realistic names, images and reviews."))
