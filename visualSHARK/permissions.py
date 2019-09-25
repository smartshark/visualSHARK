from rest_framework import permissions

class CustomPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        try:
            read_perm = view.read_perm
        except AttributeError:
            read_perm = 'NO'
        try:
            write_perm = view.write_perm
        except AttributeError:
            write_perm = read_perm
        if request.method in permissions.SAFE_METHODS:
            return request.user.has_perm(read_perm)
        else:
            return request.user.has_perm(write_perm)