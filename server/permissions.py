from rest_framework.exceptions import PermissionDenied
from rest_framework import permissions


class CreateUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.user_type == 1:
            return True
        return False


class IsSudovoditel(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated and user.user_type == 3:
            return True
        else:
            raise PermissionDenied("Доступ запрещен. Требуется должность 'Судоводитель'.")
