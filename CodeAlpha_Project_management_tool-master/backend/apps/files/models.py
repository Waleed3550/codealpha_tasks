from django.db import models
from core.models import BaseModel
from apps.users.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Attachment(BaseModel):
    """
    Polymorphic attachment model capable of attaching to any other model 
    (Tasks, Projects, ChatMessages, etc).
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    file = models.FileField(upload_to='attachments/%Y/%m/')
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100)
    
    # Phase 2 Fields
    version = models.PositiveIntegerField(default=1)
    parent_attachment = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='versions')
    
    def __str__(self):
        return f"{self.file_name} (v{self.version})"
