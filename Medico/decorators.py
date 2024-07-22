from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Doctor, Resumen
from django.contrib.auth.models import Group

#Se aplica a las vistas que deseamos proteger y como argumento pasamos en "tipo de doctor"
def user_tipo_required(allowed_tipos, allowed_views=[]):
    def decorador(view_func):
        def _wrapped_view(request,*args, **kwargs):
            print(f"Ejecutando decorador para la vista: {view_func.__name__}")
            
            if request.user.is_superuser:
                print("Usuario superuser, permitiendo acceso.")
                return view_func(request, *args, **kwargs)
            
            try:
                #verificamos si el tipo de usuario es del grupo de usuarios "Administrador"
                if request.user.groups.filter(name="Administrador").exists():
                    print("Usuario del grupo 'Administrador', permitiendo acceso...")
                    return view_func(request, *args, **kwargs)
                user_doctor = get_object_or_404(Doctor, user=request.user)
                print(f"Doctor encontrado: {user_doctor.tipo}")
                if user_doctor.tipo in allowed_tipos or view_func.__name__ in allowed_views:
                    print("Permitiendo acceso a la vista.")
                    return view_func(request, *args, **kwargs)
                else:
                    print("Doctor no encontrado para el usuario.")
            except Doctor.DoesNotExist:
                pass    
            raise PermissionDenied("No tienes permiso para entrar a esta pagina")
        return _wrapped_view
    return decorador




















#"Este decorador verifica el tipo de doctor"
#//////////////////////////////////////////////////////////////////////
def doctor_tipo_required(tipo_medico):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            
            user_doctor = get_object_or_404(Doctor, user=request.user)
            
            superuser_group = Group.objects.get(name='superusers')
            if superuser_group in request.user.groups.all():
                return view_func(request, *args, **kwargs)
            if user_doctor.tipo in tipo_medico:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    return decorator
#///////////////////////////////////////////////////////////////////////


#"Este decorador verifica el el estatus del 'documento' 
#"y lo ingresa como argumento de la funcion"
#////////////////////////////////////////////////////////////////////////
def status_permission_required(status_list):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            superuser_group = Group.objects.get(name='superusers')
            if superuser_group in request.user.groups.all():
                documentos = Resumen.objects.all()
            else:
                documentos = Resumen.objects.filter(estado__in=status_list)
            return view_func(request, documentos=documentos, *args, **kwargs)
        return _wrapped_view
    return decorator


