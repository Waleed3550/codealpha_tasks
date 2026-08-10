from django.urls import path

from products import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="list"),
    path("<slug:slug>/", views.product_detail, name="detail"),
]
