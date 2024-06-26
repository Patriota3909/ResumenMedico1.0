from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('logout', views.exit, name="exit"),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('solicitud', views.solicitud, name='solicitud'),
    path('lista_resumenes/', views.lista_resumenes, name='lista_resumenes'),
    path('MedicosRB', views.lista_solicitudes_revision, name='MedicosRB'),
    path('MedicosRB/<int:edited_id>/', views.lista_solicitudes_revision, name='MedicosRB_with_id'),
    path('MedicosADS', views.lista_resumenes_adscrito, name='MedicosADS'),
    path('MedicosADS/<int:edited_id>/', views.lista_resumenes_adscrito, name='MedicosADS_with_id'),
    path('editar_documento/<int:documento_id>/', views.editar_documento, name="editar_documento"),
    path('cambiar_estado/<int:documento_id>', views.cambiar_estado, name="cambiar_estado"),
    path('asignar_medico_resumen/<int:documento_id>', views.asignar_medico_resumen, name="asignar_medico_resumen"),
    path('generate_pdf', views.generate_pdf, name="generate_pdf"),
    path('asignar_medico_residente', views.asignar_medico_residente, name='asignar_medico_residente'),
    path('editar_froala',views.editar_froala, name="editar_froala"),
    

    
]
