"""
Script para crear tareas de ejemplo para la API.
Esto muestra cómo se conecta a la base de datos PostgreSQL y se interactúa con ella.
"""
import os
from datetime import datetime, date, timedelta
from app import create_app, db
from api_models import APITask

def create_sample_tasks():
    """
    Crea tareas de ejemplo para la API.
    """
    print("Creando tareas de ejemplo para la API...")
    
    # Lista de tareas de ejemplo
    sample_tasks = [
        {
            'title': 'Revisar inventario',
            'description': 'Realizar un conteo completo del inventario de productos.',
            'priority': 'alta',
            'frequency': 'semanal',
            'status': 'pendiente',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=30)
        },
        {
            'title': 'Actualizar documentación',
            'description': 'Actualizar la documentación técnica del sistema.',
            'priority': 'media',
            'frequency': 'mensual',
            'status': 'pendiente',
            'start_date': date.today() - timedelta(days=5),
            'end_date': None
        },
        {
            'title': 'Limpieza de base de datos',
            'description': 'Eliminar registros obsoletos de la base de datos.',
            'priority': 'baja',
            'frequency': 'mensual',
            'status': 'completada',
            'start_date': date.today() - timedelta(days=10),
            'end_date': None
        },
        {
            'title': 'Reunión de equipo',
            'description': 'Reunión semanal para revisar el progreso del proyecto.',
            'priority': 'media',
            'frequency': 'semanal',
            'status': 'pendiente',
            'start_date': date.today(),
            'end_date': None
        },
        {
            'title': 'Respaldo de datos',
            'description': 'Realizar respaldo completo de todos los sistemas.',
            'priority': 'urgente',
            'frequency': 'diaria',
            'status': 'pendiente',
            'start_date': date.today() - timedelta(days=1),
            'end_date': None
        }
    ]
    
    # Crear tareas de ejemplo
    for task_data in sample_tasks:
        task = APITask(**task_data)
        db.session.add(task)
    
    # Guardar cambios en la base de datos
    db.session.commit()
    
    print(f"Se han creado {len(sample_tasks)} tareas de ejemplo para la API.")

if __name__ == '__main__':
    # Crear la aplicación Flask con la configuración predeterminada
    app = create_app()
    
    # Establecer el contexto de la aplicación
    with app.app_context():
        try:
            # Primero crear las tablas si no existen
            db.create_all()
            print("Tablas creadas correctamente.")
            
            # Luego verificar si ya existen tareas
            existing_tasks = APITask.query.count()
            
            if existing_tasks > 0:
                print(f"Ya existen {existing_tasks} tareas en la base de datos. No se crearán nuevas tareas.")
            else:
                # Crear tareas de ejemplo
                create_sample_tasks()
        except Exception as e:
            print(f"Error: {e}")