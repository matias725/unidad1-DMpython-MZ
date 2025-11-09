#!/usr/bin/env python
"""
Script de inicialización para producción
Ejecutar después del primer despliegue
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitoreo.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User

def init_production():
    print("🚀 Inicializando EcoEnergy en producción...")
    
    # Aplicar migraciones
    print("📦 Aplicando migraciones...")
    call_command('migrate', verbosity=0)
    
    # Crear usuarios de ejemplo
    print("👥 Creando usuarios de ejemplo...")
    try:
        call_command('crear_usuarios_ecoenergy')
        print("✅ Usuarios creados")
    except Exception as e:
        print(f"⚠️  Usuarios ya existen: {e}")
    
    # Crear datos de ejemplo
    print("📊 Creando datos de ejemplo...")
    try:
        call_command('crear_datos_ecoenergy')
        print("✅ Datos creados")
    except Exception as e:
        print(f"⚠️  Datos ya existen: {e}")
    
    # Recopilar archivos estáticos
    print("🎨 Recopilando archivos estáticos...")
    call_command('collectstatic', verbosity=0, interactive=False)
    
    print("\n🎉 ¡EcoEnergy listo para usar!")
    print("\n👥 Usuarios disponibles:")
    print("- encargado / admin123 (Encargado EcoEnergy)")
    print("- admin_cliente / admin123 (Cliente Admin)")
    print("- electronico / user123 (Cliente Electrónico)")

if __name__ == '__main__':
    init_production()