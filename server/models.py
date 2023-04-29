from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from server.element_select import USER_TYPE, CHILD_OR_ABULT
from server.manager import UserManager
from django.utils import timezone
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
from datetime import datetime


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'Оператор'
        verbose_name_plural = 'Операторы'

    username = models.CharField(max_length=255, unique=True, verbose_name='Логин')
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Фамилия')
    inn = models.CharField(max_length=12, blank=True, null=True, unique=True, verbose_name='ИИН')
    user_type = models.CharField(max_length=6, choices=USER_TYPE, verbose_name='Должность', default=2)
    is_active = models.BooleanField(default=False, verbose_name='Активный')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал', editable=False)
    is_superuser = models.BooleanField(default=False, verbose_name='Админ')
    password = models.CharField(max_length=128, editable=False, verbose_name='Пароль')
    date_of_registration = models.DateTimeField(auto_now=True, verbose_name='Дата регистрации', null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='Последний вход')
    last_logout = models.DateTimeField(null=True, blank=True, verbose_name='Последний выход')

    USERNAME_FIELD = 'username'
    objects = UserManager()

    def update_last_login(self):
        self.last_login = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.username}"


class Price(models.Model):
    class Meta:
        verbose_name = 'Стоимость Билета'
        verbose_name_plural = 'Стоимости Билетов'

    price = models.DecimalField(verbose_name='Стоимость', decimal_places=2, max_digits=12)

    def __str__(self):
        return f"{self.price}"


class PriceTypes(models.Model):
    class Meta:
        verbose_name = 'Тип цен'
        verbose_name_plural = 'Типы цен'

    client_type = models.CharField(max_length=10, choices=CHILD_OR_ABULT, verbose_name='Тип клиента')
    price = models.OneToOneField(Price, on_delete=models.PROTECT, verbose_name='Стоимость')

    def __str__(self):
        return f"{self.client_type}"


class Tickets(models.Model):
    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'

    operator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Оператор')
    price_types = models.OneToOneField(PriceTypes, on_delete=models.PROTECT, verbose_name='Тип цен')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    bought = models.BooleanField(default=False, verbose_name='Куплен')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True, verbose_name='QR-код')

    def save(self, *args, **kwargs):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(f'{self.pk}-{self.operator}-{self.price_types.client_type}-{self.created_at}')
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer)
        filename = f'qr_code_{self.pk}.png'
        file = ContentFile(buffer.getvalue())
        self.qr_code.save(filename, file, save=False)
        buffer.close()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.operator}"


class LandingPlaces(models.Model):
    class Meta:
        verbose_name = 'Посадочное место'
        verbose_name_plural = 'Посадочные места'

    address = models.CharField(max_length=100, verbose_name='адрес')

    def __str__(self):
        return f"{self.address}"


class PointsSale(models.Model):
    class Meta:
        verbose_name = 'Точка продажи'
        verbose_name_plural = 'Точки продажи'

    operator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Оператор')
    landing_places = models.ManyToManyField(LandingPlaces, verbose_name='Посадочное место')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    left_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата выхода')

    def __str__(self):
        return f"{self.landing_places}"


