from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task
from apps.comments.models import Comment
from .serializers import TaskSerializer, CommentSerializer
from .services import AITaskService, TaskService
import logging

logger = logging.getLogger(__name__)

class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Tasks supporting Kanban operations and AI endpoints.
    """
    queryset = Task.objects.prefetch_related('tags', 'checklists', 'assignments__user').all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.request.query_params.get('project')
        if project_id:
            return self.queryset.filter(project_id=project_id)
        return self.queryset

    def list(self, request, *args, **kwargs):
        project_id = request.query_params.get('project')
        queryset = self.filter_queryset(self.get_queryset())
        
        if project_id and not queryset.exists():
            from apps.projects.models import Project, Board
            try:
                project = Project.objects.get(id=project_id)
                board = Board.objects.filter(project=project).first()
                if board:
                    todo_col = board.columns.filter(title="To Do").first()
                    inprog_col = board.columns.filter(title="In Progress").first()
                    if todo_col:
                        Task.objects.create(project=project, column=todo_col, title="Setup Project Infrastructure", status=str(todo_col.id))
                        Task.objects.create(project=project, column=todo_col, title="Design Database Schema", status=str(todo_col.id))
                    if inprog_col:
                        Task.objects.create(project=project, column=inprog_col, title="Develop Authentication API", status=str(inprog_col.id))
                queryset = self.queryset.filter(project_id=project_id)
            except Project.DoesNotExist:
                pass

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def generate_ai_plan(self, request, pk=None):
        """Trigger AI generation for subtasks (Connects to AIGeneratorModal)"""
        prompt = request.data.get('prompt', '')
        if not prompt:
            return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        items = AITaskService.generate_subtasks(task_id=pk, prompt=prompt)
        return Response({
            "status": "success", 
            "message": "AI Generation Complete", 
            "items_created": len(items)
        })

    @action(detail=True, methods=['get'])
    def risk_analysis(self, request, pk=None):
        """Get AI predictive risk analysis"""
        analysis = AITaskService.predict_risk(task_id=pk)
        return Response(analysis)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Fast endpoint used heavily by the drag-and-drop Kanban frontend"""
        new_status = request.data.get('status')
        if not new_status:
            return Response({"error": "Status required"}, status=status.HTTP_400_BAD_REQUEST)
            
        task = TaskService.move_task(task_id=pk, new_status=new_status, user_id=request.user.id)
        serializer = self.get_serializer(task)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    """
    Handles real-time comments creation connected to the TaskComments UI.
    """
    queryset = Comment.objects.select_related('author').all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically attach the logged-in user as the author
        serializer.save(author=self.request.user)
