from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from urllib.parse import quote

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


PENDING_SHOPPING_ACTION_KEY = "technest_pending_shopping_action"


@dataclass
class PendingShoppingActionResult:
    redirect_url: str
    message: str = ""


def store_pending_shopping_action(request, action_type: str, **payload) -> None:
    request.session[PENDING_SHOPPING_ACTION_KEY] = {"type": action_type, **payload}
    request.session.modified = True


def peek_pending_shopping_action(request) -> dict:
    return request.session.get(PENDING_SHOPPING_ACTION_KEY, {}) or {}


def pop_pending_shopping_action(request) -> dict:
    action = request.session.pop(PENDING_SHOPPING_ACTION_KEY, {}) or {}
    if action:
        request.session.modified = True
    return action


def login_redirect_url(request, next_url: str | None = None) -> str:
    target = next_url or request.META.get("HTTP_REFERER") or request.get_full_path()
    return f"{reverse('accounts:login')}?next={quote(target)}"


def register_redirect_url(request, next_url: str | None = None) -> str:
    target = next_url or request.META.get("HTTP_REFERER") or request.get_full_path()
    return f"{reverse('accounts:register')}?next={quote(target)}"


def redirect_guest_to_login(request, message: str, *, action_type: str | None = None, next_url: str | None = None, **payload):
    if action_type:
        store_pending_shopping_action(request, action_type, next_url=next_url, **payload)
    messages.info(request, message)
    return redirect(login_redirect_url(request, next_url=next_url))


def auth_required_json_payload(request, message: str, *, action_type: str | None = None, next_url: str | None = None, **payload) -> dict:
    if action_type:
        store_pending_shopping_action(request, action_type, next_url=next_url, **payload)
    return {
        "ok": False,
        "login_required": True,
        "message": message,
        "login_url": login_redirect_url(request, next_url=next_url),
        "register_url": register_redirect_url(request, next_url=next_url),
    }


def replay_pending_shopping_action(request) -> PendingShoppingActionResult | None:
    action = pop_pending_shopping_action(request)
    if not action:
        return None

    action_type = action.get("type")
    next_url = action.get("next_url") or reverse("core:home")

    if action_type == "add_to_cart":
        from cart.services import get_or_create_cart
        from products.models import Product, ProductVariant

        product_id = action.get("product_id")
        if not product_id:
            return PendingShoppingActionResult(next_url, "")
        product = Product.objects.filter(id=product_id, is_active=True).first()
        if not product:
            return PendingShoppingActionResult(next_url, "")
        cart = get_or_create_cart(request)
        if cart is None:
            return PendingShoppingActionResult(next_url, "")
        variant = None
        variant_id = action.get("variant_id")
        if variant_id:
            variant = ProductVariant.objects.filter(id=variant_id, product=product).first()
        quantity = max(1, int(action.get("quantity", 1)))
        item, created = cart.items.get_or_create(product=product, variant=variant, defaults={"quantity": quantity})
        if not created:
            item.quantity = min(item.quantity + quantity, 99)
            item.save(update_fields=["quantity"])
        messages.success(request, f"{product.name} added to your cart.")
        return PendingShoppingActionResult(next_url or reverse("cart:detail"))

    if action_type == "buy_now":
        from cart.services import get_or_create_cart
        from products.models import Product, ProductVariant

        product_id = action.get("product_id")
        if not product_id:
            return PendingShoppingActionResult(reverse("orders:checkout"))
        product = Product.objects.filter(id=product_id, is_active=True).first()
        if not product:
            return PendingShoppingActionResult(reverse("orders:checkout"))
        cart = get_or_create_cart(request)
        if cart is None:
            return PendingShoppingActionResult(reverse("orders:checkout"))
        variant = None
        variant_id = action.get("variant_id")
        if variant_id:
            variant = ProductVariant.objects.filter(id=variant_id, product=product).first()
        quantity = max(1, int(action.get("quantity", 1)))
        item, created = cart.items.get_or_create(product=product, variant=variant, defaults={"quantity": quantity})
        if not created:
            item.quantity = min(item.quantity + quantity, 99)
            item.save(update_fields=["quantity"])
        messages.success(request, f"{product.name} added to your cart. Continue to checkout.")
        return PendingShoppingActionResult(reverse("orders:checkout"))

    if action_type == "cart":
        return PendingShoppingActionResult(action.get("next_url") or reverse("cart:detail"))

    if action_type == "wishlist":
        from assistant.services import get_or_create_wishlist
        from products.models import Product

        product_id = action.get("product_id")
        if not product_id:
            return PendingShoppingActionResult(next_url)
        product = Product.objects.filter(id=product_id, is_active=True).first()
        if not product:
            return PendingShoppingActionResult(next_url)
        wishlist = get_or_create_wishlist(request)
        if wishlist is None:
            return PendingShoppingActionResult(next_url)
        wishlist.items.get_or_create(product=product)
        messages.success(request, f"{product.name} added to your wishlist.")
        return PendingShoppingActionResult(next_url or reverse("assistant:wishlist"))

    if action_type == "checkout":
        return PendingShoppingActionResult(action.get("next_url") or reverse("orders:checkout"))

    if action_type == "orders":
        return PendingShoppingActionResult(action.get("next_url") or reverse("orders:history"))

    if action_type == "profile":
        return PendingShoppingActionResult(action.get("next_url") or reverse("accounts:profile"))

    return PendingShoppingActionResult(next_url)


def shopping_action_login_required(message: str, *, action_type: str | None = None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            return redirect_guest_to_login(
                request,
                message,
                action_type=action_type,
                next_url=request.get_full_path(),
            )

        return wrapped

    return decorator
