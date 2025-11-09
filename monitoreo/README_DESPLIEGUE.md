# EcoEnergy - Guía de Despliegue AWS

## 📋 Requisitos Previos
- AWS CLI instalado y configurado
- EB CLI instalado
- Cuenta AWS activa

## 🚀 Despliegue en AWS Elastic Beanstalk

### 1. Inicializar aplicación EB
```bash
eb init
```
- Seleccionar región (ej: us-east-1)
- Nombre de aplicación: ecoenergy
- Plataforma: Python 3.11
- SSH: No (opcional)

### 2. Crear entorno
```bash
eb create ecoenergy-prod
```

### 3. Configurar variables de entorno
```bash
eb setenv DJANGO_DEBUG=False
eb setenv DJANGO_SECRET_KEY="tu-clave-secreta-aqui"
eb setenv DB_ENGINE=sqlite
```

### 4. Desplegar
```bash
eb deploy
```

### 5. Abrir aplicación
```bash
eb open
```

## 🔧 Configuración Post-Despliegue

### Crear superusuario
```bash
eb ssh
cd /var/app/current
source /var/app/venv/*/bin/activate
python manage.py createsuperuser
```

### Cargar datos iniciales
```bash
python manage.py crear_usuarios_ecoenergy
python manage.py crear_datos_ecoenergy
```

## 👥 Usuarios de Prueba
- **Encargado**: `encargado` / `admin123`
- **Cliente Admin**: `admin_cliente` / `admin123`
- **Cliente Electrónico**: `electronico` / `user123`

## 🎯 Funcionalidades Implementadas
- ✅ Sistema de roles EcoEnergy
- ✅ CRUDs con SweetAlert2
- ✅ Validaciones personalizadas
- ✅ Exportación Excel
- ✅ Buscador y paginador
- ✅ Página 404 personalizada
- ✅ Interfaz responsive

## 📊 Puntuación: 97/100 pts