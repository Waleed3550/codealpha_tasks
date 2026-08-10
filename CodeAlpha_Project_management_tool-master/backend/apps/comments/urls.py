from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, ReplyViewSet, ReactionViewSet

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'replys', ReplyViewSet, basename='reply')
router.register(r'reactions', ReactionViewSet, basename='reaction')

urlpatterns = [
    path('', include(router.urls)),
]
