"""Custom permissions for visualshark."""

from rest_framework import permissions


class CustomPermission(permissions.BasePermission):
    """Define custom permissions for visualSHARK.

    We want to be able to limit view_commits, view_issues etc.
    """

    def has_permission(self, request, view):
        """Check if given View objects requires a specific permission and checks if the user has it."""
        try:
            read_perm = view.read_perm
        except AttributeError:
            read_perm = 'NO'

        try:
            write_perm = view.write_perm
        except AttributeError:
            write_perm = 'NO'

        if request.method in permissions.SAFE_METHODS:
            return request.user.has_perm('visualSHARK.' + read_perm)
        else:
            return request.user.has_perm('visualSHARK.' + write_perm)
