from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, MessageViewSet, MessageReactionViewSet, ReadReceiptViewSet

router = DefaultRouter()
router.register(r'chatrooms', ChatRoomViewSet, basename='chatroom')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'messagereactions', MessageReactionViewSet, basename='messagereaction')
router.register(r'readreceipts', ReadReceiptViewSet, basename='readreceipt')

urlpatterns = [
    path('', include(router.urls)),
]
