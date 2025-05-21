"""
Script para iniciar la aplicación web con todos los servicios necesarios.
"""

import sys
import os
import logging
import signal
import time
import threading
import subprocess

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                   format='[%(asctime)s] [%(levelname)s] %(message)s',
                   datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def run_flask_app():
    """Ejecuta la aplicación Flask en modo desarrollo."""
    try:
        # Importar y ejecutar la aplicación Flask
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación Flask: {e}")
        sys.exit(1)

def run_db_check():
    """Verifica que la base de datos esté disponible."""
    try:
        from main import test_db_connection
        test_db_connection()
        return True
    except Exception as e:
        logger.error(f"Error de conexión a la base de datos: {e}")
        return False

def main():
    """Función principal que inicia todos los servicios."""
    logger.info("Iniciando sistema de gestión de personal...")
    
    # Verificar conexión a la base de datos
    db_ok = run_db_check()
    if not db_ok:
        logger.error("No se pudo conectar a la base de datos. Verifique la configuración.")
        sys.exit(1)
    
    # Iniciar servicios
    logger.info("Iniciando el servidor web...")
    
    # Crear y ejecutar thread para la aplicación Flask
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    
    logger.info("Sistema iniciado correctamente.")
    logger.info("Acceda a la aplicación en: http://localhost:5000")
    
    try:
        # Mantener el proceso principal vivo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Cerrando servicios...")
        sys.exit(0)

if __name__ == "__main__":
    main()