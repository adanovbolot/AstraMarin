from django.urls import path
from . import views


urlpatterns = [
    path('operator/list/', views.OperatorsList.as_view()),
    path('operator/delete/<int:pk>/', views.OperatorsDetailUpdateDelete.as_view()),
    path('operator/create/', views.OperatorsCreate.as_view()),
    path('operator/authorization/', views.OperatorAuthorization.as_view()),
    path('operator/logout/', views.OperatorLogout.as_view()),
    path('operator/change/password/', views.OperatorChangePassword.as_view()),

    path('price/create/list/', views.PriceCreateList.as_view()),
    path('price/update/delete/<int:pk>/', views.PriceUpdateDelete.as_view()),

    path('price_type/create/list/', views.PriceTypesCreate.as_view()),
    path('price_type/update/delete/<int:pk>/', views.PriceTypesUpdateDelete.as_view()),

    path('ticket/create/', views.TicketsCreate.as_view()),
    path('ticket/list/', views.TicketsList.as_view()),

    path('landing/places/create/list/', views.LandingPlacesCreateList.as_view()),
    path('landing/places/update/delete/<int:pk>/', views.LandingPlacesUpdateDelete.as_view()),

    path('points/sale/create/', views.PointsSaleCreate.as_view()),
    path('points/sale/list/', views.PointsSaleList.as_view()),
    path('points/sale/update/', views.PointsSaleUpdate.as_view()),

    path('ship/all/', views.ShipAll.as_view()),
    path('ship/create/', views.ShipCreate.as_view()),
    path('ship/update/delete/<int:pk>/', views.ShipUpdateDelete.as_view()),

    path('ship/schedule/create/', views.ShipScheduleCreate.as_view()),
    path('ship/schedule/all/', views.ShipScheduleGetAll.as_view()),
    path('ship/schedule/update/delete/<int:pk>/', views.ShipScheduleUpdateDelete.as_view()),

    path('tickets/verification/', views.TicketView.as_view()),
]
