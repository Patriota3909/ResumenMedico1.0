from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Resumen, Doctor, Asignacion, Especialidad
from django.core.mail import send_mail
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Resumen, Doctor, Asignacion, Especialidad
from django.core.mail import send_mail

def obtener_siguiente_medico(especialidad, tipo_medico):
    medicos = list(Doctor.objects.filter(especialidad=especialidad, tipo=tipo_medico).order_by('id'))
    
    if not medicos:
        return None

    asignacion, created = Asignacion.objects.get_or_create(
        especialidad=especialidad,
        tipo_medico=tipo_medico,
        defaults={'ultimo_medico': medicos[0]}  # Usar el primer médico en la lista
    )

    try:
        siguiente_medico = medicos[medicos.index(asignacion.ultimo_medico) + 1]
    except (ValueError, IndexError):
        siguiente_medico = medicos[0]

    asignacion.ultimo_medico = siguiente_medico
    asignacion.save()

    return siguiente_medico

@receiver(post_save, sender=Resumen)
def asignar_medicos(sender, instance, created, **kwargs):
    if created:
        especialidad = instance.especialidad

        with transaction.atomic():
            # Asignar un adscrito de la especialidad
            adscrito = obtener_siguiente_medico(especialidad, 'Adscrito')
            if adscrito:
                instance.medico_adscrito.add(adscrito)
                adscrito_email = [adscrito.email]
            else:
                adscrito_email = []

            # Asignar un becario de la especialidad
            becario = obtener_siguiente_medico(especialidad, 'Becario')
            instance.medico_becario = becario

            # Guardar el resumen con los médicos asignados
            instance.save()

            #Enviar correos de notificacion
            recipient_list = adscrito_email
            if becario:
                recipient_list.append(becario.email)

            if recipient_list:
                subject = 'Nuevo resumen medico asignado'
                message = f'Se ha asignado un nuevo resumen con el numero de expediente {instance.numero_expediente}. Revisalo en tu plataforma de resumenes medicos en la siguiente dirección: resumenesimo.ddns.net'
                from_email = 'arturo.olivares@imoiap.com.mx'

                try:
                    send_mail(subject, message, from_email, recipient_list)
                except Exception as e:
                    print(f'Error al enviar el correo {e}')
