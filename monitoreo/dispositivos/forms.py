import logging
from django import forms
from django.core.exceptions import ValidationError
from .models import Dispositivo, Zona, Medicion
from usuarios.models import Organizacion

logger = logging.getLogger(__name__)

class DispositivoForm(forms.ModelForm):
    class Meta:
        model = Dispositivo
        fields = ['nombre', 'categoria', 'zona', 'watts']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Sensor Temperatura 01'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'zona': forms.Select(attrs={'class': 'form-select'}),
            'watts': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '10000'}),
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre:
            raise ValidationError('El nombre del dispositivo es obligatorio.')
        if len(nombre) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres.')
        if len(nombre) > 100:
            raise ValidationError('El nombre no puede exceder 100 caracteres.')
        return nombre.strip()
    
    def clean_watts(self):
        watts = self.cleaned_data.get('watts')
        if watts is None:
            raise ValidationError('El consumo en watts es obligatorio.')
        if watts < 0:
            raise ValidationError('El consumo no puede ser negativo.')
        if watts > 10000:
            raise ValidationError('El consumo no puede exceder 10,000 watts.')
        return watts

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            try:
                user_role = getattr(user.perfil, 'rol', None) if hasattr(user, 'perfil') else None
                if user_role == 'encargado_ecoenergy':
                    self.fields['zona'].queryset = Zona.objects.all()
                else:
                    organizacion = getattr(user.perfil, 'organizacion', None) if hasattr(user, 'perfil') else None
                    if organizacion:
                        self.fields['zona'].queryset = Zona.objects.filter(organizacion=organizacion)
                    else:
                        self.fields['zona'].queryset = Zona.objects.none()
            except Exception as e:
                logger.error(f'Error en DispositivoForm.__init__: {str(e)}')
                self.fields['zona'].queryset = Zona.objects.all()

class ZonaForm(forms.ModelForm):
    class Meta:
        model = Zona
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Oficina Principal'}),
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre:
            raise ValidationError('El nombre de la zona es obligatorio.')
        if len(nombre) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres.')
        if len(nombre) > 100:
            raise ValidationError('El nombre no puede exceder 100 caracteres.')
        # Validar caracteres especiales
        import re
        if not re.match(r'^[a-zA-Z0-9À-ſ\s\-\_]+$', nombre):
            raise ValidationError('El nombre solo puede contener letras, números, espacios, guiones y guiones bajos.')
        return nombre.strip().title()

class RegistroEmpresaForm(forms.Form):
    usuario = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    nombre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

class MedicionForm(forms.ModelForm):
    class Meta:
        model = Medicion
        fields = ['dispositivo', 'consumo']
        widgets = {
            'dispositivo': forms.Select(attrs={'class': 'form-select'}),
            'consumo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '9999.99', 'placeholder': 'Ej: 125.50'}),
        }
    
    def clean_consumo(self):
        consumo = self.cleaned_data.get('consumo')
        if consumo is None:
            raise ValidationError('El consumo es obligatorio.')
        if consumo < 0:
            raise ValidationError('El consumo no puede ser negativo.')
        if consumo > 9999.99:
            raise ValidationError('El consumo no puede exceder 9,999.99 kWh.')
        # Validar que no sea un valor extremadamente pequeño
        if 0 < consumo < 0.01:
            raise ValidationError('El consumo mínimo registrable es 0.01 kWh.')
        return round(consumo, 2)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            try:
                user_role = getattr(user.perfil, 'rol', None) if hasattr(user, 'perfil') else None
                if user_role == 'encargado_ecoenergy':
                    self.fields['dispositivo'].queryset = Dispositivo.objects.all()
                else:
                    organizacion = getattr(user.perfil, 'organizacion', None) if hasattr(user, 'perfil') else None
                    if organizacion:
                        self.fields['dispositivo'].queryset = Dispositivo.objects.filter(zona__organizacion=organizacion)
                    else:
                        self.fields['dispositivo'].queryset = Dispositivo.objects.none()
            except Exception as e:
                logger.error(f'Error en MedicionForm.__init__: {str(e)}')
                self.fields['dispositivo'].queryset = Dispositivo.objects.all()