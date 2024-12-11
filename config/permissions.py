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
        # Write permissions are only allowed to the owner of the object
        return hasattr(obj, 'owner') and obj.owner == request.user


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
        return hasattr(obj, 'owner') and obj.owner == request.user
