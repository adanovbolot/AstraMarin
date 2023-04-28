from django.urls import path
from . import views


urlpatterns = [
    path('operator/list/', views.OperatorsList.as_view()),
    path('operator/update/delete/', views.OperatorsDetailUpdateDelete.as_view()),
    path('operator/create/', views.OperatorsCreate.as_view()),
    path('operator/authorization/', views.OperatorAuthorization.as_view()),
    path('operator/logout/', views.OperatorLogout.as_view()),
    path('operator/change/password/', views.OperatorChangePassword.as_view()),

    path('price/create/list/', views.PriceCreateList.as_view()),
    path('price/update/delete/<int:pk>/', views.PriceUpdateDelete.as_view()),

    path('price_type/create/', views.PriceTypesCreate.as_view()),
    path('price_type/list/', views.PriceTypesList.as_view()),
    path('price_type/update/delete/<int:pk>/', views.PriceTypesUpdateDelete.as_view()),

    path('ticket/create/', views.TicketsCreate.as_view()),
    path('ticket/list/', views.TicketsList.as_view()),

    path('landing/places/create/list/', views.LandingPlacesCreateList.as_view()),
    path('landing/places/update/delete/<int:pk>/', views.LandingPlacesUpdateDelete.as_view()),

    path('points/sale/create/', views.PointsSaleCreate.as_view()),
    path('points/sale/list/', views.PointsSaleList.as_view()),
    path('points/sale/update/delete/<int:pk>/', views.PointsSaleUpdateDelete.as_view()),
]
