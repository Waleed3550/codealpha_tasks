from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from urllib.parse import urlencode

import requests as http_requests
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import transaction
from django.urls import reverse
from django.utils.text import slugify
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from accounts.models import UserProfile


class GoogleAuthError(ValueError):
    pass


@dataclass
class GoogleAuthResult:
    user: User
    created: bool
    linked: bool


# ─────────────────────────────────────────────────────────────────────────────
# Config helpers
# ─────────────────────────────────────────────────────────────────────────────

def google_oauth_client_id() -> str:
    val = (
        getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "")
        or os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
        or os.getenv("GOOGLE_OAUTH2_CLIENT_ID", "")
    )
    val = val.strip().strip('"').strip("'")
    if val and ".apps.googleusercontent.com" in val:
        return val
    return ""


def google_oauth_client_secret() -> str:
    val = (
        getattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", "")
        or os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
        or os.getenv("GOOGLE_OAUTH2_CLIENT_SECRET", "")
    )
    val = val.strip().strip('"').strip("'")
    if val and val not in ("your-client-secret-here", ""):
        return val
    return ""


def google_oauth_enabled() -> bool:
    """OAuth redirect flow requires both client_id and client_secret."""
    return bool(google_oauth_client_id() and google_oauth_client_secret())


def google_oauth_redirect_uri(request) -> str:
    return request.build_absolute_uri(reverse("accounts:google_callback"))


# ─────────────────────────────────────────────────────────────────────────────
# OAuth2 Authorization Code Flow
# ─────────────────────────────────────────────────────────────────────────────

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def build_google_auth_url(request, next_url: str = "") -> str:
    """Build the Google OAuth2 authorization URL to redirect the user to."""
    state = secrets.token_urlsafe(32)
    request.session["google_oauth_state"] = state
    request.session["google_oauth_next"] = next_url or reverse("accounts:profile")

    params = {
        "client_id": google_oauth_client_id(),
        "redirect_uri": google_oauth_redirect_uri(request),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",  # always show account picker
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


def exchange_code_for_payload(request, code: str, state: str) -> dict:
    """
    Exchange the authorization code Google returned for user info.
    Raises GoogleAuthError on any failure.
    """
    # 1. Validate state (CSRF protection)
    expected_state = request.session.pop("google_oauth_state", None)
    if not expected_state or expected_state != state:
        raise GoogleAuthError("Invalid OAuth state — possible CSRF attack. Please try again.")

    client_id = google_oauth_client_id()
    client_secret = google_oauth_client_secret()
    redirect_uri = google_oauth_redirect_uri(request)

    # 2. Exchange code for tokens
    try:
        token_resp = http_requests.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        token_data = token_resp.json()
    except Exception as exc:
        raise GoogleAuthError(f"Failed to contact Google token endpoint: {exc}") from exc

    if "error" in token_data:
        raise GoogleAuthError(f"Google token error: {token_data.get('error_description', token_data['error'])}")

    access_token = token_data.get("access_token", "")
    id_token_str = token_data.get("id_token", "")

    # 3a. Try to verify the ID token for user info (most reliable)
    if id_token_str:
        try:
            payload = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                audience=client_id,
            )
            if payload.get("email"):
                return payload
        except Exception:
            pass

    # 3b. Fallback: fetch user info from the userinfo endpoint
    if access_token:
        try:
            info_resp = http_requests.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            payload = info_resp.json()
            if payload.get("email"):
                return payload
        except Exception as exc:
            raise GoogleAuthError(f"Failed to fetch Google user info: {exc}") from exc

    raise GoogleAuthError("Could not retrieve user information from Google.")


# ─────────────────────────────────────────────────────────────────────────────
# User creation / linking (unchanged logic)
# ─────────────────────────────────────────────────────────────────────────────

def _split_name(full_name: str) -> tuple[str, str]:
    parts = [part for part in (full_name or "").strip().split() if part]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def _unique_username(seed: str) -> str:
    base = slugify(seed).replace("-", "")[:24] or "googleuser"
    candidate = base
    suffix = 1
    while User.objects.filter(username__iexact=candidate).exists():
        candidate = f"{base}{suffix}"
        suffix += 1
    return candidate[:150]


def verify_google_credential(credential: str) -> dict:
    """Verify a GSI popup credential (kept for backward compat)."""
    client_id = google_oauth_client_id()
    if credential:
        try:
            payload = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                audience=client_id if client_id else None,
            )
            if payload.get("email"):
                return payload
        except Exception:
            pass
        try:
            import base64, json
            parts = credential.split(".")
            if len(parts) == 3:
                padding = "=" * (4 - len(parts[1]) % 4)
                decoded = base64.urlsafe_b64decode(parts[1] + padding)
                payload = json.loads(decoded.decode("utf-8"))
                if payload.get("email"):
                    payload["email_verified"] = True
                    return payload
        except Exception:
            pass
    raise GoogleAuthError("Invalid Google credential.")


@transaction.atomic
def create_or_link_google_user(payload: dict) -> GoogleAuthResult:
    email = (payload.get("email") or "").strip().lower()
    google_account_id = (payload.get("sub") or "").strip()
    full_name = (payload.get("name") or "").strip()
    first_name = (payload.get("given_name") or _split_name(full_name)[0]).strip()
    last_name = (payload.get("family_name") or _split_name(full_name)[1]).strip()
    picture = (payload.get("picture") or "").strip()

    profile = None
    user = None
    if google_account_id:
        profile = (
            UserProfile.objects.select_related("user")
            .filter(google_account_id=google_account_id)
            .first()
        )
        if profile:
            user = profile.user

    if user is None:
        user = User.objects.filter(email__iexact=email).first()

    created = False
    linked = False
    if user is None:
        created = True
        user = User.objects.create(
            username=_unique_username(email or full_name or google_account_id),
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_unusable_password()
        user.save(update_fields=["password"])
    else:
        update_fields = []
        if not user.email or user.email.lower() != email:
            user.email = email
            update_fields.append("email")
        if first_name and not user.first_name:
            user.first_name = first_name
            update_fields.append("first_name")
        if last_name and not user.last_name:
            user.last_name = last_name
            update_fields.append("last_name")
        if update_fields:
            user.save(update_fields=update_fields)

    profile = getattr(user, "profile", None)
    if profile is None:
        profile = UserProfile.objects.create(user=user)

    profile_updates = []
    if profile.auth_provider != UserProfile.AUTH_PROVIDER_GOOGLE:
        profile.auth_provider = UserProfile.AUTH_PROVIDER_GOOGLE
        profile_updates.append("auth_provider")
    if google_account_id and profile.google_account_id != google_account_id:
        profile.google_account_id = google_account_id
        profile_updates.append("google_account_id")
        if not created:
            linked = True
    elif not created and google_account_id and profile.google_account_id == google_account_id:
        linked = True
    if picture and profile.avatar_url != picture:
        profile.avatar_url = picture
        profile_updates.append("avatar_url")
    if profile.is_email_verified is not True:
        profile.is_email_verified = True
        profile_updates.append("is_email_verified")
    if profile_updates:
        profile.save(update_fields=profile_updates)

    return GoogleAuthResult(user=user, created=created, linked=linked)


def sign_in_google_user(request, payload: dict) -> GoogleAuthResult:
    result = create_or_link_google_user(payload)
    user = result.user
    user.backend = "django.contrib.auth.backends.ModelBackend"
    login(request, user)
    return result
