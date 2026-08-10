from django.urls import NoReverseMatch, reverse

from assistant.models import AISettings


def _safe_reverse(name: str) -> str:
    try:
        return reverse(name)
    except NoReverseMatch:
        return ""


def ai_assistant(request):
    settings_obj = AISettings.load()
    return {
        "ai_assistant_settings": settings_obj,
        "ai_assistant_api_url": _safe_reverse("assistant:chat_api"),
        "ai_assistant_state_url": _safe_reverse("assistant:state_api"),
        "ai_assistant_wishlist_url": _safe_reverse("assistant:wishlist"),
    }
