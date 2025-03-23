import os
import json
from datetime import datetime, date, time, timedelta
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask import current_app, abort, send_file
from flask_login import login_required, current_user
from sqlalchemy import extract, func
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from app import db
from models import User, Employee, Company, UserRole
from models_checkpoints import CheckPoint, CheckPointRecord, CheckPointIncident, EmployeeContractHours
from models_checkpoints import CheckPointStatus, CheckPointIncidentType
from forms_checkpoints import (CheckPointForm, CheckPointLoginForm, CheckPointEmployeePinForm, 
                             ContractHoursForm, CheckPointRecordAdjustmentForm,
                             SignaturePadForm, ExportCheckPointRecordsForm)
from utils import log_activity
from utils_checkpoints import generate_pdf_report, draw_signature


# Crear un Blueprint para las rutas de checkpoints
checkpoints_bp = Blueprint('checkpoints', __name__, url_prefix='/fichajes')


# Decoradores personalizados
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (
            current_user.role != UserRole.ADMIN and 
            current_user.role != UserRole.GERENTE
        ):
            flash('Acceso denegado. Se requieren permisos de gerente o administrador.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def checkpoint_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'checkpoint_id' not in session:
            flash('Debe iniciar sesión como punto de fichaje.', 'warning')
            return redirect(url_for('checkpoints.login'))
        return f(*args, **kwargs)
    return decorated_function


# Rutas para administración de checkpoints
@checkpoints_bp.route('/')
@login_required
def select_company():
    """Página de selección de empresa para el sistema de fichajes"""
    # Obtener empresas según los permisos del usuario
    if current_user.is_admin():
        companies = Company.query.filter_by(is_active=True).all()
    else:
        companies = current_user.companies
    
    # Si solo hay una empresa o el usuario solo gestiona una, redirigir directamente
    if len(companies) == 1:
        return redirect(url_for('checkpoints.index_company', company_id=companies[0].id))
    
    return render_template('checkpoints/select_company.html', companies=companies)

@checkpoints_bp.route('/company/<int:company_id>')
@login_required
def index_company(company_id):
    """Página principal del sistema de fichajes para una empresa específica"""
    # Verificar permiso para acceder a esta empresa
    company = Company.query.get_or_404(company_id)
    
    if not current_user.is_admin() and company not in current_user.companies:
        flash('No tiene permiso para gestionar esta empresa.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Guardar la empresa seleccionada en la sesión
    session['selected_company_id'] = company_id
    
    # Obtener estadísticas para el dashboard filtradas por la empresa
    stats = {
        'active_checkpoints': CheckPoint.query.filter_by(status=CheckPointStatus.ACTIVE, company_id=company_id).count(),
        'maintenance_checkpoints': CheckPoint.query.filter_by(status=CheckPointStatus.MAINTENANCE, company_id=company_id).count(),
        'disabled_checkpoints': CheckPoint.query.filter_by(status=CheckPointStatus.DISABLED, company_id=company_id).count(),
        'employees_with_hours': db.session.query(EmployeeContractHours)
            .join(Employee, EmployeeContractHours.employee_id == Employee.id)
            .filter(Employee.company_id == company_id).count(),
        'employees_with_overtime': db.session.query(EmployeeContractHours)
            .join(Employee, EmployeeContractHours.employee_id == Employee.id)
            .filter(Employee.company_id == company_id, EmployeeContractHours.allow_overtime == True).count(),
        'today_records': db.session.query(CheckPointRecord)
            .join(CheckPoint, CheckPointRecord.checkpoint_id == CheckPoint.id)
            .filter(
                CheckPoint.company_id == company_id,
                CheckPointRecord.check_in_time >= datetime.combine(date.today(), time.min)
            ).count(),
        'pending_checkout': db.session.query(CheckPointRecord)
            .join(CheckPoint, CheckPointRecord.checkpoint_id == CheckPoint.id)
            .filter(
                CheckPoint.company_id == company_id,
                CheckPointRecord.check_out_time.is_(None)
            ).count(),
        'active_incidents': db.session.query(CheckPointIncident)
            .join(CheckPointRecord, CheckPointIncident.record_id == CheckPointRecord.id)
            .join(CheckPoint, CheckPointRecord.checkpoint_id == CheckPoint.id)
            .filter(
                CheckPoint.company_id == company_id,
                CheckPointIncident.resolved == False
            ).count()
    }
    
    # Obtener los últimos registros filtrados por empresa
    latest_records = db.session.query(CheckPointRecord).\
        join(CheckPoint, CheckPointRecord.checkpoint_id == CheckPoint.id).\
        filter(CheckPoint.company_id == company_id).\
        order_by(CheckPointRecord.check_in_time.desc()).\
        limit(10).all()
    
    # Obtener las últimas incidencias filtradas por empresa
    latest_incidents = db.session.query(CheckPointIncident).\
        join(CheckPointRecord, CheckPointIncident.record_id == CheckPointRecord.id).\
        join(CheckPoint, CheckPointRecord.checkpoint_id == CheckPoint.id).\
        filter(CheckPoint.company_id == company_id).\
        order_by(CheckPointIncident.created_at.desc()).\
        limit(10).all()
    
    return render_template('checkpoints/index.html', 
                          stats=stats, 
                          latest_records=latest_records,
                          latest_incidents=latest_incidents,
                          company=company)


@checkpoints_bp.route('/checkpoints')
@login_required
@manager_required
def list_checkpoints():
    """Lista todos los puntos de fichaje disponibles"""
    # Verificar si hay una empresa seleccionada
    company_id = session.get('selected_company_id')
    if not company_id:
        return redirect(url_for('checkpoints.select_company'))
    
    # Verificar permiso para acceder a esta empresa
    company = Company.query.get_or_404(company_id)
    if not current_user.is_admin() and company not in current_user.companies:
        flash('No tiene permiso para gestionar esta empresa.', 'danger')
        return redirect(url_for('checkpoints.select_company'))
    
    # Filtrar por la empresa seleccionada
    checkpoints = CheckPoint.query.filter_by(company_id=company_id).all()
    
    return render_template('checkpoints/list_checkpoints.html', checkpoints=checkpoints, company=company)


@checkpoints_bp.route('/checkpoints/new', methods=['GET', 'POST'])
@login_required
@manager_required
def create_checkpoint():
    """Crea un nuevo punto de fichaje"""
    # Verificar si hay una empresa seleccionada
    company_id = session.get('selected_company_id')
    if not company_id:
        return redirect(url_for('checkpoints.select_company'))
    
    # Verificar permiso para acceder a esta empresa
    company = Company.query.get_or_404(company_id)
    if not current_user.is_admin() and company not in current_user.companies:
        flash('No tiene permiso para gestionar esta empresa.', 'danger')
        return redirect(url_for('checkpoints.select_company'))
    
    form = CheckPointForm()
    
    # Cargar las empresas disponibles para el usuario actual pero preseleccionar la empresa actual
    if current_user.is_admin():
        companies = Company.query.filter_by(is_active=True).all()
    else:
        companies = current_user.companies
        
    form.company_id.choices = [(c.id, c.name) for c in companies]
    
    # Si es GET, preseleccionamos la empresa de la sesión
    if request.method == 'GET':
        form.company_id.data = company_id
    
    if form.validate_on_submit():
        # Convertir el string del status a un objeto de enumeración
        status_value = form.status.data
        status_enum = CheckPointStatus.ACTIVE  # Default
        for status in CheckPointStatus:
            if status.value == status_value:
                status_enum = status
                break
                
        checkpoint = CheckPoint(
            name=form.name.data,
            description=form.description.data,
            location=form.location.data,
            status=status_enum,
            username=form.username.data,
            company_id=form.company_id.data,
            auto_checkout_time=form.auto_checkout_time.data,
            enforce_contract_hours=form.enforce_contract_hours.data,
            auto_adjust_overtime=form.auto_adjust_overtime.data
        )
        
        if form.password.data:
            checkpoint.set_password(form.password.data)
        
        db.session.add(checkpoint)
        
        try:
            db.session.commit()
            flash(f'Punto de fichaje "{checkpoint.name}" creado con éxito.', 'success')
            return redirect(url_for('checkpoints.list_checkpoints'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el punto de fichaje: {str(e)}', 'danger')
    
    return render_template('checkpoints/checkpoint_form.html', form=form, title='Nuevo Punto de Fichaje', company=company)


@checkpoints_bp.route('/checkpoints/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_checkpoint(id):
    """Edita un punto de fichaje existente"""
    checkpoint = CheckPoint.query.get_or_404(id)
    
    # Verificar permiso (solo admin o gerente de la empresa)
    if not current_user.is_admin() and checkpoint.company_id not in [c.id for c in current_user.companies]:
        flash('No tiene permiso para editar este punto de fichaje.', 'danger')
        return redirect(url_for('checkpoints.list_checkpoints'))
    
    form = CheckPointForm(obj=checkpoint)
    
    # Cargar las empresas disponibles para el usuario actual
    if current_user.is_admin():
        companies = Company.query.filter_by(is_active=True).all()
    else:
        companies = current_user.companies
        
    form.company_id.choices = [(c.id, c.name) for c in companies]
    
    if form.validate_on_submit():
        # Convertir el string del status a un objeto de enumeración
        status_value = form.status.data
        status_enum = CheckPointStatus.ACTIVE  # Default
        for status in CheckPointStatus:
            if status.value == status_value:
                status_enum = status
                break
                
        checkpoint.name = form.name.data
        checkpoint.description = form.description.data
        checkpoint.location = form.location.data
        checkpoint.status = status_enum
        checkpoint.username = form.username.data
        checkpoint.company_id = form.company_id.data
        checkpoint.auto_checkout_time = form.auto_checkout_time.data
        checkpoint.enforce_contract_hours = form.enforce_contract_hours.data
        checkpoint.auto_adjust_overtime = form.auto_adjust_overtime.data
        
        if form.password.data:
            checkpoint.set_password(form.password.data)
        
        try:
            db.session.commit()
            flash(f'Punto de fichaje "{checkpoint.name}" actualizado con éxito.', 'success')
            return redirect(url_for('checkpoints.list_checkpoints'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el punto de fichaje: {str(e)}', 'danger')
    
    return render_template('checkpoints/checkpoint_form.html', form=form, checkpoint=checkpoint, 
                          title='Editar Punto de Fichaje')


@checkpoints_bp.route('/checkpoints/<int:id>/delete', methods=['POST'])
@login_required
@manager_required
def delete_checkpoint(id):
    """Elimina un punto de fichaje"""
    checkpoint = CheckPoint.query.get_or_404(id)
    
    # Verificar permiso (solo admin o gerente de la empresa)
    if not current_user.is_admin() and checkpoint.company_id not in [c.id for c in current_user.companies]:
        flash('No tiene permiso para eliminar este punto de fichaje.', 'danger')
        return redirect(url_for('checkpoints.list_checkpoints'))
    
    try:
        db.session.delete(checkpoint)
        db.session.commit()
        flash(f'Punto de fichaje "{checkpoint.name}" eliminado con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el punto de fichaje: {str(e)}', 'danger')
    
    return redirect(url_for('checkpoints.list_checkpoints'))


@checkpoints_bp.route('/checkpoints/<int:id>/records')
@login_required
@manager_required
def list_checkpoint_records(id):
    """Muestra los registros de fichaje de un punto específico"""
    checkpoint = CheckPoint.query.get_or_404(id)
    
    # Verificar permiso (solo admin o gerente de la empresa)
    if not current_user.is_admin() and checkpoint.company_id not in [c.id for c in current_user.companies]:
        flash('No tiene permiso para ver los registros de este punto de fichaje.', 'danger')
        return redirect(url_for('checkpoints.list_checkpoints'))
    
    page = request.args.get('page', 1, type=int)
    records = CheckPointRecord.query.filter_by(checkpoint_id=id).order_by(
        CheckPointRecord.check_in_time.desc()
    ).paginate(page=page, per_page=20)
    
    return render_template('checkpoints/list_records.html', 
                          checkpoint=checkpoint, 
                          records=records)


@checkpoints_bp.route('/employees/<int:id>/contract_hours', methods=['GET', 'POST'])
@login_required
@manager_required
def manage_contract_hours(id):
    """Gestiona la configuración de horas por contrato de un empleado"""
    employee = Employee.query.get_or_404(id)
    
    # Verificar permiso (solo admin o gerente de la empresa)
    if not current_user.is_admin() and employee.company_id not in [c.id for c in current_user.companies]:
        flash('No tiene permiso para gestionar las horas de contrato de este empleado.', 'danger')
        return redirect(url_for('list_employees'))
    
    # Buscar o crear configuración de horas de contrato
    contract_hours = EmployeeContractHours.query.filter_by(employee_id=employee.id).first()
    
    if not contract_hours:
        contract_hours = EmployeeContractHours(employee_id=employee.id)
        db.session.add(contract_hours)
        db.session.commit()
    
    form = ContractHoursForm(obj=contract_hours)
    
    if form.validate_on_submit():
        form.populate_obj(contract_hours)
        
        try:
            db.session.commit()
            flash('Configuración de horas de contrato actualizada con éxito.', 'success')
            return redirect(url_for('view_employee', id=employee.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la configuración: {str(e)}', 'danger')
    
    return render_template('checkpoints/contract_hours_form.html', 
                          form=form, 
                          employee=employee)


@checkpoints_bp.route('/records/<int:id>/adjust', methods=['GET', 'POST'])
@login_required
@manager_required
def adjust_record(id):
    """Ajusta manualmente un registro de fichaje"""
    record = CheckPointRecord.query.get_or_404(id)
    
    # Verificar permiso
    employee_company_id = record.employee.company_id
    if not current_user.is_admin() and employee_company_id not in [c.id for c in current_user.companies]:
        flash('No tiene permiso para ajustar este registro de fichaje.', 'danger')
        return redirect(url_for('checkpoints.list_checkpoints'))
    
    form = CheckPointRecordAdjustmentForm()
    
    # Pre-llenar el formulario con los datos actuales
    if request.method == 'GET':
        form.check_in_date.data = record.check_in_time.strftime('%Y-%m-%d')
        form.check_in_time.data = record.check_in_time.time()
        if record.check_out_time:
            form.check_out_time.data = record.check_out_time.time()
    
    if form.validate_on_submit():
        # Guardar los valores originales si es la primera vez que se ajusta
        if not record.adjusted:
            record.original_check_in_time = record.check_in_time
            record.original_check_out_time = record.check_out_time
        
        # Actualizar con los nuevos valores
        check_in_date = datetime.strptime(form.check_in_date.data, '%Y-%m-%d').date()
        
        # Combinar fecha y hora para check_in_time
        record.check_in_time = datetime.combine(check_in_date, form.check_in_time.data)
        
        # Combinar fecha y hora para check_out_time si está presente
        if form.check_out_time.data:
            # Si la hora de salida es menor que la de entrada, asumimos que es del día siguiente
            if form.check_out_time.data < form.check_in_time.data:
                check_out_date = check_in_date + timedelta(days=1)
            else:
                check_out_date = check_in_date
                
            record.check_out_time = datetime.combine(check_out_date, form.check_out_time.data)
        
        record.adjusted = True
        record.adjustment_reason = form.adjustment_reason.data
        
        # Si se debe aplicar el límite de horas de contrato
        if form.enforce_contract_hours.data and record.check_out_time:
            contract_hours = EmployeeContractHours.query.filter_by(employee_id=record.employee_id).first()
            
            if contract_hours:
                # Ajustar el fichaje según las horas de contrato
                new_check_in, new_check_out = contract_hours.calculate_adjusted_hours(
                    record.check_in_time, record.check_out_time
                )
                
                if new_check_in and new_check_in != record.check_in_time:
                    record.check_in_time = new_check_in
                    
                    # Crear incidencia por ajuste de contrato
                    incident = CheckPointIncident(
                        record_id=record.id,
                        incident_type=CheckPointIncidentType.CONTRACT_HOURS_ADJUSTMENT,
                        description=f"Fichaje ajustado automáticamente para cumplir con el límite de {contract_hours.daily_hours} horas diarias."
                    )
                    db.session.add(incident)
        
        try:
            db.session.commit()
            flash('Registro de fichaje ajustado con éxito.', 'success')
            return redirect(url_for('checkpoints.list_checkpoint_records', id=record.checkpoint_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al ajustar el registro: {str(e)}', 'danger')
    
    return render_template('checkpoints/adjust_record_form.html', 
                          form=form, 
                          record=record)


@checkpoints_bp.route('/records/<int:id>/signature', methods=['GET', 'POST'])
@login_required
def record_signature(id):
    """Permite al empleado firmar un registro de fichaje"""
    record = CheckPointRecord.query.get_or_404(id)
    
    # Solo el empleado o un administrador pueden firmar
    is_admin_or_manager = current_user.is_admin() or current_user.is_gerente()
    is_employee_user = current_user.employee and current_user.employee.id == record.employee_id
    
    if not is_admin_or_manager and not is_employee_user:
        flash('No tiene permiso para firmar este registro.', 'danger')
        return redirect(url_for('index'))
    
    form = SignaturePadForm()
    
    if form.validate_on_submit():
        record.signature_data = form.signature_data.data
        record.has_signature = True
        
        try:
            db.session.commit()
            flash('Firma guardada con éxito.', 'success')
            
            # Redireccionar según el tipo de usuario
            if is_admin_or_manager:
                return redirect(url_for('checkpoints.list_checkpoint_records', id=record.checkpoint_id))
            else:
                return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar la firma: {str(e)}', 'danger')
    
    return render_template('checkpoints/signature_pad.html', 
                          form=form, 
                          record=record)


@checkpoints_bp.route('/records')
@login_required
@manager_required
def list_records_all():
    """Muestra todos los registros de fichaje disponibles según permisos"""
    # Determinar los registros a los que tiene acceso el usuario
    if current_user.is_admin():
        base_query = CheckPointRecord.query
    else:
        # Si es gerente, solo registros de las empresas que administra
        company_ids = [company.id for company in current_user.companies]
        
        if not company_ids:
            flash('No tiene empresas asignadas para gestionar registros.', 'warning')
            return redirect(url_for('dashboard'))
        
        # Buscar empleados de esas empresas
        employee_ids = db.session.query(Employee.id).filter(
            Employee.company_id.in_(company_ids)
        ).all()
        employee_ids = [e[0] for e in employee_ids]
        
        if not employee_ids:
            flash('No hay empleados registrados en sus empresas.', 'warning')
            return redirect(url_for('dashboard'))
        
        base_query = CheckPointRecord.query.filter(
            CheckPointRecord.employee_id.in_(employee_ids)
        )
    
    # Filtros adicionales (fecha, empleado, etc.)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    employee_id = request.args.get('employee_id', type=int)
    status = request.args.get('status')
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            base_query = base_query.filter(
                func.date(CheckPointRecord.check_in_time) >= start_date
            )
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            base_query = base_query.filter(
                func.date(CheckPointRecord.check_in_time) <= end_date
            )
        except ValueError:
            pass
    
    if employee_id:
        base_query = base_query.filter(CheckPointRecord.employee_id == employee_id)
    
    if status:
        if status == 'pending':
            base_query = base_query.filter(CheckPointRecord.check_out_time.is_(None))
        elif status == 'completed':
            base_query = base_query.filter(CheckPointRecord.check_out_time.isnot(None))
        elif status == 'adjusted':
            base_query = base_query.filter(CheckPointRecord.adjusted == True)
        elif status == 'incidents':
            # Registros con incidencias (requiere una subconsulta)
            incident_record_ids = db.session.query(CheckPointIncident.record_id).distinct().subquery()
            base_query = base_query.filter(CheckPointRecord.id.in_(incident_record_ids))
    
    # Ordenar y paginar
    page = request.args.get('page', 1, type=int)
    records = base_query.order_by(CheckPointRecord.check_in_time.desc()).paginate(
        page=page, per_page=20
    )
    
    # Datos adicionales para el filtro
    if current_user.is_admin():
        filter_employees = Employee.query.filter_by(is_active=True).all()
    else:
        company_ids = [company.id for company in current_user.companies]
        filter_employees = Employee.query.filter(
            Employee.company_id.in_(company_ids),
            Employee.is_active == True
        ).all()
    
    return render_template(
        'checkpoints/all_records.html',
        records=records,
        filter_employees=filter_employees,
        current_filters={
            'start_date': start_date.strftime('%Y-%m-%d') if isinstance(start_date, date) else None,
            'end_date': end_date.strftime('%Y-%m-%d') if isinstance(end_date, date) else None,
            'employee_id': employee_id,
            'status': status
        }
    )


@checkpoints_bp.route('/incidents')
@login_required
@manager_required
def list_incidents():
    """Muestra todas las incidencias de fichaje según permisos"""
    # Determinar las incidencias a las que tiene acceso el usuario
    if current_user.is_admin():
        base_query = CheckPointIncident.query.join(
            CheckPointRecord, CheckPointIncident.record_id == CheckPointRecord.id
        )
    else:
        # Si es gerente, solo incidencias de las empresas que administra
        company_ids = [company.id for company in current_user.companies]
        
        if not company_ids:
            flash('No tiene empresas asignadas para gestionar incidencias.', 'warning')
            return redirect(url_for('dashboard'))
        
        # Buscar empleados de esas empresas
        employee_ids = db.session.query(Employee.id).filter(
            Employee.company_id.in_(company_ids)
        ).all()
        employee_ids = [e[0] for e in employee_ids]
        
        if not employee_ids:
            flash('No hay empleados registrados en sus empresas.', 'warning')
            return redirect(url_for('dashboard'))
        
        base_query = CheckPointIncident.query.join(
            CheckPointRecord, CheckPointIncident.record_id == CheckPointRecord.id
        ).filter(
            CheckPointRecord.employee_id.in_(employee_ids)
        )
    
    # Filtros adicionales
    incident_type = request.args.get('type')
    resolved = request.args.get('resolved')
    employee_id = request.args.get('employee_id', type=int)
    
    if incident_type:
        base_query = base_query.filter(CheckPointIncident.incident_type == incident_type)
    
    if resolved == 'yes':
        base_query = base_query.filter(CheckPointIncident.resolved == True)
    elif resolved == 'no':
        base_query = base_query.filter(CheckPointIncident.resolved == False)
    
    if employee_id:
        base_query = base_query.filter(CheckPointRecord.employee_id == employee_id)
    
    # Ordenar y paginar
    page = request.args.get('page', 1, type=int)
    incidents = base_query.order_by(CheckPointIncident.created_at.desc()).paginate(
        page=page, per_page=20
    )
    
    # Datos adicionales para el filtro
    if current_user.is_admin():
        filter_employees = Employee.query.filter_by(is_active=True).all()
    else:
        company_ids = [company.id for company in current_user.companies]
        filter_employees = Employee.query.filter(
            Employee.company_id.in_(company_ids),
            Employee.is_active == True
        ).all()
    
    return render_template(
        'checkpoints/incidents.html',
        incidents=incidents,
        filter_employees=filter_employees,
        incident_types=CheckPointIncidentType,
        current_filters={
            'type': incident_type,
            'resolved': resolved,
            'employee_id': employee_id
        }
    )


@checkpoints_bp.route('/incidents/<int:id>/resolve', methods=['POST'])
@login_required
@manager_required
def resolve_incident(id):
    """Marca una incidencia como resuelta"""
    incident = CheckPointIncident.query.get_or_404(id)
    
    # Verificar permisos
    record = incident.record
    employee_company_id = record.employee.company_id
    
    if not current_user.is_admin() and employee_company_id not in [c.id for c in current_user.companies]:
        flash('No tiene permiso para resolver esta incidencia.', 'danger')
        return redirect(url_for('checkpoints.list_incidents'))
    
    # Obtener las notas de resolución
    resolution_notes = request.form.get('resolution_notes', '')
    
    # Resolver la incidencia
    incident.resolve(current_user.id, resolution_notes)
    
    try:
        db.session.commit()
        flash('Incidencia marcada como resuelta con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al resolver la incidencia: {str(e)}', 'danger')
    
    # Redirigir a la página anterior o a la lista de incidencias
    next_page = request.args.get('next') or url_for('checkpoints.list_incidents')
    return redirect(next_page)


@checkpoints_bp.route('/records/export', methods=['GET', 'POST'])
@login_required
@manager_required
def export_records():
    """Exporta registros de fichaje a PDF"""
    form = ExportCheckPointRecordsForm()
    
    # Cargar empleados según los permisos del usuario
    if current_user.is_admin():
        employees = Employee.query.filter_by(is_active=True).all()
    else:
        company_ids = [company.id for company in current_user.companies]
        employees = Employee.query.filter(
            Employee.company_id.in_(company_ids), 
            Employee.is_active == True
        ).all()
    
    form.employee_id.choices = [(0, 'Todos los empleados')] + [(e.id, f"{e.first_name} {e.last_name}") for e in employees]
    
    if form.validate_on_submit():
        try:
            # Parsear fechas
            start_date = datetime.strptime(form.start_date.data, '%Y-%m-%d').date()
            end_date = datetime.strptime(form.end_date.data, '%Y-%m-%d').date()
            
            # Construir consulta
            query = CheckPointRecord.query.filter(
                func.date(CheckPointRecord.check_in_time) >= start_date,
                func.date(CheckPointRecord.check_in_time) <= end_date
            )
            
            # Filtrar por empleado si se especifica
            if form.employee_id.data != 0:
                query = query.filter(CheckPointRecord.employee_id == form.employee_id.data)
            
            # Ejecutar consulta
            records = query.order_by(
                CheckPointRecord.employee_id,
                CheckPointRecord.check_in_time
            ).all()
            
            if not records:
                flash('No se encontraron registros para el período seleccionado.', 'warning')
                return redirect(url_for('checkpoints.export_records'))
            
            # Generar PDF
            pdf_file = generate_pdf_report(
                records=records, 
                start_date=start_date, 
                end_date=end_date,
                include_signature=form.include_signature.data
            )
            
            # Guardar temporalmente y enviar
            filename = f"fichajes_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
            return send_file(
                pdf_file,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
            
        except Exception as e:
            flash(f'Error al generar el informe: {str(e)}', 'danger')
    
    # Establecer fechas predeterminadas si es la primera carga
    if request.method == 'GET':
        today = date.today()
        # Por defecto, mostrar el mes actual
        form.start_date.data = date(today.year, today.month, 1).strftime('%Y-%m-%d')
        form.end_date.data = today.strftime('%Y-%m-%d')
    
    return render_template('checkpoints/export_form.html', form=form)


# Rutas para puntos de fichaje (interfaz tablet/móvil)
@checkpoints_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login para puntos de fichaje"""
    # Si ya hay una sesión activa, redirigir al dashboard
    if 'checkpoint_id' in session:
        return redirect(url_for('checkpoints.checkpoint_dashboard'))
    
    form = CheckPointLoginForm()
    
    if form.validate_on_submit():
        checkpoint = CheckPoint.query.filter_by(username=form.username.data).first()
        
        if checkpoint and checkpoint.verify_password(form.password.data):
            if checkpoint.status == CheckPointStatus.ACTIVE:
                # Guardar ID del punto de fichaje en la sesión
                session['checkpoint_id'] = checkpoint.id
                session['checkpoint_name'] = checkpoint.name
                session['company_id'] = checkpoint.company_id
                
                flash(f'Bienvenido al punto de fichaje {checkpoint.name}', 'success')
                return redirect(url_for('checkpoints.checkpoint_dashboard'))
            else:
                flash('Este punto de fichaje está desactivado o en mantenimiento.', 'warning')
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    
    return render_template('checkpoints/login.html', form=form)


@checkpoints_bp.route('/logout')
def logout():
    """Cierra la sesión del punto de fichaje"""
    # Limpiar variables de sesión
    session.pop('checkpoint_id', None)
    session.pop('checkpoint_name', None)
    session.pop('company_id', None)
    session.pop('employee_id', None)
    
    flash('Ha cerrado sesión correctamente.', 'success')
    return redirect(url_for('checkpoints.login'))


@checkpoints_bp.route('/dashboard')
@checkpoint_required
def checkpoint_dashboard():
    """Dashboard principal del punto de fichaje"""
    checkpoint_id = session.get('checkpoint_id')
    checkpoint = CheckPoint.query.get_or_404(checkpoint_id)
    
    # Obtener todos los empleados de la empresa asociada al punto de fichaje
    employees = Employee.query.filter_by(
        company_id=checkpoint.company_id,
        is_active=True
    ).order_by(Employee.first_name, Employee.last_name).all()
    
    # Obtener registros recientes de este punto de fichaje
    recent_records = CheckPointRecord.query.filter_by(
        checkpoint_id=checkpoint_id
    ).order_by(CheckPointRecord.check_in_time.desc()).limit(5).all()
    
    return render_template('checkpoints/dashboard.html', 
                          checkpoint=checkpoint,
                          employees=employees,
                          recent_records=recent_records)


@checkpoints_bp.route('/employee/<int:id>/pin', methods=['GET', 'POST'])
@checkpoint_required
def employee_pin(id):
    """Página para introducir el PIN del empleado"""
    checkpoint_id = session.get('checkpoint_id')
    checkpoint = CheckPoint.query.get_or_404(checkpoint_id)
    
    employee = Employee.query.get_or_404(id)
    
    # Verificar que el empleado pertenece a la empresa del punto de fichaje
    if employee.company_id != checkpoint.company_id:
        flash('Empleado no válido para este punto de fichaje.', 'danger')
        return redirect(url_for('checkpoints.checkpoint_dashboard'))
    
    form = CheckPointEmployeePinForm()
    
    # Comprobar si hay un registro de entrada sin salida para mostrar el botón correspondiente
    pending_record = CheckPointRecord.query.filter_by(
        employee_id=employee.id,
        checkpoint_id=checkpoint_id,
        check_out_time=None
    ).first()
    
    if form.validate_on_submit():
        # Aquí comprobaríamos el PIN del empleado
        # Como aún no tenemos PINs implementados, hacemos una verificación sencilla
        # En un escenario real, habría que comparar con un hash almacenado
        
        # Por ahora, asumimos que el PIN es los últimos 4 dígitos del DNI
        pin_from_dni = employee.dni[-4:] if len(employee.dni) >= 4 else employee.dni
        
        if form.pin.data == pin_from_dni:
            # Guardar el ID del empleado en la sesión
            session['employee_id'] = employee.id
            
            # Obtener la acción del formulario (checkin o checkout)
            action = request.form.get('action')
            
            # Comprobar si hay un registro de entrada sin salida
            pending_record = CheckPointRecord.query.filter_by(
                employee_id=employee.id,
                checkpoint_id=checkpoint_id,
                check_out_time=None
            ).first()
            
            if action == 'checkout' and pending_record:
                # Registrar salida
                pending_record.check_out_time = datetime.now()
                
                # Cambiar el estado de jornada del empleado a 0 (No en jornada)
                employee.is_on_shift = False
                
                db.session.commit()
                
                flash(f'Salida registrada para {employee.first_name} {employee.last_name}', 'success')
                return redirect(url_for('checkpoints.record_details', id=pending_record.id))
            elif action == 'checkin' and not pending_record:
                # Registrar entrada
                new_record = CheckPointRecord(
                    employee_id=employee.id,
                    checkpoint_id=checkpoint_id,
                    check_in_time=datetime.now()
                )
                db.session.add(new_record)
                
                # Cambiar el estado de jornada del empleado a 1 (En jornada)
                employee.is_on_shift = True
                
                db.session.commit()
                
                flash(f'Entrada registrada para {employee.first_name} {employee.last_name}', 'success')
                return redirect(url_for('checkpoints.record_details', id=new_record.id))
            else:
                # Si la acción no es válida o no coincide con el estado actual
                if pending_record and action == 'checkin':
                    flash('El empleado ya tiene una entrada activa sin salida registrada.', 'warning')
                elif not pending_record and action == 'checkout':
                    flash('El empleado no tiene ninguna entrada activa para registrar salida.', 'warning')
                else:
                    flash('Acción no válida.', 'danger')
        else:
            flash('PIN incorrecto. Inténtelo de nuevo.', 'danger')
    
    return render_template('checkpoints/employee_pin.html', 
                          form=form,
                          employee=employee,
                          pending_record=pending_record,
                          checkpoint=checkpoint)


@checkpoints_bp.route('/record/<int:id>')
@checkpoint_required
def record_details(id):
    """Muestra los detalles de un registro recién creado"""
    record = CheckPointRecord.query.get_or_404(id)
    
    # Verificar que el registro pertenece al punto de fichaje actual
    checkpoint_id = session.get('checkpoint_id')
    if record.checkpoint_id != checkpoint_id:
        flash('Registro no válido para este punto de fichaje.', 'danger')
        return redirect(url_for('checkpoints.checkpoint_dashboard'))
    
    # Obtener el checkpoint para la plantilla
    checkpoint = CheckPoint.query.get_or_404(checkpoint_id)
    
    return render_template('checkpoints/record_details.html', record=record, checkpoint=checkpoint)


@checkpoints_bp.route('/daily-report')
@checkpoint_required
def daily_report():
    """Muestra un informe de fichajes del día actual"""
    checkpoint_id = session.get('checkpoint_id')
    checkpoint = CheckPoint.query.get_or_404(checkpoint_id)
    
    # Obtener fecha actual
    today = date.today()
    
    # Obtener todos los registros del día para este punto de fichaje
    records = CheckPointRecord.query.filter(
        CheckPointRecord.checkpoint_id == checkpoint_id,
        func.date(CheckPointRecord.check_in_time) == today
    ).order_by(CheckPointRecord.check_in_time).all()
    
    return render_template('checkpoints/daily_report.html', 
                         checkpoint=checkpoint,
                         records=records,
                         today=today)


@checkpoints_bp.route('/company-employees')
@checkpoint_required
def company_employees():
    """Devuelve la lista de empleados de la empresa en formato JSON"""
    company_id = session.get('company_id')
    
    if not company_id:
        return jsonify([])
    
    employees = Employee.query.filter_by(
        company_id=company_id,
        is_active=True
    ).order_by(Employee.first_name, Employee.last_name).all()
    
    employees_data = []
    for employee in employees:
        # Verificar si el empleado tiene un fichaje pendiente (sin check_out)
        pending_record = CheckPointRecord.query.filter_by(
            employee_id=employee.id,
            checkpoint_id=session.get('checkpoint_id'),
            check_out_time=None
        ).first()
        
        employees_data.append({
            'id': employee.id,
            'name': f"{employee.first_name} {employee.last_name}",
            'position': employee.position,
            'has_pending_record': pending_record is not None,
            'is_on_shift': employee.is_on_shift,
            'dni_last_digits': employee.dni[-4:] if len(employee.dni) >= 4 else employee.dni
        })
    
    return jsonify(employees_data)


# Integrar el blueprint en la aplicación principal
def init_app(app):
    app.register_blueprint(checkpoints_bp)