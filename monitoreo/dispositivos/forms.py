from django import forms
from .models import Dispositivo, Empresa, Zona 
from django.contrib.auth.models import User

class RegistroEmpresaForm(forms.ModelForm):
    usuario = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Empresa
        fields = ['nombre']

class DispositivoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        
        super(DispositivoForm, self).__init__(*args, **kwargs)
        
        if user and not user.is_superuser:
            try:
                self.fields['zona'].queryset = Zona.objects.filter(empresa=user.empresa)
            except Empresa.DoesNotExist:
                self.fields['zona'].queryset = Zona.objects.none()
        elif user and user.is_superuser:
            self.fields['zona'].queryset = Zona.objects.all()
        else:
            self.fields['zona'].queryset = Zona.objects.all()


    class Meta:
        model = Dispositivo
        fields = ['nombre', 'categoria', 'zona', 'watts']

# ---------------------------------
# ¡NUEVO FORMULARIO PARA ZONAS!
# ---------------------------------
class ZonaForm(forms.ModelForm):
    class Meta:
        model = Zona
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Planta Norte'})
        }