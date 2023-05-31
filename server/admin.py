from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from .models import (
    LandingPlaces, PointsSale, PriceTypes, Price, Tickets, User, Ship, ShipSchedule, Berths, SalesReport, EvotorUsers,
    EvotorToken
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'inn', 'user_type', 'date_of_registration')
    fieldsets = (
        ("Данные оператора", {'fields': ('username', 'full_name', 'inn', 'user_type')}),
        ("Даты", {'fields': ('last_login', 'last_logout')}),
        ("Статусы", {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ['id', 'price']


@admin.register(PriceTypes)
class PriceTypesAdmin(admin.ModelAdmin):
    list_display = ['price', 'client_type']


@admin.register(Tickets)
class TicketsAdmin(admin.ModelAdmin):
    list_display = ['operator', 'ticket_verified', 'ticket_has_expired', 'bought', 'area', 'ship']
    fieldsets = (
        ("Оператор который продал билет", {'fields': ('operator',)}),
        ("Данные билета", {'fields': ('area', 'ship')}),
        ("Даты", {'fields': ('ticket_day', 'created_at')}),
        ("Стоимость", {'fields': ('price_types', 'adult_quantity', 'child_quantity', 'total_amount')}),
        ("Чек, QR и данные о чеке", {'fields': ('check_qr_text',)}),
        ("Статусы", {'fields': ('ticket_verified', 'ticket_has_expired', 'bought', 'ticket_return')}),
    )


@admin.register(LandingPlaces)
class LandingPlacesAdmin(admin.ModelAdmin):
    list_display = ['id', 'address', 'currently_working']


@admin.register(PointsSale)
class PointsSaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'operator', 'create_data', 'left_at', 'complete_the_work_day', 'status']
    fieldsets = (
        ("Данные о точка продажи", {'fields': ('operator', 'landing_places')}),
        ("Даты", {'fields': ('left_at', 'create_data')}),
        ("Статусы", {'fields': ('complete_the_work_day', 'status')}),
    )


@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    list_display = ['id', 'vessel_name', 'restrictions']


@admin.register(ShipSchedule)
class ShipScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'ship', 'berths', 'start_time', 'end_time']
    fieldsets = (
        ("Данные о судно", {'fields': ('ship', 'berths')}),
        ("Время", {'fields': ('start_time', 'end_time')}),
    )


class BerthsForm(forms.ModelForm):
    class Meta:
        model = Berths
        fields = '__all__'

    def clean_berths(self):
        berths = self.cleaned_data.get('berths')
        if Berths.objects.exclude(pk=self.instance.pk).filter(berths=berths).exists():
            raise ValidationError('Такой причал уже существует.')
        return berths


@admin.register(Berths)
class BerthsAdmin(admin.ModelAdmin):
    list_display = ['id', 'berths']
    form = BerthsForm


@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'operator', 'report_date', 'sales_date', 'total_amount_report']


@admin.register(EvotorUsers)
class TerminalAdmin(admin.ModelAdmin):
    list_display = ['id', 'userId', 'token']


@admin.register(EvotorToken)
class EvotorTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'userId', 'token']
