from django.core.management.base import BaseCommand
from django.db import transaction
from usuarios.models import Organizacion
from dispositivos.models import Zona, Dispositivo, Medicion
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Crea datos de ejemplo para EcoEnergy'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Obtener organizaciones
            try:
                org1 = Organizacion.objects.get(nombre='TechCorp S.A.')
                org2 = Organizacion.objects.get(nombre='GreenEnergy Ltda.')
            except Organizacion.DoesNotExist:
                self.stdout.write('Error: Ejecuta primero crear_usuarios_ecoenergy')
                return

            # Crear zonas para TechCorp
            zona1, created = Zona.objects.get_or_create(
                nombre='Oficina Principal',
                organizacion=org1
            )
            zona2, created = Zona.objects.get_or_create(
                nombre='Sala de Servidores',
                organizacion=org1
            )
            zona3, created = Zona.objects.get_or_create(
                nombre='Laboratorio',
                organizacion=org1
            )

            # Crear zonas para GreenEnergy
            zona4, created = Zona.objects.get_or_create(
                nombre='Planta Solar',
                organizacion=org2
            )
            zona5, created = Zona.objects.get_or_create(
                nombre='Centro de Control',
                organizacion=org2
            )

            self.stdout.write('* Zonas creadas')

            # Crear dispositivos para TechCorp
            dispositivos_techcorp = [
                ('Sensor Temperatura 01', 'Sensor', zona1, 15.5),
                ('Aire Acondicionado Central', 'Actuador', zona1, 2500.0),
                ('Servidor Principal', 'General', zona2, 800.0),
                ('UPS Sala Servidores', 'General', zona2, 1200.0),
                ('Microscopio Digital', 'General', zona3, 150.0),
            ]

            for nombre, categoria, zona, watts in dispositivos_techcorp:
                dispositivo, created = Dispositivo.objects.get_or_create(
                    nombre=nombre,
                    defaults={
                        'categoria': categoria,
                        'zona': zona,
                        'watts': watts
                    }
                )

            # Crear dispositivos para GreenEnergy
            dispositivos_green = [
                ('Panel Solar A1', 'Sensor', zona4, 300.0),
                ('Panel Solar A2', 'Sensor', zona4, 300.0),
                ('Inversor Principal', 'Actuador', zona4, 50.0),
                ('Monitor Central', 'General', zona5, 120.0),
            ]

            for nombre, categoria, zona, watts in dispositivos_green:
                dispositivo, created = Dispositivo.objects.get_or_create(
                    nombre=nombre,
                    defaults={
                        'categoria': categoria,
                        'zona': zona,
                        'watts': watts
                    }
                )

            self.stdout.write('* Dispositivos creados')

            # Crear mediciones de ejemplo
            dispositivos = Dispositivo.objects.all()
            for dispositivo in dispositivos:
                for i in range(10):
                    fecha = datetime.now() - timedelta(days=i)
                    consumo = round(random.uniform(10.0, 150.0), 2)
                    
                    Medicion.objects.get_or_create(
                        dispositivo=dispositivo,
                        fecha=fecha,
                        defaults={'consumo': consumo}
                    )

            self.stdout.write('* Mediciones creadas')
            self.stdout.write(
                self.style.SUCCESS('\nDatos EcoEnergy creados exitosamente!')
            )