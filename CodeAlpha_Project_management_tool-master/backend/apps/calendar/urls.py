from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CalendarEventViewSet, ReminderViewSet

router = DefaultRouter()
router.register(r'calendarevents', CalendarEventViewSet, basename='calendarevent')
router.register(r'reminders', ReminderViewSet, basename='reminder')

urlpatterns = [
    path('', include(router.urls)),
]
