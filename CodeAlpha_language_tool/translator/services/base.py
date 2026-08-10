"""
Abstract base class for all translation service adapters.

To add a new translation backend:
1. Create a module in translator/services/ (e.g. google.py).
2. Subclass BaseTranslationService and implement every abstract member.
3. Register the new class in factory.py via TranslationServiceFactory.register().
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseTranslationService(ABC):
    """
    Contract that every translation service adapter must fulfil.

    Subclasses must implement:
    - translate()
    - get_supported_languages()
    - service_name (property)
    - is_available (property)
    """

    # ------------------------------------------------------------------
    # Abstract properties
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def service_name(self) -> str:
        """Human-readable / machine identifier for this service (e.g. 'libretranslate')."""

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """
        Return True when the service is fully configured and reachable.

        Implementations should at minimum verify that required settings
        (API URL, API key, etc.) are present.  A network connectivity
        check is optional but recommended.
        """

    # ------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------

    @abstractmethod
    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> dict:
        """
        Translate *text* from *source_language* to *target_language*.

        Parameters
        ----------
        text            : The raw text to translate.
        source_language : ISO 639-1 source language code (e.g. 'en') or 'auto'.
        target_language : ISO 639-1 target language code (e.g. 'fr').

        Returns
        -------
        dict with the following keys:

        =====================  =========================================
        Key                    Type / description
        =====================  =========================================
        translated_text        str   — the translated string
        source_language        str   — the source code that was used
        target_language        str   — the target code that was used
        detected_language      Optional[str] — detected lang when 'auto'
        characters_translated  int   — len(text)
        =====================  =========================================

        Raises
        ------
        TranslationError or any of its subclasses on failure.
        """

    @abstractmethod
    def get_supported_languages(self) -> list[dict]:
        """
        Retrieve the list of language pairs supported by this service.

        Returns
        -------
        list of dicts, each containing:
            code : str  — ISO 639-1 language code
            name : str  — human-readable language name (in English)

        Raises
        ------
        TranslationError or any of its subclasses on failure.
        """
