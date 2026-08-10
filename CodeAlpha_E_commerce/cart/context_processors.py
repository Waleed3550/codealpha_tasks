from cart.services import get_or_create_cart


def cart_summary(request):
    if not request.user.is_authenticated:
        return {"cart_item_count": 0, "cart_subtotal": 0}
    try:
        cart = get_or_create_cart(request)
        if cart is None:
            return {"cart_item_count": 0, "cart_subtotal": 0}
        return {"cart_item_count": cart.item_count, "cart_subtotal": cart.subtotal}
    except Exception:
        return {"cart_item_count": 0, "cart_subtotal": 0}
