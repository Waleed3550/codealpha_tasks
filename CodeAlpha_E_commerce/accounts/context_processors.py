from django.urls import NoReverseMatch, reverse

from accounts.services import google_oauth_client_id, google_oauth_enabled


def _safe_reverse(name: str) -> str:
    try:
        return reverse(name)
    except NoReverseMatch:
        return ""


def google_auth(request):
    return {
        "google_oauth_client_id": google_oauth_client_id(),
        "google_oauth_enabled": google_oauth_enabled(),
        "google_oauth_login_url": _safe_reverse("accounts:google_oauth_init"),
    }
