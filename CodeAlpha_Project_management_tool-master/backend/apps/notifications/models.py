from django.db import models
from core.models import BaseModel
from apps.users.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(BaseModel):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='notifications_triggered')
    
    verb = models.CharField(max_length=255) # e.g. "assigned you to", "commented on"
    
    # Generic relation to the object causing the notification (Task, Comment, etc)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.UUIDField(null=True, blank=True)
    target = GenericForeignKey('content_type', 'object_id')
    
    is_read = models.BooleanField(default=False, db_index=True)
    
    def __str__(self):
        return f"Notification for {self.recipient.email}: {self.verb}"
