from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CommentViewSet

# Initialize the DefaultRouter for automatic URL routing
router = DefaultRouter()

# Register the ViewSets
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'comments', CommentViewSet, basename='comment')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
