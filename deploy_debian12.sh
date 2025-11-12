#!/usr/bin/env bash
set -euo pipefail

# deploy_debian12.sh
# Script de ayuda para desplegar en Debian 12 (EC2) siguiendo el manual.
# NO automatiza todo (revisar y sustituir placeholders antes de ejecutar).

APP_DIR="/home/admin/Unidad_1_python_JA/monitoreo"
VENV_DIR="/home/admin/Unidad_1_python_JA/.venv"
REPO_URL="REEMPLAZAR_CON_TU_REPO"
ENV_FILE="/etc/ecoenergy.env"
SSL_DIR="/etc/ssl/certs/aws-rds"
RDS_CA_URL="https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem"

echo "[1/12] Actualizando sistema e instalando paquetes base..."
sudo apt update && sudo apt -y upgrade
sudo apt -y install python3 python3-venv python3-pip build-essential git pkg-config \ 
    libjpeg-dev zlib1g-dev libmariadb-dev libmariadb-dev-compat ca-certificates curl nginx acl

echo "[2/12] Crear directorio de aplicación y usuario (si aplica)..."
sudo mkdir -p $(dirname "$APP_DIR")
# Supone que usarás usuario admin; ajusta si es otro
sudo chown -R $(whoami):$(whoami) $(dirname "$APP_DIR")

echo "[3/12] Clonando repositorio (si no está presente)..."
if [ ! -d "$APP_DIR" ] || [ -z "$(ls -A "$APP_DIR" 2>/dev/null)" ]; then
  mkdir -p "$APP_DIR"
  git clone "$REPO_URL" "$APP_DIR"
else
  echo "Directorio $APP_DIR ya existe; se asume que contiene el repo"
fi

cd "$APP_DIR"

echo "[4/12] Crear/activar virtualenv y actualizar pip..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip setuptools wheel

echo "[5/12] Instalar dependencias del proyecto..."
# Ajusta la ruta a requirements de producción si es necesario
if [ -f "monitoreo/requirements-aws.txt" ]; then
  pip install -r monitoreo/requirements-aws.txt
elif [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
else
  echo "No se encontró requirements.txt ni requirements-aws.txt. Instala dependencias manualmente." >&2
fi

echo "[6/12] Descargar certificado RDS (si se requiere) y ajustar permisos..."
sudo mkdir -p "$SSL_DIR"
sudo curl -s -o "$SSL_DIR/rds-combined-ca-bundle.pem" "$RDS_CA_URL"
sudo chown root:root "$SSL_DIR/rds-combined-ca-bundle.pem"
sudo chmod 644 "$SSL_DIR/rds-combined-ca-bundle.pem"

echo "[7/12] Crear archivo de entorno de ejemplo (no sobreescribe si existe)..."
if [ ! -f "$ENV_FILE" ]; then
  sudo tee "$ENV_FILE" > /dev/null <<EOF
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=CAMBIA_POR_UNA_CLAVE_SEGURA
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,your-ec2-host.compute.amazonaws.com
DB_ENGINE=mysql
DB_NAME=proyecto_db
DB_USER=proyecto_user
DB_PASSWORD=CAMBIA_POR_PASSWORD_SEGURA
DB_HOST=django-db.xxxxxx.region.rds.amazonaws.com
DB_PORT=3306
MYSQL_SSL_CA=$SSL_DIR/rds-combined-ca-bundle.pem
DJANGO_LANGUAGE_CODE=es-cl
DJANGO_TIME_ZONE=America/Santiago
EOF
  sudo chmod 600 "$ENV_FILE"
  echo "Archivo de entorno creado en $ENV_FILE — edítalo y añade valores reales antes de continuar."
else
  echo "Archivo $ENV_FILE ya existe. Revísalo y actualiza los valores si es necesario."
fi

echo "[8/12] Migraciones y collectstatic (requiere DB accesible si DB_ENGINE=mysql)..."
cd "$APP_DIR/monitoreo"
# Cargar variables temporales desde ENV_FILE para esta sesión
set -a
source "$ENV_FILE" || true
set +a

# Si DB_ENGINE es mysql y la BD no es accesible, estas órdenes fallarán.
python manage.py migrate --noinput || true
python manage.py collectstatic --noinput || true

echo "[9/12] Ajustando permisos ACL para que www-data (Nginx) pueda leer staticfiles..."
sudo apt -y install acl || true
if [ -d "$APP_DIR/monitoreo/staticfiles" ]; then
  sudo setfacl -R -m u:www-data:rx "$APP_DIR/monitoreo/staticfiles"
  sudo setfacl -m u:www-data:x $(dirname "$APP_DIR")
  sudo setfacl -m u:www-data:x "$APP_DIR"
  sudo setfacl -m u:www-data:x "$APP_DIR/monitoreo"
fi

echo "[10/12] Instalar y configurar Gunicorn (en venv)..."
pip install gunicorn || true

SERVICE_NAME="proyecto"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

if [ ! -f "$SERVICE_FILE" ]; then
  echo "Creando unit file systemd en $SERVICE_FILE (ajusta rutas y usuario si necesario)"
  sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Gunicorn Django Service
After=network.target

[Service]
User=$(whoami)
Group=www-data
WorkingDirectory=$APP_DIR/monitoreo
EnvironmentFile=$ENV_FILE
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 monitoreo.wsgi:application
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF
  sudo systemctl daemon-reload
  sudo systemctl enable --now "$SERVICE_NAME"
else
  echo "Service file $SERVICE_FILE ya existe — revísalo manualmente."
fi

echo "[11/12] Configurar Nginx (server block)"
NGINX_FILE="/etc/nginx/sites-available/ecoenergy"
if [ ! -f "$NGINX_FILE" ]; then
  sudo tee "$NGINX_FILE" > /dev/null <<EOF
server {
    listen 80;
    server_name your-ec2-host.compute.amazonaws.com YOUR_IP_PUBLICA;

    client_max_body_size 20m;

    location /static/ {
        alias $APP_DIR/monitoreo/staticfiles/;
        access_log off;
        expires 30d;
    }

    location /media/ {
        alias $APP_DIR/monitoreo/media/;
        access_log off;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
EOF
  sudo ln -sf "$NGINX_FILE" /etc/nginx/sites-enabled/ecoenergy
  sudo rm -f /etc/nginx/sites-enabled/default || true
  sudo nginx -t
  sudo systemctl reload nginx
else
  echo "Nginx config $NGINX_FILE ya existe — revísalo manualmente."
fi

echo "[12/12] Fin. Revisa logs y el estado del servicio systemd si algo falla."

echo "Comandos útiles:"
echo "  sudo journalctl -u proyecto -n 200 --no-pager"
echo "  sudo tail -n 200 /var/log/nginx/error.log"
echo "  curl -I http://YOUR_IP_PUBLICA/"

exit 0
