from django.db import models
import uuid

class AuditLog(models.Model):
    """
    Immutable audit trail for compliance. 
    Does not inherit from BaseModel because audit logs should never be modified or soft-deleted.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=36, null=True, blank=True) # Weak reference to avoid FK constraints
    action = models.CharField(max_length=255) # e.g. CREATE, UPDATE, DELETE
    resource_type = models.CharField(max_length=100) # e.g. Task, User
    resource_id = models.CharField(max_length=36)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']

class SystemLog(models.Model):
    """
    Application level errors and system events.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    level = models.CharField(max_length=20) # INFO, WARNING, ERROR, CRITICAL
    message = models.TextField()
    traceback = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
