from rest_framework import permissions


class CreateUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.user_type == 1:
            return True
        return False



