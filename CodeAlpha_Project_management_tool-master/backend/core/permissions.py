from rest_framework import permissions
from core.roles import RoleEnum, ROLE_LEVELS
from apps.organizations.models import WorkspaceMember

class BaseRolePermission(permissions.BasePermission):
    required_level = 0
    
    def get_workspace_role_level(self, user, workspace_id):
        if user.is_superuser:
            return ROLE_LEVELS[RoleEnum.SUPER_ADMIN]
            
        try:
            member = WorkspaceMember.objects.select_related('role').get(user=user, workspace_id=workspace_id)
            if member.role and member.role.name in ROLE_LEVELS:
                return ROLE_LEVELS[member.role.name]
        except WorkspaceMember.DoesNotExist:
            pass
        return 0

    def has_permission(self, request, view):
        # Allow superusers by default
        if request.user and request.user.is_superuser:
            return True
            
        # Get workspace_id from URL kwargs or request data
        workspace_id = view.kwargs.get('workspace_pk') or request.data.get('workspace')
        
        if not workspace_id:
            # If endpoint isn't nested under workspace, fallback to basic auth check
            return request.user and request.user.is_authenticated

        user_level = self.get_workspace_role_level(request.user, workspace_id)
        return user_level >= self.required_level

class IsAdminOrHigher(BaseRolePermission):
    required_level = ROLE_LEVELS[RoleEnum.ADMIN]

class IsProjectManagerOrHigher(BaseRolePermission):
    required_level = ROLE_LEVELS[RoleEnum.PROJECT_MANAGER]

class IsTeamLeadOrHigher(BaseRolePermission):
    required_level = ROLE_LEVELS[RoleEnum.TEAM_LEAD]

class IsTeamMemberOrHigher(BaseRolePermission):
    required_level = ROLE_LEVELS[RoleEnum.TEAM_MEMBER]

class IsGuestOrHigher(BaseRolePermission):
    required_level = ROLE_LEVELS[RoleEnum.GUEST]
