from django.shortcuts import render, redirect
from datetime import timedelta
from .decorators import doctor_tipo_required, status_permission_required
from django.contrib.auth.decorators import login_required 
from .models import Resumen, Especialidad, Doctor, Documento, Comentario
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
from django.core.paginator import Paginator
import base64
from datetime import datetime
from django.http import FileResponse
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from django.http import JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from cryptography.fernet import Fernet
import requests
from oauthlib.oauth1 import SIGNATURE_HMAC_SHA256, Client



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
    
    es_unico_becario = False
    

    if doctor.tipo == 'Becario':
        becarios_en_especialidad = Doctor.objects.filter(especialidad=doctor.especialidad, tipo = 'Becario').count()
        if becarios_en_especialidad == 1:
            es_unico_becario = True
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
    residentes = Doctor.objects.filter(tipo="Residente")  
    
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
        'es_unico_becario': es_unico_becario,
        
        
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
        resumenes_total = Resumen.objects.filter(especialidad=doctor.especialidad).order_by('-fecha_modificacion')
         # Conteo de cada categoría
        
        
        count_en_revision = resumenes_revision.count()
        count_listos_para_enviar = resumenes_listos_para_enviar.count()
        count_enviados = resumenes_enviados.count()
        count_total = resumenes_total.count()

        print(f"{doctor}")
        return render(request, 'Medico/MedicosADS.html', {
            'en_revision': resumenes_revision,
            'listos_para_enviar': resumenes_listos_para_enviar,
            'enviados': resumenes_enviados,
            'total': resumenes_total,
            'count_en_revision': count_en_revision,
            'count_listos_para_enviar': count_listos_para_enviar,
            'count_enviados': count_enviados,
            'edited_id': edited_id,
            'count_total': count_total,
            'doctor': doctor,
        })
    else:
        raise PermissionDenied("No tiene los permisos para acceder a esta vista.")
    





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
@user_tipo_required(['Adscrito','Becario','Residente'])
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
                        message= f'Se ha solicitado la revisión del resumen con numero de expedediente {documento.numero_expediente}. Puedes revisarlo en la plataforma resumenesimo.ddns.net',
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
        try:
            especialidad = Especialidad.objects.get(id=especialidad_id)
        except Especialidad.DoesNotExist:
            messages.error(request ,'la especialidad seleccionada no existe')
            return redirect('solicitud')    
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

    # Filtrar por especialidades si está presente en la solicitud
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

    # Dividir los resúmenes en dos listas: no enviados y enviados
    no_enviados = [resumen for resumen in resumenes if resumen.estado != "Enviado"]
    enviados = [resumen for resumen in resumenes if resumen.estado == "Enviado"]

    # Ordenar por fecha_entrega_programada
    no_enviados.sort(key=lambda x: x.fecha_entrega_programada)
    enviados.sort(key=lambda x: x.fecha_entrega_programada)

    # Combinar ambas listas
    resumenes_ordenados = no_enviados + enviados

    # Paginación
    paginator = Paginator(resumenes_ordenados, 10)  # Mostramos 10 resúmenes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'Medico/busqueda.html', {
        'page_obj': page_obj,
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
    comentarios = Comentario.objects.filter(resumen=documento).order_by('-fecha_de_creacion')

    #user_tipo = request.user.doctor.tipo
    user_tipo = getattr(request.user, 'doctor', None)
    user_tipo = user_tipo.tipo if user_tipo else 'Administrador'
    
    total_comments_count = Comentario.objects.filter(resumen=documento).count()

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
            
            
            <p style= "text-align: left; ">Padecimiento actual: </p>
            
            <p style= "text-align: left; ">Exploración oftalmológica: </p>

            <p style= "text-align: left;">Diagnóstico: </p>

            <p style= "text-align: left;">Tratamientos realizados: </p>

            <p style= "text-align: left;">Resultados de estudios de laboratorio y gabinete: </p>

            <p style= "text-align: left;">Evoluci&oacute;n: </p>

            <p style= "text-align: left;">Pronóstico: </p>

                        """

            documento.texto = TEMPLATE_CONTENT.format(
                nombre = documento.paciente_nombre,
                edad = documento.edad,
                expediente = documento.numero_expediente,
                
                #fecha = documento.fecha_nacimiento,
                #genero = documento.genero,

            )
        
        form = ResumenForm(instance=documento)
    print(f"comentarios: {comentarios}")
    return render(request, 'Medico/editar_documento2.html', {
        'form': form,
        'documento': documento,
        'user_tipo': user_tipo,
        'comentarios': comentarios,
        'total_comments_count': total_comments_count,
    })
    
    



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
def configuracion_view(request):
    print('Entrando a configuracion')    
    medicos = Doctor.objects.filter(tipo__in=['Becario', 'Residente','Adscrito'])
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
        doctor.activo = 'activo' in request.POST
    return redirect('configuracion_view')

@login_required
def modificar_estado_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    print(f'Entrando a modificar estado de doctor')
   
    if request.method == 'POST':
        activo = request.POST.get('active') == 'True'
        doctor.active = activo
        doctor.save()
        messages.success(request, 'Se ha configuirado el  estado del médico')
    return redirect('configuracion_view')  

@login_required
@user_tipo_required(['Adscrito', 'Residente', 'Becario'])
def agregar_comentario(request, documento_id):
    if request.method == 'POST':
        comentario_texto = request.POST.get('comentario')
        if comentario_texto:
            documento = get_object_or_404(Resumen, id=documento_id)
            Comentario.objects.create(
                resumen=documento,
                usuario=request.user,
                comentario=comentario_texto
            )
            # Redirigir a la misma página para recargar los comentarios
            return redirect('editar_documento2', documento_id=documento_id)

    return redirect('editar_documento2', documento_id=documento_id)



#__________________________________________________________________________________

#intento con weasyprint
@login_required
def generar_pdf_weasyprint(request, documento_id):
    # Obtener el documento o resumen
    documento = get_object_or_404(Resumen, id=documento_id)

    # Cargar la plantilla HTML para renderizarla como PDF
    template = get_template('Medico/pdf_template_weasyprint.html')  # Cambiamos el nombre de la plantilla
    
    # Procesar el contenido de Summernote
    content_with_absolute_urls = documento.texto.replace(
        '/media/', request.build_absolute_uri(settings.MEDIA_URL)
    ).replace(
        '/static/', request.build_absolute_uri(settings.STATIC_URL)
    )

    # Obtener la firma electrónica del doctor
    doctor = Doctor.objects.get(user=request.user)
    firma_electronica_url = doctor.firma_electronica.url

    # Generar el código QR con el enlace al resumen
    resumen_url = request.build_absolute_uri(f'/descargar_pdf/{documento_id}/')
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=2,
    )
    qr.add_data(resumen_url)
    qr.make(fit=True)

    # Generar la imagen del QR en memoria
    qr_io = BytesIO()
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_io, 'PNG')
    qr_io.seek(0)
    qr_base64 = base64.b64encode(qr_io.getvalue()).decode('utf-8')
    qr_url = f"data:image/png;base64,{qr_base64}"

    # Obtener otras variables necesarias
    logo_url = request.build_absolute_uri(static('assets/img/imo_original.svg'))
    logo_foo = request.build_absolute_uri(static('assets/img/footer.png'))
    fecha_actual = datetime.now().strftime('%d/%m/%Y')
    fecha_solicitud = documento.fecha_solicitud.strftime('%d/%m/%Y')

    # Contexto para renderizar en la plantilla
    context = {
        'content': content_with_absolute_urls,
        'nombre': documento.paciente_nombre,
        'expediente': documento.numero_expediente,
        'edad': documento.edad,
        'genero': documento.genero,
        'fecha_nacimiento': documento.fecha_nacimiento,
        'fecha_solicitud': fecha_solicitud,
        'logo_url': logo_url,
        'fecha_actual': fecha_actual,
        'logo_foo': logo_foo,
        'firma_electronica': firma_electronica_url,  # Añadir firma
        'codigo_qr': qr_url,  # Añadir código QR,
        'medico_becario': documento.medico_becario,
        'especialidad': documento.especialidad,
    }

    # Renderizar el contenido HTML
    html = template.render(context)

    # Usar WeasyPrint para convertir el HTML a PDF
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'inline; filename="resumen_medico.pdf"'

    response['X-Frame-Options'] = 'ALLOWALL'

    # Crear el PDF usando WeasyPrint
    HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response)

    return response


@login_required
def enviar_documento_weasyprint(request, documento_id):
    documento = get_object_or_404(Resumen, id=documento_id)
    correo_paciente = request.POST.get('correo_paciente')

    if request.method == 'POST':
        # Renderizar la plantilla HTML a PDF
        template = get_template('Medico/pdf_template_weasyprint.html')

        # Procesar el contenido del documento
        content_with_absolute_urls = documento.texto.replace(
            '/media/', f'{request.build_absolute_uri(settings.MEDIA_URL)}'
        ).replace(
            '/static/', f'{request.build_absolute_uri(settings.STATIC_URL)}'
        )

        # Obtener firma electrónica del médico
        doctor = Doctor.objects.get(user=request.user)
        firma_electronica_url = request.build_absolute_uri(doctor.firma_electronica.url)

        # Generar el código QR
        resumen_url = request.build_absolute_uri(f'/descargar_pdf/{documento_id}/')
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=2,
        )
        qr.add_data(resumen_url)
        qr.make(fit=True)

        # Generar la imagen del QR en memoria
        qr_io = BytesIO()
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(qr_io, 'PNG')
        qr_io.seek(0)
        qr_base64 = base64.b64encode(qr_io.getvalue()).decode('utf-8')
        qr_url = f"data:image/png;base64,{qr_base64}"

        # Variables para el template
        logo_url = request.build_absolute_uri(static('assets/img/imo_original.svg'))
        logo_foo = request.build_absolute_uri(static('assets/img/footer.png'))
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
        fecha_solicitud = documento.fecha_solicitud.strftime('%d/%m/%Y')

        # Contexto para el template
        context = {
            'content': content_with_absolute_urls,
            'nombre': documento.paciente_nombre,
            'expediente': documento.numero_expediente,
            'edad': documento.edad,
            'genero': documento.genero,
            'fecha_nacimiento': documento.fecha_nacimiento,
            'logo_url': logo_url,
            'fecha_actual': fecha_actual,
            'logo_foo': logo_foo,
            'fecha_solicitud': fecha_solicitud,
            'firma_electronica': firma_electronica_url,
            'codigo_qr': qr_url,
            'especialidad': documento.especialidad,
        }

        # Crear el PDF
        html = template.render(context)
        pdf_file = BytesIO()
        HTML(string=html).write_pdf(pdf_file)
        pdf_file.seek(0)

        # Enviar el correo electrónico con el archivo PDF adjunto
        try:
            email = EmailMessage(
                'Resumen Médico',
                'Adjunto encontrará su resumen médico en formato PDF.',
                settings.DEFAULT_FROM_EMAIL,
                [correo_paciente]
            )
            email.attach('resumen_medico.pdf', pdf_file.getvalue(), 'application/pdf')
            email.send()

            # Cambiar el estado del documento a "Enviado"
            documento.estado = 'Enviado'
            documento.save()

            return redirect('MedicosADS_with_id', edited_id=documento_id)
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            return HttpResponse('Error al enviar el correo')

    return redirect('editar_documento2', documento_id=documento_id)

@login_required
def generar_pdf_busqueda(request, documento_id):
    # Obtener el documento o resumen
    documento = get_object_or_404(Resumen, id=documento_id)

    # Cargar la plantilla HTML para renderizarla como PDF
    template = get_template('Medico/pdf_template_weasyprint.html')  
    
    # Procesar el contenido de Summernote
    content_with_absolute_urls = documento.texto.replace(
        '/media/', request.build_absolute_uri(settings.MEDIA_URL)
    ).replace(
        '/static/', request.build_absolute_uri(settings.STATIC_URL)
    )

    # Obtener la firma electrónica del primer medico adscrito
    firma_electronica_url = None
    if documento.medico_adscrito.exists():
        doctor_adscrito = documento.medico_adscrito.first()  # Primer médico adscrito
        firma_electronica_url = doctor_adscrito.firma_electronica.url

    # Obtener el nombre del médico becario
    medico_becario_nombre = documento.medico_becario

    # Generar el código QR con el enlace al resumen
    resumen_url = request.build_absolute_uri(f'/descargar_pdf/{documento_id}/')
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=2,
    )
    qr.add_data(resumen_url)
    qr.make(fit=True)

    # Generar la imagen del QR en memoria
    qr_io = BytesIO()
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_io, 'PNG')
    qr_io.seek(0)
    qr_base64 = base64.b64encode(qr_io.getvalue()).decode('utf-8')
    qr_url = f"data:image/png;base64,{qr_base64}"

    # Obtener otras variables necesarias
    logo_url = request.build_absolute_uri(static('assets/img/imo_original.svg'))
    logo_foo = request.build_absolute_uri(static('assets/img/footer.png'))
    fecha_actual = datetime.now().strftime('%d/%m/%Y')
    fecha_solicitud = documento.fecha_solicitud.strftime('%d/%m/%Y')

    # Contexto para renderizar en la plantilla
    context = {
        'content': content_with_absolute_urls,
        'nombre': documento.paciente_nombre,
        'expediente': documento.numero_expediente,
        'edad': documento.edad,
        'genero': documento.genero,
        'fecha_nacimiento': documento.fecha_nacimiento,
        'fecha_solicitud': fecha_solicitud,
        'logo_url': logo_url,
        'fecha_actual': fecha_actual,
        'logo_foo': logo_foo,
        'firma_electronica': firma_electronica_url,  # Añadir la firma del primer adscrito
        'codigo_qr': qr_url,  # Añadir código QR,
        'medico_becario': medico_becario_nombre,  # Añadir nombre del becario
        'especialidad': documento.especialidad,
    }

    # Renderizar el contenido HTML
    html = template.render(context)

    # Usar WeasyPrint para convertir el HTML a PDF
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'inline; filename="resumen_medico.pdf"'

    # Crear el PDF usando WeasyPrint
    HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response)

    return response


def pdfview(request):
    return render(request, 'Medico/pdfview.html')


def pdfview2(request):
    return render(request, 'Medico/pdfview2.html')
    


    
def obtener_licencia(request):
    cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode("utf-8"))
    decrypted_license = cipher_suite.decrypt(settings.FLIPBOOK_LICENSE_KEY.encode("utf-8")).decode("utf-8")
    return JsonResponse({'license_key': decrypted_license})

@csrf_exempt
def get_patient(request):
    
    if request.method == 'POST':
        USERID = request.POST.get('USERID')
        UUID = request.POST.get('UUID')
        Fecha = request.POST.get('Fecha')
        token = request.POST.get('token')
        
        print(f"Token recibido: '{token}'")
        print(f"Token esperado (trusted_token): '{settings.MY_TOKEN}'")
        
        if not all ([USERID, UUID, Fecha, token]):
            return JsonResponse({'error': 'No mams falta algun campo.',  'status_code':441}, status=441)
        
        trusted_token = settings.MY_TOKEN 
        
        if token != trusted_token:
            print("Token no coincide.")
            return JsonResponse({'error': 'Esta mal el token car.',  'status_code':403}, status=403)

        
        #entity_id = "185355"
    
        CONSUMER_KEY = settings.CONSUMER_KEY
        CONSUMER_SECRET = settings.CONSUMER_SECRET
        REALM = settings.REALM
        TOKEN_KEY = settings.TOKEN_KEY
        TOKEN_SECRET = settings.TOKEN_SECRET

        URL = f"https://{REALM.lower().replace('_', '-')}.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=1569&deploy=1&entityid={USERID}"


        client = Client(
            CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=TOKEN_KEY,
            resource_owner_secret=TOKEN_SECRET,
            signature_method=SIGNATURE_HMAC_SHA256,
            realm=REALM,
            signature_type='AUTH_HEADER'
        )

        uri, headers, body = client.sign(URL, http_method='GET')
    
        try: 
            response = requests.get(URL, headers=headers, data=body )

            if response.status_code == 200:
                print(f"Esta es la respuesta {response.text}")
                response_data = response.json()
                
                if response_data .get('success') == False:
                    return JsonResponse({'error': 'Este chavo(a)(e) no esta en netsuite', 'status_code':440}, status=440)
                
                
                mail = response_data.get('data', {}).get('mail','')
                
                if not mail:
                    return JsonResponse({'message':'Si esta pero sin correo'}, status=442)
                else:
                    message = 'Todo cul si existe y con correo' 
                    
                # Generación del PDF con WeasyPrint
                nombre_paciente = response_data.get('data', {}).get('name', 'Paciente Desconocido')
                
                # Renderizamos una plantilla HTML para el PDF
                html_string = render_to_string('Medico/pdf_brazalete.html', {
                    'nombre': nombre_paciente,
                    'uuid': UUID,
                    'fecha': Fecha,
                })
                
                # Convertimos la plantilla HTML a PDF usando WeasyPrint
                pdf_file = BytesIO()
                HTML(string=html_string).write_pdf(pdf_file)
                pdf_file.seek(0)

                # Enviamos el correo con el PDF adjunto
                email = EmailMessage(
                    subject='Resumen de Paciente',
                    body='Adjunto encontrarás el PDF con los detalles del paciente.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[mail]
                )
                email.attach('resumen_paciente.pdf', pdf_file.getvalue(), 'application/pdf')
                
                try:
                    email.send()
                    return JsonResponse({'message': 'Correo enviado con éxito'}, status=200)
                except Exception as e:
                    return JsonResponse({'error': f'Error al enviar el correo: {str(e)}'}, status=500)
                
                
                return JsonResponse({'Simon👌': message}, status=200)
            else:
                return JsonResponse({'error': "Error en la consulta", 'status_code':441}, status=441)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': "Error en la consulta a la API", 'detalles': str(e)}, status=500)
    return JsonResponse({'error': 'Mal peticion -_-'}, status=405)



def lista(request):
    doctores = Doctor.objects.select_related('user')  # Optimiza la consulta
    return render(request, 'Medico/lista.html', {'doctores': doctores})