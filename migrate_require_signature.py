"""
Script para añadir columna require_signature a la tabla checkpoints
"""
import logging
from sqlalchemy import text
from app import db, create_app

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def add_require_signature_column():
    """Añade la columna require_signature a la tabla checkpoints si no existe."""
    try:
        # Verificar si la columna ya existe
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'checkpoints' AND column_name = 'require_signature'
            """))
            if result.fetchone() is not None:
                logger.info("La columna 'require_signature' ya existe en la tabla 'checkpoints'.")
                return
            
            # Añadir la columna con valor por defecto TRUE
            conn.execute(text("""
                ALTER TABLE checkpoints 
                ADD COLUMN require_signature BOOLEAN NOT NULL DEFAULT TRUE
            """))
            conn.commit()
            logger.info("Columna 'require_signature' añadida correctamente a la tabla 'checkpoints'.")
    except Exception as e:
        logger.error(f"Error al añadir la columna 'require_signature': {e}")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        logger.info("Iniciando migración para añadir columna 'require_signature'...")
        add_require_signature_column()
        logger.info("Migración completada.")