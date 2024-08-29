from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('logout', views.exit, name="exit"),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    #esta vista muestra el formulario de solicitud
    path('solicitud', views.solicitud, name='solicitud'),
    #Esta vista muestra todos los resumenes en lista para la busqueda global
    path('lista_resumenes/', views.lista_resumenes, name='lista_resumenes'),
    #Vista de meédicos residentes y becarios
    path('MedicosRB', views.lista_solicitudes_revision, name='MedicosRB'),
    #Este lina con <int:edited_id> retorna un el id que fue editado para que con java script en la plantilla pueda distinguirse
    path('MedicosRB/<int:edited_id>/', views.lista_solicitudes_revision, name='MedicosRB_with_id'),
    #Esta vista muesta los resumenes de los adcritos ("En revision", "Listos para enviar", "Enviado")
    path('MedicosADS', views.lista_resumenes_adscrito, name='MedicosADS'),
    #Este lina con <int:edited_id> retorna un el id que fue editado para distinguirlo de los demas aunado a que se muestra al principio de la lista
    path('MedicosADS/<int:edited_id>/', views.lista_resumenes_adscrito, name='MedicosADS_with_id'),
    #Esta vista es para editar con summernote
    path('editar_documento/<int:documento_id>/', views.editar_documento, name="editar_documento"),
    #Esta vista muestra el editor de froala 
    path('editar_documento2/<int:documento_id>/', views.editar_documento2, name="editar_documento2"),
    #Esta vista gestiona el cambio de estado de un "Resumen"
    path('cambiar_estado/<int:documento_id>', views.cambiar_estado, name="cambiar_estado"),
    #Esta vista gestiona el asignar un resumen a un médico residente cuando el adscrito asi lo requiera
    path('asignar_medico_resumen/<int:documento_id>', views.asignar_medico_resumen, name="asignar_medico_resumen"),
    path('generate_pdf', views.generate_pdf, name="generate_pdf"),
    path('asignar_medico_residente', views.asignar_medico_residente, name='asignar_medico_residente'),
    path('insertar_firma/<int:documento_id>/', views.insertar_firma, name='insertar_firma'),
    path('enviar_documento/<int:documento_id>/', views.enviar_documento, name='enviar_documento'),
    path('configuracion_view', views.configuracion_view, name='configuracion_view'),
    path('modificar_especialidad/<int:doctor_id>/', views.modificar_especialidad, name='modificar_especialidad'),
    path('descargar_pdf/<int:documento_id>/', views.descargar_pdf, name='descargar_pdf'),
    path('documento/<int:documento_id>/comentario/', views.agregar_comentario, name='agregar_comentario')   
]
    
    

    
