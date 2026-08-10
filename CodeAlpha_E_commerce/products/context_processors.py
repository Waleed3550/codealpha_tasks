from products.models import Brand, Category


def catalog_nav(request):
    return {
        "nav_categories": Category.objects.filter(is_active=True)[:8],
        "nav_brands": Brand.objects.filter(is_featured=True)[:8],
    }
