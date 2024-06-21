from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Doctor, Resumen
from django.contrib.auth.models import Group


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
#////////////////////////////////////////////////////////////////////////


def adscrito_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user_doctor = get_object_or_404(Doctor, user=request.user)
        if user_doctor.tipo == 'Adscrito':
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return _wrapped_view
#

#verificamos la especialidad del medico adascrito
def adscrito_especialidad_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user_doctor = get_object_or_404(Doctor, user=request.user)
        if user_doctor.tipo == 'Adscrito':
            request.especialidad = user_doctor.especialidad
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return _wrapped_view