"""
Este módulo implementa las rutas para el nuevo módulo de horarios basado en React/TypeScript.
Sirve la aplicación React y proporciona los endpoints de API necesarios para la comunicación
entre el frontend y el backend.
"""

import os
import json
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, abort, current_app
from flask_login import login_required, current_user
from urllib.parse import urlparse

# Crear el blueprint
horarios_bp = Blueprint('horarios', __name__, url_prefix='/horarios')

# Lista para almacenar el estado de los horarios (temporal hasta implementar la BD)
schedules_data = []

def init_app(app):
    """
    Inicializa el módulo de horarios en la aplicación Flask.
    
    Args:
        app: La aplicación Flask
    """
    app.logger.info("Inicializando módulo de horarios")
    
    # Configuración adicional si es necesaria
    app.config.setdefault('HORARIOS_DEBUG', False)
    
    # Cargar datos iniciales si existen
    try:
        load_demo_data()
    except Exception as e:
        app.logger.error(f"Error al cargar datos de horarios: {e}")

def load_demo_data():
    """
    Carga datos de demostración para el módulo de horarios.
    """
    global schedules_data
    
    # Datos de ejemplo (estructura básica)
    schedules_data = [
        {
            "id": 1,
            "name": "Semana del 15 de Abril",
            "start_date": "2025-04-15",
            "end_date": "2025-04-21",
            "published": True,
            "location_id": 1
        },
        {
            "id": 2,
            "name": "Semana del 22 de Abril",
            "start_date": "2025-04-22",
            "end_date": "2025-04-28",
            "published": False,
            "location_id": 1
        }
    ]

# Ruta principal para el módulo de horarios (sirve la aplicación React)
@horarios_bp.route('/')
@login_required
def index():
    """
    Ruta principal del módulo de horarios. Renderiza la plantilla que contiene la app React.
    """
    # Verificar si el usuario tiene permisos para ver horarios
    if not current_user.is_admin() and not current_user.is_gerente():
        abort(403)  # Forbidden
    
    return render_template('horarios_index.html')

# API para obtener los horarios
@horarios_bp.route('/api/schedules', methods=['GET'])
@login_required
def get_schedules():
    """
    API para obtener los horarios disponibles.
    """
    # Verificar permisos
    if not current_user.is_admin() and not current_user.is_gerente():
        return jsonify({"error": "No tienes permisos para acceder a esta información"}), 403
    
    # En una implementación real, esto obtendría datos de la BD
    return jsonify(schedules_data)

# API para crear un nuevo horario
@horarios_bp.route('/api/schedules', methods=['POST'])
@login_required
def create_schedule():
    """
    API para crear un nuevo horario.
    """
    # Verificar permisos
    if not current_user.is_admin() and not current_user.is_gerente():
        return jsonify({"error": "No tienes permisos para crear horarios"}), 403
    
    # Obtener los datos del request
    data = request.json
    
    # Validar datos básicos
    if not data or not data.get('name') or not data.get('start_date') or not data.get('end_date'):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    
    # Crear nuevo horario (temporal, en una implementación real se guardaría en la BD)
    new_schedule = {
        "id": len(schedules_data) + 1,
        "name": data.get('name'),
        "start_date": data.get('start_date'),
        "end_date": data.get('end_date'),
        "published": False,
        "location_id": data.get('location_id', 1)
    }
    
    # Agregar a la lista temporal
    schedules_data.append(new_schedule)
    
    return jsonify(new_schedule), 201

# API para obtener un horario específico
@horarios_bp.route('/api/schedules/<int:schedule_id>', methods=['GET'])
@login_required
def get_schedule(schedule_id):
    """
    API para obtener un horario específico por su ID.
    """
    # Verificar permisos
    if not current_user.is_admin() and not current_user.is_gerente():
        return jsonify({"error": "No tienes permisos para acceder a esta información"}), 403
    
    # Buscar el horario en la lista temporal
    schedule = next((s for s in schedules_data if s["id"] == schedule_id), None)
    
    if not schedule:
        return jsonify({"error": "Horario no encontrado"}), 404
    
    return jsonify(schedule)

# API para actualizar un horario
@horarios_bp.route('/api/schedules/<int:schedule_id>', methods=['PUT'])
@login_required
def update_schedule(schedule_id):
    """
    API para actualizar un horario existente.
    """
    # Verificar permisos
    if not current_user.is_admin() and not current_user.is_gerente():
        return jsonify({"error": "No tienes permisos para modificar horarios"}), 403
    
    # Obtener los datos del request
    data = request.json
    
    # Buscar el horario en la lista temporal
    schedule_index = next((i for i, s in enumerate(schedules_data) if s["id"] == schedule_id), None)
    
    if schedule_index is None:
        return jsonify({"error": "Horario no encontrado"}), 404
    
    # Actualizar los campos enviados
    for key in data:
        schedules_data[schedule_index][key] = data[key]
    
    return jsonify(schedules_data[schedule_index])

# API para eliminar un horario
@horarios_bp.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
@login_required
def delete_schedule(schedule_id):
    """
    API para eliminar un horario.
    """
    # Verificar permisos
    if not current_user.is_admin():
        return jsonify({"error": "Solo los administradores pueden eliminar horarios"}), 403
    
    # Buscar el horario en la lista temporal
    schedule_index = next((i for i, s in enumerate(schedules_data) if s["id"] == schedule_id), None)
    
    if schedule_index is None:
        return jsonify({"error": "Horario no encontrado"}), 404
    
    # Eliminar el horario
    deleted_schedule = schedules_data.pop(schedule_index)
    
    return jsonify({"message": f"Horario '{deleted_schedule['name']}' eliminado correctamente"})

# Ruta para acceder directamente a un horario específico
@horarios_bp.route('/schedule/<int:schedule_id>')
@login_required
def view_schedule(schedule_id):
    """
    Renderiza la vista para un horario específico.
    """
    # Verificar permisos
    if not current_user.is_admin() and not current_user.is_gerente():
        abort(403)  # Forbidden
    
    return render_template('horarios_index.html', schedule_id=schedule_id)