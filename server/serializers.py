from rest_framework import serializers

from .element_select import CHILD_OR_ABULT
from .models import (
    LandingPlaces, PointsSale, PriceTypes, Price, Tickets, User
)


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')


class UserSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'inn', 'user_type')


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'full_name', 'user_type', 'inn', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['is_active'] = True
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ('id', 'price')


class PriceTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceTypes
        fields = ('id', 'price', 'client_type')

    def validate(self, data):
        client_type = data.get('client_type')
        existing_object = PriceTypes.objects.filter(client_type=client_type).exists()
        if existing_object:
            raise serializers.ValidationError({'client_type': 'Тип цены с таким client_type уже существует'})
        return data


class PriceTypesPriceGETSerializer(serializers.ModelSerializer):
    price = PriceSerializer()

    class Meta:
        model = PriceTypes
        fields = ('id', 'price', 'client_type')


class TicketsCreateSerializer(serializers.ModelSerializer):
    operator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    created_at = serializers.BooleanField(read_only=True)

    class Meta:
        model = Tickets
        fields = ('operator', 'price_types', 'created_at', 'bought')


class TicketsListSerializer(serializers.ModelSerializer):
    operator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    price_types = PriceTypesPriceGETSerializer()

    class Meta:
        model = Tickets
        fields = "__all__"


class LandingPlacesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandingPlaces
        fields = ('id', 'address')


class PointsSaleCreateSerializer(serializers.ModelSerializer):
    operator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PointsSale
        fields = ('id', 'operator', 'landing_places')


class PointsSaleSerializer(serializers.ModelSerializer):
    operator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    landing_places = LandingPlacesSerializer(many=True)

    class Meta:
        model = PointsSale
        fields = ('id', 'operator', 'landing_places')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['left_at'] = instance.left_at.isoformat() if instance.left_at is not None else None
        return rep
