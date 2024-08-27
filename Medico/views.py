from django.shortcuts import render, redirect
from datetime import timedelta
from .decorators import doctor_tipo_required, status_permission_required
from django.contrib.auth.decorators import login_required 
from .models import Resumen, Especialidad, Doctor, Documento
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponseBadRequest, HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from .decorators import user_tipo_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.conf import settings
from .forms import ResumenForm
from django.contrib import messages
from django.templatetags.static import static
from django.utils.html import format_html
from django.core.mail import EmailMessage
from django.contrib.auth.models import Group
from django.utils.html import escape
from django.contrib.staticfiles import finders
import os
from datetime import datetime
from django.http import FileResponse



#--------------------Pagina principal----------------------
#---vista permitida solo para grupos de usuarios-----------
@login_required
def home(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        if doctor.tipo == 'Adscrito':
            return redirect('MedicosADS')
        elif doctor.tipo in ['Residente', 'Becario']:
            return redirect('MedicosRB')
    except Doctor.DoesNotExist:
        if request.user.is_superuser:
            return redirect('admin:index')
        else:
            #vericamos si el usuario pertenece al grupo administrador
            admin_group = Group.objects.get(name="Administrador")
            if admin_group in request.user.groups.all():
                return redirect('solicitud')
            else:
                return redirect('login')

        return render(request, 'home.html')
    return render(request, 'Medico/home.html')
#-----------------------------------------------------------



#------- VISTA DE MEDICOS 
#------Decorador login y user_tipo_required
@login_required 
@user_tipo_required(['Becario','Residente'])
#------------------------------------------
def lista_solicitudes_revision(request, Especialidad_id=None, edited_id=None):
    user = request.user
    try: 
        doctor = Doctor.objects.get(user=user)
    except Doctor.DoesNotExist:
        raise PermissionDenied("No tienes permisos para acceder a esta vista")

    if doctor.tipo == 'Becario':
        documentos_solicitud = Resumen.objects.filter(estado="Solicitud", medico_becario=doctor).order_by('-fecha_modificacion')
        documentos_revison = Resumen.objects.filter(estado="En revisión", medico_becario=doctor).order_by('-fecha_modificacion')
    elif doctor.tipo == 'Residente':
        documentos_solicitud = Resumen.objects.filter(estado="Solicitud", medico_residente=doctor).order_by('-fecha_modificacion')
        documentos_revison = Resumen.objects.filter(estado="En revisión", medico_residente=doctor).order_by('-fecha_modificacion')

   
    

    if Especialidad_id:
        Especialidad_obj = get_object_or_404(Especialidad, pk=Especialidad_id)
        documentos_solicitud = documentos_solicitud.filter(Especialidad=Especialidad_obj)
        documentos_revision = documentos_revision.filter(Especialidad=Especialidad_obj)

    especialidades = Especialidad.objects.all()
    residentes = Doctor.objects.filter(especialidad=doctor.especialidad, tipo="Residente")  
    
    count_en_revision = documentos_solicitud.count()
    count_solicitud = documentos_revison.count()
    
    
    return render(request, 'Medico/MedicosRB.html', {
        'documentos_solicitud': documentos_solicitud,
        'documentos_revision': documentos_revison,
        'especialidades': especialidades,
        'count_en_revision': count_en_revision,
        'count_solicitud': count_solicitud,
        'doctor':doctor,
        'residentes':residentes,
        'edited_id':edited_id,
        'doctor':doctor,
        
        
        })



@login_required
@user_tipo_required(['Adscrito'])
def lista_resumenes_adscrito(request, edited_id=None):
    user = request.user
    try: 
        doctor = Doctor.objects.get(user=user)
    except Doctor.DoesNotExist:
        if not request.user.is_superuser:
            raise PermissionDenied("No tiene los permisos para ingresar a esta página, por favor comuníquese con soporte")
    
    if doctor.tipo == "Adscrito":
        resumenes_revision = Resumen.objects.filter(estado="En revisión", medico_adscrito=doctor).order_by('-fecha_modificacion')
        resumenes_listos_para_enviar = Resumen.objects.filter(estado="Listo para enviar", medico_adscrito=doctor).order_by('-fecha_modificacion')
        resumenes_enviados = Resumen.objects.filter(estado="Enviado", medico_adscrito=doctor).order_by('-fecha_modificacion')

         # Conteo de cada categoría
        count_en_revision = resumenes_revision.count()
        count_listos_para_enviar = resumenes_listos_para_enviar.count()
        count_enviados = resumenes_enviados.count()

        print(f"{doctor}")
        return render(request, 'Medico/MedicosADS.html', {
            'en_revision': resumenes_revision,
            'listos_para_enviar': resumenes_listos_para_enviar,
            'enviados': resumenes_enviados,
            'count_en_revision': count_en_revision,
            'count_listos_para_enviar': count_listos_para_enviar,
            'count_enviados': count_enviados,
            'edited_id': edited_id,
            'doctor': doctor,
        })
    else:
        raise PermissionDenied("No tiene los permisos para acceder a esta vista.")
    




#-----------Renderiza, guarda, y cambio de status el resumen-------------------------------------
@login_required
@user_tipo_required(['Adscrito','Residente','Becario'])
def editar_documento(request, documento_id):
    user_tipo = request.user.doctor.tipo
    documento = Resumen.objects.get(id=documento_id)  
    if request.method == 'POST':
        content = request.POST.get('editordata')
        documento.texto = content 
        documento.save()
        
        try:
            doctor = Doctor.objects.get(user=request.user)
            if doctor.tipo == "Adscrito":
                return redirect('MedicosADS_with_id', edited_id=documento.id)
            elif doctor.tipo in ['Residente', 'Becario']:
                return redirect('MedicosRB_with_id', edited_id=documento.id)
        except Doctor.DoesNotExist:
              return redirect('home') 
    return render(request, 'Medico/editar_documento.html', {
        'documento': documento,
        'user_tipo': user_tipo,
        
        })
#--------------------------------------------------------------------------------------------------
@login_required
@user_tipo_required(['Becario'])
def asignar_medico_residente(request):
    if request.method == 'POST':
        resumen_id = request.POST.get('resumen_id')
        residente_id = request.POST.get('residente')
        
        resumen = get_object_or_404(Resumen, id=resumen_id)
        residente = get_object_or_404(Doctor, id=residente_id)
        
        resumen.medico_residente = residente
        resumen.save()

        subject = 'Tiene una nueva asignación de resumen'
        message = f'ha sido asignado para realizar el resumen con el número de expediente {resumen.numero_expediente}. entra a resumenesimo.ddns.net para revisarlo'
        from_email = 'arturo.olivares@imoiap.com.mx'
        recipient_list = [residente.email]

        try: 
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print(f'Error al enviar correo: {e}')
        
        return redirect('MedicosRB')

#------------Cambia el status del Resumen----------------------------------------------------------
@login_required
@user_tipo_required(['Adscrito','Becario'])
def cambiar_estado(request, documento_id):
    print("Entrando en la vista cambiar_estado")
    if request.method == 'POST':
        
        print("Solicitud POST recibida")
        documento = get_object_or_404(Resumen, id=documento_id)
        nuevo_estado = request.POST.get('nuevo_estado')
           # Log para verificar los datos recibidos
        print(f"Documento ID: {documento_id}")
        print(f"Nuevo estado: {nuevo_estado}")
        print(f"Estado actual: {documento.estado}")
        print(f"Usuario: {request.user.username}")
        print(f"Tipo de usuario: {request.user.doctor.tipo}")
        if nuevo_estado in ['En revisión', 'Listo para enviar', 'Enviado']:
            if documento.estado == 'Solicitud' and nuevo_estado == 'En revisión':
                documento.estado = nuevo_estado
                documento.save()
                print(f"Estado cambiado a: {documento.estado}")
            
            
            #envio de correo a los medicos adscritos para revisión
                if nuevo_estado == 'En revisión':
                    adscritos = documento.medico_adscrito.all()
                    email_addresses = [adscrito.user.email for adscrito in adscritos]
                
                    send_mail(
                        subject='Se ha solicitado la revisión de un resumen',
                        message= f'Se ha solicitado la revisión del resumen con numero de expedediente {documento.numero_expediente}',
                        from_email= settings.DEFAULT_FROM_EMAIL,
                        recipient_list=email_addresses,
                        fail_silently=False,
                        )
                try:
                    doctor = Doctor.objects.get(user=request.user)
                    if doctor.tipo == "Adscrito":
                        return redirect('MedicosADS')
                    elif doctor.tipo in ['Becario']:
                        return redirect('MedicosRB')
                except Doctor.DoesNotExist:
                    return redirect('home')
            else:
                documento.estado = nuevo_estado
                documento.save()
                print(f"Estado cambiado a: {documento.estado}")
         
    return redirect('home')
#--------------------------------------------------------------------------------------------------

###############################################################################################

@csrf_exempt
def generate_pdf(request):
    if request.method == "POST":
        content = request.POST.get('content')
        template = get_template('Medico/pdf_template.html')
        context = {'content': content}
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="output.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    return HttpResponse("Invalid request")


@login_required
def historial_resumen(request, resumen_id):
    resumen = get_object_or_404(Resumen, pk=resumen_id)
    historial = resumen.historial_estados.all().order_by('-fecha_cambio')
    return render(request, 'app/historial_resumen.html', {'resumen': resumen, 'historial': historial})



@login_required
def solicitud(request):
    if request.method == 'POST':
        paciente_nombre = request.POST['paciente_nombre']
        edad = request.POST['edad']
        numero_expediente = request.POST['numero_expediente']
        motivo_solicitud = request.POST['motivo_solicitud']
        especialidad_id = request.POST['especialidad']
        especialidad = Especialidad.objects.get(id=especialidad_id)
        correo_electronico = request.POST['correo_electronico']
        fecha_nacimiento = request.POST['fecha_nacimiento']
        genero = request.POST['genero']
       
        resumen = Resumen(
            paciente_nombre=paciente_nombre,
            edad=edad,
            numero_expediente=numero_expediente,
            motivo_solicitud=motivo_solicitud,
            especialidad=especialidad,
            correo_electronico=correo_electronico,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero
            
        )
        resumen.save()
        messages.success(request, 'La solicitud se ha creado exitosamente y se ha notificado al médico becario.')
        return redirect('home') 

    especialidades = Especialidad.objects.all()

    return render(request, 'Medico/solicitud.html', {'especialidades': especialidades})


#-----Para salir de la sesion--------------------
def exit(request):
    logout(request)
    return redirect('home')
#------------------------------------------------
    
#--------Para asignar medico residente-----------    
def asignar_medico_resumen(request, documento_id):
    if request.method == 'POST':
        medico_id = request.POST.get('medico_id')
        resumen_id = request.POST.get('resumen_id')

        
        if not medico_id or not resumen_id:
            return HttpResponseBadRequest("Falta el ID del médico o del resumen")
        medico = get_object_or_404(Doctor, id=medico_id)
        resumen = get_object_or_404(Resumen, id=resumen_id)
        resumen.medico_residente = medico
        resumen.save()
        return redirect('Medico/MedicosRB.html')
    return render(request, 'Medico/MedicosRB.html')
#------------------------------------------------------


#---Esta vista bronda la lista de resumenes con todos los detalles----------------
def lista_resumenes(request):
    especialidades = Especialidad.objects.all()
    resumenes = Resumen.objects.all()

    especialidad_ids = request.GET.getlist('especialidades')
    query = request.GET.get('q')

    if especialidad_ids:
        resumenes = resumenes.filter(especialidad__id__in=especialidad_ids)
    
    if query:
        resumenes = resumenes.filter(
            Q(paciente_nombre__icontains=query) |
            Q(numero_expediente__icontains=query) |
            Q(motivo_solicitud__icontains=query) |
            Q(especialidad__name__icontains=query) |
            Q(correo_electronico__icontains=query) |
            Q(texto__icontains=query)
        )
    
    
    resumenes = sorted(resumenes, key=lambda x: x.fecha_entrega_programada)
    
    return render(request, 'Medico/busqueda.html', {
        'resumenes': resumenes,
        'especialidades': especialidades,
    })
    
#-----------------------------------------------------------------------------------------

def mi_vista(request):
    return render(request, 'Medico/index.html')


################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################



@login_required
@user_tipo_required(['Adscrito', 'Residente', 'Becario'])
def editar_documento2(request, documento_id):
    documento = get_object_or_404(Resumen, id=documento_id)

    #user_tipo = request.user.doctor.tipo
    user_tipo = getattr(request.user, 'doctor', None)
    user_tipo = user_tipo.tipo if user_tipo else 'Administrador'


    if request.method == 'POST':
        form = ResumenForm(request.POST, instance=documento)
        if form.is_valid():
            form.save()
            #doctor = Doctor.objects.get(user=request.user)
            #if doctor.tipo == "Adscrito":
            #    return redirect('MedicosADS_with_id', edited_id=documento.id)
            #elif doctor.tipo in ['Residente', 'Becario']:
            #    return redirect('MedicosRB_with_id', edited_id=documento.id)
            messages.success(request, 'Documento guardado correctamente.')
            return redirect('editar_documento2', documento_id = documento.id)
    else:
        if not documento.texto:
            image_url = static('assets/img/imo.jpg')
            TEMPLATE_CONTENT = f"""
            
            
            <p style="line-height: 1; text-align: left; ">Padecimiento actual:</p>

            <p style="line-height: 1; text-align: left;">Diagnostico:</p>

            <p style="line-height: 1; text-align: left;">Tratamientos realizados:</p>

            <p style="line-height: 1; text-align: left;">Resultados de estudios de laboratorio y gabinete:</p>

            <p style="line-height: 1; text-align: left;">Evoluci&oacute;n:</p>

            <p style="line-height: 1; text-align: left;">Pronóstico:</p>
            
            <p style="line-height: 1;">
            	<br>
            </p>

            <p style="line-height: 1;">
            	<br>
            </p>

                        """

            documento.texto = TEMPLATE_CONTENT.format(
                nombre = documento.paciente_nombre,
                edad = documento.edad,
                expediente = documento.numero_expediente,
                #fecha = documento.fecha_nacimiento,
                #genero = documento.genero,

            )
        
        form = ResumenForm(instance=documento)

    return render(request, 'Medico/editar_documento2.html', {
        'form': form,
        'documento': documento,
        'user_tipo': user_tipo,
    })
    
    
@login_required
def insertar_firma(request, documento_id):
    documento = get_object_or_404(Resumen, id=documento_id)
    doctor = Doctor.objects.get(user=request.user)

    if request.method == 'POST':
        firma_electronica_url = doctor.firma_electronica.url
        print(firma_electronica_url)

        # Insertar los datos del doctor y la firma electrónica al final del contenido del documento
        firma_html = format_html(
            '<div style="text-align: center;"><img src="{}" alt="Firma Electrónica" style="width: 200px; height: 170px;"></div>', firma_electronica_url)
        documento.texto += str(firma_html)
        documento.save()
        print('SE GUARDO EL DOCUMENTO CON LA FIRMA')

        return redirect('editar_documento2', documento_id=documento_id)

    return render(request, 'Medico/editar_documento2.html', {'documento': documento})



def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    print(f"Processing URI: {uri}")  # Debugging line

    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        print(f"URI not handled: {uri}")  # Debugging line
        return uri

    if not os.path.isfile(path):
        print(f"File not found: {path}")  # Debugging line
        raise Exception(f'Media URI must start with {settings.MEDIA_URL} or {settings.STATIC_URL}')
    return path


@login_required
def enviar_documento(request, documento_id):
    documento = get_object_or_404(Resumen, id=documento_id)
    correo_paciente = request.POST.get('correo_paciente')

    if request.method == 'POST':
        # Renderizar la plantilla HTML a PDF
        template = get_template('Medico/pdf_template.html')
        content_with_absolute_urls = documento.texto.replace(
            '/media/', f'{request.build_absolute_uri(settings.MEDIA_URL)}'
        ).replace(
            '/static/', f'{request.build_absolute_uri(settings.STATIC_URL)}'
        )
        logo_url = request.build_absolute_uri(static('assets/img/imo.jpg'))
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
        context = {
            'content': content_with_absolute_urls,
            'nombre': documento.paciente_nombre,
            'expediente': documento.numero_expediente,
            'edad': documento.edad,
            'genero': documento.genero,
            'fecha_nacimiento': documento.fecha_nacimiento,
            'logo_url': logo_url,
            'fecha_actual': fecha_actual,

        }
        html = template.render(context)

        print(html)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename ="resumen.pdf"'

        pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)

        if pisa_status.err:
            return HttpResponse('Error al generar el PDF')

        # Enviar el correo electrónico
        try:
            email = EmailMessage(
                'Resumen Médico',
                'Adjunto encontrará su resumen médico en formato PDF.',
                settings.DEFAULT_FROM_EMAIL,
                [correo_paciente]
            )
            email.attach('resumen.pdf', response.content, 'application/pdf')
            email.send()
            print("Se envio el documento")
                # Cambiar el estado del documento a "Enviado"
            documento.estado = 'Enviado'
            documento.save()

            return redirect('MedicosADS_with_id', edited_id=documento_id)
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            return HttpResponse('Error al enviar el correo')

    return redirect('editar_documento2', documento_id=documento_id)



@login_required
def configuracion_view(request):
    print('Entrando a configuracion')    
    medicos = Doctor.objects.filter(tipo__in=['Becario', 'Residente'])
    especialidades = Especialidad.objects.all()
    nombre_usuario = request.user.get_full_name() or request.user.username
    return render(request, 'Medico/configuracion.html', {
        'medicos': medicos,
        'especialidades': especialidades,
        'nombre_usuario':nombre_usuario,
    })
    
@login_required
def modificar_especialidad(request, doctor_id):
    if request.method == 'POST':
        nueva_especialidad_id = request.POST.get('especialidad')
        doctor = get_object_or_404(Doctor, id=doctor_id)
        nueva_especialidad = get_object_or_404(Especialidad, id=nueva_especialidad_id)
        doctor.especialidad = nueva_especialidad
        doctor.save()
    return redirect('configuracion_view')

def descargar_pdf(request, documento_id):
    documento = get_object_or_404(Resumen, id=documento_id)

    # Ruta del archivo PDF
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'documentos')
    pdf_path = os.path.join(pdf_dir, f'{documento_id}.pdf')

    # Verificar si la carpeta existe, si no, crearla
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    # Si el archivo no existe, genera el PDF
    if not os.path.exists(pdf_path):
        # Renderizar la plantilla HTML a PDF
        template = get_template('Medico/pdf_template.html')
        context = {
            'content': documento.texto.replace('/media/', f'{request.build_absolute_uri(settings.MEDIA_URL)}'),
            'nombre': documento.paciente_nombre,
            'expediente': documento.numero_expediente,
            'edad': documento.edad,
            'fecha_actual': timezone.now().strftime("%d/%m/%Y"),
            'logo_url': request.build_absolute_uri(static('assets/img/imo.jpg'))
        }
        html = template.render(context)
        with open(pdf_path, 'wb') as pdf_file:
            pisa_status = pisa.CreatePDF(html, dest=pdf_file, link_callback=link_callback)
            if pisa_status.err:
                return HttpResponse('Error al generar el PDF')

    # Retornar el archivo PDF como respuesta
    return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')

