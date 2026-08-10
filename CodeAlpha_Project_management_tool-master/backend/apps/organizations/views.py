from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Organization, Workspace, Team, Role
from .serializers import OrganizationSerializer, WorkspaceSerializer, TeamSerializer, RoleSerializer
from .permissions import IsOrganizationOwnerOrAdmin

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsOrganizationOwnerOrAdmin]

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        org = self.get_object()
        org.soft_delete()
        return Response({"status": "Organization archived successfully"})

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        # Must query all_objects since soft_deleted items are hidden by default manager
        org = Organization.all_objects.get(pk=pk)
        org.restore()
        return Response({"status": "Organization restored successfully"})

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        org = self.get_object()
        stats = {
            "workspaces_count": org.workspaces.count(),
            "teams_count": Team.objects.filter(workspace__organization=org).count(),
            "roles_count": Role.objects.filter(workspace__organization=org).count(),
        }
        return Response(stats)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        org = self.get_object()
        # Retrieve members across all workspaces in the org
        # In a real enterprise app, we'd serialize User objects via a UserSerializer
        members = list(org.workspaces.values_list('members__user__email', flat=True).distinct())
        return Response({"members": [m for m in members if m]})

class WorkspaceViewSet(viewsets.ModelViewSet):
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_superuser', False):
            return self.queryset
        return self.queryset.filter(members__user=user).distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        if not queryset.exists():
            user = request.user
            from apps.organizations.models import Organization, WorkspaceMember, Role
            org = Organization.objects.create(name=f"{user.first_name or user.username}'s Organization", owner=user)
            workspace = Workspace.objects.create(organization=org, name="My First Workspace")
            admin_role = Role.objects.create(workspace=workspace, name="Admin", permissions={"all": True})
            WorkspaceMember.objects.create(workspace=workspace, user=user, role=admin_role)
            queryset = self.filter_queryset(self.get_queryset())
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = self.request.user
        from apps.organizations.models import Organization, WorkspaceMember, Role
        
        # Find or create an organization for this user
        org = Organization.objects.filter(owner=user).first()
        if not org:
            org = Organization.objects.create(name=f"{user.first_name or user.username}'s Organization", owner=user)
            
        workspace = serializer.save(organization=org)
        
        # Make the creator an Admin member
        admin_role, _ = Role.objects.get_or_create(workspace=workspace, name="Admin", defaults={"permissions": {"all": True}})
        WorkspaceMember.objects.create(workspace=workspace, user=user, role=admin_role)

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

