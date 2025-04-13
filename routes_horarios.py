"""
Este módulo implementa las rutas para el módulo de horarios basado en React/TypeScript.
Sirve la aplicación React y proporciona los endpoints de API necesarios para la comunicación
entre el frontend y el backend.
"""

import os
import json
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, abort, current_app
from flask_login import login_required, current_user
from urllib.parse import urlparse
from app import db
from models import Company, Employee, User
from models_horarios import (
    Schedule, ScheduleAssignment, ScheduleTemplate, 
    EmployeeAvailability, ScheduleRule, ScheduleRequest
)

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
    if not current_user.is_admin and not current_user.is_gerente:
        abort(403)  # Forbidden
    
    return render_template('horarios_index.html')

# API para obtener la lista de empresas
@horarios_bp.route('/api/companies', methods=['GET'])
@login_required
def get_companies():
    """Obtiene las empresas disponibles para el usuario actual"""
    if current_user.is_admin:
        companies = Company.query.filter_by(is_active=True).all()
    else:
        # Obtener solo las empresas asignadas al usuario
        user_companies = current_user.get_companies()
        company_ids = [company.id for company in user_companies]
        companies = Company.query.filter(Company.id.in_(company_ids), Company.is_active==True).all()
    
    return jsonify([{
        'id': company.id,
        'name': company.name,
        'address': company.address,
        'city': company.city,
        'sector': company.sector
    } for company in companies])

# API para obtener los horarios
@horarios_bp.route('/api/schedules', methods=['GET'])
@login_required
def get_schedules():
    """
    Obtiene todos los horarios disponibles para la empresa seleccionada.
    """
    company_id = request.args.get('company_id', type=int)
    if not company_id:
        return jsonify({"error": "Se requiere el ID de la empresa"}), 400
    
    # Verificar permisos para la empresa
    if not current_user.is_admin and not current_user.has_company_access(company_id):
        abort(403)  # Forbidden
    
    schedules = Schedule.query.filter_by(company_id=company_id).order_by(Schedule.start_date.desc()).all()
    
    return jsonify([schedule.to_dict() for schedule in schedules])

# API para crear un nuevo horario
@horarios_bp.route('/api/schedules', methods=['POST'])
@login_required
def create_schedule():
    """
    Crea un nuevo horario semanal.
    """
    if not current_user.is_admin and not current_user.is_gerente:
        abort(403)  # Forbidden
    
    data = request.json
    
    if not data or not data.get('company_id') or not data.get('name'):
        return jsonify({"error": "Datos incompletos"}), 400
    
    # Verificar permisos para la empresa
    company_id = data.get('company_id')
    if not current_user.is_admin and not current_user.has_company_access(company_id):
        abort(403)
    
    try:
        # Convertir fechas de string a objetos date
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date() if data.get('start_date') else date.today()
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date() if data.get('end_date') else (start_date + timedelta(days=6))
        
        # Crear nuevo horario
        schedule = Schedule(
            name=data.get('name'),
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
            published=False
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify(schedule.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al crear horario: {e}")
        return jsonify({"error": f"Error al crear horario: {str(e)}"}), 500

# API para obtener un horario específico
@horarios_bp.route('/api/schedules/<int:schedule_id>', methods=['GET'])
@login_required
def get_schedule(schedule_id):
    """
    Obtiene un horario específico por su ID.
    """
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Verificar permisos para la empresa
    if not current_user.is_admin and not current_user.has_company_access(schedule.company_id):
        abort(403)
    
    return jsonify(schedule.to_dict())

# API para actualizar un horario
@horarios_bp.route('/api/schedules/<int:schedule_id>', methods=['PUT'])
@login_required
def update_schedule(schedule_id):
    """
    Actualiza un horario existente.
    """
    if not current_user.is_admin and not current_user.is_gerente:
        abort(403)
    
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Verificar permisos para la empresa
    if not current_user.is_admin and not current_user.has_company_access(schedule.company_id):
        abort(403)
    
    data = request.json
    
    if not data:
        return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400
    
    try:
        # Actualizar campos básicos
        if 'name' in data:
            schedule.name = data['name']
        
        if 'start_date' in data:
            schedule.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        
        if 'end_date' in data:
            schedule.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        if 'published' in data:
            schedule.published = data['published']
        
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
    Elimina un horario existente.
    """
    if not current_user.is_admin and not current_user.is_gerente:
        abort(403)
    
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Verificar permisos para la empresa
    if not current_user.is_admin and not current_user.has_company_access(schedule.company_id):
        abort(403)
    
    try:
        # Eliminar todas las asignaciones asociadas
        ScheduleAssignment.query.filter_by(schedule_id=schedule_id).delete()
        
        # Eliminar el horario
        db.session.delete(schedule)
        db.session.commit()
        
        return jsonify({"message": "Horario eliminado correctamente"}), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al eliminar horario: {e}")
        return jsonify({"error": f"Error al eliminar horario: {str(e)}"}), 500

# API para obtener las asignaciones de un horario
@horarios_bp.route('/api/schedules/<int:schedule_id>/assignments', methods=['GET'])
@login_required
def get_schedule_assignments(schedule_id):
    """
    Obtiene todas las asignaciones para un horario específico.
    """
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Verificar permisos para la empresa
    if not current_user.is_admin and not current_user.has_company_access(schedule.company_id):
        abort(403)
    
    assignments = ScheduleAssignment.query.filter_by(schedule_id=schedule_id).all()
    
    return jsonify([assignment.to_dict() for assignment in assignments])

# API para crear una asignación en un horario
@horarios_bp.route('/api/schedules/<int:schedule_id>/assignments', methods=['POST'])
@login_required
def create_assignment(schedule_id):
    """
    Crea una nueva asignación en un horario.
    """
    if not current_user.is_admin and not current_user.is_gerente:
        abort(403)
    
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Verificar permisos para la empresa
    if not current_user.is_admin and not current_user.has_company_access(schedule.company_id):
        abort(403)
    
    data = request.json
    
    if not data or not data.get('employee_id') or not data.get('day') or not data.get('start_time') or not data.get('end_time'):
        return jsonify({"error": "Datos incompletos"}), 400
    
    try:
        # Convertir día de string a objeto date
        day = datetime.strptime(data.get('day'), '%Y-%m-%d').date()
        
        # Verificar que el empleado pertenece a la empresa
        employee = Employee.query.get_or_404(data.get('employee_id'))
        if employee.company_id != schedule.company_id:
            return jsonify({"error": "El empleado no pertenece a la empresa del horario"}), 400
        
        # Crear nueva asignación
        assignment = ScheduleAssignment(
            schedule_id=schedule_id,
            employee_id=data.get('employee_id'),
            day=day,
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            break_duration=data.get('break_duration', 0)
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        return jsonify(assignment.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al crear asignación: {e}")
        return jsonify({"error": f"Error al crear asignación: {str(e)}"}), 500

# API para actualizar una asignación
@horarios_bp.route('/api/assignments/<int:assignment_id>', methods=['PUT'])
@login_required
def update_assignment(assignment_id):
    """
    Actualiza una asignación existente.
    """
    if not current_user.is_admin and not current_user.is_gerente:
        abort(403)
    
    assignment = ScheduleAssignment.query.get_or_404(assignment_id)
    
    # Verificar permisos para la empresa
    schedule = Schedule.query.get_or_404(assignment.schedule_id)
    if not current_user.is_admin and not current_user.has_company_access(schedule.company_id):
        abort(403)
    
    data = request.json
    
    if not data:
        return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400
    
    try:
        # Actualizar campos
        if 'day' in data:
            assignment.day = datetime.strptime(data['day'], '%Y-%m-%d').date()
        
        if 'start_time' in data:
            assignment.start_time = data['start_time']
        
        if 'end_time' in data:
            assignment.end_time = data['end_time']
        
        if 'break_duration' in data:
            assignment.break_duration = data['break_duration']
        
        if 'employee_id' in data:
            # Verificar que el empleado pertenece a la empresa
            employee = Employee.query.get_or_404(data['employee_id'])
            if employee.company_id != schedule.company_id:
                return jsonify({"error": "El empleado no pertenece a la empresa del horario"}), 400
            assignment.employee_id = data['employee_id']
        
        db.session.commit()
        
        return jsonify(assignment.to_dict())
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al actualizar asignación: {e}")
        return jsonify({"error": f"Error al actualizar asignación: {str(e)}"}), 500

# API para eliminar una asignación
@horarios_bp.route('/api/assignments/<int:assignment_id>', methods=['DELETE'])
@login_required
def delete_assignment(assignment_id):
    """
    Elimina una asignación existente.
    """
    if not current_user.is_admin and not current_user.is_gerente:
        abort(403)
    
    assignment = ScheduleAssignment.query.get_or_404(assignment_id)
    
    # Verificar permisos para la empresa
    schedule = Schedule.query.get_or_404(assignment.schedule_id)
    if not current_user.is_admin and not current_user.has_company_access(schedule.company_id):
        abort(403)
    
    try:
        db.session.delete(assignment)
        db.session.commit()
        
        return jsonify({"message": "Asignación eliminada correctamente"}), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al eliminar asignación: {e}")
        return jsonify({"error": f"Error al eliminar asignación: {str(e)}"}), 500

# API para obtener empleados de una empresa
@horarios_bp.route('/api/companies/<int:company_id>/employees', methods=['GET'])
@login_required
def get_company_employees(company_id):
    """
    Obtiene todos los empleados activos de una empresa específica.
    """
    # Verificar permisos para la empresa
    if not current_user.is_admin and not current_user.has_company_access(company_id):
        abort(403)
    
    employees = Employee.query.filter_by(company_id=company_id, is_active=True).all()
    
    return jsonify([{
        'id': employee.id,
        'name': f"{employee.first_name} {employee.last_name}",
        'first_name': employee.first_name,
        'last_name': employee.last_name,
        'position': employee.position,  # Cambiado de role a position
        'email': employee.email,
        'phone': employee.phone
    } for employee in employees])

# API para obtener plantillas de horario
@horarios_bp.route('/api/templates', methods=['GET'])
@login_required
def get_templates():
    """
    Obtiene todas las plantillas de horario disponibles para una empresa.
    """
    company_id = request.args.get('company_id', type=int)
    if not company_id:
        return jsonify({"error": "Se requiere el ID de la empresa"}), 400
    
    # Verificar permisos para la empresa
    if not current_user.is_admin and not current_user.has_company_access(company_id):
        abort(403)
    
    templates = ScheduleTemplate.query.filter(
        (ScheduleTemplate.company_id == company_id) | 
        (ScheduleTemplate.is_default == True)
    ).all()
    
    return jsonify([template.to_dict() for template in templates])

# API para crear una plantilla de horario
@horarios_bp.route('/api/templates', methods=['POST'])
@login_required
def create_template():
    """
    Crea una nueva plantilla de horario.
    """
    if not current_user.is_admin and not current_user.is_gerente:
        abort(403)
    
    data = request.json
    
    if not data or not data.get('name') or not data.get('company_id'):
        return jsonify({"error": "Datos incompletos"}), 400
    
    # Verificar permisos para la empresa
    company_id = data.get('company_id')
    if not current_user.is_admin and not current_user.has_company_access(company_id):
        abort(403)
    
    try:
        template = ScheduleTemplate(
            name=data.get('name'),
            description=data.get('description', ''),
            is_default=data.get('is_default', False),
            start_hour=data.get('start_hour', 8),
            end_hour=data.get('end_hour', 20),
            time_increment=data.get('time_increment', 15),
            company_id=company_id,
            created_by=current_user.id
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify(template.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al crear plantilla: {e}")
        return jsonify({"error": f"Error al crear plantilla: {str(e)}"}), 500

# Ruta para visualizar un horario específico
@horarios_bp.route('/view/<int:schedule_id>')
@login_required
def view_schedule(schedule_id):
    """
    Renderiza la vista para un horario específico.
    """
    # Verificar permisos
    if not current_user.is_admin and not current_user.is_gerente:
        abort(403)  # Forbidden
    
    return render_template('horarios_index.html')

# API para disponibilidad de empleados
@horarios_bp.route('/api/employees/<int:employee_id>/availability', methods=['GET'])
@login_required
def get_employee_availability(employee_id):
    """
    Obtiene la disponibilidad para un empleado específico.
    """
    employee = Employee.query.get_or_404(employee_id)
    
    # Verificar permisos para la empresa
    if not current_user.is_admin and not current_user.has_company_access(employee.company_id):
        abort(403)
    
    availability = EmployeeAvailability.query.filter_by(employee_id=employee_id).all()
    
    return jsonify([av.to_dict() for av in availability])

# API para crear/actualizar disponibilidad de empleado
@horarios_bp.route('/api/employees/<int:employee_id>/availability', methods=['POST'])
@login_required
def set_employee_availability(employee_id):
    """
    Establece o actualiza la disponibilidad para un empleado específico.
    """
    if not current_user.is_admin and not current_user.is_gerente:
        abort(403)
    
    employee = Employee.query.get_or_404(employee_id)
    
    # Verificar permisos para la empresa
    if not current_user.is_admin and not current_user.has_company_access(employee.company_id):
        abort(403)
    
    data = request.json
    
    if not data or not isinstance(data, list):
        return jsonify({"error": "Se esperaba una lista de disponibilidades"}), 400
    
    try:
        # Eliminar disponibilidades existentes
        EmployeeAvailability.query.filter_by(employee_id=employee_id).delete()
        
        # Crear nuevas disponibilidades
        for item in data:
            if not all(k in item for k in ('day_of_week', 'start_time', 'end_time')):
                continue
            
            availability = EmployeeAvailability(
                employee_id=employee_id,
                day_of_week=item['day_of_week'],
                start_time=item['start_time'],
                end_time=item['end_time'],
                is_available=item.get('is_available', True),
                notes=item.get('notes', '')
            )
            
            db.session.add(availability)
        
        db.session.commit()
        
        # Obtener las nuevas disponibilidades
        availabilities = EmployeeAvailability.query.filter_by(employee_id=employee_id).all()
        
        return jsonify([av.to_dict() for av in availabilities]), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al establecer disponibilidad: {e}")
        return jsonify({"error": f"Error al establecer disponibilidad: {str(e)}"}), 500

# API para obtener reglas de horario
@horarios_bp.route('/api/companies/<int:company_id>/rules', methods=['GET'])
@login_required
def get_company_rules(company_id):
    """
    Obtiene las reglas de horario para una empresa específica.
    """
    # Verificar permisos para la empresa
    if not current_user.is_admin and not current_user.has_company_access(company_id):
        abort(403)
    
    rules = ScheduleRule.query.filter_by(company_id=company_id).all()
    
    return jsonify([rule.to_dict() for rule in rules])

# API para solicitudes de cambio de horario
@horarios_bp.route('/api/schedule-requests', methods=['GET'])
@login_required
def get_schedule_requests():
    """
    Obtiene solicitudes de cambio de horario para una empresa específica.
    """
    company_id = request.args.get('company_id', type=int)
    if not company_id:
        return jsonify({"error": "Se requiere el ID de la empresa"}), 400
    
    # Verificar permisos para la empresa
    if not current_user.is_admin and not current_user.has_company_access(company_id):
        abort(403)
    
    # Obtener empleados de la empresa
    employee_ids = [e.id for e in Employee.query.filter_by(company_id=company_id).all()]
    
    # Filtrar por empleado si se especifica
    employee_id = request.args.get('employee_id', type=int)
    if employee_id and employee_id in employee_ids:
        employee_ids = [employee_id]
    
    # Filtrar por estado si se especifica
    status = request.args.get('status')
    if status:
        requests = ScheduleRequest.query.filter(
            ScheduleRequest.employee_id.in_(employee_ids),
            ScheduleRequest.status == status
        ).order_by(ScheduleRequest.created_at.desc()).all()
    else:
        requests = ScheduleRequest.query.filter(
            ScheduleRequest.employee_id.in_(employee_ids)
        ).order_by(ScheduleRequest.created_at.desc()).all()
    
    return jsonify([req.to_dict() for req in requests])

# API para crear una solicitud de cambio de horario
@horarios_bp.route('/api/schedule-requests', methods=['POST'])
@login_required
def create_schedule_request():
    """
    Crea una nueva solicitud de cambio de horario.
    """
    data = request.json
    
    if not data or not data.get('employee_id') or not data.get('request_type') or not data.get('start_date'):
        return jsonify({"error": "Datos incompletos"}), 400
    
    employee_id = data.get('employee_id')
    
    # Si no es admin o gerente, solo puede crear solicitudes para sí mismo
    if not current_user.is_admin and not current_user.is_gerente:
        # Verificar si el empleado está asociado al usuario actual
        if not current_user.has_employee_access(employee_id):
            abort(403)
    
    employee = Employee.query.get_or_404(employee_id)
    
    # Si es gerente, verificar acceso a la empresa
    if current_user.is_gerente and not current_user.has_company_access(employee.company_id):
        abort(403)
    
    try:
        # Convertir fechas de string a objetos date
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
        end_date = None
        if data.get('end_date'):
            end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
        
        # Crear nueva solicitud
        request_obj = ScheduleRequest(
            employee_id=employee_id,
            assignment_id=data.get('assignment_id'),
            request_type=data.get('request_type'),
            start_date=start_date,
            end_date=end_date,
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            reason=data.get('reason', ''),
            status='pending'
        )
        
        db.session.add(request_obj)
        db.session.commit()
        
        return jsonify(request_obj.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al crear solicitud: {e}")
        return jsonify({"error": f"Error al crear solicitud: {str(e)}"}), 500

# API para responder a una solicitud de cambio de horario
@horarios_bp.route('/api/schedule-requests/<int:request_id>', methods=['PUT'])
@login_required
def update_schedule_request(request_id):
    """
    Actualiza el estado de una solicitud de cambio de horario.
    """
    if not current_user.is_admin and not current_user.is_gerente:
        abort(403)
    
    request_obj = ScheduleRequest.query.get_or_404(request_id)
    employee = Employee.query.get_or_404(request_obj.employee_id)
    
    # Verificar permisos para la empresa
    if not current_user.is_admin and not current_user.has_company_access(employee.company_id):
        abort(403)
    
    data = request.json
    
    if not data or 'status' not in data:
        return jsonify({"error": "Se requiere el estado de la solicitud"}), 400
    
    try:
        request_obj.status = data['status']
        request_obj.reviewed_by = current_user.id
        request_obj.reviewed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(request_obj.to_dict())
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al actualizar solicitud: {e}")
        return jsonify({"error": f"Error al actualizar solicitud: {str(e)}"}), 500

# Ruta para visualizar la lista de empleados con sus horarios
@horarios_bp.route('/employee-schedules')
@login_required
def employee_schedules():
    """
    Renderiza la vista para ver los horarios de los empleados.
    """
    # Verificar permisos
    if not current_user.is_admin and not current_user.is_gerente:
        abort(403)  # Forbidden
    
    return render_template('horarios_index.html')

# Ruta para exportar horario a PDF
@horarios_bp.route('/api/schedules/<int:schedule_id>/export', methods=['GET'])
@login_required
def export_schedule(schedule_id):
    """
    Exporta un horario a formato PDF.
    """
    # Verificar permisos
    if not current_user.is_admin and not current_user.is_gerente:
        abort(403)  # Forbidden
    
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Verificar permisos para la empresa
    if not current_user.is_admin and not current_user.has_company_access(schedule.company_id):
        abort(403)
    
    # Esta función se implementará posteriormente, por ahora devuelve un mensaje
    return jsonify({"message": "Funcionalidad de exportación en desarrollo"}), 501

# Ruta para copiar horario de una semana a otra
@horarios_bp.route('/api/schedules/<int:source_id>/copy', methods=['POST'])
@login_required
def copy_schedule(source_id):
    """
    Copia un horario existente a una nueva semana.
    """
    if not current_user.is_admin and not current_user.is_gerente:
        abort(403)
    
    source_schedule = Schedule.query.get_or_404(source_id)
    
    # Verificar permisos para la empresa
    if not current_user.is_admin and not current_user.has_company_access(source_schedule.company_id):
        abort(403)
    
    data = request.json
    
    if not data or not data.get('name') or not data.get('start_date'):
        return jsonify({"error": "Datos incompletos"}), 400
    
    try:
        # Convertir fechas de string a objetos date
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
        # Calcular end_date como start_date + duración del horario original
        days_diff = (source_schedule.end_date - source_schedule.start_date).days
        end_date = start_date + timedelta(days=days_diff)
        
        # Crear nuevo horario
        new_schedule = Schedule(
            name=data.get('name'),
            company_id=source_schedule.company_id,
            start_date=start_date,
            end_date=end_date,
            published=False
        )
        
        db.session.add(new_schedule)
        db.session.flush()  # Para obtener el ID del nuevo horario
        
        # Copiar asignaciones
        source_assignments = ScheduleAssignment.query.filter_by(schedule_id=source_id).all()
        
        for source_assignment in source_assignments:
            # Calcular el día correspondiente en el nuevo horario
            day_offset = (source_assignment.day - source_schedule.start_date).days
            new_day = start_date + timedelta(days=day_offset)
            
            new_assignment = ScheduleAssignment(
                schedule_id=new_schedule.id,
                employee_id=source_assignment.employee_id,
                day=new_day,
                start_time=source_assignment.start_time,
                end_time=source_assignment.end_time,
                break_duration=source_assignment.break_duration
            )
            
            db.session.add(new_assignment)
        
        db.session.commit()
        
        return jsonify(new_schedule.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al copiar horario: {e}")
        return jsonify({"error": f"Error al copiar horario: {str(e)}"}), 500