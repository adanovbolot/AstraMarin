import django_filters
from server.element_select import USER_TYPE
from server.models import User


class UserFilter(django_filters.FilterSet):
    user_type = django_filters.ChoiceFilter(choices=USER_TYPE)

    class Meta:
        model = User
        fields = ['user_type']
