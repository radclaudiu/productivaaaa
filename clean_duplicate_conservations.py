"""
Script para limpiar tipos de conservación duplicados.
Para cada producto y tipo de conservación, se mantiene solo el registro más reciente.
"""
from app import create_app
from sqlalchemy import text

def clean_duplicate_conservations():
    """
    Elimina tipos de conservación duplicados para productos, manteniendo solo el registro más reciente.
    """
    app = create_app()
    with app.app_context():
        from app import db
        from models_tasks import Product, ProductConservation, ConservationType
        
        try:
            # Obtener todos los productos
            products = Product.query.all()
            print(f"Procesando {len(products)} productos...")
            
            total_duplicates_removed = 0
            
            for product in products:
                print(f"Procesando producto ID {product.id}: {product.name}")
                
                # Crear un diccionario para almacenar el registro más reciente para cada tipo
                latest_conservations = {}
                
                # Obtener todas las conservaciones para este producto
                conservations = ProductConservation.query.filter_by(product_id=product.id).all()
                
                if len(conservations) <= 1:
                    print(f"  - No hay duplicados para procesar.")
                    continue
                
                # Agrupar por tipo de conservación y guardar el más reciente
                for cons in conservations:
                    conservation_type = cons.conservation_type.value
                    
                    if conservation_type not in latest_conservations or \
                       cons.updated_at > latest_conservations[conservation_type].updated_at:
                        latest_conservations[conservation_type] = cons
                
                # Contar cuántos registros se eliminarán
                to_delete = len(conservations) - len(latest_conservations)
                if to_delete == 0:
                    print(f"  - No hay duplicados para procesar.")
                    continue
                
                print(f"  - Encontrados {len(conservations)} registros para {len(latest_conservations)} tipos")
                print(f"  - Se eliminarán {to_delete} duplicados")
                
                # Eliminar todos los registros que no son los más recientes
                for cons in conservations:
                    if cons != latest_conservations.get(cons.conservation_type.value):
                        print(f"    - Eliminando: ID {cons.id}, Tipo {cons.conservation_type.value}, Horas {cons.hours_valid}")
                        db.session.delete(cons)
                        total_duplicates_removed += 1
            
            # Guardar cambios
            db.session.commit()
            print(f"\n¡Limpieza completada! Se eliminaron {total_duplicates_removed} registros duplicados.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error durante la limpieza: {str(e)}")
            raise

if __name__ == "__main__":
    clean_duplicate_conservations()