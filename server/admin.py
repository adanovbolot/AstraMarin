from django.contrib import admin
from .models import (
    LandingPlaces, PointsSale, PriceTypes, Price, Tickets, User
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'full_name', 'is_active', 'inn']


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ['price']


@admin.register(PriceTypes)
class PriceTypesAdmin(admin.ModelAdmin):
    list_display = ['price', 'client_type']


@admin.register(Tickets)
class TicketsAdmin(admin.ModelAdmin):
    list_display = ['operator', 'price_types', 'bought', 'qr_code']


@admin.register(LandingPlaces)
class LandingPlacesAdmin(admin.ModelAdmin):
    list_display = ['address']


@admin.register(PointsSale)
class PointsSaleAdmin(admin.ModelAdmin):
    list_display = ['operator', 'created_at']
