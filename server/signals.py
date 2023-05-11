from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import pre_save
from django.contrib.auth import logout
from server.models import PointsSale, Tickets


@receiver(user_logged_out)
def update_last_logout(sender, user, request, **kwargs):
    user.last_logout = timezone.now()
    user.save()


@receiver(pre_save, sender=PointsSale)
def set_left_at_and_status(sender, instance, **kwargs):
    if instance.complete_the_work_day:
        instance.left_at = timezone.now()
        instance.status = 2


