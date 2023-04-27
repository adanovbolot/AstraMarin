from django.urls import path
from . import views


urlpatterns = [
    path('operators/list/', views.OperatorsList.as_view()),
    path('operator/update/delete/', views.OperatorsDetailUpdateDelete.as_view()),
    path('operator/create/', views.OperatorsCreate.as_view()),
    path('operator/authorization/', views.OperatorAuthorization.as_view()),
    path('operator/logout/', views.OperatorLogout.as_view()),
    path('operator/change/password/', views.OperatorChangePassword.as_view()),
]
