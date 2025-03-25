"""
Script para añadir el valor 'refrigerado_abierto' al enum ConservationType en PostgreSQL
"""
import os
import sys

from flask import Flask
from sqlalchemy import text

# Añadir el directorio actual al path para poder importar los modelos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import db, create_app

def update_conservation_type_enum():
    """
    Actualiza el tipo ENUM conservationtype en PostgreSQL agregando el valor 'refrigerado_abierto'
    """
    # Conexión directa para ejecutar SQL en bruto
    with db.engine.connect() as conn:
        # Comenzar transacción
        trans = conn.begin()
        try:
            # Verificar si el valor ya existe en la enumeración para evitar errores
            result = conn.execute(text(
                "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'conservationtype' AND "
                "typelem <> 0 AND EXISTS (SELECT 1 FROM pg_enum WHERE pg_enum.enumtypid = pg_type.oid "
                "AND pg_enum.enumlabel = 'refrigerado_abierto'))"
            )).scalar()
            
            if result:
                print("El valor 'refrigerado_abierto' ya existe en el enum.")
                trans.commit()
                return
            
            # Paso 1: Crear un tipo de enumeración temporal con todos los valores (incluyendo el nuevo)
            conn.execute(text(
                "CREATE TYPE conservationtype_new AS ENUM ("
                "'descongelacion', 'refrigeracion', 'refrigerado_abierto', 'gastro', 'caliente', 'seco')"
            ))
            
            # Paso 2: Crear una función para convertir el tipo antiguo al nuevo
            conn.execute(text("""
                CREATE OR REPLACE FUNCTION update_conservationtype(conservationtype)
                RETURNS conservationtype_new AS $$
                    SELECT CASE
                        WHEN $1::text = 'descongelacion' THEN 'descongelacion'::conservationtype_new
                        WHEN $1::text = 'refrigeracion' THEN 'refrigeracion'::conservationtype_new
                        WHEN $1::text = 'gastro' THEN 'gastro'::conservationtype_new
                        WHEN $1::text = 'caliente' THEN 'caliente'::conservationtype_new
                        WHEN $1::text = 'seco' THEN 'seco'::conservationtype_new
                        ELSE 'descongelacion'::conservationtype_new -- valor por defecto para manejar nulos
                    END;
                $$ LANGUAGE SQL;
            """))
            
            # Paso 3: Actualizar la columna en la tabla producto_conservations
            conn.execute(text("""
                ALTER TABLE product_conservations 
                ALTER COLUMN conservation_type TYPE conservationtype_new 
                USING update_conservationtype(conservation_type);
            """))
            
            # Paso 4: Actualizar la columna en la tabla product_labels
            conn.execute(text("""
                ALTER TABLE product_labels 
                ALTER COLUMN conservation_type TYPE conservationtype_new 
                USING update_conservationtype(conservation_type);
            """))
            
            # Paso 5: Eliminar la función temporal
            conn.execute(text("DROP FUNCTION update_conservationtype(conservationtype);"))
            
            # Paso 6: Eliminar el tipo antiguo
            conn.execute(text("DROP TYPE conservationtype;"))
            
            # Paso 7: Renombrar el nuevo tipo al nombre original
            conn.execute(text("ALTER TYPE conservationtype_new RENAME TO conservationtype;"))
            
            # Confirmar transacción
            trans.commit()
            print("¡Migración completada con éxito!")
            
        except Exception as e:
            # Revertir en caso de error
            trans.rollback()
            print(f"Error en la migración: {str(e)}")
            raise

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        update_conservation_type_enum()