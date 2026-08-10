"""
Development settings for LanguageTranslator project.

Extends base settings with development-friendly overrides.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Relax CORS in development — allow all origins
CORS_ALLOW_ALL_ORIGINS = True

# Local Memory Cache for fast API response caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
