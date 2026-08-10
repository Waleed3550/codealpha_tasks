from django.urls import path

from dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("products/", views.product_list, name="products"),
    path("products/add/", views.product_form, name="product_add"),
    path("products/<int:product_id>/edit/", views.product_form, name="product_edit"),
    path("products/<int:product_id>/delete/", views.product_delete, name="product_delete"),
    path("products/bulk/", views.product_bulk_action, name="product_bulk"),
    path("catalog/", views.taxonomy, name="taxonomy"),
    path("orders/", views.order_list, name="orders"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("orders/<int:order_id>/<slug:action>/", views.order_action, name="order_action"),
    path("customers/", views.customer_list, name="customers"),
    path("settings/", views.settings_page, name="settings"),
    path("ai-settings/", views.ai_settings, name="ai_settings"),
    path("api/stats/", views.dashboard_stats_api, name="api_stats"),
]
