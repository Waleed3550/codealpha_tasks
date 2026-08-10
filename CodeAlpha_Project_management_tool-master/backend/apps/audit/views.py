from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import AuditLog, SystemLog
from .serializers import AuditLogSerializer, SystemLogSerializer

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

class SystemLogViewSet(viewsets.ModelViewSet):
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    permission_classes = [IsAuthenticated]

