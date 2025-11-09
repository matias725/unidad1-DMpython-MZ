import os
import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import Perfil, Organizacion
from django.db import transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Crea usuarios de ejemplo con roles EcoEnergy'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Obtener contraseñas de variables de entorno
                admin_password = os.getenv('ADMIN_PASSWORD', 'changeme123!')
                user_password = os.getenv('USER_PASSWORD', 'changeme456!')
                
                # Crear organizaciones
                org1, created = Organizacion.objects.get_or_create(
                    nombre='TechCorp S.A.',
                    defaults={'nombre': 'TechCorp S.A.'}
                )
                
                org2, created = Organizacion.objects.get_or_create(
                    nombre='GreenEnergy Ltda.',
                    defaults={'nombre': 'GreenEnergy Ltda.'}
                )

                # Crear Encargado EcoEnergy
                if not User.objects.filter(username='encargado').exists():
                    user_encargado = User.objects.create_user(
                        username='encargado',
                        email='encargado@ecoenergy.com',
                        password=admin_password,
                        first_name='Carlos',
                        last_name='Administrador'
                    )
                    Perfil.objects.create(
                        user=user_encargado,
                        rol='encargado_ecoenergy',
                        telefono='+56 9 1111 1111'
                    )
                    self.stdout.write('* Encargado EcoEnergy creado')
                    logger.info('Encargado EcoEnergy creado exitosamente')

                # Crear Cliente Admin
                if not User.objects.filter(username='admin_cliente').exists():
                    user_admin = User.objects.create_user(
                        username='admin_cliente',
                        email='admin@techcorp.com',
                        password=admin_password,
                        first_name='María',
                        last_name='Gerente'
                    )
                    Perfil.objects.create(
                        user=user_admin,
                        rol='cliente_admin',
                        organizacion=org1,
                        telefono='+56 9 2222 2222'
                    )
                    self.stdout.write('* Cliente Admin creado')
                    logger.info('Cliente Admin creado exitosamente')

                # Crear Cliente Electrónico
                if not User.objects.filter(username='electronico').exists():
                    user_electronico = User.objects.create_user(
                        username='electronico',
                        email='electronico@techcorp.com',
                        password=user_password,
                        first_name='Juan',
                        last_name='Técnico'
                    )
                    Perfil.objects.create(
                        user=user_electronico,
                        rol='cliente_electronico',
                        organizacion=org1,
                        telefono='+56 9 3333 3333'
                    )
                    self.stdout.write('* Cliente Electrónico creado')
                    logger.info('Cliente Electrónico creado exitosamente')

                # Crear otro Cliente Admin para segunda organización
                if not User.objects.filter(username='admin_green').exists():
                    user_admin2 = User.objects.create_user(
                        username='admin_green',
                        email='admin@greenenergy.com',
                        password=admin_password,
                        first_name='Ana',
                        last_name='Directora'
                    )
                    Perfil.objects.create(
                        user=user_admin2,
                        rol='cliente_admin',
                        organizacion=org2,
                        telefono='+56 9 4444 4444'
                    )
                    self.stdout.write('* Cliente Admin (GreenEnergy) creado')
                    logger.info('Cliente Admin GreenEnergy creado exitosamente')

                self.stdout.write(
                    self.style.SUCCESS('\nUsuarios EcoEnergy creados exitosamente!\n')
                )
                self.stdout.write('Roles disponibles:')
                self.stdout.write('- Encargado EcoEnergy: Acceso total al sistema')
                self.stdout.write('- Cliente Admin: CRUD completo de su organización')
                self.stdout.write('- Cliente Electrónico: CRUD mediciones, lectura dispositivos')
                
        except Exception as e:
            logger.error(f'Error creando usuarios: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Error creando usuarios: {str(e)}')
            )
            raise