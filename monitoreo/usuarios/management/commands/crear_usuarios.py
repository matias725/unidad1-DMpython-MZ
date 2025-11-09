import os
import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from usuarios.models import Perfil
from django.db import transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Crear usuarios de prueba con diferentes roles'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Obtener contraseñas de variables de entorno
                admin_password = os.getenv('ADMIN_PASSWORD', 'changeme123!')
                editor_password = os.getenv('EDITOR_PASSWORD', 'changeme456!')
                lector_password = os.getenv('LECTOR_PASSWORD', 'changeme789!')
                
                # Crear grupos
                admin_group, _ = Group.objects.get_or_create(name='Administradores')
                editor_group, _ = Group.objects.get_or_create(name='Editores')
                lector_group, _ = Group.objects.get_or_create(name='Lectores')

                # Crear superusuario (Administrador)
                if not User.objects.filter(username='admin').exists():
                    admin_user = User.objects.create_superuser(
                        username='admin',
                        email='admin@monitoreo.com',
                        password=admin_password,
                        first_name='Administrador',
                        last_name='Sistema'
                    )
                    Perfil.objects.create(user=admin_user, telefono='555-0001')
                    self.stdout.write('Superusuario creado')
                    logger.info('Superusuario admin creado exitosamente')

                # Crear editor
                if not User.objects.filter(username='editor').exists():
                    editor_user = User.objects.create_user(
                        username='editor',
                        email='editor@monitoreo.com',
                        password=editor_password,
                        first_name='Editor',
                        last_name='Usuario'
                    )
                    editor_user.groups.add(editor_group)
                    Perfil.objects.create(user=editor_user, telefono='555-0002')
                    self.stdout.write('Editor creado')
                    logger.info('Usuario editor creado exitosamente')

                # Crear lector
                if not User.objects.filter(username='lector').exists():
                    lector_user = User.objects.create_user(
                        username='lector',
                        email='lector@monitoreo.com',
                        password=lector_password,
                        first_name='Lector',
                        last_name='Usuario'
                    )
                    lector_user.groups.add(lector_group)
                    Perfil.objects.create(user=lector_user, telefono='555-0003')
                    self.stdout.write('Lector creado')
                    logger.info('Usuario lector creado exitosamente')

                self.stdout.write(self.style.SUCCESS('Usuarios creados exitosamente'))
                
        except Exception as e:
            logger.error(f'Error creando usuarios: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Error creando usuarios: {str(e)}')
            )
            raise