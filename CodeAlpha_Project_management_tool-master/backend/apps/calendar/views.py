from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CalendarEvent, Reminder
from .serializers import CalendarEventSerializer, ReminderSerializer

class CalendarEventViewSet(viewsets.ModelViewSet):
    queryset = CalendarEvent.objects.all()
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_superuser', False):
            return self.queryset
        return self.queryset.filter(workspace__members__user=user).distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        if not queryset.exists():
            # Auto-create demo calendar events linked to an existing user and workspace
            from apps.organizations.models import WorkspaceMember
            member = WorkspaceMember.objects.filter(user=request.user).first()
            if member:
                from django.utils import timezone
                from datetime import timedelta
                now = timezone.now()
                
                # Create demo events
                CalendarEvent.objects.create(
                    workspace=member.workspace,
                    title="Q3 Roadmap Planning",
                    start_time=now.replace(hour=10, minute=0, second=0, microsecond=0),
                    end_time=now.replace(hour=11, minute=30, second=0, microsecond=0)
                )
                CalendarEvent.objects.create(
                    workspace=member.workspace,
                    title="Design Sync",
                    start_time=(now + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0),
                    end_time=(now + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0)
                )
                CalendarEvent.objects.create(
                    workspace=member.workspace,
                    title="Weekly Team Standup",
                    start_time=(now - timedelta(days=1)).replace(hour=9, minute=30, second=0, microsecond=0),
                    end_time=(now - timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
                )
                
                # Re-fetch queryset
                queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]

