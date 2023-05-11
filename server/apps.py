from django.apps import AppConfig
from django.utils import timezone


class ServerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'server'
    verbose_name = 'Астра Марин'

    def ready(self):
        import server.signals
