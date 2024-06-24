from django.shortcuts import render, redirect
from .decorators import doctor_tipo_required, status_permission_required
from django.contrib.auth.decorators import login_required 
from .models import Resumen, Especialidad, Doctor
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

#####################################################################################
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
            return redirect('login')

        return render(request, 'home.html')
    return render(request, 'Medico/home.html')
    

####################################################################################################################

######################################################### VISTA DE MEDICOS ##########################################################################

@login_required
@user_tipo_required(['Becario','Residente'])
def lista_solicitudes_revision(request, Especialidad_id=None):
    documentos_solicitud=Resumen.objects.filter(estado="Solicitud")
    documentos_revison=Resumen.objects.filter(estado="En revisión")
    medicos_becres =Doctor.objects.all()
    if Especialidad_id:
        Especialidad_obj = get_object_or_404(Especialidad, pk=Especialidad_id)
        documentos_solicitud = documentos_solicitud.filter(Especialidad=Especialidad_obj)
        documentos_revision = documentos_revision.filter(Especialidad=Especialidad_obj)

    especialidades = Especialidad.objects.all()  
    
    
    return render(request, 'Medico/MedicosRB.html', {
        'documentos_solicitud': documentos_solicitud,
        'documentos_revision': documentos_revison,
        'especialidades': especialidades,
        'doctor': medicos_becres,
        })
#########################################################################################

@login_required
@user_tipo_required(['Adscrito'])
def lista_resumenes_adscrito(request):
    
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
    })

#############################YA FUNCIONA NO LO TOQUES ###################################




@login_required
@user_tipo_required(['Adscrito','Residente','Becario'])
def editar_documento(request, documento_id):
 
    documento = Resumen.objects.get(id=documento_id)  
    if request.method == 'POST':
        content = request.POST.get('editordata')
        documento.texto = content 
        documento.save()
        
        try:
            doctor = Doctor.objects.get(user=request.user)
            if doctor.tipo == "Adscrito":
                return redirect('MedicosADS')
            elif doctor.tipo in ['Residente', 'Becario']:
                return redirect('MedicosRB')
        except Doctor.DoesNotExist:
              return redirect('home') 
    return render(request, 'Medico/editar_documento.html', {'documento': documento})
#########################################################################################


@login_required
@user_tipo_required(['Adscrito','Becario'], allowed_views=['cambiar_estado'])
def cambiar_estado(request, documento_id):
    if request.method == 'POST':
        
        documento = get_object_or_404(Resumen, id=documento_id)
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado in ['En revisión', 'Listo para enviar', 'Enviado']:
            documento.estado = nuevo_estado
            documento.save()
            try:
                doctor = Doctor.objects.get(user=request.user)
                if doctor.tipo == "Adscrito":
                    return redirect('MedicosADS')
                elif doctor.tipo in ['Becario']:
                    return redirect('MedicosRB')
            except Doctor.DoesNotExist:
                return redirect('home')
    return redirect('home')
       

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



def exit(request):
    logout(request)
    return redirect('home')

    
    
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
    else:
        resumenes = Resumen.objects.all().order_by("-fecha_solicitud")
    
    return render(request, 'Medico/busqueda.html', {
        'resumenes': resumenes,
        'especialidades': especialidades,
    })
    
