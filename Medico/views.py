from django.shortcuts import render, redirect
from .decorators import doctor_tipo_required, status_permission_required
from django.contrib.auth.decorators import login_required 
from .models import Resumen, Especialidad
from django.shortcuts import render, get_object_or_404

@login_required
def home(request):
    return render(request, 'Medico/home.html')




@login_required
@doctor_tipo_required(['Residente', 'Becario'])
@status_permission_required(['Solicitud', 'En revisión'])

def lista_solicitudes_revision(request, Especialidad_id=None):
    documentos_solicitud=Resumen.objects.filter(estado="Solicitud")
    documentos_revison=Resumen.objects.filter(estado="En revisión")
    
    if Especialidad_id:
        Especialidad_obj = get_object_or_404(Especialidad, pk=Especialidad_id)
        documentos_solicitud = documentos_solicitud.filter(Especialidad=Especialidad_obj)
        documentos_revision = documentos_revision.filter(Especialidad=Especialidad_obj)

    especialidades = Especialidad.objects.all()  
    
    
    return render(request, 'app/lista_solicitudes_revision.html', {
        'documentos_solicitud': documentos_solicitud,
        'documentos_revision': documentos_revison,
        'especialidades': especialidades,
        })




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