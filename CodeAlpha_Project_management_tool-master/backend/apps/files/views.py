from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Attachment
from .serializers import AttachmentSerializer
from django.db.models import Sum

class AttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_superuser', False):
            return Attachment.objects.all()
        # Return files uploaded by anyone in the same workspace
        return Attachment.objects.filter(uploader__workspace_memberships__workspace__members__user=user).distinct()

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        total_size = Attachment.objects.filter(uploader=request.user).aggregate(Sum('file_size'))['file_size__sum'] or 0
        total_files = Attachment.objects.filter(uploader=request.user).count()
        return Response({
            "total_size_bytes": total_size,
            "total_files": total_files,
            "storage_limit_bytes": 5 * 1024 * 1024 * 1024 # 5GB Example limit
        })

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        attachment = Attachment.all_objects.get(pk=pk)
        attachment.restore()
        return Response({"status": "File restored successfully"})

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        attachment = self.get_object()
        # Find all attachments with the same parent
        if attachment.parent_attachment:
            versions = Attachment.objects.filter(parent_attachment=attachment.parent_attachment)
        else:
            versions = Attachment.objects.filter(parent_attachment=attachment)
        serializer = self.get_serializer(versions, many=True)
        return Response(serializer.data)

