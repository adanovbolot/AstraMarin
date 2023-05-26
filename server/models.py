from datetime import date
from django.core.exceptions import ValidationError
from django.contrib.auth import logout
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from server.element_select import USER_TYPE, CHILD_OR_ABULT, SHIFT_STATUS
from server.manager import UserManager
from django.utils import timezone


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'Оператор'
        verbose_name_plural = 'Операторы'

    username = models.CharField(max_length=255, unique=True, verbose_name='Логин')
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Фамилия')
    inn = models.CharField(max_length=12, blank=True, null=True, unique=True, verbose_name='ИИН')
    user_type = models.CharField(max_length=13, choices=USER_TYPE, verbose_name='Должность', default=2)
    is_active = models.BooleanField(default=False, verbose_name='Активный')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')
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
        ordering = ('price',)

    price = models.DecimalField(
        verbose_name='Стоимость',
        decimal_places=2,
        max_digits=12,
        unique=True
    )

    def __str__(self):
        return f"стоимость -- {self.price}"


class PriceTypes(models.Model):
    class Meta:
        verbose_name = 'Тип цен'
        verbose_name_plural = 'Типы цен'
        ordering = ('price',)

    client_type = models.CharField(
        max_length=10,
        choices=CHILD_OR_ABULT,
        verbose_name='Тип клиента',
        unique=True
    )
    price = models.OneToOneField(
        Price,
        on_delete=models.PROTECT,
        verbose_name='Стоимость',
        unique=True
    )

    def __str__(self):
        return f"{self.client_type} {self.price}"


class Berths(models.Model):
    class Meta:
        verbose_name = 'Причал'
        verbose_name_plural = 'причал'

    berths = models.CharField(
        verbose_name='Причал',
        max_length=100,
        blank=True,
        null=True,
        unique = True,
    )

    def __str__(self):
        return f"{self.berths}"


class Tickets(models.Model):
    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'
        ordering = ('created_at',)

    operator = models.ForeignKey(
        'PointsSale',
        on_delete=models.PROTECT,
        verbose_name='Оператор'
    )
    ticket_day = models.DateField(
        verbose_name='День билета'
    )
    ship = models.ForeignKey(
        'ShipSchedule',
        verbose_name='Судно',
        related_name='ship_ticket',
        on_delete=models.PROTECT
    )
    area = models.ForeignKey(
        'LandingPlaces',
        verbose_name='Площадка',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='area_ticket'
    )
    price_types = models.ManyToManyField(
        PriceTypes,
        verbose_name='Типы цен'
    )
    adult_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество взрослых',
        blank=True,
        null=True
    )
    child_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество детей',
        blank=True,
        null=True
    )
    created_at = models.DateField(
        default=timezone.now,
        verbose_name='Дата создания'
    )
    total_amount = models.DecimalField(
        verbose_name='Общая сумма',
        decimal_places=2,
        max_digits=12,
        default=0,
    )
    bought = models.BooleanField(
        verbose_name='Купленный',
        blank=True,
        null=True,
        default=False
    )
    ticket_has_expired = models.BooleanField(
        verbose_name='Время жизни билета прошло',
        blank=True,
        null=True,
        default=False
    )
    check_qr_text = models.ImageField(
        verbose_name='Чек',
        blank=True,
        null=True,
        upload_to='tickets/check/'
    )
    ticket_verified = models.BooleanField(
        blank=True,
        null=True,
        default=False,
        verbose_name='Билет проверен'
    )

    def __str__(self):
        return f"{'Куплен' if self.bought else 'Не куплен'} --- {self.ship} --- {self.created_at}"


class Ship(models.Model):
    class Meta:
        verbose_name = 'Судно'
        verbose_name_plural = 'Судно'
        ordering = ('vessel_name',)

    vessel_name = models.CharField(
        verbose_name='Название судна',
        max_length=100,
        unique=True
    )
    restrictions = models.PositiveIntegerField(
        verbose_name='Ограничения билетов',
        null=True,
        blank=True,
        default=20
    )

    def clean(self):
        if self.restrictions == 0:
            raise ValidationError({"Сообщение": 'Мест нет в данном судне.'})
        
    def __str__(self):
        return f"{self.vessel_name}"


class ShipSchedule(models.Model):
    class Meta:
        verbose_name = 'Время посадки'
        verbose_name_plural = 'Время посадки'

    ship = models.ForeignKey(
        Ship,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Судно'
    )
    berths = models.ForeignKey(
        Berths,
        verbose_name='Причал',
        blank=True,
        null=True,
        on_delete=models.PROTECT
    )
    start_time = models.TimeField(
        verbose_name='Время начала'
    )
    end_time = models.TimeField(
        verbose_name='Время окончания'
    )

    def __str__(self):
        return f"{self.ship} - {self.start_time} - {self.end_time}"


class LandingPlaces(models.Model):
    class Meta:
        verbose_name = 'Посадочное место'
        verbose_name_plural = 'Посадочные места'
        ordering = ('address',)

    address = models.CharField(
        max_length=100,
        verbose_name='Адрес'
    )
    currently_working = models.BooleanField(
        verbose_name='На данный момент работает',
        default=False,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.address}"


class PointsSale(models.Model):
    class Meta:
        verbose_name = 'Точка продажи'
        verbose_name_plural = 'Точки продажи'

    operator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Оператор'
    )
    landing_places = models.ManyToManyField(
        LandingPlaces,
        verbose_name='Посадочное место'
    )
    create_data = models.DateField(
        default=date.today,
        verbose_name='Дата создания'
    )
    left_at = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата выхода'
    )
    complete_the_work_day = models.BooleanField(
        verbose_name='Завершить рабочий день',
        blank=True,
        null=True,
        default=False
    )
    status = models.CharField(
        verbose_name='Статус смены',
        blank=True,
        null=True,
        default='Открытая смена',
        choices=SHIFT_STATUS,
        max_length=14,
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_data = timezone.now().date()
        if self.complete_the_work_day:
            self.status = 'Архив'
            self.left_at = date.today()
            user = User.objects.get(id=self.operator_id)
            request = getattr(self, '_request', None)
            if request:
                logout(request)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.operator}"


class SalesСollection(models.Model):
    class Meta:
        verbose_name = 'Сбор продаж'
        verbose_name_plural = 'Сбор продаж'

    operator = models.ForeignKey(
        PointsSale,
        verbose_name='Оператор',
        on_delete=models.PROTECT,
    )
    tickets = models.ManyToManyField(
        Tickets,
        verbose_name='Билеты',
    )
    sales_date = models.DateField(
        verbose_name='Дата продаж',
        auto_now_add=True
    )
    total_adult_quantity = models.PositiveIntegerField(
        verbose_name='Общее количество взрослых'
    )
    total_child_quantity = models.PositiveIntegerField(
        verbose_name='Общее количество детей'
    )
    total_amount = models.DecimalField(
        verbose_name='Общая сумма',
        decimal_places=2,
        max_digits=12,
        default=0,
    )

    def __str__(self):
        return f"{self.operator}"
