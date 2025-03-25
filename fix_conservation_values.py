"""
Script para corregir los valores del enum ConservationType en la base de datos.
Este script realiza una migración más agresiva eliminando y recreando el enum.
"""
from app import create_app
from sqlalchemy import text

def fix_conservation_values():
    """
    Realiza una migración más agresiva para corregir los valores de ConservationType.
    """
    app = create_app()
    with app.app_context():
        from app import db
        
        try:
            conn = db.engine.connect()
            trans = conn.begin()
            
            # Crear un nuevo tipo para la migración
            print("Creando nuevo tipo enum...")
            conn.execute(text("""
                CREATE TYPE conservationtype_fixed AS ENUM (
                    'DESCONGELACION', 'REFRIGERACION', 'REFRIGERADO_ABIERTO', 'GASTRO', 'CALIENTE', 'SECO'
                );
            """))
            
            # Función de conversión
            print("Creando función de conversión...")
            conn.execute(text("""
                CREATE OR REPLACE FUNCTION update_conservationtype_case(conservationtype)
                RETURNS conservationtype_fixed AS $$
                    SELECT CASE
                        WHEN $1::text = 'descongelacion' THEN 'DESCONGELACION'::conservationtype_fixed
                        WHEN $1::text = 'refrigeracion' THEN 'REFRIGERACION'::conservationtype_fixed
                        WHEN $1::text = 'refrigerado_abierto' THEN 'REFRIGERADO_ABIERTO'::conservationtype_fixed
                        WHEN $1::text = 'gastro' THEN 'GASTRO'::conservationtype_fixed
                        WHEN $1::text = 'caliente' THEN 'CALIENTE'::conservationtype_fixed
                        WHEN $1::text = 'seco' THEN 'SECO'::conservationtype_fixed
                        ELSE 'DESCONGELACION'::conservationtype_fixed
                    END;
                $$ LANGUAGE SQL;
            """))
            
            # Actualizar la columna conservation_type en product_conservations
            print("Actualizando columna product_conservations...")
            conn.execute(text("""
                ALTER TABLE product_conservations 
                ALTER COLUMN conservation_type TYPE conservationtype_fixed
                USING update_conservationtype_case(conservation_type);
            """))
            
            # Actualizar la columna conservation_type en product_labels
            print("Actualizando columna product_labels...")
            conn.execute(text("""
                ALTER TABLE product_labels 
                ALTER COLUMN conservation_type TYPE conservationtype_fixed
                USING update_conservationtype_case(conservation_type);
            """))
            
            # Eliminar la función de conversión
            print("Eliminando función de conversión...")
            conn.execute(text("""
                DROP FUNCTION update_conservationtype_case(conservationtype);
            """))
            
            # Eliminar el tipo original
            print("Eliminando tipo original...")
            conn.execute(text("""
                DROP TYPE conservationtype;
            """))
            
            # Renombrar el nuevo tipo
            print("Renombrando el nuevo tipo...")
            conn.execute(text("""
                ALTER TYPE conservationtype_fixed RENAME TO conservationtype;
            """))
            
            # Confirmar la transacción
            trans.commit()
            print("¡Actualización completada con éxito!")
            
        except Exception as e:
            # Revertir en caso de error
            if 'trans' in locals():
                trans.rollback()
            print(f"Error en la actualización: {str(e)}")
            raise

if __name__ == "__main__":
    fix_conservation_values()