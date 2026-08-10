"""
URL configuration for the LanguageTranslator project.

All API routes are namespaced under the translator app.
Media files are served by Django only in development (DEBUG=True).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('translator.urls', namespace='translator')),
]

# Serve media files via Django's dev server when DEBUG is True.
# In production, a web server (nginx, etc.) or cloud storage handles media.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
