"""
Custom exception hierarchy for the translator app.

All translation-related exceptions derive from TranslationError so that
callers can catch the base class or a specific subclass as needed.
"""


class TranslationError(Exception):
    """Base exception for all translation-related errors."""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class TranslationAPIError(TranslationError):
    """Raised when the translation API returns an unexpected error."""
    pass


class TranslationTimeoutError(TranslationError):
    """Raised when the translation API request times out."""
    pass


class TranslationValidationError(TranslationError):
    """Raised when the translation API rejects the input (e.g. bad language pair)."""
    pass
