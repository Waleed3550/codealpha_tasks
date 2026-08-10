"""
Input validators for the translator app.

Provides reusable, framework-aware validators that can be called from
serializers, views, or anywhere else that needs input sanitation.
"""

from rest_framework.exceptions import ValidationError

# ---------------------------------------------------------------------------
# Supported language codes
# ---------------------------------------------------------------------------

#: Frozenset of ISO 639-1 language codes known to be supported by LibreTranslate.
#: 'auto' is the special value that triggers server-side language detection.
SUPPORTED_LANGUAGE_CODES: frozenset[str] = frozenset(
    {
        'auto', 'af', 'sq', 'am', 'ar', 'hy', 'as', 'ay', 'az', 'bm', 'eu', 'be', 'bn', 'bho', 'bs', 'bg', 'ca', 'ceb', 'ny', 'zh', 'zh-cn', 'zh-tw', 'co', 'hr', 'cs', 'da', 'dv', 'doi', 'nl', 'en', 'eo', 'et', 'ee', 'tl', 'fi', 'fr', 'fy', 'gl', 'ka', 'de', 'el', 'gn', 'gu', 'ht', 'ha', 'haw', 'iw', 'he', 'hi', 'hmn', 'hu', 'is', 'ig', 'ilo', 'id', 'ga', 'it', 'ja', 'jw', 'jv', 'kn', 'kk', 'km', 'rw', 'gom', 'ko', 'kri', 'ku', 'ckb', 'ky', 'lo', 'la', 'lv', 'ln', 'lt', 'lg', 'lb', 'mk', 'mai', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mni-mtei', 'lus', 'mn', 'my', 'ne', 'no', 'or', 'om', 'ps', 'fa', 'pl', 'pt', 'pa', 'qu', 'ro', 'ru', 'sm', 'sa', 'gd', 'nso', 'sr', 'st', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tg', 'ta', 'tt', 'te', 'th', 'ti', 'ts', 'tr', 'tk', 'ak', 'uk', 'ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu'
    }
)

# ---------------------------------------------------------------------------
# Validator functions
# ---------------------------------------------------------------------------


def validate_language_code(code: str, field_name: str = 'language') -> str:
    """
    Validate and normalise a language code.

    Parameters
    ----------
    code       : The raw language code string supplied by the caller.
    field_name : Name of the field being validated (used in error messages).

    Returns
    -------
    str — the cleaned (lowercase, stripped) language code.

    Raises
    ------
    rest_framework.exceptions.ValidationError
        When *code* is not found in SUPPORTED_LANGUAGE_CODES.
    """
    cleaned = code.strip().lower()
    if cleaned not in SUPPORTED_LANGUAGE_CODES:
        supported_list = ', '.join(sorted(SUPPORTED_LANGUAGE_CODES))
        raise ValidationError(
            {
                field_name: (
                    f"'{cleaned}' is not a supported language code. "
                    f'Supported codes are: {supported_list}.'
                )
            }
        )
    return cleaned


def validate_text_length(text: str, max_length: int = 5000) -> str:
    """
    Validate that *text* is non-empty and within *max_length* characters.

    Parameters
    ----------
    text       : The raw text to validate.
    max_length : Maximum allowed character count (default 5 000).

    Returns
    -------
    str — the stripped text.

    Raises
    ------
    rest_framework.exceptions.ValidationError
        When the text is empty after stripping or exceeds *max_length*.
    """
    stripped = text.strip()

    if not stripped:
        raise ValidationError({'text': 'Text must not be empty or consist only of whitespace.'})

    if len(stripped) > max_length:
        raise ValidationError(
            {
                'text': (
                    f'Text is too long ({len(stripped):,} characters). '
                    f'Maximum allowed length is {max_length:,} characters.'
                )
            }
        )

    return stripped
