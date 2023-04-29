from django.contrib.auth.models import User
from django.utils import timezone
from  .models import User


def logout_users():
    User.objects.filter(is_superuser=False, is_active=True).update(last_logout=timezone.now())
