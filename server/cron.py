from django.contrib.auth.models import User
from django.utils import timezone
from .models import User, PointsSale


def logout_users():
    User.objects.filter(is_superuser=False, is_active=True).update(last_logout=timezone.now())
    points_sales = PointsSale.objects.filter(complete_the_work_day=False)

    for points_sale in points_sales:
        points_sale.status = 'Архив'
        points_sale.left_at = timezone.now().date()
        points_sale.complete_the_work_day = True
        points_sale.save()
