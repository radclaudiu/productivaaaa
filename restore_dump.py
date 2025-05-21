"""
Script para restaurar estructuras de la base de datos desde un archivo de texto
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Obtener los datos de conexión
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("Error: No se encontró la variable de entorno DATABASE_URL")
    exit(1)

# Leer el contenido del archivo de dump
dump_file_path = 'attached_assets/Pasted--PostgreSQL-database-dump-Dumped-from-database-version-16-8-Dumped-by-pg-dump-version-1747838809586.txt'

print(f"Leyendo archivo de dump: {dump_file_path}")
try:
    with open(dump_file_path, 'r') as file:
        dump_content = file.read()
    
    print(f"Archivo leído correctamente. Tamaño: {len(dump_content)} bytes")
    
    # Conectar a la base de datos
    print("Conectando a la base de datos...")
    conn = psycopg2.connect(db_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Ejecutar el contenido del dump
    print("Ejecutando el dump en la base de datos...")
    cursor.execute(dump_content)
    
    # Cerrar conexión
    cursor.close()
    conn.close()
    
    print("✅ Estructura de la base de datos actualizada correctamente")
    
except FileNotFoundError:
    print(f"❌ Error: No se encontró el archivo {dump_file_path}")
except Exception as e:
    print(f"❌ Error al ejecutar el dump: {str(e)}")
    # Intentar cerrar la conexión si estaba abierta
    try:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    except:
        pass