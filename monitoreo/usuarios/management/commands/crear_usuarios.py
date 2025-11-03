from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from usuarios.models import Perfil

class Command(BaseCommand):
    help = 'Crear usuarios de prueba con diferentes roles'

    def handle(self, *args, **options):
        # Crear grupos
        admin_group, _ = Group.objects.get_or_create(name='Administradores')
        editor_group, _ = Group.objects.get_or_create(name='Editores')
        lector_group, _ = Group.objects.get_or_create(name='Lectores')

        # Crear superusuario (Administrador)
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@monitoreo.com',
                password='Admin123',
                first_name='Administrador',
                last_name='Sistema'
            )
            Perfil.objects.create(user=admin_user, telefono='555-0001')
            self.stdout.write(f'Superusuario creado: admin / Admin123')

        # Crear editor
        if not User.objects.filter(username='editor').exists():
            editor_user = User.objects.create_user(
                username='editor',
                email='editor@monitoreo.com',
                password='Editor123',
                first_name='Editor',
                last_name='Usuario'
            )
            editor_user.groups.add(editor_group)
            Perfil.objects.create(user=editor_user, telefono='555-0002')
            self.stdout.write(f'Editor creado: editor / Editor123')

        # Crear lector
        if not User.objects.filter(username='lector').exists():
            lector_user = User.objects.create_user(
                username='lector',
                email='lector@monitoreo.com',
                password='Lector123',
                first_name='Lector',
                last_name='Usuario'
            )
            lector_user.groups.add(lector_group)
            Perfil.objects.create(user=lector_user, telefono='555-0003')
            self.stdout.write(f'Lector creado: lector / Lector123')

        self.stdout.write(self.style.SUCCESS('Usuarios creados exitosamente'))