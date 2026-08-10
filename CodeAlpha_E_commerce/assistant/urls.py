from django.urls import path

from assistant import views

app_name = "assistant"

urlpatterns = [
    path("api/state/", views.state_api, name="state_api"),
    path("api/chat/", views.chat_api, name="chat_api"),
    path("wishlist/", views.wishlist_page, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", views.toggle_wishlist, name="wishlist_toggle"),
]
