from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, SystemLogViewSet

router = DefaultRouter()
router.register(r'auditlogs', AuditLogViewSet, basename='auditlog')
router.register(r'systemlogs', SystemLogViewSet, basename='systemlog')

urlpatterns = [
    path('', include(router.urls)),
]
