from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from accounts.forms import ProfileUpdateForm, RegisterForm, UserUpdateForm
from accounts.services import (
    GoogleAuthError,
    build_google_auth_url,
    exchange_code_for_payload,
    google_oauth_client_id,
    google_oauth_enabled,
    sign_in_google_user,
    verify_google_credential,
)
from core.shopping_auth import replay_pending_shopping_action


def role_redirect(user):
    if user.is_staff or user.is_superuser:
        return "dashboard:home"
    return "accounts:profile"


class RoleBasedLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next_url"] = self.get_redirect_url()
        context["cancel_url"] = self.get_redirect_url() or reverse("core:home")
        context["google_enabled"] = google_oauth_enabled()
        return context

    def get_success_url(self):
        return self.get_redirect_url() or reverse(role_redirect(self.request.user))

    def form_valid(self, form):
        response = super().form_valid(form)
        replay = replay_pending_shopping_action(self.request)
        if replay:
            if replay.message:
                messages.success(self.request, replay.message)
            return redirect(replay.redirect_url)
        return response


def _safe_next_url(request) -> str:
    candidate = (
        request.POST.get("next")
        or request.GET.get("next")
        or request.META.get("HTTP_REFERER")
        or reverse("accounts:profile")
    )
    if url_has_allowed_host_and_scheme(
        candidate, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return candidate
    return reverse("accounts:profile")


# ─────────────────────────────────────────────────────────────────────────────
# Real Google OAuth2 redirect flow
# ─────────────────────────────────────────────────────────────────────────────

def google_oauth_init(request):
    """
    Step 1 – Redirect the user to Google's OAuth2 consent/login screen.
    Works for both login and register (Google handles both the same way).
    """
    if not google_oauth_enabled():
        messages.error(
            request,
            "Google sign-in is not fully configured on this server. "
            "Please add GOOGLE_OAUTH2_CLIENT_SECRET to your .env file.",
        )
        return redirect("accounts:login")

    next_url = _safe_next_url(request)
    auth_url = build_google_auth_url(request, next_url=next_url)
    return redirect(auth_url)


def google_oauth_callback(request):
    """
    Step 2 – Google redirects back here with ?code=...&state=...
    Exchange the code for user info and sign in.
    """
    error_param = request.GET.get("error")
    if error_param:
        # User cancelled or denied access on Google's screen
        messages.warning(request, "Google sign-in was cancelled.")
        return redirect("accounts:login")

    code = request.GET.get("code", "")
    state = request.GET.get("state", "")

    if not code:
        messages.error(request, "No authorisation code received from Google.")
        return redirect("accounts:login")

    try:
        payload = exchange_code_for_payload(request, code=code, state=state)
        result = sign_in_google_user(request, payload)
    except GoogleAuthError as exc:
        messages.error(request, str(exc))
        return redirect("accounts:login")
    except Exception as exc:
        messages.error(request, f"Google sign-in failed: {exc}")
        return redirect("accounts:login")

    # Success!
    user = request.user
    display = user.get_full_name() or user.email or user.username
    messages.success(request, f"Signed in with Google as {display}.")

    # Replay any pending cart / shopping action
    next_url = request.session.pop("google_oauth_next", None) or reverse(role_redirect(user))
    replay = replay_pending_shopping_action(request)
    if replay:
        if replay.message:
            messages.success(request, replay.message)
        next_url = replay.redirect_url

    return redirect(next_url)


# ─────────────────────────────────────────────────────────────────────────────
# Legacy GSI popup handler (kept for backward compat / modal fallback)
# ─────────────────────────────────────────────────────────────────────────────

def _google_response(request, *, result=None, error: str | None = None, status: int = 200):
    next_url = _safe_next_url(request)
    if result is not None:
        replay = replay_pending_shopping_action(request)
        if replay:
            next_url = replay.redirect_url
            if replay.message:
                messages.success(request, replay.message)
        return JsonResponse(
            {
                "ok": True,
                "redirect_url": next_url,
                "created": result.created,
                "linked": result.linked,
                "message": "Signed in with Google.",
            },
            status=status,
        )
    return JsonResponse(
        {
            "ok": False,
            "error": error or "Google sign-in failed.",
            "redirect_url": reverse("accounts:login"),
        },
        status=status,
    )


def google_login(request):
    """Legacy GSI popup credential handler (still used by auth modal one-tap)."""
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Invalid request method."}, status=405)

    credential = request.POST.get("credential", "")

    try:
        payload = verify_google_credential(credential)
        result = sign_in_google_user(request, payload)
    except GoogleAuthError as exc:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _google_response(request, error=str(exc), status=400)
        messages.error(request, str(exc))
        return redirect("accounts:login")

    messages.success(request, f"Signed in with Google as {request.user.email or request.user.username}.")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return _google_response(request, result=result)

    next_url = _safe_next_url(request)
    replay = replay_pending_shopping_action(request)
    if replay:
        next_url = replay.redirect_url
        if replay.message:
            messages.success(request, replay.message)
    return redirect(next_url)


# ─────────────────────────────────────────────────────────────────────────────
# Standard account views
# ─────────────────────────────────────────────────────────────────────────────

def register(request):
    if request.user.is_authenticated:
        return redirect(role_redirect(request.user))
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome to CA-Tech. Your account is ready.")
        replay = replay_pending_shopping_action(request)
        if replay:
            if replay.message:
                messages.success(request, replay.message)
            return redirect(replay.redirect_url)
        next_url = request.GET.get("next") or request.POST.get("next")
        return redirect(next_url or "accounts:profile")
    next_url = request.GET.get("next") or request.POST.get("next")
    return render(
        request,
        "accounts/register.html",
        {"form": form, "next_url": next_url, "google_enabled": google_oauth_enabled()},
    )


@login_required
def profile(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("dashboard:home")
    orders = request.user.orders.prefetch_related("items").all()[:6]
    notifications = request.user.notifications.select_related("order")[:8]
    profile = request.user.profile
    return render(
        request,
        "accounts/profile.html",
        {
            "orders": orders,
            "notifications": notifications,
            "auth_method_label": "Google" if profile.auth_provider == profile.AUTH_PROVIDER_GOOGLE else "Email and Password",
            "account_created": request.user.date_joined,
            "last_login": request.user.last_login,
            "profile_picture": profile.avatar_url,
        },
    )


@login_required
def edit_profile(request):
    user_form = UserUpdateForm(request.POST or None, instance=request.user)
    profile_form = ProfileUpdateForm(request.POST or None, instance=request.user.profile)
    if request.method == "POST" and user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/edit_profile.html", {"user_form": user_form, "profile_form": profile_form})
