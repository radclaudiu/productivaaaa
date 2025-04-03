"""
Servicio automatizado para cerrar fichajes pendientes en puntos de fichaje
fuera de horario de operación.

Este script realiza un barrido cada 10 minutos para verificar todos los puntos
de fichaje y cerrar aquellos registros pendientes cuando se encuentran fuera
del horario de operación configurado.

Uso:
    python scheduled_checkpoints_closer.py
"""
import time
import sys
import logging
import os
from datetime import datetime, timedelta

from app import create_app
from close_operation_hours import auto_close_pending_records

# Configurar logging
log_directory = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(log_directory, 'checkpoints_closer.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_path)
    ]
)
logger = logging.getLogger(__name__)

# Intervalo de verificación en segundos (10 minutos)
CHECK_INTERVAL = 600  # 10 * 60

def verificar_sistema():
    """
    Verifica que el sistema está correctamente configurado y puede acceder a la base de datos.
    Retorna True si todo está correcto, False si hay algún problema.
    """
    try:
        # Creamos una app temporal para verificar la conexión a la BD
        test_app = create_app()
        with test_app.app_context():
            # Comprobar que podemos acceder a los checkpoints (prueba de acceso a BD)
            from models_checkpoints import CheckPoint
            count = CheckPoint.query.count()
            logger.info(f"✓ Verificación de sistema: Conexión a BD correcta - {count} checkpoints encontrados")
            
            # Comprobar que podemos acceder a la zona horaria
            from timezone_config import get_current_time, TIMEZONE
            current_time = get_current_time()
            logger.info(f"✓ Verificación de sistema: Zona horaria configurada correctamente - {TIMEZONE} - Hora actual: {current_time}")
            
            return True
    except Exception as e:
        logger.error(f"✗ Error en verificación del sistema: {e}", exc_info=True)
        return False

def run_service():
    """
    Ejecuta el servicio de verificación periódica para el cierre de fichajes
    pendientes en puntos de fichaje fuera de horario.
    """
    start_time = datetime.now()
    logger.info("="*80)
    logger.info(f"INICIO SERVICIO DE CIERRE AUTOMÁTICO - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Versión: 1.2.0 - Barrido con logs detallados y detección de redeploy")
    logger.info(f"Intervalo configurado: {CHECK_INTERVAL} segundos ({CHECK_INTERVAL/60:.1f} minutos)")
    logger.info("-"*80)
    
    # Eliminamos el archivo de startup para forzar la detección del primer inicio después de redeploy
    startup_file = '.checkpoint_closer_startup'
    if os.path.exists(startup_file):
        try:
            os.remove(startup_file)
            logger.info(f"✓ Archivo de startup eliminado para forzar la detección de redeploy")
        except Exception as e:
            logger.warning(f"No se pudo eliminar el archivo de startup: {e}")
    else:
        logger.info("Primer inicio del servicio (no existe archivo de startup)")
    
    # Verificar que el sistema funciona correctamente
    if not verificar_sistema():
        logger.critical("No se pudo iniciar el servicio debido a errores en la verificación del sistema")
        return False
        
    logger.info("✓ Sistema verificado correctamente - Iniciando servicio de barrido")
    
    app = create_app()
    
    try:
        # Bucle infinito para ejecución continua
        barrido_count = 0
        while True:
            start_time = time.time()
            barrido_count += 1
            logger.info(f"======= INICIO BARRIDO #{barrido_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =======")
            
            with app.app_context():
                try:
                    # Ejecutar la verificación de puntos de fichaje
                    success = auto_close_pending_records()
                    if success:
                        logger.info("Barrido completado correctamente")
                    else:
                        logger.error("El barrido finalizó con errores")
                except Exception as e:
                    logger.error(f"Error durante el barrido: {e}", exc_info=True)
            
            # Calcular tiempo de espera hasta la próxima ejecución
            execution_time = time.time() - start_time
            logger.info(f"Tiempo de ejecución del barrido: {execution_time:.2f} segundos")
            
            # Si la ejecución tomó menos que el intervalo, esperar el tiempo restante
            wait_time = max(1, CHECK_INTERVAL - execution_time)
            next_time = datetime.now() + timedelta(seconds=wait_time)
            logger.info(f"Esperando {wait_time:.2f} segundos hasta el próximo barrido...")
            logger.info(f"Próximo barrido programado para: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"======= FIN BARRIDO #{barrido_count} =======\n")
            
            time.sleep(wait_time)
    
    except KeyboardInterrupt:
        logger.info("Servicio detenido manualmente")
    except Exception as e:
        logger.critical(f"Error fatal en el servicio: {e}", exc_info=True)
        return False
    
    return True

if __name__ == "__main__":
    success = run_service()
    sys.exit(0 if success else 1)