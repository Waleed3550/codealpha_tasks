from django.contrib import admin
from .models import AuditLog, SystemLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    pass

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    pass

