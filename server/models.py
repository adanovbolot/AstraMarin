from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from server.element_select import USER_TYPE, CHILD_OR_ABULT, SHIFT_STATUS
from server.manager import UserManager
from django.utils import timezone
from django.core.files.base import ContentFile
from decimal import Decimal
import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'Оператор'
        verbose_name_plural = 'Операторы'

    username = models.CharField(max_length=255, unique=True, verbose_name='Логин')
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Фамилия')
    inn = models.CharField(max_length=12, blank=True, null=True, unique=True, verbose_name='ИИН')
    user_type = models.CharField(max_length=6, choices=USER_TYPE, verbose_name='Должность', default=2)
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
        return f"{self.price}"


class PriceTypes(models.Model):
    class Meta:
        verbose_name = 'Тип цен'
        verbose_name_plural = 'Типы цен'
        ordering = ('client_type',)

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
        null=True
    )

    def __str__(self):
        return f"{self.berths}"


class Tickets(models.Model):
    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'
        ordering = ('created_at',)

    operator = models.ForeignKey(
        User,
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
    description_check = models.TextField(
        verbose_name='Данные чека',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
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
    qr_code = models.ImageField(
        verbose_name='QR код',
        upload_to='tickets/qr_codes/',
        null=True,
        blank=True,
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

    def generate_check_image(self):
        TEXT = \
            f'АстраМарин\n' \
            f'___________________________________\n' \
            f'Билет №                   {self.pk}\n' \
            f'\n' \
            f' Дата создания:           {self.created_at}\n' \
            f'___________________________________\n' \
            f'Кассир:                   {self.operator}\n' \
            f'\n' \
            f'_ _ _ _Время начало и время окончания\n' \
            f'_ _ _ _{self.ship.start_time} - - - -{self.ship.end_time}\n' \
            f'\n' \
            f'_ _ _ _ Причал:- - - - - - - - - - - -{self.ship.berths}\n' \
            f'\n' \
            f'_ _ _ _ Судно: - - - - - - - - - - - {self.ship.ship}\n' \
            f'\n' \
            f'_ _ _ _ Стоимость:- - - - - - - - - -{self.total_amount}\n' \
            f'\n' \
            f'_ _ _ _ День билета: - - - - - - - - {self.ticket_day}\n' \
            f'\n' \
            f'_ _ _ _ Количество взрослых:- - - - -{self.adult_quantity}\n' \
            f'\n' \
            f'_ _ _ _ Количество детей: - - - - - -{self.child_quantity}\n' \
            f'\n' \
            f'_ _ _ _ Площадка:- - - - - - - - - - {self.area}\n' \
            f'\n' \
            f'- - - - Купил: - - - - - - - - - - -  {self.bought}\n' \

        data_str = f'id-{self.pk},\n' \
                   f'operator-{self.operator},\n' \
                   f'ticket_day-{self.ticket_day},\n' \
                   f'ship-vessel-{self.ship.ship},\n' \
                   f'ship-start_time{self.ship.start_time},\n' \
                   f'ship-end_time-{self.ship.end_time},\n' \
                   f'total_amount-{self.total_amount},\n' \
                   f'area-{self.area},\n' \
                   f'created_at-{self.created_at},\n' \
                   f'bought-{self.bought},\n' \
                   f'ticket_has_expired-{self.ticket_has_expired},\n' \

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=1
        )

        qr.add_data(data_str)
        qr.make(fit=True)
        qr_img = qr.make_image(
            fill_color='black',
            back_color='white'
        )

        font_size = 15
        font = ImageFont.truetype("arial.ttf", font_size)
        text_width, text_height = font.getsize(TEXT)
        check_img = Image.new('RGB', (qr_img.width + 400, qr_img.height + text_height + 500), color='white')
        check_draw = ImageDraw.Draw(check_img)
        check_draw.text((20, 20), TEXT, font=font, fill='black')

        qr_x = (check_img.width - qr_img.width) // 2
        qr_y = check_img.height - qr_img.height - 40
        check_img.paste(qr_img, (qr_x, qr_y))

        buffer = BytesIO()
        check_img.save(buffer, format='PNG')
        filename = f'check_qr_{self.pk}.png'
        file = ContentFile(buffer.getvalue())
        self.check_qr_text.save(filename, file, save=False)
        buffer.close()

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
        total_price = Decimal('0')
        for price_type in self.price_types.all():
            if price_type.client_type == 'Ребенок':
                total_price += price_type.price.price * self.child_quantity
            elif price_type.client_type == 'Взрослый':
                total_price += price_type.price.price * self.adult_quantity
        self.total_amount = total_price
        data_str = f'id-{self.pk}-\n' \
                   f'operator-{self.operator}\n' \
                   f'price_types-{self.price_types.all()}\n' \
                   f'День билета: {self.ticket_day}' \
                   f'created_at-{self.created_at}\n' \
                   f'adult_quantity-{self.adult_quantity}\n' \
                   f'child_quantity-{self.child_quantity}\n' \
                   f'area-{self.area}\n' \
                   f'ship-{self.ship}\n' \
                   f'total_amount-{self.total_amount}\n' \

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=4
        )

        qr.add_data(data_str)
        qr.make(fit=True)
        img = qr.make_image(
            fill_color='black',
            back_color='white'
        )
        buffer = BytesIO()
        img.save(buffer)
        filename = f'qr_code_{self.pk}.png'
        file = ContentFile(buffer.getvalue())
        self.qr_code.save(filename, file, save=False)
        buffer.close()
        price_type_str = ''
        for price_type in self.price_types.all():
            price_type_str += f'Тип клиента: {price_type.client_type}. Стоимость: {price_type.price}\n'

        self.description_check = \
            f'АстраМарин\n' \
            f'___________________________________\n' \
            f'Билет №                   {self.pk}\n' \
            f'\n' \
            f' Дата создания:           {self.created_at}\n' \
            f'___________________________________\n' \
            f'Кассир:                   {self.operator}\n' \
            f'\n' \
            f'_ _ _ _Время начало и время окончания\n' \
            f'_ _ _ _{self.ship.start_time} - - - -{self.ship.end_time}\n' \
            f'\n' \
            f'_ _ _ _ Причал:- - - - - - - - - - - -{self.ship.berths}\n' \
            f'\n' \
            f'_ _ _ _ Судно: - - - - - - - - - - - {self.ship.ship}\n' \
            f'\n' \
            f'_ _ _ _ Стоимость:- - - - - - - - - -{self.total_amount} РУБЛЕЙ\n' \
            f'\n' \
            f'_ _ _ _ День билета: - - - - - - - - {self.ticket_day}\n' \
            f'\n' \
            f'_ _ _ _ Количество взрослых:- - - - -{self.adult_quantity}\n' \
            f'\n' \
            f'_ _ _ _ Количество детей: - - - - - -{self.child_quantity}\n' \
            f'\n' \
            f'_ _ _ _ Площадка:- - - - - - - - - - {self.area}\n' \

        self.generate_check_image()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{'Куплен' if self.bought else 'Не куплен'}"


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
    objects = models.Manager()

    @classmethod
    def currently_working_places(cls):
        return cls.objects.filter(currently_working=True)

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
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    left_at = models.DateTimeField(
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
        default=1,
        choices=SHIFT_STATUS,
        max_length=3,
    )

    def __str__(self):
        return f"{self.operator}"

