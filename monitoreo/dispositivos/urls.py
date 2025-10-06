from django.urls import path
from . import views

urlpatterns = [
    # DISPOSITIVOS
    path('', views.listar_dispositivos, name='listar_dispositivos'),          # /dispositivos/
    path('crear/', views.crear_dispositivo, name='crear_dispositivo'),        # /dispositivos/crear/
    path('<int:dispositivo_id>/', views.detalle_dispositivo, name='detalle_dispositivo'),  # /dispositivos/1/
    path('<int:dispositivo_id>/editar/', views.editar_dispositivo, name='editar_dispositivo'), # /dispositivos/1/editar/
    path('<int:dispositivo_id>/eliminar/', views.eliminar_dispositivo, name='eliminar_dispositivo'), # /dispositivos/1/eliminar/

    # MEDICIONES
    path('mediciones/', views.listar_mediciones, name='listar_mediciones'),  # /dispositivos/mediciones/

    # DASHBOARD
    path('dashboard/', views.dashboard, name='dashboard'),                  # /dispositivos/dashboard/
]
