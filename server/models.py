from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from server.manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'Оператор'
        verbose_name_plural = 'Операторы'

    username = models.CharField(max_length=255, unique=True, verbose_name='Логин')
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Фамилия')
    inn = models.CharField(max_length=12, blank=True, null=True, unique=True, verbose_name='ИИН')
    is_active = models.BooleanField(default=False, verbose_name='Активный')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал', editable=False)
    is_superuser = models.BooleanField(default=False, verbose_name='Админ')
    password = models.CharField(max_length=128, editable=False, verbose_name='Пароль')

    USERNAME_FIELD = 'username'
    objects = UserManager()

    def __str__(self):
        return self.username

