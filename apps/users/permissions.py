# ============================================================================
# apps/users/permissions.py
# ============================================================================

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj == request.user


class IsModerator(permissions.BasePermission):
    """
    Permission class for moderator and admin users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.role in ['moderator', 'admin']