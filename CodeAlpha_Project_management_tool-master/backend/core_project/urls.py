from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Routes
    path('api/v1/', include('core.urls')),
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/', include('apps.tasks.urls')),
    path('api/v1/', include('apps.audit.urls')),
    path('api/v1/calendar/', include('apps.calendar.urls')),
    path('api/v1/chat/', include('apps.chat.urls')),
    path('api/v1/', include('apps.comments.urls')),
    path('api/v1/files/', include('apps.files.urls')),
    path('api/v1/', include('apps.notifications.urls')),
    path('api/v1/', include('apps.organizations.urls')),
    path('api/v1/', include('apps.projects.urls')),
    
    # Step 16: Configure Swagger (OpenAPI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
