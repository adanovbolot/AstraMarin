from .models import User
from .serializers import UserSerializer, CreateUserSerializer, UserLoginSerializer
from rest_framework import generics, permissions
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class OperatorsList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class OperatorsDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.IsAdminUser]


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
    permission_classes = [permissions.IsAdminUser]

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
