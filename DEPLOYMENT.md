# Despliegue en Debian 12 (EC2) con RDS MySQL — Guía rápida

Este repo incluye ahora un script de ayuda `deploy_debian12.sh` y una plantilla `.env.example`.

Resumen de pasos (alto nivel)
1. Crear EC2 Debian 12 y configurar Security Groups (HTTP, SSH y puerto de administración si lo deseas).
2. Asignar IP elástica (opcional).
3. Conectar por SSH (usuario `admin` en tu manual) y ejecutar `deploy_debian12.sh` **después de editar los placeholders**.

Archivos añadidos
- `deploy_debian12.sh` — script de despliegue para Debian 12 (ayuda a instalar dependencias, venv, descargar CA de RDS, crear unit systemd y configurar nginx). Revisa y sustituye las variables: `REPO_URL`, `APP_DIR`, `VENV_DIR`, `SERVICE_NAME`, `your-ec2-host.compute.amazonaws.com`.
- `monitoreo/.env.example` — plantilla existente en el proyecto (revisa y adapta para producción). Puedes copiarlo a `/etc/ecoenergy.env` o a `monitoreo/.env` según prefieras.

Notas importantes
- Edita `deploy_debian12.sh` y `monitoreo/.env.example` antes de ejecutar para no dejar valores placeholder (clave secreta, DB_HOST, DB_PASSWORD, REPO_URL).
- El script crea un unit file systemd llamado `proyecto.service` apuntando al venv definido. Ajusta `User`, `WorkingDirectory` y `EnvironmentFile` según tu instalación.
- Asegúrate de que la base de datos RDS permite conexiones desde el Security Group del EC2.

Siguientes pasos recomendados
- Revisa y actualiza el `.env` con valores reales y permisos 600.
- Ejecuta `deploy_debian12.sh` en la instancia EC2 (tras clonar o si prefieres subir el script al servidor).
- Si el servicio falla, revisa `sudo journalctl -u proyecto -n 200` y `/var/log/nginx/error.log`.

Si quieres, puedo:
- Crear un unit file adaptado a la ruta exacta de tu proyecto y commitearlo.
- Subir estos cambios al repo (commit+push) por ti.
