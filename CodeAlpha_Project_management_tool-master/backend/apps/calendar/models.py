from django.db import models
from core.models import BaseModel
from apps.organizations.models import Workspace
from apps.users.models import User

class CalendarEvent(BaseModel):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='calendar_events')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    attendees = models.ManyToManyField(User, related_name='events', blank=True)
    
    def __str__(self):
        return self.title

class Reminder(BaseModel):
    event = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name='reminders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    remind_at = models.DateTimeField(db_index=True)
    is_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Reminder for {self.user.email} at {self.remind_at}"
