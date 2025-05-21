"""
Script para inicializar la base de datos sin depender de la aplicación completa.
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtener URL de la base de datos
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    logger.error("La variable de entorno DATABASE_URL no está configurada")
    exit(1)

# Crear el motor de base de datos
engine = create_engine(DATABASE_URL)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    """Inicializa la base de datos creando todas las tablas."""
    
    # Importar todos los modelos para que SQLAlchemy los registre
    import models
    import models_tasks
    import models_checkpoints
    
    try:
        import models_horarios
        logger.info("Modelos de horarios importados correctamente")
    except ImportError:
        logger.warning("Modelos de horarios no disponibles")
        
    try:
        import models_turnos
        logger.info("Modelos de turnos importados correctamente")
    except ImportError:
        logger.warning("Modelos de turnos no disponibles")
    
    # Crear todas las tablas
    logger.info("Creando todas las tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas creadas correctamente")

if __name__ == '__main__':
    init_db()
    logger.info("Base de datos inicializada. Ahora puede ejecutar 'python main.py' para iniciar la aplicación.")