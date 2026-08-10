from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

router = DefaultRouter()
router.register(r'notifications/notifications', NotificationViewSet, basename='notification')
router.register(r'notifications', NotificationViewSet, basename='notification_base')

urlpatterns = [
    path('', include(router.urls)),
]
