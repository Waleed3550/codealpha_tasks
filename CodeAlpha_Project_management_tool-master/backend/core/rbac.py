import logging
from rest_framework import permissions, filters
from django.db.models import Q
from apps.organizations.models import WorkspaceMember, Organization, Workspace, Team, Role
from apps.projects.models import Project, ProjectMember
from apps.tasks.models import Task
from apps.users.models import User

logger = logging.getLogger(__name__)

def get_workspace_for_obj(obj):
    if hasattr(obj, 'workspace'):
        return obj.workspace
    if hasattr(obj, 'project') and hasattr(obj.project, 'workspace'):
        return obj.project.workspace
    if hasattr(obj, 'task') and hasattr(obj.task, 'project'):
        return obj.task.project.workspace
    if isinstance(obj, Workspace):
        return obj
    return None

def get_user_role(user, workspace):
    if user.is_superuser:
        return "Super Admin"
    if not workspace:
        if user.is_staff:
            return "Admin"
        return None
    try:
        member = WorkspaceMember.objects.select_related('role').get(user=user, workspace=workspace)
        if member.role:
            return member.role.name
        elif user.is_staff:
            return "Admin"
        return "Employee"  # Default
    except WorkspaceMember.DoesNotExist:
        if user.is_staff:
            return "Admin"
        return None

class RBACPermission(permissions.BasePermission):
    """
    Global RBAC Permission Class enforcing roles:
    1. Super Admin
    2. Admin
    3. Project Manager
    4. Team Lead
    5. Employee
    6. Client
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        # Admin cannot delete Super Admin, cannot transfer ownership
        # Handled in has_object_permission or specific views.
        
        # General creation limits (POST requests)
        if request.method == 'POST':
            model = getattr(getattr(view, 'queryset', None), 'model', None)
            if model == Organization or model == Workspace:
                return request.user.is_staff
            if model == Project:
                workspace_id = request.data.get('workspace')
                if workspace_id:
                    role = get_user_role(request.user, Workspace.objects.filter(id=workspace_id).first())
                    if role in ["Admin", "Project Manager"]:
                        return True
                    return False
                return request.user.is_staff
        
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True

        if isinstance(obj, User):
            if request.method in permissions.SAFE_METHODS:
                return True
            if obj.is_superuser and not user.is_superuser:
                return False
            return True
            
        from apps.users.models import Profile
        if isinstance(obj, Profile):
            if request.method in permissions.SAFE_METHODS:
                return True
            return obj.user == request.user or user.is_staff
            
        workspace = get_workspace_for_obj(obj)
        role = get_user_role(user, workspace)
        
        if not role:
            return False
            
        if role == "Admin":
            return True
            
        if role == "Client":
            if request.method not in permissions.SAFE_METHODS:
                return False
            if isinstance(obj, Project):
                return obj.members.filter(user=user).exists()
            if isinstance(obj, Task):
                return obj.project.members.filter(user=user).exists()
            return False
            
        if role == "Employee":
            if isinstance(obj, Project):
                return obj.members.filter(user=user).exists() and request.method in permissions.SAFE_METHODS
            if isinstance(obj, Task):
                if request.method in permissions.SAFE_METHODS:
                    return obj.project.members.filter(user=user).exists()
                return obj.assignments.filter(user=user).exists()
            return False
            
        if role == "Team Lead":
            if isinstance(obj, Project):
                return request.method in permissions.SAFE_METHODS and obj.members.filter(user=user).exists()
            if isinstance(obj, Task):
                return obj.project.members.filter(user=user).exists()
            if isinstance(obj, Team):
                return obj.members.filter(id=user.id).exists()
            return False
            
        if role == "Project Manager":
            if isinstance(obj, Project):
                return obj.members.filter(user=user).exists()
            if isinstance(obj, Task):
                return obj.project.members.filter(user=user).exists()
            if isinstance(obj, Team):
                return True 
                
        return False

class RBACFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.user
        if not user.is_authenticated:
            return queryset.none()
            
        if user.is_superuser:
            return queryset
            
        model = queryset.model
        
        if model == Organization:
            if user.is_staff:
                return queryset
            return queryset.filter(workspaces__members__user=user).distinct()
            
        if model == Workspace:
            if user.is_staff:
                return queryset
            return queryset.filter(members__user=user).distinct()
            
        if model == Project:
            if user.is_staff:
                return queryset
            return queryset.filter(members__user=user).distinct()
            
        if model == Task:
            if user.is_staff:
                return queryset
            return queryset.filter(project__members__user=user).distinct()
            
        if model == Team:
            if user.is_staff:
                return queryset
            return queryset.filter(workspace__members__user=user).distinct()
            
        return queryset
