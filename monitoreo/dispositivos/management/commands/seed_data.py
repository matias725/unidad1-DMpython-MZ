# dispositivos/management/commands/seed_data.py
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from dispositivos.models import Empresa, Zona, Dispositivo, Medicion

class Command(BaseCommand):
    help = 'Crea datos de prueba para la aplicación para la revisión en vivo'

    def handle(self, *args, **kwargs):
        self.stdout.write("Limpiando la base de datos de datos de prueba anteriores...")
        
        User.objects.filter(is_superuser=False).delete()
        Group.objects.all().delete()
        Empresa.objects.all().delete()

        self.stdout.write("Creando grupos y usuarios de prueba...")

        cliente_group, created = Group.objects.get_or_create(name='Cliente')

        # Usuario y Empresa A
        user_a = User.objects.create_user('cliente_a', 'clientea@demo.com', 'password123')
        user_a.is_staff = True  # <-- LÍNEA IMPORTANTE
        user_a.groups.add(cliente_group)
        user_a.save()  # <-- LÍNEA IMPORTANTE
        empresa_a = Empresa.objects.create(usuario=user_a, nombre='EcoEnergy Corp')

        # Usuario y Empresa B
        user_b = User.objects.create_user('cliente_b', 'clienteb@demo.com', 'password123')
        user_b.is_staff = True  # <-- LÍNEA IMPORTANTE
        user_b.groups.add(cliente_group)
        user_b.save()  # <-- LÍNEA IMPORTANTE
        empresa_b = Empresa.objects.create(usuario=user_b, nombre='Solaris Inc')

        self.stdout.write("Creando Zonas de prueba...")
        zona_norte_a = Zona.objects.create(nombre='Planta Norte', empresa=empresa_a)
        zona_sur_a = Zona.objects.create(nombre='Bodega Sur', empresa=empresa_a)
        zona_principal_b = Zona.objects.create(nombre='Oficina Central', empresa=empresa_b)

        self.stdout.write("Creando Dispositivos y Mediciones de prueba...")

        dispositivos_a = [
            Dispositivo.objects.create(nombre='Sensor de Temperatura A-1', categoria='Sensor', zona=zona_norte_a, watts=15.5),
            Dispositivo.objects.create(nombre='Actuador de Riego A-2', categoria='Actuador', zona=zona_sur_a, watts=120)
        ]
        dispositivos_b = [
            Dispositivo.objects.create(nombre='Medidor de Consumo B-1', categoria='General', zona=zona_principal_b, watts=50)
        ]

        for disp in dispositivos_a + dispositivos_b:
            for _ in range(random.randint(3, 7)):
                Medicion.objects.create(
                    dispositivo=disp,
                    consumo=round(random.uniform(10.0, 250.0), 2)
                )
        
        self.stdout.write(self.style.SUCCESS('¡Semillas creadas exitosamente!'))
        self.stdout.write('Puedes iniciar sesión con:')
        self.stdout.write('Superusuario: el que creaste con "createsuperuser"')
        self.stdout.write('Usuario Limitado A: cliente_a / password123')
        self.stdout.write('Usuario Limitado B: cliente_b / password123')