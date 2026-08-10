from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from cart.services import get_or_create_cart
from core.shopping_auth import auth_required_json_payload, redirect_guest_to_login
from products.models import Product, ProductVariant


def cart_detail(request):
    if not request.user.is_authenticated:
        return redirect_guest_to_login(
            request,
            "Please sign in to continue shopping and save your cart.",
            next_url=request.get_full_path(),
        )
    cart = get_or_create_cart(request)
    if cart is None:
        return redirect_guest_to_login(
            request,
            "Please sign in to continue shopping and save your cart.",
            next_url=request.get_full_path(),
        )
    return render(request, "cart/cart_detail.html", {"cart": cart})


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    variant = None
    variant_id = request.POST.get("variant")
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
    quantity = max(1, int(request.POST.get("quantity", 1)))
    action = (request.POST.get("action") or "add_to_cart").strip().lower()

    if not request.user.is_authenticated:
        next_url = request.META.get("HTTP_REFERER") or product.get_absolute_url()
        payload = auth_required_json_payload(
            request,
            "Please sign in to continue shopping and save your cart.",
            action_type=action if action in {"add_to_cart", "buy_now"} else "add_to_cart",
            product_id=product.id,
            variant_id=variant.id if variant else None,
            quantity=quantity,
            next_url=next_url,
        )
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(payload)
        return redirect_guest_to_login(
            request,
            payload["message"],
            action_type=action if action in {"add_to_cart", "buy_now"} else "add_to_cart",
            product_id=product.id,
            variant_id=variant.id if variant else None,
            quantity=quantity,
            next_url=next_url,
        )

    cart = get_or_create_cart(request)
    if cart is None:
        return redirect("core:home")
    item, created = cart.items.get_or_create(product=product, variant=variant, defaults={"quantity": quantity})
    if not created:
        item.quantity = min(item.quantity + quantity, 99)
        item.save(update_fields=["quantity"])
    if action == "buy_now":
        messages.success(request, f"{product.name} added to your cart. Continue to checkout.")
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "count": cart.item_count, "subtotal": f"{cart.subtotal:.2f}", "redirect_url": reverse("orders:checkout")})
        return redirect("orders:checkout")
    messages.success(request, f"{product.name} added to your cart.")
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "count": cart.item_count, "subtotal": f"{cart.subtotal:.2f}"})
    return redirect("cart:detail")


@require_POST
def update_cart_item(request, item_id):
    if not request.user.is_authenticated:
        return redirect_guest_to_login(
            request,
            "Please sign in to continue shopping and save your cart.",
            next_url=request.META.get("HTTP_REFERER") or reverse("cart:detail"),
        )
    cart = get_or_create_cart(request)
    if cart is None:
        return redirect_guest_to_login(
            request,
            "Please sign in to continue shopping and save your cart.",
            next_url=request.get_full_path(),
        )
    item = get_object_or_404(cart.items, id=item_id)
    quantity = int(request.POST.get("quantity", 1))
    if quantity <= 0:
        item.delete()
    else:
        item.quantity = min(quantity, 99)
        item.save(update_fields=["quantity"])
    messages.info(request, "Cart updated.")
    return redirect("cart:detail")


@require_POST
def remove_cart_item(request, item_id):
    if not request.user.is_authenticated:
        return redirect_guest_to_login(
            request,
            "Please sign in to continue shopping and save your cart.",
            next_url=request.META.get("HTTP_REFERER") or reverse("cart:detail"),
        )
    cart = get_or_create_cart(request)
    if cart is None:
        return redirect_guest_to_login(
            request,
            "Please sign in to continue shopping and save your cart.",
            next_url=request.get_full_path(),
        )
    get_object_or_404(cart.items, id=item_id).delete()
    messages.info(request, "Item removed from cart.")
    return redirect("cart:detail")
