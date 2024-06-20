from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('solicitud', views.solicitud, name='solicitud'),
    path('MedicosRB', views.lista_solicitudes_revision, name='MedicosRB'),
    path('logout', views.exit, name="exit"),
    path('cambiar_estado/<int:documento_id>', views.cambiar_estado, name="cambiar_estado"),
    path('asignar_medico_resumen/<int:documento_id>', views.asignar_medico_resumen, name="asignar_medico_resumen"),
    path('generate_pdf', views.generate_pdf, name="generate_pdf"),
    path('editar_documento/<int:documento_id>/', views.editar_documento, name="editar_documento"),
    path('prueba', views.prueba, name="prueba"),
    
]
