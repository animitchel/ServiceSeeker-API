from rest_framework import permissions


class IsNotAuthenticated(permissions.BasePermission):
    """
    Custom permission to only allow non-authenticated
    users to access the view.
    """

    def has_permission(self, request, view):
        return not request.user.is_authenticated
