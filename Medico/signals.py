from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Resumen, Doctor, Asignacion, Especialidad
from django.core.mail import send_mail

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
            adscritos_emails = []

            for adscrito in adscritos:
                instance.medico_adscrito.add(adscrito)
                adscritos_emails.append(adscrito.email)
            
            # Asignar un becario de la especialidad
            becario = obtener_siguiente_becario(especialidad)
            instance.medico_becario = becario

            # Guardar el resumen con los médicos asignados
            instance.save()

            #Enviar correos de notificacion
            if adscritos_emails or becario:
                subject = 'Nuevo resumen medico asignado'
                message = f'Se ha asignado un nuevo resumen con el numero de expediente {instance.numero_expediente}. Revisalo en tu plataforma de resumenes medicos en la siguiente dirección: resumenesimo.ddns.net'
                from_email = 'arturo.olivares@imoiap.com.mx'

                recipient_list = adscritos_emails
                if becario:
                    recipient_list.append(becario.email)

                try:
                    send_mail(subject, message, from_email, recipient_list)
                except Exception as e:
                    print(f'Error al enviar el correo {e}')
