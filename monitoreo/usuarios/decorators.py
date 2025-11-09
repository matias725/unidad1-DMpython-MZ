from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps

def get_user_role(user):
    if not user.is_authenticated:
        return None
    try:
        return user.perfil.rol
    except:
        return None

def encargado_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        # Permitir superusuarios
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        role = get_user_role(request.user)
        if role != 'encargado_ecoenergy':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def cliente_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        # Permitir superusuarios
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        role = get_user_role(request.user)
        if role not in ['cliente_admin', 'encargado_ecoenergy']:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def cliente_electronico_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        # Permitir superusuarios
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        role = get_user_role(request.user)
        if role not in ['cliente_electronico', 'cliente_admin', 'encargado_ecoenergy']:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Mantener compatibilidad
admin_required = encargado_required
editor_required = cliente_admin_required
lector_required = cliente_electronico_required