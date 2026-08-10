from django.contrib import admin
from django.utils.translation import ngettext
from django.contrib import messages
from orders.models import Notification, Order, OrderEvent, OrderItem, PaymentTransaction


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "sku", "quantity", "unit_price", "line_total")


class OrderEventInline(admin.TabularInline):
    model = OrderEvent
    extra = 0
    readonly_fields = ("title", "description", "status", "created_at")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "full_name", "status", "payment_status", "payment_method", "payment_gateway", "transaction_id", "grand_total", "created_at")
    list_filter = ("status", "payment_status", "payment_method", "payment_gateway", "created_at")
    search_fields = ("order_number", "full_name", "email", "phone", "transaction_id")
    inlines = [OrderItemInline, OrderEventInline]


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("order_number", "full_name", "payment_method", "payment_gateway", "transaction_id", "grand_total", "payment_status", "status", "created_at")
    list_filter = ("payment_status", "payment_method", "payment_gateway", "created_at")
    search_fields = ("order_number", "full_name", "email", "phone", "transaction_id")
    actions = ["approve_manual_payments", "reject_payments", "refund_payments", "download_reports"]

    @admin.action(description="Approve selected manual payments")
    def approve_manual_payments(self, request, queryset):
        updated = queryset.update(payment_status=Order.PAYMENT_APPROVED, status=Order.CONFIRMED)
        self.message_user(request, ngettext(
            '%d payment was successfully approved.',
            '%d payments were successfully approved.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description="Mark selected payments as rejected")
    def reject_payments(self, request, queryset):
        updated = queryset.update(payment_status=Order.PAYMENT_REJECTED)
        self.message_user(request, ngettext(
            '%d payment was marked as rejected.',
            '%d payments were marked as rejected.',
            updated,
        ) % updated, messages.WARNING)

    @admin.action(description="Refund selected payments")
    def refund_payments(self, request, queryset):
        updated = queryset.update(payment_status=Order.PAYMENT_REFUNDED, status=Order.CANCELLED)
        self.message_user(request, ngettext(
            '%d payment was marked as refunded.',
            '%d payments were marked as refunded.',
            updated,
        ) % updated, messages.INFO)

    @admin.action(description="Download Analytics & Reports (CSV)")
    def download_reports(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="payment_analytics_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Transaction ID', 'Payment Gateway', 'Customer', 'Email', 'Method', 'Total', 'Payment Status', 'Date'])
        for order in queryset:
            writer.writerow([order.transaction_id or order.order_number, order.payment_gateway, order.full_name, order.email, order.payment_method, order.grand_total, order.payment_status, order.created_at])
        return response


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "order", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("title", "message", "user__username", "order__order_number")


@admin.register(OrderEvent)
class OrderEventAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order__order_number", "title", "description")
