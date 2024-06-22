from django.shortcuts import redirect
from django.urls import reverse
from .models import Doctor

#Este middle se utiliza para validar en cada solicitud el tipo de usuario de forma globalizada para darle acceso a ciertas vistas 
class tipo_usuario_middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Excluir la ruta de login para evitar bucles de redirección
        excluded_paths = [
            reverse('login'), 
            reverse('logout'), 
            reverse('admin:login'),
            reverse('MedicosADS'),
           
            ]
        
        if request.path in excluded_paths:
            return self.get_response(request)
        
        if not request.resolver_match:
            return self.get_response(request)
        
        current_view_name = request.resolver_match.view_name
        # Verificar si el usuario está autenticado
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return self.get_response(request)
            try:
                
                doctor = Doctor.objects.get(user=request.user)
                if doctor.tipo == 'Adscrito':
                    allowed_views =['MedicosADS', 'editar_documento']
                    if current_view_name not in allowed_views:
                        return redirect('MedicosADS')
                elif doctor.tipo in ['Residente', 'Becario']:
                    if request.path != reverse('MedicosRB'):
                        return redirect('MedicosRB')
                
            except Doctor.DoesNotExist:
                pass  # Si el usuario no es un doctor, permitir el acceso a la vista solicitada en este caso a administradores para revisar el estatus de resumenes completos

        response = self.get_response(request)
        return response
