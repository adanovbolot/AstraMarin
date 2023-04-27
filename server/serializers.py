from rest_framework import serializers
from .models import User


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'full_name', 'inn', 'password')

    def create(self, validated_data):
        validated_data['is_active'] = True
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
