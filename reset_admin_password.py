"""
Script para restablecer la contraseña del usuario administrador.
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from werkzeug.security import generate_password_hash

# Obtener los datos de conexión
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("Error: No se encontró la variable de entorno DATABASE_URL")
    exit(1)

# Generar un nuevo hash para la contraseña 'admin123'
new_password = 'admin123'
password_hash = generate_password_hash(new_password)

print(f"Conectando a la base de datos...")
try:
    # Conectar a la base de datos
    conn = psycopg2.connect(db_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Actualizar la contraseña del usuario admin
    cursor.execute("""
    UPDATE users 
    SET password_hash = %s 
    WHERE username = 'admin'
    """, (password_hash,))
    
    # Verificar que se haya actualizado
    cursor.execute("SELECT id, username, email FROM users WHERE username = 'admin'")
    admin_user = cursor.fetchone()
    
    if admin_user:
        print(f"✅ Contraseña restablecida correctamente para el usuario admin (ID: {admin_user[0]})")
        print(f"   Usuario: {admin_user[1]}")
        print(f"   Email: {admin_user[2]}")
        print(f"   Nueva contraseña: {new_password}")
    else:
        print("❌ No se encontró el usuario admin")
    
    # Cerrar la conexión
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error al restablecer la contraseña: {str(e)}")