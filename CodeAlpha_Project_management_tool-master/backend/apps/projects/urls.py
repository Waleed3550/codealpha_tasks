from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectMemberViewSet, ProjectActivityViewSet, BoardViewSet, ColumnViewSet

router = DefaultRouter()

router.register(r'projects', ProjectViewSet, basename='project')

# Register other standard viewsets
router.register(r'projectmembers', ProjectMemberViewSet, basename='projectmember')
router.register(r'projectactivitys', ProjectActivityViewSet, basename='projectactivity')
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'columns', ColumnViewSet, basename='column')

urlpatterns = [
    # Explicitly map the nested routes BEFORE the DRF router to guarantee no <pk> collision
    path('projects/boards/', BoardViewSet.as_view({'get': 'list', 'post': 'create'}), name='project-boards'),
    path('projects/boards/<uuid:pk>/', BoardViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='project-boards-detail'),
    path('projects/columns/', ColumnViewSet.as_view({'get': 'list', 'post': 'create'}), name='project-columns'),
    path('projects/columns/<uuid:pk>/', ColumnViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='project-columns-detail'),
    
    path('', include(router.urls)),
]
