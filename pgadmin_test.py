"""
Script para probar si pgadmin.py funciona correctamente.
"""
import os
import psycopg2
from urllib.parse import urlparse

# Configuración
DATABASE_URL = os.environ.get('DATABASE_URL')
print(f"Using DATABASE_URL: {DATABASE_URL}")

# Analizar la URL de la base de datos
try:
    url = urlparse(DATABASE_URL)
    
    db_user = url.username
    db_password = url.password
    db_host = url.hostname
    db_port = url.port if url.port else 5432
    
    # Extraer nombre de la base de datos y parámetros de la ruta y consulta
    path = url.path.strip('/')
    if '?' in path:
        db_name = path.split('?')[0]
    else:
        db_name = path
    
    # Extraer modo SSL si está presente
    query = url.query
    ssl_mode = 'require' if 'sslmode=require' in query else None
    
    print(f"Parsed connection parameters:")
    print(f"  User: {db_user}")
    print(f"  Host: {db_host}")
    print(f"  Port: {db_port}")
    print(f"  Database: {db_name}")
    print(f"  SSL Mode: {ssl_mode}")
    
    # Intentar conectarse a la base de datos
    print("Trying to connect to database...")
    conn_params = {
        'host': db_host,
        'port': db_port,
        'dbname': db_name,
        'user': db_user,
        'password': db_password
    }
    
    # Agregar modo SSL si es necesario
    if ssl_mode:
        conn_params['sslmode'] = ssl_mode
    
    conn = psycopg2.connect(**conn_params)
    print("Connection successful!")
    
    # Ejecutar una consulta simple
    cursor = conn.cursor()
    cursor.execute("SELECT current_timestamp, current_database(), current_user")
    result = cursor.fetchone()
    print(f"Current time: {result[0]}")
    print(f"Current database: {result[1]}")
    print(f"Current user: {result[2]}")
    
    # Cerrar la conexión
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {str(e)}")