"""
Script para crear directamente las tablas en la base de datos PostgreSQL
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Obtener los datos de conexión
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("Error: No se encontró la variable de entorno DATABASE_URL")
    exit(1)

print(f"Conectando a la base de datos...")
try:
    # Conectar a la base de datos
    conn = psycopg2.connect(db_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Crear tablas principales del sistema
    print("Creando tablas del sistema...")
    
    # Tabla users (usuarios)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(64) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(256) NOT NULL,
        role VARCHAR(20) NOT NULL,
        first_name VARCHAR(64),
        last_name VARCHAR(64),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE
    )
    ''')
    
    # Tabla companies (empresas)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        id SERIAL PRIMARY KEY,
        name VARCHAR(128) NOT NULL,
        address VARCHAR(256),
        city VARCHAR(64),
        postal_code VARCHAR(16),
        country VARCHAR(64),
        sector VARCHAR(64),
        tax_id VARCHAR(32) UNIQUE,
        phone VARCHAR(13),
        email VARCHAR(120),
        website VARCHAR(128),
        bank_account VARCHAR(24),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE
    )
    ''')
    
    # Tabla de relación usuarios-empresas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_companies (
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
        PRIMARY KEY (user_id, company_id)
    )
    ''')
    
    # Tabla empleados
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(64) NOT NULL,
        last_name VARCHAR(64) NOT NULL,
        dni VARCHAR(16) UNIQUE NOT NULL,
        social_security_number VARCHAR(20),
        email VARCHAR(120),
        address VARCHAR(200),
        phone VARCHAR(20),
        position VARCHAR(64),
        contract_type VARCHAR(20),
        bank_account VARCHAR(64),
        start_date DATE,
        end_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        status VARCHAR(20),
        status_start_date DATE,
        status_end_date DATE,
        status_notes TEXT,
        is_on_shift BOOLEAN DEFAULT FALSE,
        company_id INTEGER REFERENCES companies(id) NOT NULL,
        user_id INTEGER REFERENCES users(id) UNIQUE
    )
    ''')
    
    # Crear usuario administrador
    print("Creando usuario administrador...")
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    result = cursor.fetchone()
    admin_exists = 0
    if result and result[0]:
        admin_exists = result[0]
    
    if not admin_exists:
        # Contraseña: admin123 (hash generado con werkzeug.security)
        admin_hash = 'pbkdf2:sha256:150000$cYhiJMbC$3fc05d2e9b6e8d6695bbec41445f17b6cde96cd0a57066c89b323b9eb47d43d4'
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, role, first_name, last_name)
        VALUES ('admin', 'admin@example.com', %s, 'ADMIN', 'Admin', 'Usuario')
        ''', (admin_hash,))
        print("✅ Usuario administrador creado correctamente")
    else:
        print("✅ El usuario administrador ya existe")
    
    # Crear empresa por defecto si no existe
    cursor.execute("SELECT COUNT(*) FROM companies WHERE name = 'Empresa Demo'")
    result = cursor.fetchone()
    company_exists = 0
    if result and result[0]:
        company_exists = result[0]
    
    if not company_exists:
        cursor.execute('''
        INSERT INTO companies (name, address, city, country, tax_id, email)
        VALUES ('Empresa Demo', 'Calle Principal 123', 'Madrid', 'España', 'B12345678', 'info@empresademo.com')
        ''')
        print("✅ Empresa demo creada correctamente")
    else:
        print("✅ La empresa demo ya existe")
    
    # Asignar empresa al administrador
    cursor.execute('''
    INSERT INTO user_companies (user_id, company_id)
    SELECT 
        (SELECT id FROM users WHERE username = 'admin'), 
        (SELECT id FROM companies WHERE name = 'Empresa Demo')
    WHERE NOT EXISTS (
        SELECT 1 FROM user_companies 
        WHERE user_id = (SELECT id FROM users WHERE username = 'admin')
        AND company_id = (SELECT id FROM companies WHERE name = 'Empresa Demo')
    )
    ''')
    
    # Cerrar la conexión
    cursor.close()
    conn.close()
    
    print("✅ Base de datos inicializada correctamente")
    print("Ya puede ejecutar 'python main.py' para iniciar la aplicación")
    
except Exception as e:
    print(f"❌ Error al inicializar la base de datos: {str(e)}")