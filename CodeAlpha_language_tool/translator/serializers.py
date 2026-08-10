"""
Serializers for the translator app.

TranslationRequestSerializer  — validates incoming translation requests.
TranslationResponseSerializer — serializes the successful translation response.
"""

from rest_framework import serializers


class TranslationRequestSerializer(serializers.Serializer):
    """
    Validates a translation request payload.

    Fields
    ------
    text            : The text to translate (up to 5 000 characters).
    source_language : BCP-47 / ISO 639-1 source language code (e.g. 'en', 'auto').
    target_language : BCP-47 / ISO 639-1 target language code (e.g. 'fr').
    """

    text = serializers.CharField(
        max_length=5000,
        required=True,
        allow_blank=False,
        trim_whitespace=False,
        help_text='The text to translate (max 5 000 characters).',
    )
    source_language = serializers.CharField(
        max_length=10,
        required=True,
        help_text="Source language code, e.g. 'en' or 'auto' for auto-detection.",
    )
    target_language = serializers.CharField(
        max_length=10,
        required=True,
        help_text="Target language code, e.g. 'fr'.",
    )

    # ------------------------------------------------------------------
    # Field-level validators
    # ------------------------------------------------------------------

    def validate_text(self, value: str) -> str:
        """Strip whitespace and reject blank text."""
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError(
                'Text must not be empty or consist only of whitespace.'
            )
        return stripped

    def validate_source_language(self, value: str) -> str:
        """Normalise source language code to lowercase."""
        return value.strip().lower()

    def validate_target_language(self, value: str) -> str:
        """Normalise target language code to lowercase."""
        return value.strip().lower()

    # ------------------------------------------------------------------
    # Cross-field validation
    # ------------------------------------------------------------------

    def validate(self, attrs: dict) -> dict:
        """
        Ensure source and target languages are not identical
        (unless source is 'auto', in which case we cannot know).
        """
        source = attrs.get('source_language', '')
        target = attrs.get('target_language', '')

        if source != 'auto' and source == target:
            raise serializers.ValidationError(
                {
                    'target_language': (
                        'Target language must differ from source language. '
                        f"Both are set to '{target}'."
                    )
                }
            )
        return attrs


class TranslationResponseSerializer(serializers.Serializer):
    """
    Serializes a successful translation result returned by the service layer.

    Fields
    ------
    translated_text      : The translated output string.
    source_language      : The source language code used.
    target_language      : The target language code used.
    detected_language    : Language detected by the API (only when source was 'auto').
    characters_translated: Number of characters in the original text.
    """

    translated_text = serializers.CharField()
    source_language = serializers.CharField()
    target_language = serializers.CharField()
    detected_language = serializers.CharField(allow_null=True, required=False)
    characters_translated = serializers.IntegerField()
