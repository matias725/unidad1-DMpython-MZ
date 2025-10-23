# Archivo: monitoreo/dispositivos/decorators.py

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def group_required(group_name):
    """
    Decorador que comprueba si un usuario pertenece a un grupo específico.
    Si no pertenece, lanza PermissionDenied (Error 403).
    """
    def check_group(user):
        if user.groups.filter(name=group_name).exists():
            return True
        # Si no pertenece al grupo, lanzamos un error 403
        raise PermissionDenied
    
    # user_passes_test se encarga de revisar el usuario logueado
    # y manejar la redirección al login si no está autenticado.
    return user_passes_test(check_group)