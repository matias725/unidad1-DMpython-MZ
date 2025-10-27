from django.urls import path
from . import views

urlpatterns = [
    # DISPOSITIVOS
    path('', views.listar_dispositivos, name='listar_dispositivos'),
    path('crear/', views.crear_dispositivo, name='crear_dispositivo'),
    path('<int:dispositivo_id>/', views.detalle_dispositivo, name='detalle_dispositivo'),
    path('<int:dispositivo_id>/editar/', views.editar_dispositivo, name='editar_dispositivo'),
    path('<int:dispositivo_id>/eliminar/', views.eliminar_dispositivo, name='eliminar_dispositivo'),
    
    # ZONAS (¡NUEVO!)
    path('zonas/', views.listar_zonas, name='listar_zonas'),
    path('zonas/crear/', views.crear_zona, name='crear_zona'),
    path('zonas/<int:zona_id>/editar/', views.editar_zona, name='editar_zona'),
    path('zonas/<int:zona_id>/eliminar/', views.eliminar_zona, name='eliminar_zona'),

    # MEDICIONES
    path('mediciones/', views.listar_mediciones, name='listar_mediciones'),
    
    # NOTA: Eliminamos 'dashboard/' de aquí porque ya está en monitoreo/urls.py
]