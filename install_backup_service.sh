#!/bin/bash
# Script para configurar el servicio de backups automáticos

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Obtener el directorio actual (donde está la aplicación)
APP_DIR=$(pwd)
SCRIPT_PATH="$APP_DIR/scheduled_backup.py"

echo -e "${YELLOW}Configurando servicio de backups automáticos...${NC}"

# Verificar que el script exista
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${RED}Error: No se encontró el script de backups en $SCRIPT_PATH${NC}"
    exit 1
fi

# Verificar que tiene permisos de ejecución
chmod +x "$SCRIPT_PATH"

echo -e "${GREEN}Script de backups encontrado y con permisos de ejecución.${NC}"

# Crear entrada en crontab para ejecutar cada día a las 3 AM
(crontab -l 2>/dev/null || echo "") | grep -v "$SCRIPT_PATH" | \
{ cat; echo "0 3 * * * cd $APP_DIR && python $SCRIPT_PATH >> $APP_DIR/scheduled_backup.log 2>&1"; } | \
crontab -

echo -e "${GREEN}Servicio de backups configurado para ejecutarse diariamente a las 3:00 AM.${NC}"
echo -e "${YELLOW}Los logs de ejecución se guardarán en $APP_DIR/scheduled_backup.log${NC}"

# Crear script para verificar el estado del servicio
STATUS_SCRIPT="$APP_DIR/check_backup_service.sh"

cat > "$STATUS_SCRIPT" << EOF
#!/bin/bash
# Script para verificar el estado del servicio de backups automáticos

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Verificando servicio de backups automáticos...${NC}"

# Verificar si está configurado en crontab
if crontab -l 2>/dev/null | grep -q "$SCRIPT_PATH"; then
    echo -e "${GREEN}✅ El servicio de backups está correctamente configurado.${NC}"
else
    echo -e "${RED}❌ El servicio de backups NO está configurado en crontab.${NC}"
fi

# Verificar últimos logs
LOG_FILE="$APP_DIR/scheduled_backup.log"
if [ -f "\$LOG_FILE" ]; then
    echo -e "${YELLOW}Últimas 5 líneas del log:${NC}"
    tail -n 5 "\$LOG_FILE"
else
    echo -e "${YELLOW}No se encontró archivo de log.${NC}"
fi

# Verificar directorio de backups
BACKUP_DIR="$APP_DIR/backups"
if [ -d "\$BACKUP_DIR" ]; then
    COUNT=\$(ls -1 "\$BACKUP_DIR" | grep -c "backup_")
    echo -e "${GREEN}Directorio de backups: \$BACKUP_DIR${NC}"
    echo -e "${GREEN}Número de backups disponibles: \$COUNT${NC}"
else
    echo -e "${RED}No se encontró el directorio de backups.${NC}"
fi
EOF

chmod +x "$STATUS_SCRIPT"

echo -e "${GREEN}Script de verificación creado en $STATUS_SCRIPT${NC}"
echo -e "${YELLOW}Puede ejecutar este script para verificar el estado del servicio.${NC}"

# Crear script para desinstalar el servicio
UNINSTALL_SCRIPT="$APP_DIR/uninstall_backup_service.sh"

cat > "$UNINSTALL_SCRIPT" << EOF
#!/bin/bash
# Script para desinstalar el servicio de backups automáticos

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Desinstalando servicio de backups automáticos...${NC}"

# Eliminar entrada de crontab
(crontab -l 2>/dev/null || echo "") | grep -v "$SCRIPT_PATH" | crontab -

echo -e "${GREEN}Servicio de backups desinstalado correctamente.${NC}"
EOF

chmod +x "$UNINSTALL_SCRIPT"

echo -e "${GREEN}Script de desinstalación creado en $UNINSTALL_SCRIPT${NC}"
echo -e "${YELLOW}Puede ejecutar este script para desinstalar el servicio.${NC}"

# Ejecutar una vez para comprobar
echo -e "${YELLOW}Ejecutando backup manual para comprobar funcionamiento...${NC}"
python "$SCRIPT_PATH" --force

echo -e "${GREEN}¡Configuración completada!${NC}"
echo -e "${YELLOW}El servicio de backups está configurado y funcionando.${NC}"