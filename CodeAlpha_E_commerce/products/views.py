from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from products.models import Brand, Category, Product


def product_list(request):
    products = Product.objects.select_related("category", "brand").prefetch_related("images").filter(is_active=True)
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "")
    brand_slug = request.GET.get("brand", "")
    sort = request.GET.get("sort", "featured")

    if query:
        products = products.filter(Q(name__icontains=query) | Q(short_description__icontains=query) | Q(description__icontains=query) | Q(brand__name__icontains=query))
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)

    ordering = {
        "price_asc": "price",
        "price_desc": "-price",
        "newest": "-created_at",
        "rating": "-rating",
        "featured": "-is_featured",
    }.get(sort, "-is_featured")
    products = products.order_by(ordering, "name")

    paginator = Paginator(products, 9)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "products/product_list.html",
        {
            "page_obj": page_obj,
            "categories": Category.objects.filter(is_active=True),
            "brands": Brand.objects.all(),
            "query": query,
            "active_category": category_slug,
            "active_brand": brand_slug,
            "sort": sort,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category", "brand").prefetch_related("images", "variants"), slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id).prefetch_related("images")[:4]
    recently_viewed = request.session.get("recently_viewed_products", [])
    recently_viewed = [pid for pid in recently_viewed if pid != product.id]
    recently_viewed.insert(0, product.id)
    request.session["recently_viewed_products"] = recently_viewed[:8]
    request.session.modified = True
    recent_products = Product.objects.filter(id__in=recently_viewed[1:6], is_active=True).select_related("category", "brand").prefetch_related("images")
    recent_map = {item.id: item for item in recent_products}
    ordered_recent = [recent_map[pid] for pid in recently_viewed[1:6] if pid in recent_map]
    return render(request, "products/product_detail.html", {"product": product, "related": related, "recently_viewed_products": ordered_recent})

def category_page(request, category_slug):
    products = Product.objects.select_related("category", "brand").prefetch_related("images").filter(is_active=True)
    query = request.GET.get("q", "").strip()
    brand_slug = request.GET.get("brand", "")
    sort = request.GET.get("sort", "featured")

    if category_slug == "laptops":
        products = products.filter(category__slug__in=["laptops", "laptop"])
        brands = Brand.objects.filter(products__category__slug__in=["laptops", "laptop"], products__is_active=True).distinct()
        category_name = "Laptops"
    elif category_slug == "smartphones":
        products = products.filter(category__slug__in=["smartphones", "smartphone", "phones"])
        brands = Brand.objects.filter(products__category__slug__in=["smartphones", "smartphone", "phones"], products__is_active=True).distinct()
        category_name = "Smartphones"
    elif category_slug == "other-devices":
        products = products.exclude(category__slug__in=["laptops", "laptop", "smartphones", "smartphone", "phones"])
        brands = Brand.objects.exclude(products__category__slug__in=["laptops", "laptop", "smartphones", "smartphone", "phones"]).filter(products__is_active=True).distinct()
        category_name = "Other Devices"
    else:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
        brands = Brand.objects.filter(products__category=category, products__is_active=True).distinct()
        category_name = category.name

    if query:
        products = products.filter(Q(name__icontains=query) | Q(short_description__icontains=query) | Q(description__icontains=query) | Q(brand__name__icontains=query))
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)

    ordering = {
        "price_asc": "price",
        "price_desc": "-price",
        "newest": "-created_at",
        "rating": "-rating",
        "featured": "-is_featured",
    }.get(sort, "-is_featured")
    products = products.order_by(ordering, "name")

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    
    return render(
        request,
        "products/category_page.html",
        {
            "page_obj": page_obj,
            "category_name": category_name,
            "category_slug": category_slug,
            "brands": brands,
            "query": query,
            "active_brand": brand_slug,
            "sort": sort,
            "total_products": products.count(),
        },
    )
