from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from dashboard.decorators import admin_required
from assistant.forms import AISettingsForm
from assistant.models import AIConversation, AISettings, AIVoiceLog
from dashboard.forms import BrandForm, CategoryForm, OrderNoteForm, ProductForm
from orders.models import Notification, Order, OrderEvent, OrderItem
from products.models import Brand, Category, Product, ProductImage, ProductReview


def notify_order_customer(order, title, message):
    if order.user:
        Notification.objects.create(user=order.user, order=order, title=title, message=message)


@admin_required
def dashboard_home(request):
    revenue = Order.objects.filter(payment_status=Order.PAYMENT_APPROVED).aggregate(total=Sum("grand_total"))["total"] or 0
    today = timezone.localdate()
    today_revenue = (
        Order.objects.filter(created_at__date=today, payment_status=Order.PAYMENT_APPROVED)
        .aggregate(total=Sum("grand_total"))["total"]
        or 0
    )
    pending_orders = Order.objects.filter(status=Order.PENDING).count()
    delivered_orders = Order.objects.filter(status=Order.DELIVERED).count()
    cancelled_orders = Order.objects.filter(status=Order.CANCELLED).count()
    low_stock_count = Product.objects.filter(stock__lte=5, stock__gt=0).count()
    out_of_stock_count = Product.objects.filter(stock=0).count()
    approved_payments = Order.objects.filter(payment_status=Order.PAYMENT_APPROVED).count()
    status_counts = Order.objects.values("status").annotate(total=Count("id")).order_by("status")
    low_stock = Product.objects.filter(stock__lte=5, stock__gt=0).select_related("brand", "category")[:8]
    monthly = (
        Order.objects.filter(payment_status=Order.PAYMENT_APPROVED)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("grand_total"), orders=Count("id"))
        .order_by("month")
    )
    category_distribution = Category.objects.filter(is_active=True).annotate(total=Count("products")).order_by("name")
    country_distribution = (
        Order.objects.exclude(visitor_country__isnull=True)
        .exclude(visitor_country__exact="")
        .values("visitor_country")
        .annotate(total=Count("id"))
        .order_by("-total")[:8]
    )
    top_products = (
        OrderItem.objects.values("product_name")
        .annotate(total_sold=Sum("quantity"), revenue=Sum("line_total"))
        .order_by("-total_sold")[:6]
    )

    recent_customers = User.objects.order_by("-date_joined")[:6]
    activities = Notification.objects.select_related("user", "order")[:8]
    latest_reviews = ProductReview.objects.select_related("product", "user").filter(is_approved=True)[:6]
    users_count = User.objects.filter(is_staff=False, is_superuser=False).count()
    products_count = Product.objects.filter(is_active=True).count()
    
    db_status = "Operational"
    try:
        Order.objects.exists()
    except Exception:
        db_status = "Offline"
        
    uploads_status = "Operational"
    try:
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage
        path = default_storage.save("tmp_test.txt", ContentFile(b"test"))
        default_storage.delete(path)
    except Exception:
        uploads_status = "Offline"
        
    checkout_status = "Operational"
    try:
        from cart.models import Cart
        Cart.objects.exists()
    except Exception:
        checkout_status = "Offline"

    return render(
        request,
        "dashboard/index.html",
        {
            "revenue": revenue,
            "today_revenue": today_revenue,
            "orders_count": Order.objects.count(),
            "pending_orders": pending_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "products_count": products_count,
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "users_count": users_count,
            "categories_count": Category.objects.count(),
            "brands_count": Brand.objects.count(),
            "approved_payments": approved_payments,
            "recent_orders": Order.objects.prefetch_related("items")[:8],
            "recent_customers": recent_customers,
            "status_counts": status_counts,
            "low_stock": low_stock,
            "top_products": top_products,
            "activities": activities,
            "latest_reviews": latest_reviews,
            "monthly_labels": [row["month"].strftime("%b %Y") for row in monthly],
            "monthly_revenue": [float(row["total"] or 0) for row in monthly],
            "monthly_orders": [row["orders"] for row in monthly],
            "category_labels": [row.name for row in category_distribution],
            "category_counts": [row.total for row in category_distribution],
            "country_labels": [row["visitor_country"] for row in country_distribution],
            "country_counts": [row["total"] for row in country_distribution],
            "system_status": {"database": db_status, "checkout": checkout_status, "uploads": uploads_status},
        },
    )

from django.http import JsonResponse

@admin_required
def dashboard_stats_api(request):
    revenue = Order.objects.filter(payment_status=Order.PAYMENT_APPROVED).aggregate(total=Sum("grand_total"))["total"] or 0
    today = timezone.localdate()
    today_revenue = (
        Order.objects.filter(created_at__date=today, payment_status=Order.PAYMENT_APPROVED)
        .aggregate(total=Sum("grand_total"))["total"]
        or 0
    )
    pending_orders = Order.objects.filter(status=Order.PENDING).count()
    delivered_orders = Order.objects.filter(status=Order.DELIVERED).count()
    low_stock_count = Product.objects.filter(stock__lte=5, stock__gt=0).count()
    out_of_stock_count = Product.objects.filter(stock=0).count()
    users_count = User.objects.filter(is_staff=False, is_superuser=False).count()
    products_count = Product.objects.filter(is_active=True).count()
    
    monthly = (
        Order.objects.filter(payment_status=Order.PAYMENT_APPROVED)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("grand_total"), orders=Count("id"))
        .order_by("month")
    )
    category_distribution = Category.objects.filter(is_active=True).annotate(total=Count("products")).order_by("name")
    country_distribution = (
        Order.objects.exclude(visitor_country__isnull=True)
        .exclude(visitor_country__exact="")
        .values("visitor_country")
        .annotate(total=Count("id"))
        .order_by("-total")[:8]
    )

    return JsonResponse({
        "revenue": float(revenue),
        "today_revenue": float(today_revenue),
        "orders_count": Order.objects.count(),
        "pending_orders": pending_orders,
        "delivered_orders": delivered_orders,
        "users_count": users_count,
        "products_count": products_count,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "monthly_labels": [row["month"].strftime("%b %Y") for row in monthly],
        "monthly_revenue": [float(row["total"] or 0) for row in monthly],
        "monthly_orders": [row["orders"] for row in monthly],
        "category_labels": [row.name for row in category_distribution],
        "category_counts": [row.total for row in category_distribution],
        "country_labels": [row["visitor_country"] for row in country_distribution],
        "country_counts": [row["total"] for row in country_distribution]
    })



@admin_required
def product_list(request):
    products = Product.objects.select_related("brand", "category").prefetch_related("images")
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    brand = request.GET.get("brand", "")
    sort = request.GET.get("sort", "name")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query) | Q(brand__name__icontains=query))
    if category:
        products = products.filter(category_id=category)
    if brand:
        products = products.filter(brand_id=brand)
    products = products.order_by({"price": "price", "-price": "-price", "stock": "stock", "-created": "-created_at"}.get(sort, "name"))
    paginator = Paginator(products, 12)
    return render(request, "dashboard/products.html", {"page_obj": paginator.get_page(request.GET.get("page")), "categories": Category.objects.all(), "brands": Brand.objects.all(), "query": query, "active_category": category, "active_brand": brand, "sort": sort})


@admin_required
def product_form(request, product_id=None):
    product = get_object_or_404(Product, id=product_id) if product_id else None
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        urls = [line.strip() for line in form.cleaned_data.get("image_urls", "").splitlines() if line.strip()]
        existing_count = product.images.count()
        for index, url in enumerate(urls, start=existing_count):
            ProductImage.objects.create(product=product, image_url=url, alt_text=product.name, is_primary=not product.images.exists(), sort_order=index)
        for index, image in enumerate(form.cleaned_data.get("uploaded_images", []), start=product.images.count()):
            ProductImage.objects.create(product=product, image=image, alt_text=product.name, is_primary=not product.images.exists(), sort_order=index)
        messages.success(request, "Product saved successfully.")
        return redirect("dashboard:products")
    return render(request, "dashboard/product_form.html", {"form": form, "product": product})


@admin_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted.")
        return redirect("dashboard:products")
    return render(request, "dashboard/confirm_delete.html", {"object": product, "back_url": reverse("dashboard:products")})


@admin_required
def product_bulk_action(request):
    if request.method == "POST":
        ids = request.POST.getlist("selected")
        action = request.POST.get("action")
        queryset = Product.objects.filter(id__in=ids)
        if action == "delete":
            count = queryset.count()
            queryset.delete()
            messages.success(request, f"{count} products deleted.")
        elif action == "activate":
            messages.success(request, f"{queryset.update(is_active=True)} products activated.")
        elif action == "deactivate":
            messages.success(request, f"{queryset.update(is_active=False)} products deactivated.")
    return redirect("dashboard:products")


@admin_required
def taxonomy(request):
    category_form = CategoryForm(request.POST or None, prefix="category")
    brand_form = BrandForm(request.POST or None, prefix="brand")
    if request.method == "POST" and "save_category" in request.POST and category_form.is_valid():
        category_form.save()
        messages.success(request, "Category saved.")
        return redirect("dashboard:taxonomy")
    if request.method == "POST" and "save_brand" in request.POST and brand_form.is_valid():
        brand_form.save()
        messages.success(request, "Brand saved.")
        return redirect("dashboard:taxonomy")
    return render(request, "dashboard/taxonomy.html", {"category_form": category_form, "brand_form": brand_form, "categories": Category.objects.all(), "brands": Brand.objects.all()})


@admin_required
def order_list(request):
    orders = Order.objects.select_related("user").prefetch_related("items")
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    payment_status = request.GET.get("payment_status", "")
    if query:
        orders = orders.filter(Q(order_number__icontains=query) | Q(full_name__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query))
    if status:
        orders = orders.filter(status=status)
    if payment_status:
        orders = orders.filter(payment_status=payment_status)
    paginator = Paginator(orders, 12)
    return render(request, "dashboard/orders.html", {"page_obj": paginator.get_page(request.GET.get("page")), "query": query, "status": status, "payment_status": payment_status, "status_choices": Order.STATUS_CHOICES, "payment_status_choices": Order.PAYMENT_STATUS_CHOICES})


@admin_required
def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.select_related("user").prefetch_related("items"), id=order_id)
    form = OrderNoteForm(request.POST or None, instance=order)
    if request.method == "POST" and request.POST.get("action") == "save_notes" and form.is_valid():
        form.save()
        messages.success(request, "Internal notes saved.")
        return redirect("dashboard:order_detail", order_id=order.id)
    return render(request, "dashboard/order_detail.html", {"order": order, "form": form})


@admin_required
def order_action(request, order_id, action):
    order = get_object_or_404(Order, id=order_id)
    actions = {
        "approve-payment": (Order.PAYMENT_APPROVED, Order.CONFIRMED, "Payment Approved", "Your payment has been approved and your order is confirmed."),
        "reject-payment": (Order.PAYMENT_REJECTED, Order.CANCELLED, "Payment Rejected", "Payment was rejected and the order has been cancelled."),
        "processing": (None, Order.PROCESSING, "Order Processing", "Your order is now being prepared."),
        "shipped": (None, Order.SHIPPED, "Order Shipped", "Your order has been shipped."),
        "delivered": (None, Order.DELIVERED, "Order Delivered", "Your order has been delivered."),
        "cancel": (None, Order.CANCELLED, "Order Cancelled", "Your order has been cancelled."),
    }
    if request.method == "POST" and action in actions:
        payment_status, status, title, message = actions[action]
        if payment_status:
            order.payment_status = payment_status
        order.status = status
        order.updated_at = timezone.now()
        order.save()
        OrderEvent.objects.create(order=order, title=title, description=message, status=order.status)
        notify_order_customer(order, title, message)
        messages.success(request, f"{order.order_number}: {title}.")
    return redirect("dashboard:order_detail", order_id=order.id)


@admin_required
def customer_list(request):
    users = User.objects.filter(is_staff=False, is_superuser=False).select_related("profile").annotate(order_count=Count("orders")).order_by("-date_joined")
    query = request.GET.get("q", "").strip()
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
    paginator = Paginator(users, 16)
    return render(request, "dashboard/customers.html", {"page_obj": paginator.get_page(request.GET.get("page")), "query": query})


@admin_required
def settings_page(request):
    return render(
        request,
        "dashboard/settings.html",
        {
            "settings_groups": [
                ("Store", "CA-Tech Electronics storefront, checkout, and catalog configuration."),
                ("Payments", "Cash on delivery approval workflow and payment status controls."),
                ("Security", "Role based dashboard access and staff-only management permissions."),
                ("Notifications", "Customer notifications for order and payment status updates."),
            ]
        },
    )


@admin_required
def ai_settings(request):
    settings_obj = AISettings.load()
    form = AISettingsForm(request.POST or None, instance=settings_obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "AI settings saved.")
        return redirect("dashboard:ai_settings")
    conversations = AIConversation.objects.annotate(message_count=Count("messages")).order_by("-last_message_at")[:12]
    voice_logs = AIVoiceLog.objects.select_related("conversation", "user").order_by("-created_at")[:12]
    return render(
        request,
        "dashboard/ai_settings.html",
        {
            "form": form,
            "conversations": conversations,
            "voice_logs": voice_logs,
            "settings_obj": settings_obj,
        },
    )
