from django.contrib import admin
from .models import (
    LandingPlaces, PointsSale, PriceTypes, Price, Tickets, User, Ship, ShipSchedule, Berths
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'inn', 'user_type', 'date_of_registration')
    fieldsets = (
        ("Данные оператора", {'fields': ('username', 'full_name', 'inn', 'user_type')}),
        ("Даты", {'fields': ('last_login', 'last_logout')}),
        ("Статусы", {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ['price']


@admin.register(PriceTypes)
class PriceTypesAdmin(admin.ModelAdmin):
    list_display = ['price', 'client_type']


@admin.register(Tickets)
class TicketsAdmin(admin.ModelAdmin):
    list_display = ['operator', 'bought', 'qr_code']


@admin.register(LandingPlaces)
class LandingPlacesAdmin(admin.ModelAdmin):
    list_display = ['address']


@admin.register(PointsSale)
class PointsSaleAdmin(admin.ModelAdmin):
    list_display = ['operator', 'created_at']


@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    pass


@admin.register(ShipSchedule)
class ShipScheduleAdmin(admin.ModelAdmin):
    pass


@admin.register(Berths)
class BerthsAdmin(admin.ModelAdmin):
    pass

