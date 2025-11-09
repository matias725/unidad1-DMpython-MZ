from functools import wraps
from django.http import Http404
from django.contrib.auth.decorators import login_required

def cliente_admin_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            user_role = request.user.perfil.rol
            if user_role in ['cliente_admin', 'encargado_ecoenergy']:
                return view_func(request, *args, **kwargs)
            else:
                raise Http404("Acceso denegado")
        except:
            raise Http404("Acceso denegado")
    return _wrapped_view

def cliente_electronico_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            user_role = request.user.perfil.rol
            if user_role in ['cliente_electronico', 'cliente_admin', 'encargado_ecoenergy']:
                return view_func(request, *args, **kwargs)
            else:
                raise Http404("Acceso denegado")
        except:
            raise Http404("Acceso denegado")
    return _wrapped_view

def encargado_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            user_role = request.user.perfil.rol
            if user_role == 'encargado_ecoenergy':
                return view_func(request, *args, **kwargs)
            else:
                raise Http404("Acceso denegado")
        except:
            raise Http404("Acceso denegado")
    return _wrapped_view