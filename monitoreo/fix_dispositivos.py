#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitoreo.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import Organizacion, Perfil
from dispositivos.models import Zona, Dispositivo

def diagnosticar_problema():
    print("=== DIAGNÓSTICO DEL PROBLEMA DE DISPOSITIVOS ===\n")
    
    # 1. Verificar usuarios
    usuarios = User.objects.all()
    print(f"Total de usuarios: {usuarios.count()}")
    
    for user in usuarios:
        print(f"\nUsuario: {user.username}")
        try:
            perfil = user.perfil
            print(f"  - Rol: {perfil.rol}")
            print(f"  - Organización: {perfil.organizacion}")
        except:
            print("  - Sin perfil asignado")
    
    # 2. Verificar organizaciones
    organizaciones = Organizacion.objects.all()
    print(f"\nTotal de organizaciones: {organizaciones.count()}")
    for org in organizaciones:
        print(f"  - {org.nombre}")
    
    # 3. Verificar zonas
    zonas = Zona.objects.all()
    print(f"\nTotal de zonas: {zonas.count()}")
    for zona in zonas:
        print(f"  - {zona.nombre} (Org: {zona.organizacion})")
    
    # 4. Verificar dispositivos
    dispositivos = Dispositivo.objects.all()
    print(f"\nTotal de dispositivos: {dispositivos.count()}")

def arreglar_problema():
    print("\n=== ARREGLANDO PROBLEMAS ===\n")
    
    # 1. Crear organización por defecto si no existe
    org_default, created = Organizacion.objects.get_or_create(
        nombre='EcoEnergy Default'
    )
    if created:
        print("✓ Organización por defecto creada")
    
    # 2. Asignar organización a usuarios sin perfil o sin organización
    usuarios_sin_perfil = []
    for user in User.objects.all():
        try:
            perfil = user.perfil
            if not perfil.organizacion:
                perfil.organizacion = org_default
                perfil.save()
                print(f"✓ Organización asignada a {user.username}")
        except:
            # Crear perfil si no existe
            perfil = Perfil.objects.create(
                user=user,
                rol='cliente_admin',
                organizacion=org_default
            )
            usuarios_sin_perfil.append(user.username)
            print(f"✓ Perfil creado para {user.username}")
    
    # 3. Crear zona por defecto si no hay zonas para la organización
    zona_default, created = Zona.objects.get_or_create(
        nombre='Zona Principal',
        organizacion=org_default
    )
    if created:
        print("✓ Zona por defecto creada")
    
    # 4. Verificar que todas las zonas tengan organización
    zonas_sin_org = Zona.objects.filter(organizacion__isnull=True)
    for zona in zonas_sin_org:
        zona.organizacion = org_default
        zona.save()
        print(f"✓ Organización asignada a zona {zona.nombre}")
    
    print(f"\n✓ Problemas corregidos. Usuarios sin perfil encontrados: {len(usuarios_sin_perfil)}")

if __name__ == "__main__":
    diagnosticar_problema()
    
    respuesta = input("\n¿Deseas arreglar los problemas encontrados? (s/n): ")
    if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        arreglar_problema()
        print("\n=== DIAGNÓSTICO DESPUÉS DE LA CORRECCIÓN ===")
        diagnosticar_problema()
    else:
        print("No se realizaron cambios.")