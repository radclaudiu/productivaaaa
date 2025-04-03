"""
Script para ejecutar manualmente una única verificación de puntos de fichaje
y cerrar aquellos registros pendientes que están fuera de horario.

Esto es útil para pruebas o ejecuciones manuales.

Uso:
    python run_checkpoint_closer.py
"""
import sys
import os
import logging
from datetime import datetime

from app import create_app
from close_operation_hours import auto_close_pending_records, STARTUP_FILE

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

def verificar_acceso_bd():
    """
    Verifica que podemos acceder a la base de datos y que las tablas necesarias están configuradas.
    """
    try:
        test_app = create_app()
        with test_app.app_context():
            from models_checkpoints import CheckPoint, CheckPointRecord, CheckPointStatus
            
            checkpoints_count = CheckPoint.query.count()
            
            # Comprobar si hay checkpoints activos
            active_checkpoints = CheckPoint.query.filter_by(status=CheckPointStatus.ACTIVE).count()
            
            # Comprobar si hay registros pendientes
            from sqlalchemy import func
            pending_records = CheckPointRecord.query.filter(
                CheckPointRecord.check_out_time.is_(None)
            ).count()
            
            # Comprobar la configuración de zona horaria
            from timezone_config import get_current_time, TIMEZONE
            current_time = get_current_time()
            
            # Loggear los resultados de la verificación
            logger.info(f"✓ Verificación de Base de Datos completada:")
            logger.info(f"  - Total de puntos de fichaje: {checkpoints_count}")
            logger.info(f"  - Puntos de fichaje activos: {active_checkpoints}")
            logger.info(f"  - Registros pendientes: {pending_records}")
            logger.info(f"  - Zona horaria configurada: {TIMEZONE}")
            logger.info(f"  - Hora actual (Madrid): {current_time}")
            
            return True
    except Exception as e:
        logger.error(f"✗ Error en verificación de acceso a base de datos: {e}", exc_info=True)
        return False

def run_once():
    """
    Ejecuta una verificación única de puntos de fichaje fuera de horario
    y cierra los registros pendientes.
    """
    start_time = datetime.now()
    logger.info("="*80)
    logger.info(f"INICIANDO VERIFICACIÓN MANUAL DE CIERRE AUTOMÁTICO - {start_time}")
    logger.info(f"Versión: 1.2.0 - Verificación con logs detallados y detección de redeploy")
    logger.info("-"*80)
    
    # Eliminar el archivo de startup para forzar la detección de redeploy
    if os.path.exists(STARTUP_FILE):
        try:
            os.remove(STARTUP_FILE)
            logger.info(f"✓ Archivo de startup eliminado para forzar la detección de redeploy")
        except Exception as e:
            logger.warning(f"No se pudo eliminar el archivo de startup: {e}")
    else:
        logger.info("No existe archivo de startup previo (primera ejecución)")
    
    # Comprobar que podemos acceder a la BD
    if not verificar_acceso_bd():
        logger.error("No se pudo realizar la verificación debido a errores de acceso a la BD")
        return False
        
    logger.info(f"Ejecutando verificación manual de puntos de fichaje: {datetime.now()}")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Ejecutar la verificación de puntos de fichaje
            success = auto_close_pending_records()
            if success:
                logger.info("Verificación completada correctamente")
            else:
                logger.error("La verificación finalizó con errores")
                return False
        except Exception as e:
            logger.error(f"Error durante la verificación: {e}", exc_info=True)
            return False
    
    return True

if __name__ == "__main__":
    success = run_once()
    sys.exit(0 if success else 1)