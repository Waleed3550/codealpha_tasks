from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from accounts import views as account_views

from products import views as product_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("category/<slug:category_slug>/", product_views.category_page, name="category_page"),
    path("accounts/", include("accounts.urls")),
    path("products/", include("products.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("assistant/", include("assistant.urls")),
    path("dashboard/", account_views.profile, name="customer_dashboard"),
    path("admin-dashboard/", include("dashboard.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
