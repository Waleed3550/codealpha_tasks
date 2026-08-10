from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer

class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_superuser', False):
            return ChatRoom.objects.all()
        return ChatRoom.objects.filter(workspace__members__user=user).distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        if not queryset.exists():
            from apps.organizations.models import Workspace, WorkspaceMember
            user = request.user
            
            # Find a valid workspace for the user (or any workspace if superuser)
            if getattr(user, 'is_superuser', False):
                workspace = Workspace.objects.first()
            else:
                member = WorkspaceMember.objects.filter(user=user).first()
                if not member:
                    # Auto-create workspace if the user has none
                    from apps.organizations.models import Organization, Role
                    org = Organization.objects.create(name=f"{user.first_name or user.username}'s Organization", owner=user)
                    workspace = Workspace.objects.create(organization=org, name="My First Workspace")
                    admin_role = Role.objects.create(workspace=workspace, name="Admin", permissions={"all": True})
                    member = WorkspaceMember.objects.create(workspace=workspace, user=user, role=admin_role)
                
                workspace = member.workspace
                
            if workspace:
                # Create demo rooms
                ChatRoom.objects.create(workspace=workspace, name="general", room_type="group")
                ChatRoom.objects.create(workspace=workspace, name="engineering", room_type="group")
                ChatRoom.objects.create(workspace=workspace, name="random", room_type="group")
                
                # Re-fetch
                queryset = self.filter_queryset(self.get_queryset())
                
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Message.objects.all()
        room = self.request.query_params.get('room')
        if room:
            queryset = queryset.filter(room_id=room)
        return queryset.order_by('created_at')

from .models import MessageReaction, ReadReceipt
from .serializers import MessageReactionSerializer, ReadReceiptSerializer

class MessageReactionViewSet(viewsets.ModelViewSet):
    queryset = MessageReaction.objects.all()
    serializer_class = MessageReactionSerializer
    permission_classes = [IsAuthenticated]

class ReadReceiptViewSet(viewsets.ModelViewSet):
    queryset = ReadReceipt.objects.all()
    serializer_class = ReadReceiptSerializer
    permission_classes = [IsAuthenticated]
