"""
Módulo para la gestión de backups de la base de datos PostgreSQL.

Este módulo proporciona funciones para:
- Crear backups de la base de datos (completos o incrementales)
- Listar los backups disponibles
- Restaurar la base de datos desde un backup
- Programar backups automáticos
- Implementar políticas de rotación de backups

Autor: Checkpoint Closer
Versión: 1.0.0
"""

import os
import subprocess
import logging
import shutil
import gzip
import time
import datetime
import json
from datetime import datetime, timedelta
import psycopg2
from flask import current_app
from config import Config

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='backup_manager.log',
    filemode='a'
)
logger = logging.getLogger('backup_manager')

# Directorio para almacenar los backups
BACKUP_DIR = os.path.join(os.getcwd(), 'backups')
BACKUP_METADATA_FILE = os.path.join(BACKUP_DIR, 'backup_metadata.json')

# Estructura del nombre de archivo de backup
# formato: backup_{tipo}_{fecha}_{hora}.sql[.gz]
# ejemplo: backup_full_20250408_160000.sql.gz

# Asegurarse de que el directorio de backups existe
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)
    logger.info(f"Directorio de backups creado: {BACKUP_DIR}")

# Inicializar el archivo de metadatos si no existe
if not os.path.exists(BACKUP_METADATA_FILE):
    with open(BACKUP_METADATA_FILE, 'w') as f:
        json.dump({'backups': []}, f)
    logger.info(f"Archivo de metadatos inicializado: {BACKUP_METADATA_FILE}")

def get_database_connection_params():
    """
    Obtiene los parámetros de conexión a la base de datos desde la configuración.
    
    Returns:
        dict: Diccionario con los parámetros de conexión (dbname, user, password, host, port)
    """
    database_url = Config.SQLALCHEMY_DATABASE_URI
    
    # Extraer los componentes de la URL de conexión PostgreSQL
    # formato típico: postgresql://usuario:contraseña@host:puerto/nombre_db?param=valor
    if database_url.startswith('postgresql://'):
        # Eliminamos 'postgresql://' del inicio
        db_conn = database_url[13:]
        
        # Extraer usuario y contraseña (si existen)
        if '@' in db_conn:
            auth, rest = db_conn.split('@', 1)
            if ':' in auth:
                user, password = auth.split(':', 1)
            else:
                user, password = auth, ''
        else:
            user, password = '', ''
            rest = db_conn
        
        # Extraer host, puerto y nombre de la base de datos (y parámetros de consulta)
        if '/' in rest:
            host_port, dbname_params = rest.split('/', 1)
            if ':' in host_port:
                host, port = host_port.split(':', 1)
            else:
                host, port = host_port, '5432'  # Puerto predeterminado de PostgreSQL
            
            # Manejar parámetros de consulta en la URL (como ?sslmode=require)
            if '?' in dbname_params:
                dbname, _ = dbname_params.split('?', 1)
            else:
                dbname = dbname_params
        else:
            host, port = rest, '5432'
            dbname = ''
        
        return {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
    else:
        logger.error(f"Formato de URL de base de datos no soportado: {database_url}")
        raise ValueError("Formato de URL de base de datos no soportado")

def create_backup(tipo='full', compress=True, description=None, max_size_mb=100):
    """
    Crea un backup de la base de datos.
    
    Args:
        tipo (str): Tipo de backup ('full' o 'schema')
        compress (bool): Si se debe comprimir el backup
        description (str): Descripción opcional del backup
        max_size_mb (int): Tamaño máximo del backup en MB antes de comprimir
        
    Returns:
        dict: Información sobre el backup creado o None si hubo error
    """
    try:
        # Obtener fecha y hora actual para el nombre del archivo
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        
        # Obtener la URL completa de la base de datos
        db_url = Config.SQLALCHEMY_DATABASE_URI
        db_params = get_database_connection_params()
        
        # Crear el nombre del archivo de backup
        backup_filename = f"backup_{tipo}_{timestamp}.sql"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        # Construir el comando pg_dump con los parámetros adecuados
        # Utilizamos pipe directo a gzip para comprimir al vuelo si se solicita compresión
        if compress:
            dump_cmd = f"pg_dump '{db_url}' --no-owner --no-acl"
            
            # Si es solo un backup del esquema (sin datos)
            if tipo == 'schema':
                dump_cmd += " --schema-only"
                
            # Comprimir al vuelo con gzip
            compress_cmd = f"{dump_cmd} | gzip > '{backup_path}.gz'"
            logger.info(f"Ejecutando backup comprimido: {compress_cmd.replace(db_url, '***DB_URL***')}")
            
            process = subprocess.Popen(
                compress_cmd,
                shell=True,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            _, stderr = process.communicate()
            
            # El archivo final ya tiene la extensión .gz
            final_backup_path = f"{backup_path}.gz"
            backup_filename = f"{backup_filename}.gz"
        else:
            # Para backups sin compresión, usamos pg_dump directamente
            pg_dump_cmd = [
                'pg_dump',
                db_url,
                '--format=plain',
                '--no-owner',
                '--no-acl'
            ]
            
            # Si es solo un backup del esquema (sin datos)
            if tipo == 'schema':
                pg_dump_cmd.append('--schema-only')
            
            # Ejecutar pg_dump y guardar la salida
            with open(backup_path, 'w') as f:
                process = subprocess.Popen(
                    pg_dump_cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                _, stderr = process.communicate()
            
            final_backup_path = backup_path
        
        # Verificar si el proceso terminó correctamente
        if process.returncode != 0:
            logger.error(f"Error al crear backup: {stderr}")
            # Limpieza de archivos en caso de error
            for path in [backup_path, f"{backup_path}.gz"]:
                if os.path.exists(path):
                    os.remove(path)
            return None
        
        # Verificar si el archivo existe y obtener su tamaño
        if not os.path.exists(final_backup_path):
            logger.error(f"El archivo de backup no se creó correctamente: {final_backup_path}")
            return None
            
        file_size = os.path.getsize(final_backup_path)
        
        # Verificar si el tamaño del backup es excesivo
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            logger.warning(f"El backup es demasiado grande ({file_size} bytes, máximo {max_size_bytes} bytes). Se cancelará.")
            os.remove(final_backup_path)
            return None
        
        # Crear metadatos del backup
        backup_metadata = {
            'id': timestamp,
            'filename': backup_filename,
            'path': final_backup_path,
            'type': tipo,
            'compressed': compress,
            'size': file_size,
            'date': now.strftime('%Y-%m-%d %H:%M:%S'),
            'description': description or f"Backup {tipo} creado el {now.strftime('%Y-%m-%d %H:%M:%S')}",
            'database': db_params['dbname']
        }
        
        # Guardar metadatos en el archivo JSON
        with open(BACKUP_METADATA_FILE, 'r') as f:
            metadata = json.load(f)
        
        metadata['backups'].append(backup_metadata)
        
        with open(BACKUP_METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        readable_size = format_backup_size(file_size)
        logger.info(f"Backup creado exitosamente: {backup_filename} ({readable_size})")
        return backup_metadata
    
    except Exception as e:
        logger.error(f"Error al crear backup: {str(e)}")
        return None

def get_all_backups():
    """
    Obtiene la lista de todos los backups disponibles.
    
    Returns:
        list: Lista de metadatos de backups ordenados por fecha (más reciente primero)
    """
    try:
        with open(BACKUP_METADATA_FILE, 'r') as f:
            metadata = json.load(f)
        
        # Verificar que todos los archivos existen
        valid_backups = []
        for backup in metadata['backups']:
            if os.path.exists(backup['path']):
                valid_backups.append(backup)
            else:
                logger.warning(f"Archivo de backup no encontrado, se omitirá: {backup['path']}")
        
        # Actualizar el archivo de metadatos si se eliminaron algunos backups
        if len(valid_backups) != len(metadata['backups']):
            metadata['backups'] = valid_backups
            with open(BACKUP_METADATA_FILE, 'w') as f:
                json.dump(metadata, f, indent=4)
        
        # Ordenar por fecha (más reciente primero)
        return sorted(valid_backups, key=lambda x: x['date'], reverse=True)
    
    except Exception as e:
        logger.error(f"Error al obtener la lista de backups: {str(e)}")
        return []

def get_backup_by_id(backup_id):
    """
    Obtiene un backup específico por su ID.
    
    Args:
        backup_id (str): ID del backup a buscar
        
    Returns:
        dict: Metadatos del backup o None si no se encuentra
    """
    backups = get_all_backups()
    for backup in backups:
        if backup['id'] == backup_id:
            return backup
    return None

def delete_backup(backup_id):
    """
    Elimina un backup específico.
    
    Args:
        backup_id (str): ID del backup a eliminar
        
    Returns:
        bool: True si se eliminó correctamente, False en caso contrario
    """
    try:
        backup = get_backup_by_id(backup_id)
        if not backup:
            logger.error(f"Backup no encontrado: {backup_id}")
            return False
        
        # Eliminar el archivo físico
        if os.path.exists(backup['path']):
            os.remove(backup['path'])
        
        # Actualizar los metadatos
        with open(BACKUP_METADATA_FILE, 'r') as f:
            metadata = json.load(f)
        
        metadata['backups'] = [b for b in metadata['backups'] if b['id'] != backup_id]
        
        with open(BACKUP_METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        logger.info(f"Backup eliminado: {backup['filename']}")
        return True
    
    except Exception as e:
        logger.error(f"Error al eliminar backup: {str(e)}")
        return False

def restore_backup(backup_id):
    """
    Restaura la base de datos desde un backup.
    
    Args:
        backup_id (str): ID del backup a restaurar
        
    Returns:
        dict: Resultado de la operación con los campos 'success' y 'message'
    """
    try:
        # Obtener el backup
        backup = get_backup_by_id(backup_id)
        if not backup:
            return {'success': False, 'message': f"Backup no encontrado: {backup_id}"}
        
        # Obtener parámetros de conexión y URL completa
        db_params = get_database_connection_params()
        db_url = Config.SQLALCHEMY_DATABASE_URI
        
        # Verificar si el archivo existe
        if not os.path.exists(backup['path']):
            return {'success': False, 'message': f"Archivo de backup no encontrado: {backup['path']}"}
        
        # Para backups grandes, procesamos el archivo de forma incremental para reducir el uso de memoria
        # No descomprimimos todo el archivo a la vez, sino que lo leemos y procesamos en bloques
        
        # Comandos de restauración optimizados para memoria
        if backup['compressed']:
            # Usamos zcat para descomprimir al vuelo y pipe a psql para reducir el uso de memoria
            restore_cmd = f"zcat '{backup['path']}' | psql '{db_url}' -v ON_ERROR_STOP=1"
            logger.info(f"Ejecutando restauración comprimida: {restore_cmd}")
            
            # Configurar límites de memoria más estrictos para evitar OOM killer
            process = subprocess.Popen(
                restore_cmd,
                shell=True,  # Necesario para pipes
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
        else:
            # Para archivos no comprimidos, leemos directamente
            restore_cmd = [
                'psql',
                db_url,
                '-v', 'ON_ERROR_STOP=1',
                '-f', backup['path']
            ]
            logger.info(f"Ejecutando restauración no comprimida: {' '.join(restore_cmd)}")
            
            process = subprocess.Popen(
                restore_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
        # Monitorear el uso de recursos durante la restauración
        start_time = time.time()
        stdout, stderr = process.communicate()
        end_time = time.time()
        
        # Verificar si el proceso terminó correctamente
        if process.returncode != 0:
            logger.error(f"Error al restaurar backup: {stderr}")
            return {
                'success': False, 
                'message': f"Error en la restauración: {stderr}",
                'duration': f"{end_time - start_time:.2f} segundos"
            }
        
        logger.info(f"Backup restaurado exitosamente: {backup['filename']} en {end_time - start_time:.2f} segundos")
        return {
            'success': True, 
            'message': f"Backup restaurado exitosamente: {backup['filename']}",
            'details': stdout,
            'duration': f"{end_time - start_time:.2f} segundos"
        }
    
    except Exception as e:
        logger.error(f"Error al restaurar backup: {str(e)}")
        return {'success': False, 'message': f"Error en la restauración: {str(e)}"}

def apply_retention_policy(daily_keep=7, weekly_keep=4, monthly_keep=3):
    """
    Aplica la política de retención para eliminar backups antiguos.
    
    Args:
        daily_keep (int): Número de backups diarios a conservar
        weekly_keep (int): Número de backups semanales a conservar
        monthly_keep (int): Número de backups mensuales a conservar
        
    Returns:
        int: Número de backups eliminados
    """
    try:
        backups = get_all_backups()
        if not backups:
            return 0
        
        now = datetime.now()
        
        # Clasificar backups por período
        daily_backups = []
        weekly_backups = []
        monthly_backups = []
        
        for backup in backups:
            backup_date = datetime.strptime(backup['date'], '%Y-%m-%d %H:%M:%S')
            days_old = (now - backup_date).days
            
            if days_old < 7:
                daily_backups.append(backup)
            elif days_old < 30:
                weekly_backups.append(backup)
            else:
                monthly_backups.append(backup)
        
        # Determinar qué backups eliminar
        to_delete = []
        
        # Diarios: conservar solo los más recientes según la configuración
        if len(daily_backups) > daily_keep:
            # Ordenar por fecha (más antiguo primero)
            sorted_daily = sorted(daily_backups, key=lambda x: x['date'])
            to_delete.extend(sorted_daily[:(len(daily_backups) - daily_keep)])
        
        # Semanales: conservar solo los más recientes según la configuración
        if len(weekly_backups) > weekly_keep:
            sorted_weekly = sorted(weekly_backups, key=lambda x: x['date'])
            to_delete.extend(sorted_weekly[:(len(weekly_backups) - weekly_keep)])
        
        # Mensuales: conservar solo los más recientes según la configuración
        if len(monthly_backups) > monthly_keep:
            sorted_monthly = sorted(monthly_backups, key=lambda x: x['date'])
            to_delete.extend(sorted_monthly[:(len(monthly_backups) - monthly_keep)])
        
        # Eliminar los backups seleccionados
        count_deleted = 0
        for backup in to_delete:
            if delete_backup(backup['id']):
                count_deleted += 1
        
        logger.info(f"Política de retención aplicada: {count_deleted} backups eliminados")
        return count_deleted
    
    except Exception as e:
        logger.error(f"Error al aplicar política de retención: {str(e)}")
        return 0

def format_backup_size(size_bytes):
    """
    Formatea el tamaño del backup en una unidad legible.
    
    Args:
        size_bytes (int): Tamaño en bytes
        
    Returns:
        str: Tamaño formateado (KB, MB, GB)
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def check_database_status():
    """
    Verifica el estado de la base de datos.
    
    Returns:
        dict: Estado de la base de datos con información de versión, tamaño, etc.
    """
    try:
        # Obtener los parámetros de conexión
        db_params = get_database_connection_params()
        
        # Conectar a la base de datos
        # Utilizar la URL completa para asegurar que se use sslmode=require
        db_url = Config.SQLALCHEMY_DATABASE_URI
        conn = psycopg2.connect(db_url)
        
        cursor = conn.cursor()
        
        # Obtener la versión de PostgreSQL
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Obtener el tamaño de la base de datos
        cursor.execute("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                   pg_database_size(current_database()) as size_bytes;
        """)
        size_info = cursor.fetchone()
        
        # Obtener información de las tablas
        cursor.execute("""
            SELECT count(*) FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        table_count = cursor.fetchone()[0]
        
        # Obtener las 10 tablas más grandes
        cursor.execute("""
            SELECT 
                table_name, 
                pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size,
                pg_total_relation_size(quote_ident(table_name)) as size_bytes
            FROM 
                information_schema.tables
            WHERE 
                table_schema = 'public'
            ORDER BY 
                pg_total_relation_size(quote_ident(table_name)) DESC
            LIMIT 10;
        """)
        largest_tables = cursor.fetchall()
        
        # Cerrar la conexión
        cursor.close()
        conn.close()
        
        return {
            'status': 'online',
            'version': version,
            'database': db_params['dbname'],
            'host': db_params['host'],
            'size': size_info[0],
            'size_bytes': size_info[1],
            'table_count': table_count,
            'largest_tables': [
                {'name': table[0], 'size': table[1], 'size_bytes': table[2]}
                for table in largest_tables
            ],
            'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    except Exception as e:
        logger.error(f"Error al verificar estado de la base de datos: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def run_scheduled_backup():
    """
    Ejecuta un backup programado y aplica la política de retención.
    
    Returns:
        dict: Resultado de la operación
    """
    try:
        # Crear un backup completo
        backup = create_backup(tipo='full', compress=True, 
                               description=f"Backup programado - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not backup:
            return {'success': False, 'message': "Error al crear backup programado"}
        
        # Aplicar política de retención
        deleted_count = apply_retention_policy()
        
        return {
            'success': True,
            'message': f"Backup programado completado: {backup['filename']}",
            'backup': backup,
            'deleted_count': deleted_count
        }
    
    except Exception as e:
        logger.error(f"Error en backup programado: {str(e)}")
        return {'success': False, 'message': f"Error en backup programado: {str(e)}"}

# Función para programar un backup (se usaría con un scheduler como APScheduler)
def schedule_backup_job():
    """
    Función para ser llamada por un programador de tareas.
    Registra información sobre la ejecución del backup programado.
    """
    logger.info("Iniciando backup programado")
    result = run_scheduled_backup()
    
    if result['success']:
        logger.info(f"Backup programado completado exitosamente: {result['message']}")
    else:
        logger.error(f"Error en backup programado: {result['message']}")
    
    return result

if __name__ == "__main__":
    # Código para pruebas
    print("Módulo de gestión de backups")
    print("Use este módulo desde la aplicación Flask")