#!/bin/bash
#
# Script para instalar el servicio de cierre automático de fichajes como un servicio de systemd.
# Debe ejecutarse con permisos de root.
#

# Verificar si se ejecuta como root
if [ "$EUID" -ne 0 ]; then
  echo "Este script debe ejecutarse como root"
  exit 1
fi

# Obtener el directorio actual
APP_DIR=$(pwd)
echo "Directorio de la aplicación: $APP_DIR"

# Crear archivo de servicio
SERVICE_FILE="/etc/systemd/system/checkpoint-closer.service"
echo "Creando archivo de servicio en $SERVICE_FILE..."

cat > $SERVICE_FILE << EOF
[Unit]
Description=Servicio de cierre automático de fichajes
After=network.target postgresql.service

[Service]
User=$(logname)
Group=$(logname)
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/python3 $APP_DIR/run_checkpoint_closer.py
Restart=always
RestartSec=30
Environment="DATABASE_URL=${DATABASE_URL}"
Environment="SESSION_SECRET=${SESSION_SECRET}"

[Install]
WantedBy=multi-user.target
EOF

# Recargar configuración de systemd
echo "Recargando configuración de systemd..."
systemctl daemon-reload

# Habilitar el servicio para que se inicie con el sistema
echo "Habilitando servicio para que se inicie con el sistema..."
systemctl enable checkpoint-closer.service

# Iniciar el servicio
echo "Iniciando servicio..."
systemctl start checkpoint-closer.service

# Verificar estado del servicio
echo "Estado del servicio:"
systemctl status checkpoint-closer.service

echo "
Instalación completada.

Para controlar el servicio, use los siguientes comandos:
  - Ver estado: sudo systemctl status checkpoint-closer.service
  - Iniciar:    sudo systemctl start checkpoint-closer.service
  - Detener:    sudo systemctl stop checkpoint-closer.service
  - Reiniciar:  sudo systemctl restart checkpoint-closer.service
  - Ver logs:   sudo journalctl -u checkpoint-closer.service
"
