from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Project, ProjectMember, ProjectActivity
from .serializers import ProjectSerializer, ProjectMemberSerializer, ProjectActivitySerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        workspace = self.request.query_params.get('workspace')
        if workspace:
            queryset = queryset.filter(workspace_id=workspace)
        return queryset

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        project = self.get_object()
        project.soft_delete()
        return Response({"status": "Project archived successfully"})

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        project = Project.all_objects.get(pk=pk)
        project.restore()
        return Response({"status": "Project restored successfully"})

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        project = self.get_object()
        project.pk = None
        project.name = f"{project.name} (Copy)"
        project.status = 'planning'
        project.is_template = False
        project.save()
        serializer = self.get_serializer(project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        project = self.get_object()
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        from apps.users.models import User
        try:
            user = User.objects.get(email=email)
            # Add to ProjectMember
            ProjectMember.objects.get_or_create(project=project, user=user)
            # Also ensure they are in the workspace
            from apps.organizations.models import WorkspaceMember
            WorkspaceMember.objects.get_or_create(workspace=project.workspace, user=user)
            return Response({"status": f"Project shared with {email}"})
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        from django.db.models import Count, Sum, Avg, Q
        project = self.get_object()
        
        # Basic task completion metrics
        tasks = project.tasks.all()
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='done').count() # Needs dynamic column logic in a real env
        
        # Time tracking
        estimated_time = tasks.aggregate(Sum('estimated_time'))['estimated_time__sum'] or 0
        actual_time = tasks.aggregate(Sum('actual_time'))['actual_time__sum'] or 0
        
        # Productivity (velocity simulation)
        team_productivity = project.members.annotate(
            completed_tasks=Count('user__assigned_tasks', filter=Q(user__assigned_tasks__task__project=project))
        ).values('user__email', 'completed_tasks')

        report = {
            "project_name": project.name,
            "progress_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "task_completion": f"{completed_tasks}/{total_tasks}",
            "time_tracking": {
                "estimated_hours": estimated_time,
                "actual_hours": actual_time,
                "difference": estimated_time - actual_time
            },
            "team_productivity": list(team_productivity)
        }
        
        # Mock export handlers
        export_format = request.query_params.get('export')
        if export_format in ['pdf', 'csv', 'excel']:
            return Response({"status": f"Exported to {export_format.upper()}", "url": f"https://cdn.nexus.com/exports/{project.id}.{export_format}"})
            
        return Response(report)

class ProjectMemberViewSet(viewsets.ModelViewSet):
    queryset = ProjectMember.objects.all()
    serializer_class = ProjectMemberSerializer
    permission_classes = [IsAuthenticated]

class ProjectActivityViewSet(viewsets.ModelViewSet):
    queryset = ProjectActivity.objects.all()
    serializer_class = ProjectActivitySerializer
    permission_classes = [IsAuthenticated]

from .models import Board, Column
from .serializers import BoardSerializer, ColumnSerializer

class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.prefetch_related('columns').all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project = self.request.query_params.get('project')
        if project:
            return self.queryset.filter(project_id=project)
        return self.queryset

    def list(self, request, *args, **kwargs):
        project_id = request.query_params.get('project')
        queryset = self.filter_queryset(self.get_queryset())
        
        if project_id and not queryset.exists():
            from .models import Project, Board, Column
            try:
                project = Project.objects.get(id=project_id)
                board = Board.objects.create(project=project, name="Main Kanban Board")
                Column.objects.create(board=board, title="To Do", color="bg-slate-500", order=1)
                Column.objects.create(board=board, title="In Progress", color="bg-blue-500", order=2)
                Column.objects.create(board=board, title="Review", color="bg-purple-500", order=3)
                Column.objects.create(board=board, title="Completed", color="bg-emerald-500", order=4)
                queryset = self.queryset.filter(project_id=project_id)
            except Project.DoesNotExist:
                pass
                
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ColumnViewSet(viewsets.ModelViewSet):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        board = self.request.query_params.get('board')
        if board:
            return self.queryset.filter(board_id=board)
        return self.queryset
