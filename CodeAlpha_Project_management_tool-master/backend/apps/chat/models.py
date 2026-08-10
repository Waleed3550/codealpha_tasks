from django.db import models
from core.models import BaseModel
from apps.organizations.models import Workspace
from apps.users.models import User

class ChatRoom(BaseModel):
    ROOM_TYPES = (
        ('direct', 'Direct Message'),
        ('group', 'Group Chat'),
        ('project', 'Project Chat'),
        ('organization', 'Organization Chat'),
    )
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='chat_rooms')
    name = models.CharField(max_length=255)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='group')
    is_private = models.BooleanField(default=False)
    members = models.ManyToManyField(User, related_name='chat_rooms', blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.room_type})"

class Message(BaseModel):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    content = models.TextField()
    is_edited = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message by {self.sender.email} in {self.room.name}"

class MessageReaction(BaseModel):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=50)

    class Meta:
        unique_together = ('message', 'user', 'emoji')

class ReadReceipt(BaseModel):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_receipts')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user')
