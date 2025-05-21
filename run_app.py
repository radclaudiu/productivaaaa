"""
Script para ejecutar la aplicación principal de forma optimizada en Replit.
Este archivo configura el entorno y luego lanza el servidor.
"""

import os
import sys
import logging
import subprocess

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def run_app():
    """
    Ejecuta la aplicación Flask en el puerto 5000 y expone el servicio.
    """
    try:
        # Verificar la conexión a la base de datos primero
        logger.info("Verificando conexión a la base de datos...")
        from main import test_db_connection
        test_db_connection()
        
        # Ejecutar la aplicación
        logger.info("Iniciando la aplicación en el puerto 5000...")
        from app import app
        
        # Configurar la aplicación para que sea accesible desde el exterior
        app.run(host="0.0.0.0", port=5000, debug=True)
        
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_app()