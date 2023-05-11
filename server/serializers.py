import re
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from .models import (
    LandingPlaces, PointsSale, PriceTypes, Price, Tickets, User, Ship, ShipSchedule
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

    def get_user_type(self, obj):
        return obj.get_user_type_display()


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

    def validate_price(self, value):
        if Price.objects.filter(price=value).exists():
            raise serializers.ValidationError({'Сообщение': 'Эта цена уже существует'})
        return value


class PriceTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceTypes
        fields = ('id', 'price', 'client_type')

    def validate(self, data):
        client_type = data.get('client_type')
        existing_object = PriceTypes.objects.filter(client_type=client_type).exists()
        if existing_object:
            raise serializers.ValidationError({'client_type': 'Тип цены с таким уже существует'})
        return data


class PriceTypesPriceGETSerializer(serializers.ModelSerializer):
    price = PriceSerializer()

    class Meta:
        model = PriceTypes
        fields = ('id', 'price', 'client_type')


class ShipAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ship
        fields = ('id', 'vessel_name', 'restrictions')

    def validate(self, data):
        vessel_name = data.get('vessel_name')
        if Ship.objects.filter(vessel_name=vessel_name).exists():
            raise serializers.ValidationError('Это название судна уже существует')
        restrictions = data.get('restrictions')
        if restrictions is not None and restrictions < 0:
            raise serializers.ValidationError('Ограничения билетов не могут быть отрицательными')
        return data


class TicketsCreateSerializer(serializers.ModelSerializer):
    operator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    created_at = serializers.BooleanField(read_only=True)

    class Meta:
        model = Tickets
        fields = "__all__"


class LandingPlacesGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandingPlaces
        fields = "__all__"


class TicketsListSerializer(serializers.ModelSerializer):
    operator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    price_types = PriceTypesPriceGETSerializer(many=True)
    ship = ShipAllSerializer()
    area = LandingPlacesGetSerializer()

    class Meta:
        model = Tickets
        fields = "__all__"


class LandingPlacesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandingPlaces
        fields = "__all__"


class PointsSaleCreateSerializer(serializers.ModelSerializer):
    operator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PointsSale
        fields = "__all__"


class PointsSaleSerializer(serializers.ModelSerializer):
    landing_places = LandingPlacesSerializer(many=True)
    operator = UserLoginSerializer()

    class Meta:
        model = PointsSale
        fields = "__all__"


class PointsSaleEndStatus(serializers.ModelSerializer):
    operator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PointsSale
        fields = ('id', 'operator', 'complete_the_work_day')


class ShipScheduleGetAllSerializer(serializers.ModelSerializer):
    ship = ShipAllSerializer()

    class Meta:
        model = ShipSchedule
        fields = ('id', 'ship', 'start_time', 'end_time')


class ShipScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipSchedule
        fields = ('id', 'ship', 'start_time', 'end_time')

    def create(self, validated_data):
        ship_schedule = ShipSchedule.objects.create(**validated_data)
        message = f"График отправления '{ship_schedule}' успешно создан"
        return Response(
            {'message': message, 'data': self.data},
            status=status.HTTP_201_CREATED
        )


class TicketSerializer(serializers.Serializer):
    data = serializers.CharField()

    def to_representation(self, instance):
        data = instance.get('data', '')

        id_match = re.search(r'id-(\d+)', data)
        operator_match = re.search(r'operator-(\w+)', data)
        ticket_day_match = re.search(r'ticket_day-(\d{4}-\d{2}-\d{2})', data)
        ship_vessel_match = re.search(r'ship-vessel-(\w+)', data)
        ship_start_time_match = re.search(r'ship-start_time(\d{2}:\d{2}:\d{2})', data)
        ship_end_time_match = re.search(r'ship-end_time-(\d{2}:\d{2}:\d{2})', data)
        total_amount_match = re.search(r'total_amount-(\d+\.\d{2})', data)
        area_match = re.search(r'area-(\w+)', data)
        ticket_verified_match = re.search(r'ticket_verified-(\w+)', data)
        created_at_match = re.search(r'created_at-(.+)', data)
        price_types_match = re.search(r'price_types-(.+)', data)
        bought_match = re.search(r'bought-(\w+)', data)
        ticket_has_expired_match = re.search(r'ticket_has_expired-(\w+)', data)
        receipt_key_generation_match = re.search(r'receipt_key_generation-(\w+)', data)

        id_value = id_match.group(1) if id_match else None
        operator_value = operator_match.group(1) if operator_match else None
        ticket_day_value = ticket_day_match.group(1) if ticket_day_match else None
        ship_vessel_value = ship_vessel_match.group(1) if ship_vessel_match else None
        ship_start_time_value = ship_start_time_match.group(1) if ship_start_time_match else None
        ship_end_time_value = ship_end_time_match.group(1) if ship_end_time_match else None
        total_amount_value = total_amount_match.group(1) if total_amount_match else None
        area_value = area_match.group(1) if area_match else None
        created_at_value = created_at_match.group(1) if created_at_match else None
        price_types_value = price_types_match.group(1) if price_types_match else None
        bought_value = bought_match.group(1) if bought_match else None
        ticket_has_expired_value = ticket_has_expired_match.group(1) if ticket_has_expired_match else None

        if created_at_value:
            created_at_parts = created_at_value.split(',')
            created_at_datetime = created_at_parts[0].strip()
            bought_value = None
            ticket_has_expired_value = None

            for part in created_at_parts[1:]:
                part = part.strip()
                if part.startswith('bought-'):
                    bought_value = part[len('bought-'):]
                elif part.startswith('ticket_has_expired-'):
                    ticket_has_expired_value = part[len('ticket_has_expired-'):]

            return {
                'id': id_value,
                'operator': operator_value,
                'ticket_day': ticket_day_value,
                'ship_vessel': ship_vessel_value,
                'ship_start_time': ship_start_time_value,
                'ship_end_time': ship_end_time_value,
                'total_amount': total_amount_value,
                'area': area_value,
                'created_at': created_at_datetime,
                'price_types': price_types_value,
                'bought': bought_value,
                'ticket_has_expired': ticket_has_expired_value,
            }
