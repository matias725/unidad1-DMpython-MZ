from django.urls import path
from . import views

app_name = 'dispositivos'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Dispositivos
    path('dispositivos/', views.listar_dispositivos, name='dispositivo_list'),
    path('dispositivos/crear/', views.crear_dispositivo, name='dispositivo_create'),
    path('dispositivos/<int:dispositivo_id>/', views.detalle_dispositivo, name='dispositivo_detail'),
    path('dispositivos/<int:dispositivo_id>/editar/', views.editar_dispositivo, name='dispositivo_edit'),
    path('dispositivos/<int:dispositivo_id>/eliminar/', views.eliminar_dispositivo, name='dispositivo_delete'),
    path('dispositivos/exportar/', views.exportar_dispositivos_excel, name='dispositivo_export'),

    
    # Zonas
    path('zonas/', views.listar_zonas, name='zona_list'),
    path('zonas/crear/', views.crear_zona, name='zona_create'),
    path('zonas/<int:zona_id>/editar/', views.editar_zona, name='zona_edit'),
    path('zonas/<int:zona_id>/eliminar/', views.eliminar_zona, name='zona_delete'),
    
    # Mediciones
    path('mediciones/', views.listar_mediciones, name='medicion_list'),
    path('mediciones/crear/', views.crear_medicion, name='medicion_create'),
    path('mediciones/<int:medicion_id>/', views.detalle_medicion, name='medicion_detail'),
    path('mediciones/<int:medicion_id>/editar/', views.editar_medicion, name='medicion_edit'),
    path('mediciones/<int:medicion_id>/eliminar/', views.eliminar_medicion, name='medicion_delete'),
    
    # Alertas
    path('alertas/', views.listar_alertas, name='alerta_list'),
]