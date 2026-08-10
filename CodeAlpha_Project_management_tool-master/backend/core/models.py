import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class SoftDeleteManager(models.Manager):
    """
    Manager that automatically filters out soft-deleted objects.
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class BaseModel(models.Model):
    """
    Abstract base model that implements enterprise standards:
    - UUID primary key
    - Audit timestamps (created_at, updated_at)
    - Soft delete (deleted_at, is_active)
    - User tracking (created_by, updated_by)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    # We use strings for lazy evaluation of the User model to avoid circular imports
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated"
    )
    is_active = models.BooleanField(default=True, db_index=True)

    # Default manager ignores soft-deleted items
    objects = SoftDeleteManager()
    # Manager to access everything including soft-deleted items
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        """Soft deletes the object."""
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['deleted_at', 'is_active'])
        
    def restore(self):
        """Restores a soft-deleted object."""
        self.deleted_at = None
        self.is_active = True
        self.save(update_fields=['deleted_at', 'is_active'])
