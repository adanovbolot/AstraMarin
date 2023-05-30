from django.db.models import Q, Max, Min
from django.db.models import Sum
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import (
    LandingPlaces, PointsSale, PriceTypes, Price, Tickets, User, Ship, ShipSchedule, SalesReport, EvotorUsers

)


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'full_name', 'inn', 'user_type',
            'last_login', 'last_logout', 'date_of_registration'
        )


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
            raise serializers.ValidationError({'Сообщение': 'Тип цены с таким уже существует'})
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
    operator = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Tickets
        fields = (
            'operator', 'ship', 'area', 'price_types', 'ticket_day',
            'adult_quantity', 'child_quantity', 'bought'
        )

    def validate(self, data):
        adult_quantity = data.get('adult_quantity')
        child_quantity = data.get('child_quantity')

        if adult_quantity is not None and adult_quantity < 0:
            raise serializers.ValidationError({'Сообщение': ["Количество взрослых не может быть отрицательным."]})
        if child_quantity is not None and child_quantity < 0:
            raise serializers.ValidationError({'Сообщение': ["Количество детей не может быть отрицательным."]})
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        points_sale = get_object_or_404(PointsSale, operator=user)
        validated_data['operator'] = points_sale
        return super().create(validated_data)


class LandingPlacesGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandingPlaces
        fields = "__all__"


class ShipScheduleGetAllSerializer(serializers.ModelSerializer):
    ship = ShipAllSerializer()

    class Meta:
        model = ShipSchedule
        fields = ('id', 'ship', 'start_time', 'end_time')


class TicketsListSerializer(serializers.ModelSerializer):
    operator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    price_types = PriceTypesPriceGETSerializer(many=True)
    ship = ShipScheduleGetAllSerializer()
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
    id = serializers.IntegerField()
    operator = serializers.CharField()
    ticket_day = serializers.DateField()
    ship_vessel = serializers.CharField()
    ship_start_time = serializers.TimeField()
    ship_end_time = serializers.TimeField()
    total_amount = serializers.DecimalField(max_digits=8, decimal_places=2)
    area = serializers.CharField()
    created_at = serializers.DateTimeField()
    bought = serializers.BooleanField()
    ticket_has_expired = serializers.BooleanField()
    adult_quantity = serializers.IntegerField()
    child_quantity = serializers.IntegerField()

    def to_representation(self, instance):
        return {
            'id': instance['id'],
            'operator': instance['operator'],
            'ticket_day': instance['ticket_day'],
            'ship_vessel': instance['ship_vessel'],
            'ship_start_time': instance['ship_start_time'],
            'ship_end_time': instance['ship_end_time'],
            'total_amount': instance['total_amount'],
            'area': instance['area'],
            'created_at': instance['created_at'],
            'bought': instance['bought'],
            'ticket_has_expired': instance['ticket_has_expired'],
            'adult_quantity': instance['adult_quantity'],
            'child_quantity': instance['child_quantity'],
        }


class SalesReportGETSerializer(serializers.ModelSerializer):
    operator = PointsSaleSerializer()

    class Meta:
        model = SalesReport
        fields = "__all__"

    def filter_reports(self, queryset, filters):
        date = filters.get('date')
        month = filters.get('month')
        year = filters.get('year')
        operator_id = filters.get('operator')
        max_amount = filters.get('max_amount')
        min_amount = filters.get('min_amount')

        if operator_id:
            queryset = queryset.filter(operator__id=operator_id)
        if date:
            queryset = queryset.filter(report_date=date)
        elif month and year:
            queryset = queryset.filter(report_date__month=month, report_date__year=year)
        elif month:
            queryset = queryset.filter(report_date__month=month)
        elif year:
            queryset = queryset.filter(report_date__year=year)
        if max_amount:
            queryset = queryset.annotate(max_amount=Max('total_amount_report')).order_by('max_amount')
        if min_amount:
            queryset = queryset.annotate(min_amount=Min('total_amount_report')).order_by('min_amount')
        return queryset

    def to_representation(self, instance):
        data = super().to_representation(instance)
        month = self.context.get('request').query_params.get('month')
        year = self.context.get('request').query_params.get('year')
        if month and year:
            total_monthly_sales = SalesReport.objects.filter(
                Q(report_date__month=month, report_date__year=year) &
                Q(operator=instance.operator)
            ).aggregate(
                total_adult_quantity=Sum('total_adult_quantity'),
                total_child_quantity=Sum('total_child_quantity'),
                total_amount_report=Sum('total_amount_report')
            )
            data['total_monthly_sales'] = total_monthly_sales
        return data


class EvotorUsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = EvotorUsers
        fields = ('id', 'userid', 'token')
