"""
Script para ejecutar el servicio de cierre automático de fichajes.

Este script inicia el servicio de cierre automático de fichajes y
lo mantiene en ejecución hasta que el proceso es terminado.

Uso:
  python run_checkpoint_closer.py
"""
from app import create_app
from checkpoint_closer_service import start_checkpoint_closer_service, get_service_status
import time
import logging
import signal
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("checkpoints_closer.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Variable para controlar la ejecución
running = True

def signal_handler(sig, frame):
    """Manejador de señales para terminar el proceso correctamente."""
    global running
    logger.info(f"Recibida señal de terminación ({sig}). Deteniendo servicio...")
    running = False
    sys.exit(0)

def main():
    """Función principal que inicia y mantiene el servicio en ejecución."""
    app = create_app()
    
    # Registrar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Iniciando servicio de cierre automático de fichajes...")
    
    with app.app_context():
        # Iniciar el servicio
        success = start_checkpoint_closer_service()
        
        if not success:
            logger.error("Error al iniciar el servicio. Abortando.")
            return
        
        # Obtener y mostrar el estado inicial
        status = get_service_status()
        logger.info(f"Servicio iniciado. Estado: {status}")
        
        # Mantener el proceso en ejecución
        try:
            logger.info("Servicio en ejecución. Presiona Ctrl+C para detener.")
            
            while running:
                # Cada 5 minutos mostrar el estado actual
                for _ in range(5):
                    if running:
                        time.sleep(60)  # Dormir 1 minuto entre verificaciones
                
                status = get_service_status()
                logger.info(f"Estado actual del servicio: {status}")
        
        except KeyboardInterrupt:
            logger.info("Interrupción de teclado detectada. Deteniendo servicio...")
        
        finally:
            logger.info("Servicio finalizado.")

if __name__ == "__main__":
    main()