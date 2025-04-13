"""
Script para migrar las tablas necesarias para el módulo de horarios.
Este script creará las tablas 'schedule' y 'schedule_assignment' en la base de datos.
"""

import logging
import os
from urllib.parse import urlparse
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='[%(asctime)s] [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Obtiene una conexión a la base de datos usando los parámetros de conexión de environment."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        logger.error("No se encontró la variable de entorno DATABASE_URL")
        return None
    
    try:
        # Parsear la URL para extraer los componentes
        parsed = urlparse(db_url)
        dbname = parsed.path[1:]  # eliminar la barra inicial
        user = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 5432  # Usar puerto 5432 si no está especificado
        
        # Conectar con SSL
        conn_string = f"dbname={dbname} user={user} password={password} host={host} port={port} sslmode=require"
        logger.info(f"Conectando a: dbname={dbname} user={user} host={host} port={port}")
        
        conn = psycopg2.connect(conn_string)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        logger.info("Conexión exitosa a la base de datos")
        return conn
    
    except Exception as e:
        logger.error(f"Error de conexión: {e}")
        return None

def check_if_tables_exist(conn):
    """Verifica si las tablas ya existen en la base de datos."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'schedule'
            )
        """)
        schedule_exists = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'schedule_assignment'
            )
        """)
        assignment_exists = cursor.fetchone()[0]
        
        cursor.close()
        
        return schedule_exists, assignment_exists
    
    except Exception as e:
        logger.error(f"Error al verificar tablas: {e}")
        return False, False

def create_schedules_tables(conn):
    """Crea las tablas necesarias para el módulo de horarios."""
    try:
        cursor = conn.cursor()
        
        # Crear tabla schedule
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                id SERIAL PRIMARY KEY,
                name VARCHAR(128) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                published BOOLEAN DEFAULT FALSE,
                company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Crear tabla schedule_assignment
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedule_assignment (
                id SERIAL PRIMARY KEY,
                schedule_id INTEGER NOT NULL REFERENCES schedule(id) ON DELETE CASCADE,
                employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
                day DATE NOT NULL,
                start_time VARCHAR(5) NOT NULL,
                end_time VARCHAR(5) NOT NULL,
                break_duration INTEGER DEFAULT 0,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Crear índices para mejorar el rendimiento
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_schedule_company ON schedule(company_id);
            CREATE INDEX IF NOT EXISTS idx_assignment_schedule ON schedule_assignment(schedule_id);
            CREATE INDEX IF NOT EXISTS idx_assignment_employee ON schedule_assignment(employee_id);
            CREATE INDEX IF NOT EXISTS idx_assignment_day ON schedule_assignment(day);
        """)
        
        cursor.close()
        logger.info("Tablas creadas correctamente")
        return True
    
    except Exception as e:
        logger.error(f"Error al crear tablas: {e}")
        return False

def main():
    # Obtener conexión a la base de datos
    conn = get_db_connection()
    if not conn:
        logger.error("No se pudo conectar a la base de datos")
        return
    
    try:
        # Verificar si las tablas ya existen
        schedule_exists, assignment_exists = check_if_tables_exist(conn)
        
        if schedule_exists and assignment_exists:
            logger.info("Las tablas de horarios ya existen")
        else:
            # Crear las tablas
            if create_schedules_tables(conn):
                logger.info("✓ Migración completada correctamente")
            else:
                logger.error("❌ Error al realizar la migración")
    
    finally:
        # Cerrar la conexión
        if conn:
            conn.close()
            logger.info("Conexión a la base de datos cerrada")

if __name__ == "__main__":
    main()