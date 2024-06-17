from django.shortcuts import render, redirect
from .decorators import doctor_tipo_required, status_permission_required
from django.contrib.auth.decorators import login_required 
from .models import Resumen, Especialidad
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout

@login_required
def home(request):
    return render(request, 'Medico/home.html')




@login_required
#@doctor_tipo_required(['Residente', 'Becario'])
#@status_permission_required(['Solicitud', 'En revisión'])

def lista_solicitudes_revision(request, Especialidad_id=None):
    documentos_solicitud=Resumen.objects.filter(estado="Solicitud")
    documentos_revison=Resumen.objects.filter(estado="En revisión")
    
    if Especialidad_id:
        Especialidad_obj = get_object_or_404(Especialidad, pk=Especialidad_id)
        documentos_solicitud = documentos_solicitud.filter(Especialidad=Especialidad_obj)
        documentos_revision = documentos_revision.filter(Especialidad=Especialidad_obj)

    especialidades = Especialidad.objects.all()  
    
    
    return render(request, 'Medico/MedicosRB.html', {
        'documentos_solicitud': documentos_solicitud,
        'documentos_revision': documentos_revison,
        'especialidades': especialidades,
        })



@login_required
@doctor_tipo_required(['Residente', 'Becario'])
@status_permission_required(['Solicitud', 'En revisión'])

def editar_documento(request, documento_id):
    documento = get_object_or_404(Resumen, id=documento_id)
    template_content = f"""
    <body lang="es-ES-u-co-trad" link="#0563c1" vlink="#800000" dir="ltr">
    <div title="header"><p style="orphans: 2; widows: 2; margin-bottom: 1.1in">
	<span class="sd-abs-pos" style="position: absolute; top: -0.41in; left: 0in; width: 779px"><img src="64d91f302280affdea8f83db02d1e95e_html_f3cc0972.jpg" name="Imagen 438394229" width="779" height="1008" border="0"/>
    </span><br/>

	</p>
    </div><p lang="es-MX" class="western" align="justify" style="line-height: 100%; orphans: 2; widows: 2; margin-bottom: 0.11in">
    <font face="Calibri, serif"><font size="2" style="font-size: 11pt"><font face="Arial, serif"><font size="2" style="font-size: 10pt">						Querétaro,
    Qro. a___ del mes____ del año 20___</font></font></font></font></p>
    <p lang="es-MX" class="western" align="justify" style="line-height: 100%; orphans: 2; widows: 2; margin-bottom: 0.11in">
    <br/>
    <br/>

    </p>
    <table width="717" cellpadding="1" cellspacing="0">
    	<col width="157"/>
    	<col width="102"/>
    	<col width="111"/>
    	<col width="336"/>
    	<tr>
    		<td colspan="4" width="713" height="20" valign="top" bgcolor="#bebebe" style="background: #bebebe; border: 1px solid #000000; padding: 0in 0in"><p lang="es-MX" class="western" align="center" style="orphans: 2; widows: 2; margin-left: 2.99in; margin-right: 3in; margin-top: 0.05in">
    			<font face="Calibri, serif"><font size="2" style="font-size: 11pt"><font face="Calibri Light, serif"><b>D</b></font><font face="Calibri Light, serif"><span style="letter-spacing: -0.1pt"><b>A</b></span></font><font face="Calibri Light, serif"><b>TOS</b></font><font face="Calibri Light, serif"><span style="letter-spacing: 0.3pt">
    			</span></font><font face="Calibri Light, serif"><b>D</b></font><font face="Calibri Light, serif"><span style="letter-spacing: -0.1pt"><b>E</b></span></font><font face="Calibri Light, serif"><b>L</b></font><font face="Calibri Light, serif"><span style="letter-spacing: -0.4pt">
    			</span></font><font face="Calibri Light, serif"><b>PA</b></font><font face="Calibri Light, serif"><span style="letter-spacing: -0.1pt"><b>C</b></span></font><font face="Calibri Light, serif"><span style="letter-spacing: -0.1pt"><b>I</b></span></font><font face="Calibri Light, serif"><b>E</b></font><font face="Calibri Light, serif"><span style="letter-spacing: 0.1pt"><b>N</b></span></font><font face="Calibri Light, serif"><span style="letter-spacing: -0.1pt"><b>T</b></span></font><font face="Calibri Light, serif"><b>E</b></font></font></font></p>
    		</td>
    	</tr>
    	<tr valign="top">
    		<td width="157" height="21" style="border: 1px solid #000000; padding: 0in 0in"><p lang="es-MX" class="western" style="orphans: 2; widows: 2; margin-left: 0.27in; margin-top: 0.03in">
    			<font face="Calibri, serif"><font size="2" style="font-size: 11pt"><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: 0.1pt">N</span></font><font face="Amasis MT Pro Light, serif">o</font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: -0.1pt">m</span></font><font face="Amasis MT Pro Light, serif">bre</font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: -0.1pt">
    			</span></font><font face="Amasis MT Pro Light, serif">c</font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: -0.2pt">o</span></font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: 0.1pt">m</span></font><font face="Amasis MT Pro Light, serif">p</font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: -0.2pt">l</span></font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: 0.1pt">e</span></font><font face="Amasis MT Pro Light, serif">to</font></font></font></p>
    		</td>
    		<td colspan="3" width="554" style="border: 1px solid #000000; padding: 0in 0in"><p lang="es-MX" class="western" style="orphans: 2; widows: 2">
    			<br/>

    			</p>
    		</td>
    	</tr>
    	<tr valign="top">
    		<td width="157" height="21" style="border: 1px solid #000000; padding: 0in 0in"><p lang="es-MX" class="western" style="orphans: 2; widows: 2; margin-left: 0.19in; margin-top: 0.03in">
    			<font face="Calibri, serif"><font size="2" style="font-size: 11pt"><font face="Amasis MT Pro Light, serif">F</font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: 0.1pt">e</span></font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: -0.1pt">ch</span></font><font face="Amasis MT Pro Light, serif">a</font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: 0.5pt">
    			</span></font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: -0.1pt">d</span></font><font face="Amasis MT Pro Light, serif">e</font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: 0.1pt">
    			</span></font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: 0.1pt">n</span></font><font face="Amasis MT Pro Light, serif">a</font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: -0.1pt">c</span></font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: -0.1pt">i</span></font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: 0.1pt">m</span></font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: -0.2pt">i</span></font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: 0.1pt">e</span></font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: -0.1pt">n</span></font><font face="Amasis MT Pro Light, serif">to</font></font></font></p>
    		</td>
    		<td colspan="3" width="554" style="border-top: 1px solid #000000; border-bottom: none; border-left: 1px solid #000000; border-right: 1px solid #000000; padding: 0in 0in"><p lang="es-MX" class="western" style="orphans: 2; widows: 2">
    			<br/>

    			</p>
    		</td>
    	</tr>
    	<tr valign="top">
    		<td width="157" height="20" style="border: 1px solid #000000; padding: 0in 0in"><p lang="es-MX" class="western" align="center" style="orphans: 2; widows: 2; margin-left: 0.58in; margin-right: 0.58in; margin-top: 0.02in">
    			<font face="Calibri, serif"><font size="2" style="font-size: 11pt"><font face="Amasis MT Pro Light, serif">Gener</font><font face="Amasis MT Pro Light, serif">o</font></font></font></p>
    		</td>
    		<td width="102" style="border: 1px solid #000000; padding: 0in 0in"><p lang="es-MX" class="western" style="orphans: 2; widows: 2; margin-top: 0.02in">
    			<br/>

    			</p>
    		</td>
    		<td width="111" style="border: 1px solid #000000; padding: 0in 0in"><p lang="es-MX" class="western" style="orphans: 2; widows: 2; margin-left: 0.24in; margin-top: 0.02in">
    			<font face="Calibri, serif"><font size="2" style="font-size: 11pt"><font face="Amasis MT Pro Light, serif">Exp</font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: -0.1pt">e</span></font><font face="Amasis MT Pro Light, serif">di</font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: -0.1pt">e</span></font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: 0.1pt">n</span></font><font face="Amasis MT Pro Light, serif"><span style="letter-spacing: -0.1pt">t</span></font><font face="Amasis MT Pro Light, serif">e</font></font></font></p>
    		</td>
    		<td width="336" style="border: 1px solid #000000; padding: 0in 0in"><p lang="es-MX" class="western" style="orphans: 2; widows: 2">
    			<br/>

    			</p>
    		</td>
    	</tr>
    </table>
    <p lang="es-MX" class="western" align="justify" style="line-height: 100%; orphans: 2; widows: 2; margin-bottom: 0.11in">
    <br/>
    <br/>

    </p>
    <p lang="es-MX" class="western" align="justify" style="line-height: 100%; orphans: 2; widows: 2">
    <br/>

    </p>
    <p lang="es-MX" class="western" align="justify" style="line-height: 150%; orphans: 2; widows: 2; margin-top: 0.17in; margin-bottom: 0.17in">
    <font face="Calibri, serif"><font size="2" style="font-size: 11pt"><font face="Arial, serif"><font size="2" style="font-size: 10pt">Padecimiento
    actual:</font></font></font></font></p>
    <p lang="es-MX" class="western" align="justify" style="line-height: 150%; orphans: 2; widows: 2; margin-top: 0.17in; margin-bottom: 0.17in">
    <br/>
    <br/>

    </p>
    <p lang="es-MX" class="western" align="justify" style="line-height: 150%; orphans: 2; widows: 2; margin-top: 0.17in; margin-bottom: 0.17in">
    <font face="Calibri, serif"><font size="2" style="font-size: 11pt"><font face="Arial, serif"><font size="2" style="font-size: 10pt">Diagnostico:</font></font></font></font></p>
    <p lang="es-MX" class="western" align="justify" style="line-height: 150%; orphans: 2; widows: 2; margin-top: 0.17in; margin-bottom: 0.17in">
    <font face="Calibri, serif"><font size="2" style="font-size: 11pt"><font face="Arial, serif"><font size="2" style="font-size: 10pt">Tratamientos
    realizados:</font></font></font></font></p>
    <p lang="es-MX" class="western" align="justify" style="line-height: 150%; orphans: 2; widows: 2; margin-top: 0.17in; margin-bottom: 0.17in">
    <br/>
    <br/>

    </p>
    <p lang="es-MX" class="western" align="justify" style="line-height: 150%; orphans: 2; widows: 2; margin-top: 0.17in; margin-bottom: 0.17in">
    <font face="Calibri, serif"><font size="2" style="font-size: 11pt"><font face="Arial, serif"><font size="2" style="font-size: 10pt">Resultados
    de estudios de laboratorio y gabinete:</font></font></font></font></p>
    <p lang="es-MX" class="western" align="justify" style="line-height: 150%; orphans: 2; widows: 2; margin-top: 0.17in; margin-bottom: 0.17in">
    <br/>
    <br/>

    </p>
    <p lang="es-MX" class="western" align="justify" style="line-height: 150%; orphans: 2; widows: 2; margin-top: 0.17in; margin-bottom: 0.17in">
    <font face="Calibri, serif"><font size="2" style="font-size: 11pt"><font face="Arial, serif"><font size="2" style="font-size: 10pt">Evolución:</font></font></font></font></p>
    <p lang="es-MX" class="western" align="justify" style="line-height: 150%; orphans: 2; widows: 2; margin-top: 0.17in; margin-bottom: 0.17in">
    <br/>
    <br/>

    </p>
    <p lang="es-MX" class="western" align="justify" style="line-height: 100%; orphans: 2; widows: 2; margin-bottom: 0.11in">
    <br/>
    <br/>

    </p>
    <p lang="es-MX" class="western" align="justify" style="line-height: 150%; orphans: 2; widows: 2; margin-top: 0.17in; margin-bottom: 0.17in">
    <table dir="ltr" align="left" width="259" hspace="9" cellpadding="1" cellspacing="0">
    	<col width="92"/>
    	<col width="163"/>
    	<tr valign="top">
    		<td rowspan="3" width="92" height="17" style="border-top: 1px solid #7e7e7e; border-bottom: none; border-left: none; border-right: 1px solid #7e7e7e; padding-top: 0in; padding-bottom: 0in; padding-left: 0in; padding-right: 0in"><p lang="es-MX" class="western" style="orphans: 2; widows: 2; margin-left: 0.29in; margin-bottom: 0.11in">
    			<font face="Calibri, serif"><font size="2" style="font-size: 11pt"><font face="Times New Roman, serif">Fa</font><font face="Times New Roman, serif"><span style="letter-spacing: 0.1pt">v</span></font><font face="Times New Roman, serif">o</font><font face="Times New Roman, serif"><span style="letter-spacing: -0.1pt">r</span></font><font face="Times New Roman, serif">able</font></font></font></p>
    			<p lang="es-MX" class="western" style="orphans: 2; widows: 2; margin-left: 0.24in; margin-top: 0.02in; margin-bottom: 0.11in">
    			<font face="Calibri, serif"><font size="2" style="font-size: 11pt"><font face="Times New Roman, serif"><span style="letter-spacing: -0.1pt">R</span></font><font face="Times New Roman, serif"><span style="letter-spacing: 0.1pt">e</span></font><font face="Times New Roman, serif"><span style="letter-spacing: -0.1pt">s</span></font><font face="Times New Roman, serif"><span style="letter-spacing: 0.1pt">e</span></font><font face="Times New Roman, serif"><span style="letter-spacing: -0.1pt">r</span></font><font face="Times New Roman, serif">va</font><font face="Times New Roman, serif"><span style="letter-spacing: 0.1pt">d</span></font><font face="Times New Roman, serif">o</font></font></font></p>
    			<p lang="es-MX" class="western" style="orphans: 2; widows: 2; margin-left: 0.08in; margin-top: 0.02in">
    			<font face="Calibri, serif"><font size="2" style="font-size: 11pt"><font face="Times New Roman, serif">De</font><font face="Times New Roman, serif"><span style="letter-spacing: 0.1pt">s</span></font><font face="Times New Roman, serif">f</font><font face="Times New Roman, serif"><span style="letter-spacing: -0.2pt">a</span></font><font face="Times New Roman, serif">vo</font><font face="Times New Roman, serif"><span style="letter-spacing: 0.1pt">r</span></font><font face="Times New Roman, serif"><span style="letter-spacing: -0.1pt">a</span></font><font face="Times New Roman, serif">ble</font></font></font></p>
    		</td>
    		<td width="163" bgcolor="#f1f1f1" style="background: #f1f1f1; border-top: none; border-bottom: none; border-left: 1px solid #7e7e7e; border-right: none; padding: 0in"><p lang="es-MX" class="western" style="orphans: 2; widows: 2">
    			<br/>

    			</p>
    		</td>
    	</tr>
    	<tr valign="top">
    		<td width="163" style="border-top: none; border-bottom: none; border-left: 1px solid #7e7e7e; border-right: none; padding: 0in"><p lang="es-MX" class="western" style="orphans: 2; widows: 2">
    			<br/>

			</p>
		</td>
	</tr>
	<tr valign="top">
		<td width="163" bgcolor="#f1f1f1" style="background: #f1f1f1; border-top: none; border-bottom: none; border-left: 1px solid #7e7e7e; border-right: none; padding: 0in"><p lang="es-MX" class="western" style="orphans: 2; widows: 2">
			<br/>

			</p>
		</td>
	</tr>
    </table><br/>
    <br/>

    </p>
    <p lang="es-MX" class="western" style="line-height: 100%; orphans: 2; widows: 2">
    <br/>

    </p>
    <p lang="es-MX" class="western" style="line-height: 100%; orphans: 2; widows: 2">
    <br/>

    </p>
    <p lang="es-MX" class="western" style="line-height: 100%; orphans: 2; widows: 2; margin-left: -0.2in">
    <br/>

    </p>
    <p lang="es-MX" class="western" style="line-height: 100%; orphans: 2; widows: 2; margin-left: -0.2in">
    <br/>

    </p>
    <div title="footer"><p lang="es-ES" align="center" style="orphans: 2; widows: 2; margin-top: 0.89in">
    	<br/>

    	</p>
    </div>
    </body>
    
    
    """
    
    if request.method == 'POST':
        content = request.POST.get('content')
        documento.texto = content
        documento.ultimo_editor = request.user
        documento.save()
        return redirect('lista_solicitudes_revision')
        
    return render(request, 'Medico/editar_documento.html', {
        'documento': documento,
        'template_content':template_content,
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