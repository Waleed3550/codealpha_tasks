from cart.models import Cart


def get_or_create_cart(request):
    if not request.user.is_authenticated:
        return None
    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(user=request.user)
    anonymous = Cart.objects.filter(session_key=request.session.session_key, user__isnull=True).first()
    if anonymous and anonymous.id != cart.id:
        for item in anonymous.items.all():
            existing = cart.items.filter(product=item.product, variant=item.variant).first()
            if existing:
                existing.quantity += item.quantity
                existing.save(update_fields=["quantity"])
            else:
                item.cart = cart
                item.save(update_fields=["cart"])
        anonymous.delete()
    return cart
