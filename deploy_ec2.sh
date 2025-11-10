#!/bin/bash

# Script de despliegue para EC2
echo "=== Iniciando despliegue en EC2 ==="

# Actualizar sistema
sudo apt update
sudo apt upgrade -y

# Instalar Python y dependencias
sudo apt install -y python3 python3-pip python3-venv nginx git

# Crear directorio del proyecto
sudo mkdir -p /var/www/ecoenergy
cd /var/www/ecoenergy

# Clonar repositorio (reemplazar con tu URL de GitHub)
# sudo git clone https://github.com/tu-usuario/ecoenergy-monitoreo.git .

# Crear entorno virtual
sudo python3 -m venv venv
sudo chown -R ubuntu:ubuntu /var/www/ecoenergy
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export DJANGO_DEBUG=False
export DJANGO_SECRET_KEY="tu-clave-secreta-aqui"
export ALLOWED_HOSTS="tu-dominio.com,tu-ip-publica"

# Ejecutar migraciones
python manage.py migrate
python manage.py collectstatic --noinput

# Crear superusuario (opcional)
# python manage.py createsuperuser

# Configurar Gunicorn
pip install gunicorn

# Configurar Nginx
sudo tee /etc/nginx/sites-available/ecoenergy << EOF
server {
    listen 80;
    server_name tu-dominio.com tu-ip-publica;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/ecoenergy;
    }
    
    location /media/ {
        root /var/www/ecoenergy;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/ecoenergy/ecoenergy.sock;
    }
}
EOF

# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/ecoenergy /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

# Configurar servicio systemd para Gunicorn
sudo tee /etc/systemd/system/ecoenergy.service << EOF
[Unit]
Description=Gunicorn instance to serve EcoEnergy
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/ecoenergy
Environment="PATH=/var/www/ecoenergy/venv/bin"
Environment="DJANGO_DEBUG=False"
Environment="DJANGO_SECRET_KEY=tu-clave-secreta-aqui"
Environment="ALLOWED_HOSTS=tu-dominio.com,tu-ip-publica"
ExecStart=/var/www/ecoenergy/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/ecoenergy/ecoenergy.sock monitoreo.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Iniciar servicios
sudo systemctl start ecoenergy
sudo systemctl enable ecoenergy
sudo systemctl status ecoenergy

echo "=== Despliegue completado ==="
echo "Accede a tu aplicación en: http://tu-ip-publica"