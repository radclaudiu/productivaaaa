"""
Script para ejecutar backups programados automáticamente.

Este script está diseñado para ser ejecutado mediante un cron job o programador
de tareas similar para realizar backups automáticos de la base de datos según
la configuración definida.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime, timedelta

# Configurar la ruta de importación para acceder a módulos de la aplicación
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar el módulo de gestión de backups
import backup_manager

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='scheduled_backup.log',
    filemode='a'
)
logger = logging.getLogger('scheduled_backup')

# Archivo de configuración de backups programados
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backup_schedule.json')

def load_config():
    """
    Carga la configuración de backups programados desde el archivo JSON.
    Si el archivo no existe, crea una configuración predeterminada.
    
    Returns:
        dict: Configuración de backups programados
    """
    if not os.path.exists(CONFIG_FILE):
        # Configuración predeterminada
        config = {
            'enabled': True,
            'frequency': 'daily',
            'time': '03:00',
            'retention': {
                'daily': 7,
                'weekly': 4,
                'monthly': 3
            },
            'last_run': None,
            'next_run': None
        }
        
        # Guardar la configuración predeterminada
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        
        logger.info("Archivo de configuración creado con valores predeterminados")
        return config
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        logger.info("Configuración cargada correctamente")
        return config
    
    except Exception as e:
        logger.error(f"Error al cargar la configuración: {str(e)}")
        return None

def save_config(config):
    """
    Guarda la configuración en el archivo JSON.
    
    Args:
        config (dict): Configuración a guardar
    
    Returns:
        bool: True si se guardó correctamente, False en caso contrario
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        
        logger.info("Configuración guardada correctamente")
        return True
    
    except Exception as e:
        logger.error(f"Error al guardar la configuración: {str(e)}")
        return False

def should_run_backup(config):
    """
    Determina si se debe ejecutar un backup en este momento según la configuración.
    
    Args:
        config (dict): Configuración de backups programados
    
    Returns:
        bool: True si se debe ejecutar un backup, False en caso contrario
    """
    if not config or not config.get('enabled', False):
        logger.info("Backups programados deshabilitados")
        return False
    
    now = datetime.now()
    last_run = config.get('last_run')
    
    # Si nunca se ha ejecutado, ejecutar ahora
    if not last_run:
        logger.info("Primera ejecución de backup programado")
        return True
    
    # Convertir last_run a objeto datetime
    last_run = datetime.strptime(last_run, '%Y-%m-%d %H:%M:%S')
    
    # Verificar la frecuencia configurada
    frequency = config.get('frequency', 'daily')
    
    if frequency == 'daily':
        # Verificar si ha pasado más de un día desde la última ejecución
        next_run = last_run + timedelta(days=1)
    elif frequency == 'weekly':
        # Verificar si ha pasado más de una semana desde la última ejecución
        next_run = last_run + timedelta(weeks=1)
    elif frequency == 'monthly':
        # Verificar si ha pasado más de un mes (30 días) desde la última ejecución
        next_run = last_run + timedelta(days=30)
    else:
        # Frecuencia no reconocida, usar diario
        next_run = last_run + timedelta(days=1)
    
    # Actualizar next_run en la configuración
    config['next_run'] = next_run.strftime('%Y-%m-%d %H:%M:%S')
    save_config(config)
    
    # Verificar si es hora de ejecutar
    return now >= next_run

def run_backup():
    """
    Ejecuta un backup programado y actualiza la configuración.
    
    Returns:
        bool: True si el backup se ejecutó correctamente, False en caso contrario
    """
    logger.info("Iniciando proceso de backup programado")
    
    try:
        # Cargar la configuración
        config = load_config()
        
        if should_run_backup(config):
            # Ejecutar el backup
            logger.info("Ejecutando backup programado")
            result = backup_manager.run_scheduled_backup()
            
            if result['success']:
                logger.info(f"Backup programado completado exitosamente: {result['message']}")
                
                # Actualizar timestamp de última ejecución
                config['last_run'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                save_config(config)
                
                # Aplicar política de retención
                retention = config.get('retention', {'daily': 7, 'weekly': 4, 'monthly': 3})
                backup_manager.apply_retention_policy(
                    daily_keep=retention.get('daily', 7),
                    weekly_keep=retention.get('weekly', 4),
                    monthly_keep=retention.get('monthly', 3)
                )
                
                return True
            else:
                logger.error(f"Error al ejecutar backup programado: {result['message']}")
                return False
        else:
            logger.info("No es momento de ejecutar un backup programado según la configuración")
            return False
    
    except Exception as e:
        logger.error(f"Error inesperado al ejecutar backup programado: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando script de backup programado")
    
    # Intentar obtener un argumento de línea de comandos (--force para forzar la ejecución)
    force = len(sys.argv) > 1 and sys.argv[1] == '--force'
    
    if force:
        logger.info("Ejecución forzada por parámetro de línea de comandos")
        result = backup_manager.run_scheduled_backup()
        
        if result['success']:
            logger.info(f"Backup forzado completado exitosamente: {result['message']}")
            
            # Cargar y actualizar configuración
            config = load_config()
            config['last_run'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_config(config)
            
            # Aplicar política de retención
            retention = config.get('retention', {'daily': 7, 'weekly': 4, 'monthly': 3})
            backup_manager.apply_retention_policy(
                daily_keep=retention.get('daily', 7),
                weekly_keep=retention.get('weekly', 4),
                monthly_keep=retention.get('monthly', 3)
            )
            
            sys.exit(0)
        else:
            logger.error(f"Error al ejecutar backup forzado: {result['message']}")
            sys.exit(1)
    else:
        # Ejecución normal, verificar configuración
        if run_backup():
            logger.info("Proceso de backup programado completado exitosamente")
            sys.exit(0)
        else:
            logger.info("No se ejecutó ningún backup en esta pasada")
            sys.exit(0)