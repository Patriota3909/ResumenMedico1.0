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

@login_required
def home(request):
    return render(request, 'Medico/home.html')




@login_required
#@doctor_tipo_required(['Residente', 'Becario'])
#@status_permission_required(['Solicitud', 'En revisión'])

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



@login_required
#@doctor_tipo_required(['Residente', 'Becario'])
#@status_permission_required(['Solicitud', 'En revisión'])

def editar_documento(request, documento_id):
#    documento = get_object_or_404(Resumen, id=documento_id)
#    
#    if request.method == 'POST':
#        content = request.POST.get('content')
#        documento.texto = content
#        documento.ultimo_editor = request.user
#        documento.save()
#        return redirect('lista_solicitudes_revision')
#        
#    return render(request, 'Medico/editar_documento.html', {
#        'documento': documento,
#        })

   
    documento = Resumen.objects.get(id=documento_id)  # Obtén el documento por ID
    if request.method == 'POST':
        content = request.POST.get('editordata')
        documento.texto = content  # Actualiza el contenido
        documento.save()  # Guarda los cambios
        return redirect('home')  # Redirige a otra página tras guardar
    return render(request, 'Medico/editar_documento.html', {'documento': documento})




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
@doctor_tipo_required(['Adscrito'])
@status_permission_required(['En revisión','Listo para enviar', 'Enviado'])

def lista_listo_enviado(request, documentos):
    return render(request, 'app/lista_listo_enviado.html', {'documentos': documentos})



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

def cambiar_estado(request, documento_id):
    documento = get_object_or_404(Resumen, id=documento_id)
    if request.method == 'POST':
        documento.estado = "En revisión"
        documento.save()
        return redirect('Medico/MedicosRB')
    
    return render(request, 'Medico/MedicosRB.html', {
        'documento':documento
    })
    
    
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




def prueba(request):
    return render(request,"Medico/Prueba1.html")

def save_document(request):
    if request.method == 'POST':
        content = request.POST.get('editordata')
        # Suponiendo que tienes un modelo llamado Document con un campo text
        doc = Resumen(text=content)
        doc.save()
        return redirect('home')  # Redirige a una página de éxito o donde prefieras
    return render(request, 'your_template.html')