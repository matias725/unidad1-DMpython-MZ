from django.contrib import admin
from .models import Zona, Dispositivo, Medicion, Alerta
from usuarios.models import Organizacion

def resetear_watts(modeladmin, request, queryset):
    queryset.update(watts=0)
resetear_watts.short_description = "Resetear consumo (watts) a 0"

class MedicionInline(admin.TabularInline):
    model = Medicion
    extra = 1

@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'zona', 'watts')
    search_fields = ('nombre', 'categoria')
    list_filter = ('zona', 'categoria')
    ordering = ('nombre',)
    list_select_related = ('zona',)
    inlines = [MedicionInline]
    actions = [resetear_watts]

@admin.register(Medicion)
class MedicionAdmin(admin.ModelAdmin):
    list_display = ('dispositivo', 'consumo', 'fecha')
    list_filter = ('dispositivo__zona', 'fecha')
    list_select_related = ('dispositivo',)

@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('dispositivo', 'mensaje', 'gravedad', 'fecha')
    list_filter = ('gravedad',)
    list_select_related = ('dispositivo',)

admin.site.register(Zona)