import logging
import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from django.views.decorators.cache import never_cache
from django.utils.html import escape
from .forms import RegistroForm, PerfilForm, CambiarPasswordForm
from .models import Perfil

logger = logging.getLogger(__name__)

def validate_safe_path(path_param):
    """Valida que el parámetro no contenga path traversal"""
    if not path_param:
        return True
    
    dangerous_patterns = ['../', '..\\', '/..', '\\..', '../', '..\\']
    path_str = str(path_param)
    
    for pattern in dangerous_patterns:
        if pattern in path_str:
            return False
    return True

class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True

@never_cache
def registro(request):
    try:
        if request.method == 'POST':
            # Validar datos de entrada contra path traversal
            for key, value in request.POST.items():
                if not validate_safe_path(value):
                    logger.warning(f'Intento de path traversal en registro: {key}={value}')
                    messages.error(request, 'Datos de entrada no válidos.')
                    return redirect('usuarios:registro')
                    
            form = RegistroForm(request.POST)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        user = form.save()
                        Perfil.objects.create(user=user)
                        username = escape(form.cleaned_data.get('username'))
                        logger.info(f'Nuevo usuario registrado: {username}')
                        messages.success(request, f'Cuenta creada para {username}!')
                        return redirect('usuarios:login')
                except Exception as e:
                    logger.error(f'Error creando usuario: {str(e)}')
                    messages.error(request, 'Error al crear la cuenta. Inténtalo de nuevo.')
        else:
            form = RegistroForm()
            
        return render(request, 'usuarios/registro.html', {'form': form})
        
    except Exception as e:
        logger.error(f'Error en registro: {str(e)}')
        messages.error(request, 'Error interno. Inténtalo más tarde.')
        return redirect('usuarios:login')

@login_required
def perfil(request):
    perfil_obj, created = Perfil.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil_obj, user=request.user)
        if form.is_valid():
            # Actualizar datos del usuario
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            
            # Actualizar perfil
            form.save()
            messages.success(request, 'Perfil actualizado correctamente!')
            return redirect('usuarios:perfil')
    else:
        form = PerfilForm(instance=perfil_obj, user=request.user)
    
    return render(request, 'usuarios/perfil.html', {'form': form})

@login_required
def cambiar_password(request):
    if request.method == 'POST':
        form = CambiarPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Contraseña cambiada correctamente!')
            return redirect('usuarios:perfil')
    else:
        form = CambiarPasswordForm(request.user)
    
    return render(request, 'usuarios/cambiar_password.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('usuarios:login')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'usuarios/password_reset.html'
    email_template_name = 'usuarios/password_reset_email.html'
    success_url = reverse_lazy('usuarios:password_reset_done')