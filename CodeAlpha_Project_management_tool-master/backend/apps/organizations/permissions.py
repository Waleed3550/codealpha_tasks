from rest_framework import permissions

class IsOrganizationOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an organization or system superadmins to edit, delete, or archive it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write, Delete, or Archive permissions are restricted to the owner or superadmin
        return request.user == obj.owner or request.user.is_superuser
