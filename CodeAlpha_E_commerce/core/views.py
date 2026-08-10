from django.db.models import Count
from django.shortcuts import render

from orders.models import OrderItem
from products.models import Brand, Category, Product


def home(request):
    featured = list(Product.objects.filter(is_active=True, is_featured=True).prefetch_related("images")[:8])
    if len(featured) < 8:
        # Fallback to the latest active products if there aren't enough featured
        needed = 8 - len(featured)
        existing_ids = [p.id for p in featured]
        fallback = list(Product.objects.filter(is_active=True).exclude(id__in=existing_ids).prefetch_related("images").order_by('-created_at')[:needed])
        featured.extend(fallback)
        
    categories = Category.objects.filter(is_active=True)[:6]
    brands = Brand.objects.filter(is_featured=True)[:8]
    latest = Product.objects.filter(is_active=True).prefetch_related("images")[:4]
    top_seller_rows = list(OrderItem.objects.values("product_id").annotate(total_sold=Count("id")).order_by("-total_sold")[:8])
    top_seller_ids = [row["product_id"] for row in top_seller_rows if row["product_id"]]
    top_seller_products = Product.objects.filter(id__in=top_seller_ids, is_active=True).prefetch_related("images")
    top_seller_map = {product.id: product for product in top_seller_products}
    best_sellers = [top_seller_map[product_id] for product_id in top_seller_ids if product_id in top_seller_map]
    recently_viewed_ids = request.session.get("recently_viewed_products", [])
    recent_products = Product.objects.filter(id__in=recently_viewed_ids, is_active=True).prefetch_related("images")
    recent_map = {item.id: item for item in recent_products}
    recently_viewed = [recent_map[pid] for pid in recently_viewed_ids if pid in recent_map][:4]
    return render(request, "core/home.html", {"featured": featured, "categories": categories, "brands": brands, "latest": latest, "best_sellers": best_sellers, "recently_viewed": recently_viewed})


def about(request):
    return render(request, "core/about.html")


def contact(request):
    return render(request, "core/contact.html")

def support(request):
    return render(request, "core/support.html")
