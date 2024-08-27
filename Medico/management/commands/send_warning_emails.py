from django.core.management.base import BaseCommand
from Medico.models import Resumen

class Command(BaseCommand):
    help = 'Send warning emails to doctors if deadlines are approaching'

    def handle(self, *args, **kwargs):
        # Obtener todos los resúmenes que necesitan ser verificados
        resumenes = Resumen.objects.all()

        for resumen in resumenes:
            resumen.verificar_y_enviar_advertencia()
