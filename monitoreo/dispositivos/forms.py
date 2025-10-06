from django import forms
from .models import Dispositivo, Empresa
from django.contrib.auth.models import User

class RegistroEmpresaForm(forms.ModelForm):
    usuario = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Empresa
        fields = ['nombre']

class DispositivoForm(forms.ModelForm):
    class Meta:
        model = Dispositivo
        fields = ['nombre', 'categoria', 'zona', 'watts']  # 👈 agrega watts
