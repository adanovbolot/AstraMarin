from datetime import date
from django.core.exceptions import ValidationError
from django.contrib.auth import logout
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from server.element_select import USER_TYPE, CHILD_OR_ABULT, SHIFT_STATUS
from server.manager import UserManager
from django.utils import timezone
import uuid


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    # userid = models.UUIDField(primary_key=True, default=uuid.uuid4)
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
        verbose_name='Оператор',
        related_name='tickets_points_sale'
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
    ticket_return = models.BooleanField(
        verbose_name='Возрат билета',
        default=False,
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


class SalesReport(models.Model):
    class Meta:
        verbose_name = 'Отчет о продажах'
        verbose_name_plural = 'Отчеты о продажах'

    operator = models.ForeignKey(
        PointsSale,
        on_delete=models.CASCADE,
        verbose_name='Оператор',
        related_name='sales_reports'
    )
    report_date = models.DateField(
        verbose_name='Дата отчета',
        blank=True,
        null=True
    )
    sales_date = models.DateField(
        verbose_name='Дата продаж',
        auto_now_add=True,
        blank=True,
        null=True
    )
    total_adult_quantity = models.PositiveIntegerField(
        verbose_name='Общее количество взрослых',
        blank=True,
        null=True,
        default=0
    )
    total_child_quantity = models.PositiveIntegerField(
        verbose_name='Общее количество детей',
        blank=True,
        null=True,
        default=0
    )
    total_amount_report = models.DecimalField(
        verbose_name='Общая сумма продаж',
        decimal_places=2,
        max_digits=12,
        default=0,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.operator} -- {self.report_date}"


class EvotorUsers(models.Model):
    class Meta:
        verbose_name = 'Пользователи Эвотор'
        verbose_name_plural = 'Пользователи Эвотор'

    userId = models.CharField(
        verbose_name='UserID',
        max_length=100,
        # unique=True
    )
    token = models.CharField(
        verbose_name='Токен',
        max_length=250,
        blank=True,
        null=True,
        # unique=True
    )

    def __str__(self):
        return f"{self.userId}"


class EvotorToken(models.Model):
    class Meta:
        verbose_name = 'Эвотор токен'
        verbose_name_plural = 'Эвотор токены'

    userId = models.CharField(
        verbose_name='UserID',
        max_length=100,
        # unique=True
    )
    token = models.CharField(
        verbose_name='Токен',
        max_length=250,
        blank=True,
        null=True,
        # unique=True
    )

    def __str__(self):
        return f"{self.userId}, {self.token}"


class Shops(models.Model):
    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'

    uuid = models.CharField(
        verbose_name='uuid',
        max_length=200,
    )
    address = models.CharField(
        verbose_name='Адрес',
        max_length=200,
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    code = models.CharField(
        verbose_name='Код',
        max_length=100,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.name} {self.address}"


class EvotorOperator(models.Model):
    class Meta:
        verbose_name = 'Эвотор Оператор'
        verbose_name_plural = 'Эвотор Операторы'

    uuid = models.CharField(
        verbose_name='uuid',
        max_length=200,
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    code = models.CharField(
        verbose_name='Код',
        max_length=100,
        blank=True,
        null=True
    )
    stores = models.CharField(
        verbose_name='Магазин',
        max_length=200,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=100
    )

    def __str__(self):
        return f"{self.name} {self.stores}"


class Terminal(models.Model):
    class Meta:
        verbose_name = 'Терминал'
        verbose_name_plural = 'Терминалы'

    uuid = models.CharField(
        verbose_name='UUID',
        max_length=200,
        null=True,
        blank=True
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        null=True,
        blank=True
    )
    store_uuid = models.CharField(
        verbose_name='UUID магазина',
        max_length=200,
        null=True,
        blank=True
    )
    timezone_offset = models.IntegerField(
        verbose_name='Смещение часового пояса',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class Product(models.Model):
    uuid = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    bar_codes = models.JSONField(default=list)
    alco_codes = models.JSONField(default=list)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=3)
    measure_name = models.CharField(max_length=50)
    tax = models.CharField(max_length=50)
    allow_to_sell = models.BooleanField()
    description = models.TextField()
    article_number = models.CharField(max_length=50)
    parent_uuid = models.CharField(max_length=100)
    group = models.BooleanField()
    type = models.CharField(max_length=50)
    alcohol_by_volume = models.DecimalField(max_digits=5, decimal_places=2)
    alcohol_product_kind_code = models.IntegerField()
    tare_volume = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name
