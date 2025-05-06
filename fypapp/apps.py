from django.apps import AppConfig
from django.apps import AppConfig


class FypappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fypapp'

class FypappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fypapp'

    def ready(self):
        import fypapp.signals 


from django.apps import AppConfig

class FypappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fypapp'

    def ready(self):
        import fypapp.signals  # Ensure signals are loaded

