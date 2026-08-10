from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from apps.organizations.models import Organization, WorkspaceMember
from apps.projects.models import Project, ProjectActivity
from apps.tasks.models import Task
from apps.users.models import User
from django.db.models import Q

class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()

        # Get role for UI
        role = "Employee"
        if user.is_superuser:
            role = "Super Admin"
        else:
            member = WorkspaceMember.objects.filter(user=user).select_related('role').first()
            if member and member.role:
                role = member.role.name

        if user.is_superuser or role == "Super Admin":
            # Super Admin sees everything
            total_users = User.objects.count()
            org_count = Organization.objects.count()
            projects = Project.objects.all()
            tasks = Task.objects.all()
        elif role == "Admin":
            # Admin sees their orgs
            org_count = Organization.objects.filter(owner=user).count()
            total_users = WorkspaceMember.objects.filter(workspace__organization__owner=user).values('user').distinct().count()
            projects = Project.objects.filter(workspace__organization__owner=user)
            tasks = Task.objects.filter(project__workspace__organization__owner=user)
        elif role == "Project Manager":
            # Project manager sees assigned projects
            org_count = Organization.objects.filter(owner=user).count() # Just their own
            total_users = 0
            projects = Project.objects.filter(members__user=user).distinct()
            tasks = Task.objects.filter(project__in=projects)
        else:
            # Employee / Client
            org_count = 0
            total_users = 0
            projects = Project.objects.filter(workspace__members__user=user).distinct()
            tasks = Task.objects.filter(assignments__user=user)

        project_count = projects.count()
        active_projects = projects.exclude(status='completed').count()
        completed_projects = projects.filter(status='completed').count()
        
        task_count = tasks.count()
        completed_tasks = tasks.filter(status='done').count()
        pending_tasks = tasks.exclude(status='done').count()
        overdue_tasks = tasks.filter(due_date__lt=now.date(), status__in=['todo', 'in_progress']).count()
        todays_tasks = tasks.filter(due_date=now.date()).count()

        # Revenue Mock
        revenue = org_count * 99.00 if role in ["Super Admin", "Admin"] else 0.0

        # Recent Activities
        recent_activities = ProjectActivity.objects.filter(
            project__in=projects
        ).order_by('-created_at')[:5].values('id', 'action', 'created_at', 'project__name')

        # Upcoming Deadlines (Tasks)
        upcoming_tasks = tasks.filter(
            due_date__gte=now.date()
        ).order_by('due_date')[:5].values('id', 'title', 'due_date', 'priority', 'project__name')

        weekly_productivity = [12, 19, 15, 25, 22, 10, 18]

        data = {
            'user': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': role
            },
            'total_users': total_users,
            'organization_count': org_count,
            'project_count': project_count,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'task_count': task_count,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'overdue_tasks': overdue_tasks,
            'todays_tasks': todays_tasks,
            'revenue': revenue,
            'recent_activities': list(recent_activities),
            'upcoming_deadlines': list(upcoming_tasks),
            'weekly_productivity': weekly_productivity,
        }
        return Response(data)
