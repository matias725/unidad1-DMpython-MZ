from django.contrib import admin

# Register your models here.
from .models import Empresa, Zona, Dispositivo, Medicion, Alerta

admin.site.register(Empresa)
admin.site.register(Zona)
admin.site.register(Dispositivo)
admin.site.register(Medicion)
admin.site.register(Alerta)