"""
translator/services package.

Exports the TranslationServiceFactory so that the rest of the application
only needs to import from this package, not from individual modules.
"""

from .factory import TranslationServiceFactory

__all__ = ['TranslationServiceFactory']
