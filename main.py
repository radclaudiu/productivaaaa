import logging
import os
from urllib.parse import urlparse
import psycopg2

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='[%(asctime)s] [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def test_db_connection():
    """Prueba la conexión a la base de datos y muestra información sobre ella."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        logger.error("No se encontró la variable de entorno DATABASE_URL")
        return
    
    try:
        # Parsear la URL para extraer los componentes
        parsed = urlparse(db_url)
        dbname = parsed.path[1:]  # eliminar la barra inicial
        user = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port
        
        # Conectar con SSL
        port = port or 5432  # Usar puerto 5432 si no está especificado
        conn_string = f"dbname={dbname} user={user} password={password} host={host} port={port} sslmode=require"
        logger.info(f"Intentando conectar a: dbname={dbname} user={user} host={host} port={port}")
        
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        
        # Probar la conexión
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.info(f"Conexión exitosa! Versión de PostgreSQL: {version[0]}")
        
        # Cerrar recursos
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error de conexión: {e}")

# Probar la conexión antes de importar la app
test_db_connection()

from app import app

# Iniciar servicio de cierre automático de fichajes cuando se inicia la aplicación
try:
    logger.info("Iniciando servicio de cierre automático de fichajes...")
    from checkpoint_closer_service import start_checkpoint_closer_service
    
    # Iniciar el servicio
    success = start_checkpoint_closer_service()
    if success:
        logger.info("✓ Servicio de cierre automático iniciado correctamente")
    else:
        logger.warning("⚠ No se pudo iniciar el servicio de cierre automático")
except Exception as e:
    logger.error(f"❌ Error al iniciar el servicio de cierre automático: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)