from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework import permissions
from server.models import PointsSale
from rest_framework.exceptions import APIException
from rest_framework import status


class CreateUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.user_type == 'Администрация':
            return True
        return False


class IsSudovoditel(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated and user.user_type == 'Судоводитель':
            return True
        else:
            raise PermissionDenied({"Сообщение": "Доступ запрещен. Требуется должность 'Судоводитель'."})


class IsOperator(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 'Оператор':
            operator = request.user
            current_date = timezone.now().date()
            points_sale = PointsSale.objects.filter(
                operator=operator, create_data=current_date, status='Открытая смена'
            ).first()
            if not points_sale:
                raise PermissionDenied('Невозможно создать билет. Смена не открыта.')
            return True
        raise PermissionDenied('Требуется авторизация оператора.')


class AdminOnlyPermission(permissions.BasePermission):
    message = 'Доступ запрещен. Доступно для Администрации.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated or request.user.user_type != 'Администрация':
            raise PermissionDenied(self.message)
        return True