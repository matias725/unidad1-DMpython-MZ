import logging
import os
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.html import escape
from .models import Perfil

logger = logging.getLogger(__name__)

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class PerfilForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu nombre'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu apellido'})
    )
    email = forms.EmailField(
        required=True, 
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'})
    )
    
    class Meta:
        model = Perfil
        fields = ['telefono', 'avatar']
        labels = {
            'telefono': 'Teléfono',
            'avatar': 'Imagen de perfil'
        }
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise ValidationError('El nombre es obligatorio.')
        if len(first_name) < 2:
            raise ValidationError('El nombre debe tener al menos 2 caracteres.')
        import re
        if not re.match(r'^[a-zA-ZÀ-ſ\s]+$', first_name):
            raise ValidationError('El nombre solo puede contener letras y espacios.')
        return first_name.strip().title()
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise ValidationError('El apellido es obligatorio.')
        if len(last_name) < 2:
            raise ValidationError('El apellido debe tener al menos 2 caracteres.')
        import re
        if not re.match(r'^[a-zA-ZÀ-ſ\s]+$', last_name):
            raise ValidationError('El apellido solo puede contener letras y espacios.')
        return last_name.strip().title()
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            import re
            # Remover espacios y caracteres especiales para validación
            telefono_clean = re.sub(r'[\s\-\(\)\+]', '', telefono)
            if not re.match(r'^[0-9]{8,15}$', telefono_clean):
                raise ValidationError('Ingresa un teléfono válido (8-15 dígitos).')
        return telefono
    
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'size'):
            try:
                # Validar tamaño (2MB máximo)
                if avatar.size > 2 * 1024 * 1024:
                    raise ValidationError('El archivo es muy grande. Máximo 2MB.')
                
                # Validar nombre de archivo contra path traversal
                if avatar.name and ('..' in avatar.name or '/' in avatar.name or '\\' in avatar.name):
                    raise ValidationError('Nombre de archivo no válido.')
                
                # Validar tipo de archivo
                if hasattr(avatar, 'content_type'):
                    allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
                    if avatar.content_type not in allowed_types:
                        raise ValidationError('Solo se permiten archivos JPG o PNG.')
                
                # Validar extensión
                if avatar.name:
                    ext = os.path.splitext(avatar.name)[1].lower()
                    if ext not in ['.jpg', '.jpeg', '.png']:
                        raise ValidationError('Solo se permiten archivos .jpg, .jpeg o .png.')
                
                # Validar dimensiones mínimas y máximas
                try:
                    from PIL import Image
                    avatar.seek(0)
                    img = Image.open(avatar)
                    width, height = img.size
                    
                    if width < 100 or height < 100:
                        raise ValidationError('La imagen debe tener al menos 100x100 píxeles.')
                    if width > 2000 or height > 2000:
                        raise ValidationError('La imagen no puede exceder 2000x2000 píxeles.')
                    
                    if img.format not in ['JPEG', 'PNG']:
                        raise ValidationError('Formato de imagen no válido.')
                    
                    avatar.seek(0)
                        
                except ImportError:
                    logger.warning('PIL no disponible para validación de imágenes')
                except Exception as e:
                    logger.error(f'Error validando imagen: {str(e)}')
                    raise ValidationError('Archivo de imagen corrupto o inválido.')
                    
            except ValidationError:
                raise
            except Exception as e:
                logger.error(f'Error inesperado validando avatar: {str(e)}')
                raise ValidationError('Error procesando el archivo de imagen.')
        
        return avatar

class CambiarPasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('La contraseña debe contener al menos una mayúscula.')
        if not re.search(r'[0-9]', password):
            raise ValidationError('La contraseña debe contener al menos un número.')
        return password