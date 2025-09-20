from rest_framework import permissions

class IsMasterAdminOrDeptAdmin(permissions.BasePermission):
    """
    Custom permission to only allow master_admin or dept_admin users to access.
    """
    def has_permission(self, request, view):
        # Return None to let authentication handle 401 for unauthenticated
        if not request.user or not request.user.is_authenticated:
            return None
        # Only allow master_admin or dept_admin
        if request.user.role == 'master_admin' or request.user.role == 'dept_admin':
            return True
        # Authenticated but forbidden role: 403
        return False

class IsMasterAdmin(permissions.BasePermission):
    """
    Custom permission to only allow master_admin users to access.
    """
    def has_permission(self, request, view):
        # Return None to let authentication handle 401 for unauthenticated
        if not request.user or not request.user.is_authenticated:
            return None
        # Only allow master_admin
        if request.user.role == 'master_admin':
            return True
        # Authenticated but forbidden role: 403
        return False