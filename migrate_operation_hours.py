"""
Migración para agregar los campos de configuración de horario de funcionamiento a los puntos de fichaje
"""
import sys
from sqlalchemy import Column, Time, Boolean, text
from flask import Flask

from app import db, create_app

def migrate():
    """
    Agrega los campos necesarios para la configuración de horario de funcionamiento:
    - operation_start_time: Hora de inicio de funcionamiento
    - operation_end_time: Hora de fin de funcionamiento
    - enforce_operation_hours: Si se debe aplicar el horario de funcionamiento
    """
    print("Iniciando migración para agregar campos de configuración de horario de funcionamiento...")
    
    try:
        with app.app_context():
            # Verificar si ya se ha ejecutado esta migración
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('checkpoints')]
            
            # Si la columna ya existe, la migración ya se realizó
            if 'operation_start_time' in columns:
                print("La migración ya ha sido ejecutada anteriormente. No se realizaron cambios.")
                return
            
            # Agregar las nuevas columnas
            print("Agregando nuevas columnas...")
            
            # Agregar columna operation_start_time
            db.session.execute(text("""
                ALTER TABLE checkpoints 
                ADD COLUMN operation_start_time TIME NULL
            """))
            
            # Agregar columna operation_end_time
            db.session.execute(text("""
                ALTER TABLE checkpoints 
                ADD COLUMN operation_end_time TIME NULL
            """))
            
            # Agregar columna enforce_operation_hours
            db.session.execute(text("""
                ALTER TABLE checkpoints 
                ADD COLUMN enforce_operation_hours BOOLEAN NOT NULL DEFAULT false
            """))
            
            print("Migración completada con éxito!")
    
    except Exception as e:
        print(f"Error durante la migración: {e}")
        return False
    
    return True


if __name__ == "__main__":
    app = create_app()
    success = migrate()
    sys.exit(0 if success else 1)