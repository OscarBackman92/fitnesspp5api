from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to allow only the owner of an object to edit or delete it.
    Other users can only read the object.
    """

    def has_object_permission(self, request, view, obj):
        # Read-only permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check for owner field first (used by Workout model)
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
            
        # Check for user field next (used by UserProfile and other models)
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        return False


class IsCurrentUserOrReadOnly(BasePermission):
    """
    Custom permission for UserProfile to ensure only the profile owner
    can edit their own profile. Other users have read-only access.
    """

    def has_object_permission(self, request, view, obj):
        # Allow read-only access for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow write access only to the owner of the profile
        return hasattr(obj, 'user') and obj.user == request.user