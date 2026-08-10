from django.urls import path

from orders import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("confirmation/<str:order_number>/", views.confirmation, name="confirmation"),
    path("history/", views.history, name="history"),
    path("<str:order_number>/payment/", views.payment, name="payment"),
    path("<str:order_number>/invoice/", views.invoice, name="invoice"),
    path("<str:order_number>/", views.detail, name="detail"),
]
