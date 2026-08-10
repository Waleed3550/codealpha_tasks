from decimal import Decimal
from uuid import uuid4

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from cart.services import get_or_create_cart
from core.shopping_auth import redirect_guest_to_login, shopping_action_login_required
from orders.forms import CheckoutForm
from orders.models import Notification, Order, OrderEvent, OrderItem
from products.models import Product, ProductVariant


PAYMENT_GATEWAYS = {
    "pakistan": ["jazzcash", "easypaisa", "banktransfer", "visa", "mastercard"],
    "india": ["upi", "phonepe", "paytm", "razorpay", "visa", "mastercard"],
    "default": ["stripe", "googlepay", "applepay", "paypal", "visa", "mastercard"],
}

GATEWAY_LABELS = {
    "jazzcash": "JazzCash",
    "easypaisa": "EasyPaisa",
    "banktransfer": "Bank Transfer",
    "upi": "UPI",
    "phonepe": "PhonePe",
    "paytm": "Paytm",
    "razorpay": "Razorpay",
    "stripe": "Stripe",
    "googlepay": "Google Pay",
    "applepay": "Apple Pay",
    "paypal": "PayPal",
    "visa": "Visa",
    "mastercard": "Mastercard",
}


def _country_key(country: str | None) -> str:
    normalized = (country or "").strip().lower()
    if normalized in {"pk", "pakistan"}:
        return "pakistan"
    if normalized in {"in", "india"}:
        return "india"
    return "default"


def _available_gateways(country: str | None) -> list[str]:
    return PAYMENT_GATEWAYS[_country_key(country)]


def _gateway_label(gateway: str) -> str:
    return GATEWAY_LABELS.get(gateway, gateway.replace("_", " ").title())


def _generate_transaction_id(order_number: str) -> str:
    return f"TXN-{order_number}-{uuid4().hex[:8].upper()}"


def _validate_inventory(items):
    product_ids = {item.product_id for item in items}
    variant_ids = {item.variant_id for item in items if item.variant_id}
    products = Product.objects.select_for_update().filter(id__in=product_ids).in_bulk()
    variants = ProductVariant.objects.select_for_update().filter(id__in=variant_ids).in_bulk()

    shortages = []
    for item in items:
        product = products.get(item.product_id)
        if not product:
            shortages.append(f"{item.product.name} is no longer available.")
            continue
        if product.stock < item.quantity:
            shortages.append(f"Only {product.stock} units of {product.name} are available.")
        if item.variant_id:
            variant = variants.get(item.variant_id)
            if not variant:
                shortages.append(f"Selected variant for {product.name} is no longer available.")
            elif variant.stock < item.quantity:
                shortages.append(f"Only {variant.stock} units of {product.name} ({variant.name}: {variant.value}) are available.")
    return shortages, products, variants


def checkout(request):
    if not request.user.is_authenticated:
        return redirect_guest_to_login(
            request,
            "Please sign in to continue shopping and save your cart.",
            action_type="checkout",
            next_url=request.get_full_path(),
        )
    cart = get_or_create_cart(request)
    if cart is None:
        return redirect_guest_to_login(
            request,
            "Please sign in to continue shopping and save your cart.",
            action_type="checkout",
            next_url=request.get_full_path(),
        )
    items = list(cart.items.select_related("product", "variant"))
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("cart:detail")

    initial = {}
    if request.user.is_authenticated:
        profile = request.user.profile
        initial = {
            "full_name": request.user.get_full_name(),
            "email": request.user.email,
            "phone": profile.phone,
            "billing_address": profile.address_line_1,
            "shipping_address": profile.address_line_1,
            "city": profile.city,
            "state": profile.state,
            "postal_code": profile.postal_code,
            "country": profile.country,
        }
    form = CheckoutForm(request.POST or None, initial=initial)
    subtotal = cart.subtotal
    shipping_total = Decimal("0.00") if subtotal >= Decimal("500.00") else Decimal("19.00")
    tax_total = (subtotal * Decimal("0.0825")).quantize(Decimal("0.01"))
    grand_total = subtotal + shipping_total + tax_total

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            loc = getattr(request, 'localization', {})
            shortages, products, variants = _validate_inventory(items)
            if shortages:
                for shortage in shortages:
                    messages.error(request, shortage)
                return redirect("cart:detail")

            cleaned_data = form.cleaned_data.copy()
            payment_method = cleaned_data.pop("payment_method", "cod")
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                order_number=f"TN-{uuid4().hex[:10].upper()}",
                payment_method=payment_method,
                subtotal=subtotal,
                shipping_total=shipping_total,
                tax_total=tax_total,
                grand_total=grand_total,
                converted_currency=loc.get('currency'),
                exchange_rate=loc.get('rate'),
                visitor_country=loc.get('country'),
                visitor_language=loc.get('language'),
                visitor_timezone=loc.get('timezone'),
                **cleaned_data,
            )
            for item in items:
                product = products.get(item.product_id) or item.product
                variant = variants.get(item.variant_id) if item.variant_id else item.variant
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    variant=variant,
                    product_name=product.name,
                    sku=product.sku,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.line_total,
                )
                product.stock = max(0, product.stock - item.quantity)
                product.save(update_fields=["stock"])
                if variant:
                    variant.stock = max(0, variant.stock - item.quantity)
                    variant.save(update_fields=["stock"])
            cart.items.all().delete()
            OrderEvent.objects.create(
                order=order,
                title="Order Placed",
                description="Checkout completed successfully.",
                status=order.status,
            )
            if order.user:
                Notification.objects.create(
                    user=order.user,
                    order=order,
                    title="Order received",
                    message="Your order has been received successfully. Waiting for admin approval.",
                )
            if order.payment_method == "card":
                return redirect("orders:payment", order_number=order.order_number)
        return redirect("orders:confirmation", order_number=order.order_number)
    return render(request, "orders/checkout.html", {"form": form, "cart": cart, "items": items, "subtotal": subtotal, "shipping_total": shipping_total, "tax_total": tax_total, "grand_total": grand_total})


def confirmation(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related("items"), order_number=order_number)
    return render(request, "orders/confirmation.html", {"order": order})


from django.core.mail import send_mail
from django.conf import settings

def payment(request, order_number):
    if not request.user.is_authenticated:
        return redirect_guest_to_login(
            request,
            "Please sign in to continue to payment.",
            next_url=request.get_full_path(),
        )
    order = get_object_or_404(Order, order_number=order_number)
    if order.payment_method != "card" or order.payment_status == Order.PAYMENT_APPROVED:
        return redirect("orders:confirmation", order_number=order.order_number)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "pay":
            gateway = (request.POST.get("gateway") or "").strip().lower()
            if gateway not in _available_gateways(order.country):
                messages.error(request, "Please select a valid payment method.")
                return redirect("orders:payment", order_number=order.order_number)
            with transaction.atomic():
                order.payment_status = Order.PAYMENT_APPROVED
                order.status = Order.CONFIRMED
                order.payment_gateway = gateway
                order.transaction_id = order.transaction_id or _generate_transaction_id(order.order_number)
                order.save(update_fields=["payment_status", "status", "payment_gateway", "transaction_id"])
                OrderEvent.objects.create(
                    order=order,
                    title="Payment Received",
                    description=f"Payment approved via {gateway}.",
                    status=order.status,
                )

                if order.user:
                    Notification.objects.create(
                        user=order.user,
                        order=order,
                        title="Payment successful",
                        message="Your payment has been approved and your order is confirmed.",
                    )

            # Send confirmation email
            try:
                send_mail(
                    subject=f"Order Confirmation - {order.order_number}",
                    message=(
                        f"Dear {order.full_name},\n\n"
                        f"Thank you for your purchase! Your payment was successful and your order ({order.order_number}) is now confirmed.\n\n"
                        f"Total: {order.grand_total}\n"
                        f"Transaction ID: {order.transaction_id}\n\n"
                        f"You can view your invoice here: {request.build_absolute_uri(order.get_absolute_url() + 'invoice/')}"
                    ),
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@technest.com'),
                    recipient_list=[order.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, "Payment successful! Your order is now confirmed.")
            return redirect("orders:confirmation", order_number=order.order_number)
        else:
            with transaction.atomic():
                order.payment_status = Order.PAYMENT_REJECTED
                order.status = Order.CANCELLED
                order.save(update_fields=["payment_status", "status"])
                OrderEvent.objects.create(
                    order=order,
                    title="Payment Failed",
                    description="Payment was rejected by the selected gateway.",
                    status=order.status,
                )
            messages.error(request, "Payment failed. Your transaction was rejected.")
            # Keep them on the payment page so they can retry
            return redirect("orders:payment", order_number=order.order_number)

    return render(request, "orders/payment.html", {"order": order, "available_gateways": _available_gateways(order.country), "gateway_labels": GATEWAY_LABELS})


@shopping_action_login_required("Please sign in to view your order history.")
def history(request):
    orders = request.user.orders.prefetch_related("items").all()
    return render(request, "orders/history.html", {"orders": orders})


@shopping_action_login_required("Please sign in to track your order.")
def detail(request, order_number):
    order = get_object_or_404(request.user.orders.prefetch_related("items"), order_number=order_number)

    if order.payment_status == "rejected":
        timeline = [
            ("pending", "Order Placed"),
            ("rejected", "Payment Failed"),
        ]
        current_index = 1
    else:
        timeline = [
            ("pending", "Order Placed"),
            ("confirmed", "Payment Successful"),
            ("processing", "Processing"),
            ("shipped", "Shipped"),
            ("delivered", "Delivered"),
        ]
        order_positions = {step[0]: index for index, step in enumerate(timeline)}
        current_index = order_positions.get(order.status, 0)

    return render(request, "orders/detail.html", {"order": order, "timeline": timeline, "current_index": current_index})


@shopping_action_login_required("Please sign in to download your invoice.")
def invoice(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related("items"), order_number=order_number)
    if order.user and request.user != order.user and not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to view this invoice.")

    return render(request, "orders/invoice.html", {"order": order})
