from django import forms
from django.core.exceptions import ValidationError
from .models import Dispositivo, Zona, Medicion

class DispositivoForm(forms.ModelForm):
    class Meta:
        model = Dispositivo
        fields = ['nombre', 'categoria', 'zona', 'watts']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'zona': forms.Select(attrs={'class': 'form-select'}),
            'watts': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and not user.is_superuser:
            try:
                empresa = user.empresa
                self.fields['zona'].queryset = Zona.objects.filter(empresa=empresa)
            except:
                self.fields['zona'].queryset = Zona.objects.all()

class ZonaForm(forms.ModelForm):
    class Meta:
        model = Zona
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }

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
            'consumo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and not user.is_superuser:
            try:
                empresa = user.empresa
                self.fields['dispositivo'].queryset = Dispositivo.objects.filter(zona__empresa=empresa)
            except:
                self.fields['dispositivo'].queryset = Dispositivo.objects.all()
        else:
            self.fields['dispositivo'].queryset = Dispositivo.objects.all()