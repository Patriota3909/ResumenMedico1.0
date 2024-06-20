from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Resumen, Doctor, Asignacion, Especialidad

def obtener_siguiente_medico(especialidad, tipo_medico):
    # Obtener todos los médicos de la especialidad y tipo
    medicos = list(Doctor.objects.filter(especialidad=especialidad, tipo=tipo_medico).order_by('id'))
    
    if not medicos:
        return None
    
    # Obtener o crear el registro de asignación para la especialidad y tipo
    asignacion, created = Asignacion.objects.get_or_create(
        especialidad=especialidad,
        tipo_medico=tipo_medico,
        defaults={'ultimo_medico': medicos[0]}  # Usar el primer médico en la lista
    )
    
    # Encontrar el siguiente médico en la lista
    try:
        siguiente_medico = medicos[medicos.index(asignacion.ultimo_medico) + 1]
    except (ValueError, IndexError):
        siguiente_medico = medicos[0]
    
    # Actualizar el registro de asignación
    asignacion.ultimo_medico = siguiente_medico
    asignacion.save()
    
    return siguiente_medico

@receiver(post_save, sender=Resumen)
def asignar_medicos(sender, instance, created, **kwargs):
    if created:
        especialidad = instance.especialidad

        # Asignar un residente
        residente = obtener_siguiente_medico(especialidad, 'Residente')
        instance.medico_residente = residente

        # Asignar un adscrito
        adscrito = obtener_siguiente_medico(especialidad, 'Adscrito')
        instance.medico_adscrito = adscrito

        # Guardar el resumen con los médicos asignados
        instance.save()
