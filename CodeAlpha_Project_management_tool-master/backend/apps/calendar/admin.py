from django.contrib import admin
from .models import CalendarEvent, Reminder

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    pass

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    pass

