"""
Translation service factory.

Provides a registry-based mechanism for selecting and instantiating
translation backends at runtime.

How to add a new translation service
-------------------------------------
1. Create a new module in translator/services/ (e.g. google.py).
2. Subclass BaseTranslationService and implement all abstract members.
3. Import your class here and call:

       TranslationServiceFactory.register('google', GoogleTranslateService)

   Alternatively, call register() from the new module's own __init__ block.

4. Set TRANSLATION_SERVICE=google in your .env file.

Example
-------
    from translator.services.factory import TranslationServiceFactory
    service = TranslationServiceFactory.get_service()   # uses settings
    result  = service.translate('Hello', 'en', 'fr')
"""

from django.conf import settings

from .base import BaseTranslationService


class TranslationServiceFactory:
    """
    Registry and factory for translation service adapters.

    The factory decouples the rest of the application from concrete
    service implementations.  New services can be registered at any time
    without modifying existing code.
    """

    _registry: dict[str, type] = {}

    # ------------------------------------------------------------------
    # Registry management
    # ------------------------------------------------------------------

    @classmethod
    def register(cls, name: str, service_class: type) -> None:
        """
        Register a translation service class under the given *name*.

        Parameters
        ----------
        name          : Identifier used in the TRANSLATION_SERVICE env var.
        service_class : A concrete subclass of BaseTranslationService.
        """
        if not issubclass(service_class, BaseTranslationService):
            raise TypeError(
                f'{service_class.__name__} must subclass BaseTranslationService.'
            )
        cls._registry[name.lower()] = service_class

    # ------------------------------------------------------------------
    # Factory method
    # ------------------------------------------------------------------

    @classmethod
    def get_service(cls, service_name: str = None) -> BaseTranslationService:
        """
        Instantiate and return the requested translation service.

        Parameters
        ----------
        service_name : Optional override.  When omitted the value of
                       settings.TRANSLATION_SERVICE is used.

        Returns
        -------
        An instance of the requested BaseTranslationService subclass.

        Raises
        ------
        ValueError  : When the requested service name is not registered.
        """
        if service_name is None:
            service_name = getattr(settings, 'TRANSLATION_SERVICE', 'libretranslate')

        key = service_name.lower()
        if key not in cls._registry:
            available = ', '.join(sorted(cls._registry.keys())) or '(none)'
            raise ValueError(
                f"Translation service '{service_name}' is not registered. "
                f'Available services: {available}. '
                'Register a new service with TranslationServiceFactory.register().'
            )

        service_class = cls._registry[key]
        return service_class()


# ---------------------------------------------------------------------------
# Pre-register built-in services
# ---------------------------------------------------------------------------

# Import here (after class definition) to avoid circular imports.
from .libretranslate import LibreTranslateService  # noqa: E402

TranslationServiceFactory.register('libretranslate', LibreTranslateService)
