from rest_framework import permissions

class IsSelfOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow users to edit their own profile, unless they are admin.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # For Profile model, check obj.user. For User model, check obj.id
        user_id = obj.user.id if hasattr(obj, 'user') else obj.id
        return user_id == request.user.id or request.user.is_staff
