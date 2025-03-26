"""
Script para migrar la base de datos y añadir el valor 'refrigerado_abierto' al enum ConservationType
"""
import os
import sys
from sqlalchemy import create_engine, text
from flask import Flask

def add_refrigerado_abierto_to_enum():
    """Agrega el valor 'refrigerado_abierto' al tipo enum conservationtype en la base de datos"""
    # Obtener conexión a la base de datos
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("Error: La variable de entorno DATABASE_URL no está configurada")
        sys.exit(1)
    
    try:
        # Crear conexión
        engine = create_engine(database_url)
        
        # Crear una conexión
        with engine.connect() as conn:
            # Iniciar una transacción
            with conn.begin():
                # Verificar si el valor ya existe en el enum
                result = conn.execute(text("""
                    SELECT e.enumlabel
                    FROM pg_type t
                    JOIN pg_enum e ON t.oid = e.enumtypid
                    WHERE t.typname = 'conservationtype'
                """))
                
                enum_values = [row[0] for row in result]
                print(f"Valores actuales del enum: {enum_values}")
                
                if 'refrigerado_abierto' in enum_values:
                    print("El valor 'refrigerado_abierto' ya existe en el enum. No es necesario realizar cambios.")
                    return
                
                # Modificar el tipo enum para añadir el nuevo valor
                # Nota: los valores reales están en mayúsculas en la BD
                conn.execute(text("""
                    ALTER TYPE conservationtype ADD VALUE 'REFRIGERADO_ABIERTO' AFTER 'REFRIGERACION';
                """))
                
                print("Valor 'refrigerado_abierto' añadido al enum conservationtype.")
        
        # Verificar después de la modificación
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT e.enumlabel
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE t.typname = 'conservationtype'
                ORDER BY e.enumsortorder
            """))
            
            enum_values_after = [row[0] for row in result]
            print(f"Valores actualizados del enum: {enum_values_after}")
    
    except Exception as e:
        print(f"Error al modificar el enum: {str(e)}")
        sys.exit(1)
    
    print("Migración completada correctamente.")

if __name__ == "__main__":
    add_refrigerado_abierto_to_enum()