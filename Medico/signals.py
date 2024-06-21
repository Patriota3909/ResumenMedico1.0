from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Resumen, Doctor, Asignacion, Especialidad

def obtener_siguiente_becario(especialidad):
    becarios = list(Doctor.objects.filter(especialidad=especialidad, tipo='Becario').order_by('id'))
    
    if not becarios:
        return None

    asignacion, created = Asignacion.objects.get_or_create(
        especialidad=especialidad,
        tipo_medico='Becario',
        defaults={'ultimo_medico': becarios[0]}  # Usar el primer becario en la lista
    )

    try:
        siguiente_becario = becarios[becarios.index(asignacion.ultimo_medico) + 1]
    except (ValueError, IndexError):
        siguiente_becario = becarios[0]

    asignacion.ultimo_medico = siguiente_becario
    asignacion.save()

    return siguiente_becario

@receiver(post_save, sender=Resumen)
def asignar_medicos(sender, instance, created, **kwargs):
    if created:
        especialidad = instance.especialidad

        with transaction.atomic():
            # Asignar todos los adscritos de la especialidad
            adscritos = Doctor.objects.filter(especialidad=especialidad, tipo='Adscrito')
            for adscrito in adscritos:
                instance.medico_adscrito.add(adscrito)
            
            # Asignar un becario de la especialidad
            becario = obtener_siguiente_becario(especialidad)
            instance.medico_becario = becario

            # Guardar el resumen con los médicos asignados
            instance.save()
