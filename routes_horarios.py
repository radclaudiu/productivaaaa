"""
Este módulo implementa las rutas para el nuevo módulo de horarios basado en React/TypeScript.
Sirve la aplicación React y proporciona los endpoints de API necesarios para la comunicación
entre el frontend y el backend.
"""

import os
import json
from datetime import datetime, date
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, abort, current_app
from flask_login import login_required, current_user
from urllib.parse import urlparse
from app import db
from models import Company, Employee
from models_horarios import Schedule, ScheduleAssignment

# Crear el blueprint
horarios_bp = Blueprint('horarios', __name__, url_prefix='/horarios')

def init_app(app):
    """
    Inicializa el módulo de horarios en la aplicación Flask.
    
    Args:
        app: La aplicación Flask
    """
    app.logger.info("Inicializando módulo de horarios")
    
    # Configuración adicional si es necesaria
    app.config.setdefault('HORARIOS_DEBUG', False)
    
    # Asegurarnos de que las tablas del módulo de horarios existan
    try:
        with app.app_context():
            db.create_all()
            app.logger.info("Tablas de horarios creadas/verificadas correctamente")
    except Exception as e:
        app.logger.error(f"Error al crear tablas de horarios: {e}")

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
    
    try:
        # Obtener el company_id actual del usuario (usar el primero si tiene varios)
        company_id = current_user.company_id
        if not company_id:
            return jsonify({"error": "No tienes una empresa asignada"}), 400
        
        # Obtener todos los horarios de la base de datos para esta empresa
        schedules = Schedule.query.filter_by(company_id=company_id).order_by(Schedule.start_date.desc()).all()
        
        # Convertir a diccionario para JSON
        return jsonify([schedule.to_dict() for schedule in schedules])
    except Exception as e:
        current_app.logger.error(f"Error al obtener horarios: {e}")
        return jsonify({"error": f"Error al obtener horarios: {str(e)}"}), 500

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
    
    # Obtener el company_id actual del usuario
    company_id = current_user.company_id
    if not company_id:
        return jsonify({"error": "No tienes una empresa asignada"}), 400
    
    try:
        # Convertir las fechas de string a date
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
        
        # Crear nuevo horario
        new_schedule = Schedule(
            name=data.get('name'),
            start_date=start_date,
            end_date=end_date,
            published=False,
            company_id=company_id
        )
        
        # Guardar en la base de datos
        db.session.add(new_schedule)
        db.session.commit()
        
        return jsonify(new_schedule.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al crear horario: {e}")
        return jsonify({"error": f"Error al crear horario: {str(e)}"}), 500

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
    
    # Buscar el horario en la base de datos
    schedule = Schedule.query.get(schedule_id)
    
    if not schedule:
        return jsonify({"error": "Horario no encontrado"}), 404
    
    # Verificar que el horario pertenece a la empresa del usuario
    if schedule.company_id != current_user.company_id and not current_user.is_admin():
        return jsonify({"error": "No tienes permisos para acceder a este horario"}), 403
    
    # Obtener también las asignaciones
    assignments = ScheduleAssignment.query.filter_by(schedule_id=schedule_id).all()
    
    # Crear un diccionario con toda la información
    schedule_data = schedule.to_dict()
    schedule_data['assignments'] = [assignment.to_dict() for assignment in assignments]
    
    return jsonify(schedule_data)

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
    
    # Buscar el horario en la base de datos
    schedule = Schedule.query.get(schedule_id)
    
    if not schedule:
        return jsonify({"error": "Horario no encontrado"}), 404
    
    # Verificar que el horario pertenece a la empresa del usuario
    if schedule.company_id != current_user.company_id and not current_user.is_admin():
        return jsonify({"error": "No tienes permisos para modificar este horario"}), 403
    
    try:
        # Actualizar los campos enviados
        if 'name' in data:
            schedule.name = data['name']
        
        if 'start_date' in data:
            schedule.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        
        if 'end_date' in data:
            schedule.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        if 'published' in data:
            schedule.published = data['published']
        
        # Guardar los cambios
        db.session.commit()
        
        return jsonify(schedule.to_dict())
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al actualizar horario: {e}")
        return jsonify({"error": f"Error al actualizar horario: {str(e)}"}), 500

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
    
    # Buscar el horario en la base de datos
    schedule = Schedule.query.get(schedule_id)
    
    if not schedule:
        return jsonify({"error": "Horario no encontrado"}), 404
    
    # Verificar que el horario pertenece a la empresa del usuario
    if schedule.company_id != current_user.company_id and not current_user.is_admin():
        return jsonify({"error": "No tienes permisos para eliminar este horario"}), 403
    
    try:
        # Guardar el nombre para el mensaje
        schedule_name = schedule.name
        
        # Eliminar primero las asignaciones (aunque esto debería manejarse con CASCADE)
        ScheduleAssignment.query.filter_by(schedule_id=schedule_id).delete()
        
        # Eliminar el horario
        db.session.delete(schedule)
        db.session.commit()
        
        return jsonify({"message": f"Horario '{schedule_name}' eliminado correctamente"})
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al eliminar horario: {e}")
        return jsonify({"error": f"Error al eliminar horario: {str(e)}"}), 500

# API para obtener los empleados de una empresa para asignar a horarios
@horarios_bp.route('/api/employees', methods=['GET'])
@login_required
def get_employees():
    """
    API para obtener los empleados disponibles para asignar a horarios.
    """
    # Verificar permisos
    if not current_user.is_admin() and not current_user.is_gerente():
        return jsonify({"error": "No tienes permisos para acceder a esta información"}), 403
    
    # Obtener el company_id actual del usuario
    company_id = current_user.company_id
    if not company_id:
        return jsonify({"error": "No tienes una empresa asignada"}), 400
    
    # Obtener los empleados activos de la empresa
    employees = Employee.query.filter_by(company_id=company_id, is_active=True).all()
    
    # Formatear la información para la API
    employees_data = []
    for employee in employees:
        employees_data.append({
            'id': employee.id,
            'firstName': employee.first_name,
            'lastName': employee.last_name,
            'position': employee.position,
            'department': '',  # Campo no existe en nuestro modelo actual
            'contractedHours': 40  # Valor por defecto, adaptar según el modelo
        })
    
    return jsonify(employees_data)

# API para obtener las asignaciones de un horario
@horarios_bp.route('/api/schedules/<int:schedule_id>/assignments', methods=['GET'])
@login_required
def get_schedule_assignments(schedule_id):
    """
    API para obtener las asignaciones de un horario específico.
    """
    # Verificar permisos
    if not current_user.is_admin() and not current_user.is_gerente():
        return jsonify({"error": "No tienes permisos para acceder a esta información"}), 403
    
    # Verificar que el horario existe
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({"error": "Horario no encontrado"}), 404
    
    # Verificar que el horario pertenece a la empresa del usuario
    if schedule.company_id != current_user.company_id and not current_user.is_admin():
        return jsonify({"error": "No tienes permisos para acceder a este horario"}), 403
    
    # Obtener las asignaciones
    assignments = ScheduleAssignment.query.filter_by(schedule_id=schedule_id).all()
    
    # Formatear para la API
    assignments_data = [assignment.to_dict() for assignment in assignments]
    
    return jsonify(assignments_data)

# API para guardar asignaciones de horario
@horarios_bp.route('/api/schedules/<int:schedule_id>/assignments', methods=['POST'])
@login_required
def save_schedule_assignments(schedule_id):
    """
    API para guardar asignaciones de un horario.
    Puede recibir múltiples asignaciones en una sola llamada.
    """
    # Verificar permisos
    if not current_user.is_admin() and not current_user.is_gerente():
        return jsonify({"error": "No tienes permisos para modificar horarios"}), 403
    
    # Verificar que el horario existe
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({"error": "Horario no encontrado"}), 404
    
    # Verificar que el horario pertenece a la empresa del usuario
    if schedule.company_id != current_user.company_id and not current_user.is_admin():
        return jsonify({"error": "No tienes permisos para modificar este horario"}), 403
    
    # Obtener los datos del request
    data = request.json
    if not data or not isinstance(data, list):
        return jsonify({"error": "Se esperaba una lista de asignaciones"}), 400
    
    try:
        # Crear o actualizar las asignaciones
        saved_assignments = []
        
        for assignment_data in data:
            # Verificar datos requeridos
            if not all(key in assignment_data for key in ['employeeId', 'day', 'startTime', 'endTime']):
                continue  # Ignorar datos incompletos
            
            # Convertir la fecha si es necesario
            if isinstance(assignment_data['day'], str):
                day = datetime.strptime(assignment_data['day'], '%Y-%m-%d').date()
            else:
                day = assignment_data['day']
            
            # Buscar si ya existe esta asignación
            assignment = ScheduleAssignment.query.filter_by(
                schedule_id=schedule_id,
                employee_id=assignment_data['employeeId'],
                day=day,
                start_time=assignment_data['startTime']
            ).first()
            
            if assignment:
                # Actualizar la existente
                assignment.end_time = assignment_data['endTime']
                assignment.break_duration = assignment_data.get('breakDuration', 0)
            else:
                # Crear una nueva
                assignment = ScheduleAssignment(
                    schedule_id=schedule_id,
                    employee_id=assignment_data['employeeId'],
                    day=day,
                    start_time=assignment_data['startTime'],
                    end_time=assignment_data['endTime'],
                    break_duration=assignment_data.get('breakDuration', 0)
                )
                db.session.add(assignment)
            
            saved_assignments.append(assignment)
        
        # Guardar cambios
        db.session.commit()
        
        return jsonify({
            "message": f"Se guardaron {len(saved_assignments)} asignaciones",
            "assignments": [a.to_dict() for a in saved_assignments]
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al guardar asignaciones: {e}")
        return jsonify({"error": f"Error al guardar asignaciones: {str(e)}"}), 500

# API para eliminar todas las asignaciones de un horario
@horarios_bp.route('/api/schedules/<int:schedule_id>/assignments', methods=['DELETE'])
@login_required
def clear_schedule_assignments(schedule_id):
    """
    API para eliminar todas las asignaciones de un horario.
    """
    # Verificar permisos
    if not current_user.is_admin() and not current_user.is_gerente():
        return jsonify({"error": "No tienes permisos para modificar horarios"}), 403
    
    # Verificar que el horario existe
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({"error": "Horario no encontrado"}), 404
    
    # Verificar que el horario pertenece a la empresa del usuario
    if schedule.company_id != current_user.company_id and not current_user.is_admin():
        return jsonify({"error": "No tienes permisos para modificar este horario"}), 403
    
    try:
        # Eliminar todas las asignaciones
        deleted_count = ScheduleAssignment.query.filter_by(schedule_id=schedule_id).delete()
        db.session.commit()
        
        return jsonify({
            "message": f"Se eliminaron {deleted_count} asignaciones",
            "count": deleted_count
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al eliminar asignaciones: {e}")
        return jsonify({"error": f"Error al eliminar asignaciones: {str(e)}"}), 500

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