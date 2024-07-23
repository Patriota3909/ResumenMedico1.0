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
from django.utils.html import format_html
from django.core.mail import EmailMessage
from django.contrib.auth.models import Group
from django.utils.html import escape



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
    
    
    return render(request, 'Medico/MedicosRB.html', {
        'documentos_solicitud': documentos_solicitud,
        'documentos_revision': documentos_revison,
        'especialidades': especialidades,
        'doctor':doctor,
        'residentes':residentes,
        'edited_id':edited_id,
        
        
        })
@login_required
@user_tipo_required(['Adscrito'])
def lista_resumenes_adscrito(request, edited_id=None):
    
    #Obtenemos la especialidad del doctor
    especialidad = None
    try: 
        doctor = Doctor.objects.get(user=request.user)
        especialidad = doctor.especialidad
    #Fitlamos los resumenes por estado y por la especialidad del medico
    except Doctor.DoesNotExist:
        if not request.user.is_superuser:
            raise PermissionDenied("No tiene los permisos para ingresar a esta pagina, por favor comincate con soporte")
                
    en_revision = Resumen.objects.filter(estado='En revisión', especialidad=especialidad)
    listos_para_enviar = Resumen.objects.filter(estado='Listo para enviar', especialidad=especialidad)
    enviados = Resumen.objects.filter(estado='Enviado', especialidad=especialidad)

    return render(request, 'Medico/MedicosADS.html', {
        'en_revision': en_revision,
        'listos_para_enviar': listos_para_enviar,
        'enviados': enviados,
        'edited_id': edited_id,
    })

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
        message = f'ha sido asignado para realizar el resumen con el número de expediente {resumen.numero_expediente}. entra a tu plataforma .... para revisarlo'
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
       
        resumen = Resumen(
            paciente_nombre=paciente_nombre,
            edad=edad,
            numero_expediente=numero_expediente,
            motivo_solicitud=motivo_solicitud,
            especialidad=especialidad,
            correo_electronico=correo_electronico,
            
        )
        resumen.save()
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
TEMPLATE_CONTENT ="""
<p><img src="{{ MEDIA_URL }}img/image.png" style="width: 64px;" class="fr-fic fr-dii fr-fil fr-rounded">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;Quer&eacute;taro, Qro. a__ del mes__ del a&ntilde;o 20___</p>

<p style="text-align: center;"><strong>RESUMEN M&Eacute;DICO</strong></p>

<p style="text-align: center;"><strong>_________________________________________________________________________________</strong></p>

<ul>
	<li style="text-align: left; line-height: 1;">Nombre del paciente: <strong>{nombre}</strong></li>
	<li style="text-align: left; line-height: 1;">N&uacute;mero de expediente: <strong>{expediente}</strong></li>
	<li style="text-align: left; line-height: 1;">Edad: <strong>{edad}</strong></li>
	<li style="text-align: left; line-height: 1;">G&eacute;nero:&nbsp;</li>
	<li style="text-align: left; line-height: 1;">Fecha de nacimiento:</li>
</ul>

<p style="margin-left: 40px; text-align: center;"><span style="font-size: 12px;"><u>INFORME</u></span></p>

<p style="margin-left: 40px; text-align: left;"><span style="font-size: 12px;">Padecimiento actual:</span></p>

<p style="margin-left: 40px; text-align: left;"><span style="font-size: 12px;"><br></span></p>

<p style="margin-left: 40px; text-align: left;"><span style="font-size: 12px;"><strong>Diagnostico:</strong></span></p>

<p style="margin-left: 40px; text-align: left;"><span style="font-size: 12px;"><strong>Tratamientos&nbsp;</strong><strong>realizados</strong>:</span></p>

<p style="margin-left: 40px; text-align: left;"><span style="font-size: 12px;"><strong>Resultados&nbsp;</strong><strong>de&nbsp;</strong><strong>estudios&nbsp;</strong><strong>de&nbsp;</strong><strong>laboratorio&nbsp;</strong><strong>y&nbsp;</strong><strong>gabinete</strong>:</span></p>

<p style="margin-left: 40px; text-align: left;"><span style="font-size: 12px;"><strong>Evoluci&oacute;n</strong>:</span></p>

<p style="margin-left: 40px; text-align: left;">
	<br>
</p>

<p style="margin-left: 40px; text-align: left;">
	<br>
</p>

<p>
	<br>
</p>

<table style="width: 46%; margin-right: 54%;">
	<thead>
		<tr>
			<th colspan="3" style="width: 99.723%;" class="fr-thick"><span style="font-size: 12px;"><span style="font-family: Tahoma, Geneva, sans-serif;">PRON&Oacute;STICO (PARA LA VIDA Y PARA LA FUNCI&Oacute;N)</span>&nbsp;</span></th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td style="width: 25.6283%; vertical-align: middle; text-align: center;" class="fr-thick"><span style="font-size: 11px;"><br></span></td>
			<td style="width: 37.3583%; vertical-align: middle; text-align: center;" class="fr-thick"><span style="font-size: 11px;">FUNCI&Oacute;N</span></td>
			<td style="width: 35.0152%; vertical-align: middle; text-align: center;" class="fr-thick"><span style="font-size: 11px;">VIDA</span></td>
		</tr>
		<tr>
			<td style="width: 25.6283%; vertical-align: middle; text-align: center;" class="fr-thick"><span style="font-size: 11px;">Favorable</span></td>
			<td style="width: 37.3583%; vertical-align: middle; text-align: center;" class="fr-thick"><span style="font-size: 11px;"><br></span></td>
			<td style="width: 35.0152%; vertical-align: middle; text-align: center;" class="fr-thick"><span style="font-size: 11px;"><br></span></td>
		</tr>
		<tr>
			<td style="width: 25.6283%; vertical-align: middle; text-align: center;" class="fr-thick"><span style="font-size: 11px;">Reservado</span></td>
			<td style="width: 37.3583%; vertical-align: middle; text-align: center;" class="fr-thick"><span style="font-size: 11px;"><br></span></td>
			<td style="width: 35.0152%; vertical-align: middle; text-align: center;" class="fr-thick"><span style="font-size: 11px;"><br></span></td>
		</tr>
		<tr>
			<td style="width: 25.6283%; vertical-align: middle; text-align: center;" class="fr-thick"><span style="font-size: 11px;">Desfavorable</span></td>
			<td style="width: 37.3583%; vertical-align: middle; text-align: center;" class="fr-thick"><span style="font-size: 11px;"><br></span></td>
			<td style="width: 35.0152%; vertical-align: middle; text-align: center;" class="fr-thick"><span style="font-size: 11px;"><br></span></td>
		</tr>
	</tbody>
</table>
<br>

"""




@login_required
@user_tipo_required(['Adscrito', 'Residente', 'Becario'])
def editar_documento2(request, documento_id):
    user_tipo = request.user.doctor.tipo
    documento = get_object_or_404(Resumen, id=documento_id)

    if request.method == 'POST':
        form = ResumenForm(request.POST, instance=documento)
        if form.is_valid():
            form.save()
            doctor = Doctor.objects.get(user=request.user)
            if doctor.tipo == "Adscrito":
                return redirect('MedicosADS_with_id', edited_id=documento.id)
            elif doctor.tipo in ['Residente', 'Becario']:
                return redirect('MedicosRB_with_id', edited_id=documento.id)
    else:
        if not documento.texto:
            documento.texto = TEMPLATE_CONTENT.format(
                nombre = documento.paciente_nombre,
                edad = documento.edad,
                expediente = documento.numero_expediente,

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
            '<div style="text-align: center;"><img src="{}" alt="Firma Electrónica" style="width: 100px; height: 100px;"></div>', firma_electronica_url)
        documento.texto += firma_html
        documento.save()

        return redirect('editar_documento2', documento_id=documento_id)

    return render(request, 'Medico/editar_documento2.html', {'documento': documento})

@login_required
def enviar_documento(request, documento_id):
    documento = get_object_or_404(Resumen, id=documento_id)
    correo_paciente = request.POST.get('correo_paciente')

    if request.method == 'POST':
        # Renderizar la plantilla HTML a PDF
        template = get_template('Medico/pdf_template.html')
        content_with_absolute_urls = documento.texto.replace(
            '/media/', f'{request.build_absolute_uri(settings.MEDIA_URL)}'
        )
        context = {
            'content': content_with_absolute_urls
        }
        html = template.render(context)
        print(html)
        response = HttpResponse(content_type='application/pdf')
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error al generar el PDF')

        # Enviar el correo electrónico
        email = EmailMessage(
            'Resumen Médico',
            'Adjunto encontrará su resumen médico en formato PDF.',
            'from@example.com',
            [correo_paciente]
        )
        email.attach('resumen.pdf', response.content, 'application/pdf')
        email.send()
        print("Se envio el documento")
                # Cambiar el estado del documento a "Enviado"
        documento.estado = 'Enviado'
        documento.save()

        return redirect('MedicosADS_with_id', edited_id=documento_id)

    return redirect('editar_documento2', documento_id=documento_id)


@login_required
def configuracion_view(request):
    print('Entrando a configuracion')    
    medicos = Doctor.objects.filter(tipo__in=['Becario', 'Residente'])
    especialidades = Especialidad.objects.all()
    return render(request, 'Medico/configuracion.html', {
        'medicos': medicos,
        'especialidades': especialidades
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

