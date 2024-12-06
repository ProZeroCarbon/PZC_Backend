from rest_framework.permissions import BasePermission

class IsNotAdmin(BasePermission):
    """
    Custom permission to deny access to admin users (superusers).
    """

    def has_permission(self, request, view):
        # Deny access if the user is an admin
        if request.user.is_authenticated and request.user.is_superuser:
            return False
        return True

class IsAdmin(BasePermission):
    """
    Custom permission to allow only admin (superuser) users.
    """

    def has_permission(self, request, view):
        # Grant permission only if the user is authenticated and a superuser
        return request.user.is_authenticated and request.user.is_superuser

