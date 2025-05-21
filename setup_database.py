"""
Script para inicializar la base de datos.
Crea las tablas necesarias y configura datos iniciales.
"""

import os
import sys
from app import db, create_app
from utils import create_admin_user

def setup_database():
    """
    Configura la base de datos e inicializa con datos básicos.
    """
    print("Iniciando configuración de la base de datos...")
    
    # Crear la aplicación Flask con el contexto adecuado
    app = create_app()
    
    with app.app_context():
        # Crear todas las tablas
        print("Creando tablas en la base de datos...")
        db.create_all()
        print("✅ Tablas creadas correctamente")
        
        # Crear usuario administrador
        print("Creando usuario administrador...")
        create_admin_user()
        print("✅ Usuario administrador creado correctamente")
        
        print("Base de datos inicializada con éxito.")

if __name__ == "__main__":
    setup_database()