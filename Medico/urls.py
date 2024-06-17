from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('solicitud', views.solicitud, name='solicitud'),
    path('MedicosRB', views.lista_solicitudes_revision, name='MedicosRB'),
    path('editar/<int:documento_id>/', views.editar_documento, name='editar'),
    path('logout', views.exit, name="exit"),
    path('cambiar_estado/<int:documento_id>', views.cambiar_estado, name="cambiar_estado"),
  
   
]
