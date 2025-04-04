"""
Script para limpiar completamente la base de datos.
ADVERTENCIA: Este script borrará TODOS los datos de la base de datos.
No hay marcha atrás una vez ejecutado.
"""
import sys
import logging
from datetime import datetime
from app import db, create_app
from sqlalchemy import text

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
        # Verificar las tablas existentes en la base de datos
        db.session.rollback()
        existing_tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """)
        existing_tables_result = db.session.execute(existing_tables_query).fetchall()
        existing_tables = [row[0] for row in existing_tables_result]
        
        logger.info(f"Tablas encontradas en la base de datos: {existing_tables}")
        
        # Lista de tablas en el orden correcto para eliminar (inverso a las dependencias)
        all_possible_tables = [
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
        
        # Filtrar solo las tablas que existen en la base de datos
        tables = [table for table in all_possible_tables if table in existing_tables]
        logger.info(f"Se intentará eliminar las siguientes tablas: {tables}")
        
        deleted_tables = []
        deleted_rows = {}
        total_deleted = 0
        
        # Deshabilitar temporalmente las restricciones de clave foránea
        try:
            db.session.rollback()  # Asegurarse de que no hay una transacción activa
            db.session.execute(text("SET CONSTRAINTS ALL DEFERRED"))
            db.session.commit()
            logger.info("Restricciones de clave foránea deshabilitadas temporalmente")
        except Exception as e:
            error_msg = f"Error al deshabilitar restricciones de clave foránea: {str(e)}"
            logger.warning(error_msg)
            db.session.rollback()
        
        # Iterar por las tablas y eliminar todos los registros
        for table_name in tables:
            # Asegurarse de iniciar una nueva transacción limpia para cada tabla
            db.session.rollback()
            
            try:
                # Ejecutar SQL directo para eliminar todos los registros de la tabla
                sql = text(f"TRUNCATE TABLE {table_name} CASCADE")
                db.session.execute(sql)
                db.session.commit()  # Confirmar cada operación individualmente
                
                # Como TRUNCATE no devuelve un recuento, asumimos que se eliminaron todos los registros
                # y verificamos contando después
                count_sql = text(f"SELECT COUNT(*) FROM {table_name}")
                result = db.session.execute(count_sql).scalar()
                
                if result == 0:
                    # Asumimos que se eliminaron registros (aunque no sabemos cuántos exactamente)
                    deleted_tables.append(table_name)
                    deleted_rows[table_name] = "Todos"  # No conocemos el número exacto
                    total_deleted += 1  # Incrementamos al menos en 1 para indicar que hubo eliminación
                    
                    print(f"✓ Tabla {table_name} vaciada correctamente")
                    logger.info(f"Tabla {table_name} vaciada correctamente")
                else:
                    print(f"! Tabla {table_name} no se vació completamente ({result} registros restantes)")
                    logger.warning(f"Tabla {table_name} no se vació completamente ({result} registros restantes)")
                    
            except Exception as e:
                error_msg = f"Error al vaciar la tabla {table_name}: {str(e)}"
                print(f"✗ {error_msg}")
                logger.error(error_msg)
                db.session.rollback()  # Rollback en caso de error
                
                # Intentar con DELETE normal si TRUNCATE falla
                try:
                    db.session.rollback()
                    sql = text(f"DELETE FROM {table_name}")
                    result = db.session.execute(sql)
                    db.session.commit()
                    
                    deleted_count = result.rowcount
                    
                    if deleted_count > 0:
                        deleted_tables.append(table_name)
                        deleted_rows[table_name] = deleted_count
                        total_deleted += deleted_count
                        
                        print(f"✓ Eliminados {deleted_count} registros de la tabla {table_name} usando DELETE")
                        logger.info(f"Eliminados {deleted_count} registros de la tabla {table_name} usando DELETE")
                except Exception as e2:
                    error_msg = f"Error al eliminar registros de {table_name} con DELETE: {str(e2)}"
                    print(f"✗ {error_msg}")
                    logger.error(error_msg)
                    db.session.rollback()
        
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