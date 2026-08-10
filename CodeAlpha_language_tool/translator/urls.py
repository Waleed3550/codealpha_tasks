"""
URL patterns for the translator app.

All routes are prefixed at the project level by LanguageTranslator/urls.py
which includes this file at the root path ''.
"""

from django.urls import path

from .views import HealthCheckView, IndexView, SupportedLanguagesView, TranslateAPIView

app_name = 'translator'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('translate/', TranslateAPIView.as_view(), name='translate'),
    path('health/', HealthCheckView.as_view(), name='health'),
    path('languages/', SupportedLanguagesView.as_view(), name='languages'),
]
