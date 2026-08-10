from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, WorkspaceViewSet, TeamViewSet, RoleViewSet

router = DefaultRouter()
# Register more specific routes first so they don't get swallowed by detail views
router.register(r'organizations/workspaces', WorkspaceViewSet, basename='workspace')
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'roles', RoleViewSet, basename='role')

urlpatterns = [
    path('', include(router.urls)),
]
