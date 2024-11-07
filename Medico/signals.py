from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Resumen, Doctor, Asignacion, Especialidad
from django.core.mail import send_mail


ESPECIALIDADES_CON_ADSCRITO_Y_BECARIO = ['Retina', 'Segmento Anterior', 'Estrabismo', 'Glaucoma','Baja Visión']
ESPECIALIDADES_CON_ADSCRITO_Y_RESIDENTE = ['Primera Vez', 'Uveitis', 'Oculoplástica']

def obtener_siguiente_medico(especialidad=None, tipo_medico=None, especialidad_especifica=True):
    
    especialidad_obj = None 

    if not especialidad_especifica:
        medicos = list(Doctor.objects.filter(tipo=tipo_medico).order_by('id')) 
    else:
        if especialidad:
            try:
                especialidad_obj = Especialidad.objects.get(name=especialidad)
            except Especialidad.DoesNotExist:
                print(f"Especialidad {especialidad} no encontrada.")
                return None

        # Si la especialidad está presente, filtra por especialidad y tipo de médico
        medicos = list(Doctor.objects.filter(especialidad=especialidad_obj, tipo=tipo_medico, active = True).order_by('id'))

    if not medicos:
        return None

    # Para residentes, no vinculamos a ninguna especialidad específica
    if especialidad_especifica:
        asignacion, created = Asignacion.objects.get_or_create(
            especialidad=especialidad_obj,
            tipo_medico=tipo_medico,
            defaults={'ultimo_medico': medicos[0]}  # Iniciar con el primer médico si es la primera vez
        )
    else:
        asignacion, created = Asignacion.objects.get_or_create(
            especialidad=None,  # Ignoramos la especialidad para residentes
            tipo_medico=tipo_medico,
            defaults={'ultimo_medico': medicos[0]}  # Iniciar con el primer médico si es la primera vez
        )

    # Encuentra el siguiente médico en la lista de manera rotativa
    try:
        siguiente_medico = medicos[medicos.index(asignacion.ultimo_medico) + 1]
    except (ValueError, IndexError):
        siguiente_medico = medicos[0]  # Si llega al final, vuelve al inicio

    # Actualiza el último médico asignado y guarda la asignación
    asignacion.ultimo_medico = siguiente_medico
    asignacion.save()

    return siguiente_medico


@receiver(post_save, sender=Resumen)
def asignar_medicos(sender, instance, created, **kwargs):
    if created:
        especialidad_nombre = instance.especialidad.name  # Asumiendo que la especialidad tiene un campo 'name'

        # Lista para almacenar los correos de los médicos asignados
        recipient_list = []

        with transaction.atomic():
            # Asignar siempre un adscrito de la especialidad
            adscrito = obtener_siguiente_medico(especialidad_nombre, 'Adscrito')
            if adscrito:
                instance.medico_adscrito.add(adscrito)
                recipient_list.append(adscrito.email)

            # Si la especialidad es una de las que requiere un residente
            if especialidad_nombre in ESPECIALIDADES_CON_ADSCRITO_Y_RESIDENTE:
                # Asignar un residente sin importar la especialidad
                residente = obtener_siguiente_medico(tipo_medico='Residente', especialidad_especifica=False)
                if residente:
                    instance.medico_residente = residente
                    recipient_list.append(residente.email)

            elif especialidad_nombre in ESPECIALIDADES_CON_ADSCRITO_Y_BECARIO:
                # Asignar un becario de la especialidad
                becario = obtener_siguiente_medico(especialidad_nombre, 'Becario')
                if becario:
                    instance.medico_becario = becario
                    recipient_list.append(becario.email)

            # Guardar el resumen con los médicos asignados (dentro de la transacción atómica)
            instance.save()

        # Enviar correos de notificación (fuera de la transacción atómica)
        if recipient_list:
            subject = 'Nuevo resumen médico asignado'
            message = f'Se ha asignado un nuevo resumen con el número de expediente {instance.numero_expediente}. Revisa la plataforma de resúmenes médicos en la siguiente dirección: resumenesimo.ddns.net'
            from_email = 'resumenes.imo@imoiap.com.mx'

            try:
                send_mail(subject, message, from_email, recipient_list)
            except Exception as e:
                print(f"Error al enviar el correo: {e}")
