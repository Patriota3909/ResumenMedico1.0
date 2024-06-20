from django.apps import AppConfig


class MedicoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Medico'

    def ready(self):
        import Medico.signals