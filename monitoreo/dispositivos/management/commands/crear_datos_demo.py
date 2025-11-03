from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dispositivos.models import Empresa, Zona, Dispositivo, Medicion, Alerta
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Crear datos de demostración'

    def handle(self, *args, **options):
        # Crear empresa para usuarios no admin
        editor_user = User.objects.get(username='editor')
        lector_user = User.objects.get(username='lector')
        
        empresa, created = Empresa.objects.get_or_create(
            usuario=editor_user,
            defaults={'nombre': 'EcoEnergy'}
        )
        
        # Crear zonas
        zona1, _ = Zona.objects.get_or_create(
            nombre='Oficina Principal',
            empresa=empresa
        )
        zona2, _ = Zona.objects.get_or_create(
            nombre='Almacén',
            empresa=empresa
        )
        
        # Crear dispositivos
        dispositivos_data = [
            {'nombre': 'Sensor Temperatura 1', 'categoria': 'Sensor', 'zona': zona1, 'watts': 25.5},
            {'nombre': 'Aire Acondicionado', 'categoria': 'Actuador', 'zona': zona1, 'watts': 1500.0},
            {'nombre': 'Sensor Movimiento', 'categoria': 'Sensor', 'zona': zona2, 'watts': 15.0},
            {'nombre': 'Iluminación LED', 'categoria': 'General', 'zona': zona2, 'watts': 120.0},
        ]
        
        for data in dispositivos_data:
            dispositivo, created = Dispositivo.objects.get_or_create(
                nombre=data['nombre'],
                defaults=data
            )
            
            # Crear mediciones
            for i in range(10):
                fecha = datetime.now() - timedelta(days=i)
                consumo = random.uniform(20, 150)
                Medicion.objects.get_or_create(
                    dispositivo=dispositivo,
                    fecha=fecha,
                    defaults={'consumo': consumo}
                )
                
                # Crear alertas ocasionales
                if consumo > 100:
                    Alerta.objects.get_or_create(
                        dispositivo=dispositivo,
                        fecha=fecha,
                        defaults={
                            'mensaje': f'Consumo elevado detectado: {consumo:.1f} kWh',
                            'gravedad': 'Grave' if consumo > 120 else 'Alta'
                        }
                    )
        
        self.stdout.write(self.style.SUCCESS('Datos de demostración creados exitosamente'))