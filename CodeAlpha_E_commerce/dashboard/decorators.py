from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            raise PermissionDenied("Admin access required.")
        return redirect("accounts:profile")

    return wrapper
