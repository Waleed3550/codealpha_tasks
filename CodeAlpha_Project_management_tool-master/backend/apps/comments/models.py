from django.db import models
from core.models import BaseModel
from apps.users.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Comment(BaseModel):
    """
    Polymorphic comment model that can attach to Tasks, Projects, or Files.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    
    def __str__(self):
        return f"Comment by {self.author.email}"

class Reply(BaseModel):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    
    def __str__(self):
        return f"Reply to {self.comment.id} by {self.author.email}"

class Reaction(BaseModel):
    """
    Polymorphic reactions for Comments or Replies.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    emoji = models.CharField(max_length=50) # Stores unicode or string like :smile:
    
    class Meta:
        unique_together = ('content_type', 'object_id', 'user', 'emoji')
        
    def __str__(self):
        return f"{self.user.email} reacted {self.emoji}"
