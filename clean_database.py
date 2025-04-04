"""
Script para limpiar completamente la base de datos.
ADVERTENCIA: Este script borrará TODOS los datos de la base de datos.
No hay marcha atrás una vez ejecutado.
"""
import sys
import logging
from datetime import datetime
from app import db, create_app

# Configurar logging
logging.basicConfig(
    filename='database_cleaning.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('database_cleaning')

def clean_database(confirm=False):
    """
    Elimina TODOS los datos de la base de datos.
    
    Args:
        confirm: Booleano que debe ser True para confirmar la operación.
        
    Returns:
        dict: Diccionario con el resultado de la operación.
    """
    if not confirm:
        return {
            "success": False,
            "message": "La operación no fue confirmada. Se requiere confirmación explícita."
        }
    
    timestamp = datetime.now()
    
    # Registrar el inicio de la operación
    start_message = f"INICIANDO LIMPIEZA COMPLETA DE BASE DE DATOS - {timestamp}"
    logger.warning(start_message)
    print(f"\n{'!' * 100}")
    print(f"! {start_message}")
    print(f"{'!' * 100}\n")
    
    try:
        # Lista de tablas en el orden correcto para eliminar (inverso a las dependencias)
        tables = [
            # Primero tablas con más dependencias
            "checkpoint_incidents",
            "checkpoint_original_records",
            "checkpoint_records",
            "task_instances_assigned_users",
            "task_instances_labels",
            "task_instances",
            "task_label_templates",
            "task_labels",
            "task_item_updates",
            "task_items",
            "task_updates",
            "tasks",
            "employee_contract_hours",
            "checkpoints",
            "employees",
            "companies",
            "permissions",
            "roles_permissions",
            "users_roles",
            "roles",
            "users"
        ]
        
        deleted_tables = []
        deleted_rows = {}
        total_deleted = 0
        
        # Usar una transacción para garantizar atomicidad
        with db.session.begin():
            # Iterar por las tablas y eliminar todos los registros
            for table_name in tables:
                try:
                    # Ejecutar SQL directo para eliminar todos los registros de la tabla
                    result = db.session.execute(f"DELETE FROM {table_name}")
                    deleted_count = result.rowcount
                    
                    if deleted_count > 0:
                        deleted_tables.append(table_name)
                        deleted_rows[table_name] = deleted_count
                        total_deleted += deleted_count
                        
                    print(f"✓ Eliminados {deleted_count} registros de la tabla {table_name}")
                    logger.info(f"Eliminados {deleted_count} registros de la tabla {table_name}")
                except Exception as e:
                    error_msg = f"Error al eliminar registros de {table_name}: {str(e)}"
                    print(f"✗ {error_msg}")
                    logger.error(error_msg)
        
        # Crear resumen de la operación
        end_timestamp = datetime.now()
        duration = (end_timestamp - timestamp).total_seconds()
        
        summary = {
            "success": True,
            "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "duration_seconds": duration,
            "tables_affected": len(deleted_tables),
            "total_records_deleted": total_deleted,
            "details": deleted_rows
        }
        
        # Registrar el resultado
        logger.warning(f"BASE DE DATOS LIMPIADA COMPLETAMENTE - {total_deleted} registros eliminados en {duration:.2f} segundos")
        print(f"\n{'!' * 100}")
        print(f"! BASE DE DATOS LIMPIADA COMPLETAMENTE")
        print(f"! {total_deleted} registros eliminados en {duration:.2f} segundos")
        print(f"{'!' * 100}\n")
        
        return summary
        
    except Exception as e:
        error_msg = f"ERROR CRÍTICO durante la limpieza de la base de datos: {str(e)}"
        logger.critical(error_msg)
        print(f"\n{'!' * 100}")
        print(f"! {error_msg}")
        print(f"{'!' * 100}\n")
        
        return {
            "success": False,
            "message": f"Error durante la limpieza: {str(e)}"
        }

if __name__ == "__main__":
    # Verificar si se ha pasado el parámetro de confirmación
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'confirm':
        app = create_app()
        with app.app_context():
            result = clean_database(confirm=True)
            print(result)
    else:
        print("ADVERTENCIA: Este script eliminará TODOS los datos de la base de datos.")
        print("Para ejecutar, debe pasar el parámetro 'confirm':")
        print("python clean_database.py confirm")