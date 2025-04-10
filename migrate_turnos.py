"""
Script para crear las tablas para el sistema de turnos.

Este script crea todas las tablas necesarias para el módulo de gestión de turnos
de empleados si no existen previamente.
"""

from flask import Flask
from sqlalchemy import inspect
import os

from app import db, create_app
from models_turnos import (Turno, Horario, Ausencia, RequisitoPersonal, PlantillaHorario, 
                         DetallePlantilla, AsignacionPlantilla, PreferenciaDisponibilidad,
                         HistorialCambios)

def migrate_turnos():
    """
    Crea las tablas para el sistema de turnos si no existen previamente.
    """
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Obtener todas las tablas existentes
        existing_tables = inspector.get_table_names()
        
        # Listar todas las tablas del sistema de turnos
        turnos_tables = [
            'turnos_turno',
            'turnos_horario',
            'turnos_ausencia',
            'turnos_requisito_personal',
            'turnos_plantilla_horario',
            'turnos_detalle_plantilla',
            'turnos_asignacion_plantilla',
            'turnos_preferencia_disponibilidad',
            'turnos_historial_cambios'
        ]
        
        # Verificar cuáles tablas ya existen
        existing_turnos_tables = [table for table in turnos_tables if table in existing_tables]
        missing_turnos_tables = [table for table in turnos_tables if table not in existing_tables]
        
        if missing_turnos_tables:
            print(f"Creando {len(missing_turnos_tables)} tablas para el sistema de turnos:")
            for table in missing_turnos_tables:
                print(f" - {table}")
            
            # Crear las tablas
            db.create_all()
            
            print("\nTablas creadas exitosamente!")
            
            # Crear turnos de ejemplo si no hay ninguno
            if Turno.query.count() == 0:
                print("\nCreando turnos de ejemplo...")
                from datetime import time
                from models_turnos import TipoTurno
                
                # Turnos comunes de ejemplo
                turnos_ejemplo = [
                    {
                        'nombre': 'Mañana',
                        'tipo': TipoTurno.MANANA,
                        'hora_inicio': time(8, 0),
                        'hora_fin': time(16, 0),
                        'color': '#28a745',  # Verde
                        'descanso_inicio': time(13, 0),
                        'descanso_fin': time(14, 0),
                        'descripcion': 'Turno de mañana con 1 hora de descanso'
                    },
                    {
                        'nombre': 'Tarde',
                        'tipo': TipoTurno.TARDE,
                        'hora_inicio': time(16, 0),
                        'hora_fin': time(0, 0),  # 24:00
                        'color': '#007bff',  # Azul
                        'descanso_inicio': time(20, 0),
                        'descanso_fin': time(21, 0),
                        'descripcion': 'Turno de tarde con 1 hora de descanso'
                    },
                    {
                        'nombre': 'Noche',
                        'tipo': TipoTurno.NOCHE,
                        'hora_inicio': time(0, 0),  # 00:00
                        'hora_fin': time(8, 0),
                        'color': '#6f42c1',  # Morado
                        'descanso_inicio': time(4, 0),
                        'descanso_fin': time(4, 30),
                        'descripcion': 'Turno de noche con 30 minutos de descanso'
                    },
                    {
                        'nombre': 'Media Jornada',
                        'tipo': TipoTurno.PERSONALIZADO,
                        'hora_inicio': time(9, 0),
                        'hora_fin': time(13, 0),
                        'color': '#fd7e14',  # Naranja
                        'descripcion': 'Turno de media jornada sin descanso'
                    }
                ]
                
                # Asignar estos turnos a todas las empresas en la base de datos
                from models import Company
                companies = Company.query.filter_by(is_active=True).all()
                
                if companies:
                    for company in companies:
                        print(f" - Creando turnos para la empresa: {company.name}")
                        for turno_data in turnos_ejemplo:
                            # Crear una copia para esta empresa
                            turno = Turno(
                                company_id=company.id,
                                **turno_data
                            )
                            db.session.add(turno)
                    
                    db.session.commit()
                    print(f"Se crearon {len(turnos_ejemplo)} turnos para {len(companies)} empresas.")
                else:
                    print("No se encontraron empresas activas para asignar turnos de ejemplo.")
        else:
            print("Todas las tablas del sistema de turnos ya existen.")
            print("Tablas existentes: ", ", ".join(existing_turnos_tables))
        
        print("\nMigración de turnos completada.")

if __name__ == "__main__":
    migrate_turnos()