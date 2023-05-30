from datetime import datetime

import requests
from django.utils import timezone
from .filters import UserFilter
from .permissions import CreateUserPermission, IsSudovoditel, IsOperator, AdminOnlyPermission
from rest_framework import generics, permissions
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework import status
import logging
from rest_framework.response import Response
from .models import (
    LandingPlaces, PointsSale, PriceTypes, Price, Tickets, User, Ship, ShipSchedule, SalesReport, EvotorUsers
)
from .serializers import (
    UserSerializer, CreateUserSerializer, UserLoginSerializer, PriceSerializer, PriceTypesSerializer,
    TicketsCreateSerializer, TicketsListSerializer, LandingPlacesSerializer, PointsSaleCreateSerializer,
    PointsSaleSerializer, PointsSaleEndStatus, ShipAllSerializer, ShipScheduleSerializer, ShipScheduleGetAllSerializer,
    TicketSerializer, SalesReportGETSerializer, EvotorUsersSerializer
)

logger = logging.getLogger(__name__)


class OperatorsList(generics.ListAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AdminOnlyPermission]
    filterset_class = UserFilter

    def get_queryset(self):
        queryset = User.objects.exclude(is_superuser=True)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        data = {'сообщение': 'Список сотрудников'}
        response.data.append(data)
        return response


class OperatorsDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AdminOnlyPermission]
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"Сообщение": "Оператор успешно удален."}, status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"Сообщение": "Оператор успешно обновлен."})

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"Сообщение": "Оператор успешно обновлен."})


class OperatorAuthorization(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)

            operator = request.user
            current_date = timezone.now().date()
            points_sale = PointsSale.objects.filter(
                operator=operator, create_data=current_date, status='Открытая смена'
            ).first()

            if not points_sale:
                points_sale = PointsSale.objects.create(operator=operator, status='Открытая смена')

            user_data = {
                'id': operator.id,
                'username': operator.username,
                'user_type': operator.user_type,
            }

            return Response({'Сообщение': 'Вы успешно вошли в свой аккаунт!', 'Пользователь': user_data},
                            status=status.HTTP_200_OK)
        else:
            return Response({'Сообщение': 'Неверный логин или пароль'},
                            status=status.HTTP_400_BAD_REQUEST)


class OperatorsCreate(generics.CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [CreateUserPermission]

    def perform_create(self, serializer):
        serializer.save(is_active=True)
        return Response({'Сообщение': 'Пользователь успешно создан'}, status=status.HTTP_201_CREATED)


class OperatorLogout(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        logout(request)
        return Response({'Сообщение': 'Вы успешно вышли из своего аккаунта.'}, status=status.HTTP_200_OK)


class OperatorChangePassword(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not user.check_password(old_password):
            return Response({'Сообщение': 'Неверный старый пароль.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'Сообщение': 'Пароль успешно изменен.'}, status=status.HTTP_200_OK)


class PriceCreateList(generics.ListCreateAPIView):
    permission_classes = [AdminOnlyPermission]
    queryset = Price.objects.all()
    serializer_class = PriceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {'Сообщение': 'Цена успешно создана'},
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class PriceUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AdminOnlyPermission]
    queryset = Price.objects.all()
    serializer_class = PriceSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'Сообщение': 'Цена успешно обновлена.'})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'Сообщение': 'Цена успешно удалена.'}, status=status.HTTP_204_NO_CONTENT)


class PriceTypesCreate(generics.ListCreateAPIView):
    serializer_class = PriceTypesSerializer
    queryset = PriceTypes.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'Администрация':
            return Response({'ошибка': 'Доступ запрещен. Только администратор может создавать типы цен.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {'Сообщение': 'Тип цены успешно создан.'},
            status=status.HTTP_201_CREATED, headers=headers
        )


class PriceTypesUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PriceTypesSerializer
    queryset = PriceTypes.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def update(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated and user.user_type == 'Администрация':
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({'Сообщение': 'Тип цены успешно обновлен.'}, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    'ошибка': 'Доступ запрещен. Только пользователи с должностью'
                              ' "Администрация" могут выполнять эту операцию.'},
                    status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated and user.user_type == 'Администрация':
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'Сообщение': 'Тип цены успешно удален.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {
                    'ошибка': 'Доступ запрещен. Только пользователи с должностью'
                              ' "Администрация" могут выполнять эту операцию.'},
                    status=status.HTTP_403_FORBIDDEN)


class TicketsCreate(generics.CreateAPIView):
    queryset = Tickets.objects.all()
    permission_classes = [IsOperator]
    serializer_class = TicketsCreateSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'Оператор':
            return Response({'ошибка': 'Доступ запрещен. Только операторы могут создавать билеты.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response_data = {
            "Сообщение": "Билет куплен",
            "Билет": serializer.data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class TicketsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketsListSerializer

    def get_queryset(self):
        return Tickets.objects.filter(operator__operator=self.request.user)


class LandingPlacesCreateList(generics.ListCreateAPIView):
    permission_classes = [AdminOnlyPermission]
    serializer_class = LandingPlacesSerializer
    queryset = LandingPlaces.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'Сообщение': 'Место посадки успешно создано.'},
                        status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'Сообщение': 'Список мест посадки получен успешно.', 'data': serializer.data},
                        status=status.HTTP_200_OK)


class LandingPlacesUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AdminOnlyPermission]
    serializer_class = LandingPlacesSerializer
    queryset = LandingPlaces.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'Сообщение': 'Место посадки успешно обновлено.'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'Сообщение': 'Место посадки успешно удалено.'}, status=status.HTTP_204_NO_CONTENT)


class PointsSaleCreate(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PointsSaleCreateSerializer
    queryset = PointsSale.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'Сообщение': 'Объект успешно создан.'}, status=status.HTTP_201_CREATED, headers=headers)


class PointsSaleList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PointsSaleSerializer

    def get_queryset(self):
        operator = self.request.user
        queryset = PointsSale.objects.filter(operator_id=operator.id)

        day = self.request.query_params.get('day')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        if day:
            queryset = queryset.filter(create_data__day=day)
        if month:
            queryset = queryset.filter(create_data__month=month)
        if year:
            queryset = queryset.filter(create_data__year=year)
        return queryset


class PointsSaleUpdate(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PointsSaleEndStatus
    queryset = PointsSale.objects.all()

    def perform_update(self, serializer):
        if serializer.validated_data.get('complete_the_work_day', False):
            instance = serializer.save()
            instance.left_at = timezone.now()
            instance.status = 2
            instance.save()
            logout(self.request)
            return Response({'Сообщение': 'Смена закрыта и вы вышли из системы.'}, status=status.HTTP_200_OK)
        else:
            serializer.save()
            return Response({'Сообщение': 'Статус смены активен.'}, status=status.HTTP_200_OK)

    def get_object(self):
        operator = self.request.user
        obj = PointsSale.objects.get(operator=operator)
        return obj


class ShipAll(generics.ListAPIView):
    queryset = Ship.objects.all()
    serializer_class = ShipAllSerializer
    permission_classes = [AdminOnlyPermission]


class ShipCreate(generics.CreateAPIView):
    queryset = Ship.objects.all()
    serializer_class = ShipAllSerializer
    permission_classes = [AdminOnlyPermission]

    def perform_create(self, serializer):
        serializer.save()
        return Response({'Сообщение': 'Корабль успешно создан.'}, status=status.HTTP_201_CREATED)


class ShipUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ship.objects.all()
    serializer_class = ShipAllSerializer
    permission_classes = [AdminOnlyPermission]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"Сообщение": "Судно успешно удалено."}, status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"Сообщение": "Судно успешно обновлено."})


class ShipScheduleCreate(generics.CreateAPIView):
    queryset = ShipSchedule.objects.all()
    permission_classes = [AdminOnlyPermission]
    serializer_class = ShipScheduleSerializer


class ShipScheduleGetAll(generics.ListAPIView):
    queryset = ShipSchedule.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShipScheduleGetAllSerializer


class ShipScheduleUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShipSchedule.objects.all()
    permission_classes = [AdminOnlyPermission]
    serializer_class = ShipScheduleSerializer

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        message = f"График отправления с id {kwargs['pk']} был успешно обновлен"
        return Response({'Сообщение': message}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        message = f"График отправления с id {kwargs['pk']} был успешно удален"
        return Response({'Сообщение': message}, status=status.HTTP_204_NO_CONTENT)


class TicketView(APIView):
    permission_classes = [IsSudovoditel]

    def post(self, request):
        serializer = TicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        parsed_data = serializer.validated_data
        ticket_verified = parsed_data.get('ticket_verified')
        if ticket_verified == "True":
            error_message = "Билет уже использован."
            return Response({'Сообщение': error_message, 'data': parsed_data}, status=status.HTTP_400_BAD_REQUEST)
        ticket_day = parsed_data.get('ticket_day')
        ship_start_time = parsed_data.get('ship_start_time')
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        current_time = current_datetime.time()
        if ticket_day < current_date or (ticket_day == current_date and ship_start_time <= current_time):
            parsed_data['ticket_has_expired'] = True
            error_message = "Билет просрочен."
            return Response({'Сообщение': error_message, 'data': parsed_data}, status=status.HTTP_400_BAD_REQUEST)
        parsed_data['ticket_verified'] = True
        message = "Билет проверен и является действующим."
        return Response({'Сообщение': message, 'data': parsed_data}, status=status.HTTP_200_OK)


class SalesReportListResultsDay(APIView):
    serializer_class = SalesReportGETSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = SalesReport.objects.all()
        filters = {
            'date': request.query_params.get('date'),
            'month': request.query_params.get('month'),
            'year': request.query_params.get('year')
        }
        queryset = self.serializer_class().filter_reports(queryset, filters)
        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class EvotorUsersCreate(generics.ListCreateAPIView):
    queryset = EvotorUsers.objects.all()
    serializer_class = EvotorUsersSerializer

    def perform_create(self, serializer):
        token = self.request.data.get('token', 'toaWaep4chou7ahkoogiu9Iusaht9ima')
        serializer.save(token=token)
        logger = logging.getLogger(__name__)
        logger.info(f"Token '{token}' сохранен в базе данных.")
        logger.info(f"Request data: {self.request.data}")
        logger.info(f"Serializer data: {serializer.data}")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response_data = {
            'token': serializer.data['token']
        }
        logger = logging.getLogger(__name__)
        logger.info(f"Response data: {response_data}")
        return Response(response_data, status=status.HTTP_200_OK, headers=headers)
