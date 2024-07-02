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
            reverse('MedicosRB'),
            
            ]
        print(f"Requested path: {request.path}")

        
        if request.path in excluded_paths:
            print("Path is excluded from checks.")
            return self.get_response(request)
        
        if not request.resolver_match:
            print("No resolver match found.")
            return self.get_response(request)
        
        current_view_name = request.resolver_match.view_name
        print(f"Current view name: {current_view_name}")
        # Verificar si el usuario está autenticado
        if request.user.is_authenticated:
            print("User is authenticated.")
            if request.user.is_superuser:
                print("User is superuser.")
                return self.get_response(request)
            try:
                
                doctor = Doctor.objects.get(user=request.user)
                (f"Doctor type: {doctor.tipo}")
                if doctor.tipo == 'Adscrito':
                    allowed_views =['MedicosADS', 'editar_documento','cambiar_estado']
                    if current_view_name not in allowed_views:
                        print(f"View {current_view_name} is not allowed for Adscrito.")
                        return redirect('MedicosADS')
                elif doctor.tipo in ['Residente', 'Becario']:
                    allowed_views =['MedicosRB','editar_documento','cambiar_estado']
                    if current_view_name not in allowed_views:
                        print(f"View {current_view_name} is not allowed for {doctor.tipo}.")
                        return redirect('MedicosRB')
                
            except Doctor.DoesNotExist:
                print("Doctor does not exist.")
                return redirect('home')  # Si el usuario no es un doctor, permitir el acceso a la vista solicitada en este caso a administradores para revisar el estatus de resumenes completos

        response = self.get_response(request)
        return response
