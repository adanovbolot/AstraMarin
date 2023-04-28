from .models import User
from .permissions import CreateUserPermission
from rest_framework import generics, permissions
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import (
    LandingPlaces, PointsSale, PriceTypes, Price, Tickets, User
)
from .serializers import \
    (UserSerializer, CreateUserSerializer, UserLoginSerializer, PriceSerializer,
     PriceTypesSerializer, TicketsCreateSerializer, TicketsListSerializer,
     LandingPlacesSerializer, PointsSaleSerializer, PointsSaleCreateSerializer)


class OperatorsList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class OperatorsDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"Сообщение": "Оператор успешно удален."}, status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"Сообщение": "Оператор успешно обновлен."})

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class OperatorAuthorization(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return Response({'Сообщение': 'Вы успешно вошли в свой аккаунт!'},
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
    permission_classes = [permissions.IsAuthenticated]
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
    permission_classes = [permissions.IsAuthenticated]
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


class PriceTypesList(generics.ListAPIView):
    queryset = PriceTypes.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PriceTypesSerializer


class PriceTypesCreate(generics.CreateAPIView):
    serializer_class = PriceTypesSerializer
    queryset = PriceTypes.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'Сообщение': 'Тип цены успешно создан.'}, status=status.HTTP_201_CREATED, headers=headers)


class PriceTypesUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PriceTypesSerializer
    queryset = PriceTypes.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'Сообщение': 'Тип цены успешно обновлен.'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'Сообщение': 'Тип цены успешно удален.'}, status=status.HTTP_204_NO_CONTENT)


class TicketsCreate(generics.CreateAPIView):
    queryset = Tickets.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketsCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'Сообщение': 'Билет успешно создан.'},
                        status=status.HTTP_201_CREATED, headers=headers)


class TicketsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketsListSerializer

    def get_queryset(self):
        return Tickets.objects.filter(operator=self.request.user)


class LandingPlacesCreateList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LandingPlacesSerializer
    queryset = LandingPlaces.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'Сообщение': 'Место посадки успешно создано.'}, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'Сообщение': 'Список мест посадки получен успешно.', 'data': serializer.data}, status=status.HTTP_200_OK)


class LandingPlacesUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
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
    queryset = PointsSale.objects.all()


class PointsSaleUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PointsSaleCreateSerializer
    queryset = PointsSale.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'Сообщение': 'Объект успешно обновлен.'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'Сообщение': 'Объект успешно удален.'}, status=status.HTTP_204_NO_CONTENT)
