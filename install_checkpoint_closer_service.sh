#!/bin/bash
# Script para instalar el servicio de cierre automático de fichajes como un servicio systemd
# Versión 1.1.0 - Actualizado con verificación de sistema mejorada

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================================${NC}"
echo -e "${BLUE}   INSTALACIÓN DEL SERVICIO DE CIERRE AUTOMÁTICO DE FICHAJES${NC}"
echo -e "${BLUE}   Versión 1.1.0${NC}"
echo -e "${BLUE}========================================================${NC}"

# Verificar si se está ejecutando como root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[ERROR] Este script debe ejecutarse como root${NC}"
  echo "Por favor, ejecuta: sudo $0"
  exit 1
fi

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
  echo -e "${RED}[ERROR] Python3 no está instalado en el sistema${NC}"
  echo -e "Por favor, instálelo con: ${YELLOW}apt-get install python3${NC}"
  exit 1
fi

# Verificar que el archivo principal existe
if [ ! -f "$(pwd)/scheduled_checkpoints_closer.py" ]; then
  echo -e "${RED}[ERROR] No se encuentra el archivo scheduled_checkpoints_closer.py${NC}"
  echo -e "Por favor, asegúrese de ejecutar este script desde el directorio raíz del proyecto"
  exit 1
fi

# Probar la conexión a la base de datos y la funcionalidad básica
echo -e "${YELLOW}Verificando la conexión a la base de datos...${NC}"
VERIFY_RESULT=$(python3 -c "
import sys
try:
    from app import create_app
    app = create_app()
    with app.app_context():
        from models_checkpoints import CheckPoint
        count = CheckPoint.query.count()
        print(f'✓ Conexión exitosa - {count} checkpoints encontrados')
        sys.exit(0)
except Exception as e:
    print(f'✗ Error: {e}')
    sys.exit(1)
" 2>&1)

if [ $? -ne 0 ]; then
  echo -e "${RED}[ERROR] No se pudo conectar a la base de datos:${NC}"
  echo -e "$VERIFY_RESULT"
  echo -e "${YELLOW}¿Desea continuar con la instalación de todas formas? (s/N)${NC}"
  read -r CONTINUE
  if [[ ! "$CONTINUE" =~ ^[Ss]$ ]]; then
    echo -e "${RED}Instalación cancelada${NC}"
    exit 1
  fi
else
  echo -e "${GREEN}$VERIFY_RESULT${NC}"
fi

# Verificación completa
echo -e "${GREEN}✓ Verificaciones preliminares completadas${NC}"

# Obtener el directorio actual del proyecto
PROJECT_DIR=$(pwd)
echo -e "${YELLOW}Directorio del proyecto:${NC} $PROJECT_DIR"

# Crear el archivo de servicio systemd
SERVICE_FILE="/etc/systemd/system/checkpoints-closer.service"
echo -e "${YELLOW}Creando archivo de servicio en:${NC} $SERVICE_FILE"

cat > $SERVICE_FILE << EOF
[Unit]
Description=Servicio de cierre automático de fichajes pendientes
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 $PROJECT_DIR/scheduled_checkpoints_closer.py
Restart=on-failure
RestartSec=5s
StandardOutput=append:/var/log/checkpoints-closer.log
StandardError=append:/var/log/checkpoints-closer.log

[Install]
WantedBy=multi-user.target
EOF

# Recargar configuración de systemd
echo -e "${YELLOW}Recargando configuración de systemd...${NC}"
systemctl daemon-reload

# Habilitar el servicio para que se inicie automáticamente
echo -e "${YELLOW}Habilitando el servicio para que se inicie con el sistema...${NC}"
systemctl enable checkpoints-closer.service

# Iniciar el servicio
echo -e "${YELLOW}Iniciando el servicio...${NC}"
systemctl start checkpoints-closer.service

# Verificar el estado del servicio
echo -e "${YELLOW}Verificando el estado del servicio:${NC}"
systemctl status checkpoints-closer.service

echo -e "\n${GREEN}¡Servicio instalado correctamente!${NC}"
echo -e "Para administrar el servicio, usa los siguientes comandos:"
echo -e "${YELLOW}Ver estado:${NC} sudo systemctl status checkpoints-closer.service"
echo -e "${YELLOW}Iniciar:${NC} sudo systemctl start checkpoints-closer.service"
echo -e "${YELLOW}Detener:${NC} sudo systemctl stop checkpoints-closer.service"
echo -e "${YELLOW}Reiniciar:${NC} sudo systemctl restart checkpoints-closer.service"
echo -e "${YELLOW}Ver logs:${NC} sudo journalctl -u checkpoints-closer.service -f"
echo -e "\n${YELLOW}Los logs también se guardan en:${NC}"
echo -e "- /var/log/checkpoints-closer.log (salida del servicio)"
echo -e "- $PROJECT_DIR/checkpoints_closer.log (logs internos de la aplicación)"