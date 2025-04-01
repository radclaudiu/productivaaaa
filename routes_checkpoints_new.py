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
from utils import log_activity, slugify
from utils_checkpoints import generate_pdf_report, draw_signature


# Crear un Blueprint para las rutas de checkpoints con nombres slugificados
checkpoints_bp = Blueprint('checkpoints_slug', __name__, url_prefix='/fichajes')


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
            return redirect(url_for('checkpoints_slug.login'))
        return f(*args, **kwargs)
    return decorated_function

# Resto del código...

@checkpoints_bp.route('/company/<slug>/rrrrrr', methods=['GET'])
@login_required
@admin_required
def view_original_records(slug):
    """Página secreta para ver los registros originales antes de ajustes de una empresa específica"""
    from models_checkpoints import CheckPointOriginalRecord
    
    # Buscar la empresa por slug
    companies = Company.query.all()
    company = None
    company_id = None
    
    for comp in companies:
        if slugify(comp.name) == slug:
            company = comp
            company_id = comp.id
            break
    
    if not company:
        abort(404)
    
    # Esta página es solo para administradores
    page = request.args.get('page', 1, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    employee_id = request.args.get('employee_id', type=int)
    show_all = request.args.get('show_all', 'false')
    
    # Obtener los IDs de los empleados de esta empresa
    employee_ids = db.session.query(Employee.id).filter_by(company_id=company_id).all()
    employee_ids = [e[0] for e in employee_ids]
    
    # Construir la consulta base con filtro de empresa
    query = db.session.query(
        CheckPointOriginalRecord, 
        CheckPointRecord, 
        Employee
    ).join(
        CheckPointRecord, 
        CheckPointOriginalRecord.record_id == CheckPointRecord.id
    ).join(
        Employee,
        CheckPointRecord.employee_id == Employee.id
    ).filter(
        Employee.company_id == company_id
    )
    
    # Filtrar solo registros completos (con hora de salida)
    query = query.filter(CheckPointOriginalRecord.original_check_out_time.isnot(None))
    
    # Aplicar filtros si los hay
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(func.date(CheckPointOriginalRecord.original_check_in_time) >= start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(func.date(CheckPointOriginalRecord.original_check_in_time) <= end_date)
        except ValueError:
            pass
    
    if employee_id:
        query = query.filter(Employee.id == employee_id)
    
    # Ejecutar la consulta y obtener todos los resultados
    all_records = query.order_by(
        CheckPointOriginalRecord.adjusted_at.desc()
    ).all()
    
    # Filtrar registros duplicados (mismo empleado, misma fecha) manteniendo solo los completos
    filtered_records = []
    seen_records = set()  # Para rastrear combinaciones empleado-fecha ya procesadas
    
    for original, record, employee in all_records:
        # Crear una clave única para identificar registros del mismo empleado en el mismo día
        record_date = original.original_check_in_time.date()
        record_key = (employee.id, record_date)
        
        # Solo incluir cada combinación empleado-fecha una vez
        # Y asegurar que tenga hora de salida completa
        if record_key not in seen_records and original.original_check_out_time is not None:
            filtered_records.append((original, record, employee))
            seen_records.add(record_key)
    
    # Paginar los resultados filtrados manualmente
    total_records = len(filtered_records)
    per_page = 20
    total_pages = (total_records + per_page - 1) // per_page  # Redondear hacia arriba
    
    # Validar número de página
    if page < 1:
        page = 1
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # Calcular índices de inicio y fin para la página actual
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_records)
    
    # Obtener los registros para la página actual
    page_records = filtered_records[start_idx:end_idx] if filtered_records else []
    
    # Crear un objeto similar a la paginación de SQLAlchemy para usar en la plantilla
    class Pagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            
        @property
        def pages(self):
            return (self.total + self.per_page - 1) // self.per_page
            
        @property
        def has_prev(self):
            return self.page > 1
            
        @property
        def has_next(self):
            return self.page < self.pages
            
        @property
        def prev_num(self):
            return self.page - 1 if self.has_prev else None
            
        @property
        def next_num(self):
            return self.page + 1 if self.has_next else None
    
    # Crear objeto de paginación
    paginated_records = Pagination(page_records, page, per_page, total_records)
    
    # Obtener la lista de empleados para el filtro (solo de esta empresa)
    employees = Employee.query.filter_by(company_id=company_id, is_active=True).order_by(Employee.first_name).all()
    
    # Si se solicita exportación
    export_format = request.args.get('export')
    if export_format == 'pdf':
        return export_original_records_pdf(filtered_records, start_date, end_date, company)
    
    return render_template(
        'checkpoints/original_records.html',
        original_records=paginated_records,
        employees=employees,
        company=company,
        company_id=company_id,
        filters={
            'start_date': start_date.strftime('%Y-%m-%d') if isinstance(start_date, date) else None,
            'end_date': end_date.strftime('%Y-%m-%d') if isinstance(end_date, date) else None,
            'employee_id': employee_id
        },
        show_all=show_all,
        title=f"Registros Originales de {company.name if company else ''} (Antes de Ajustes)"
    )

@checkpoints_bp.route('/company/<slug>/rrrrrr/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_original_record(slug, id):
    """Edita un registro original"""
    from models_checkpoints import CheckPointOriginalRecord
    from flask_wtf import FlaskForm
    from wtforms import StringField, TimeField, TextAreaField, SubmitField
    from wtforms.validators import DataRequired, Optional, Length
    
    # Buscar la empresa por slug
    companies = Company.query.all()
    company = None
    company_id = None
    
    for comp in companies:
        if slugify(comp.name) == slug:
            company = comp
            company_id = comp.id
            break
    
    if not company:
        abort(404)
    
    # Obtener el registro original
    original_record = CheckPointOriginalRecord.query.get_or_404(id)
    record = CheckPointRecord.query.get_or_404(original_record.record_id)
    
    # Verificar que el registro pertenece a esta empresa
    if record.employee.company_id != company_id:
        flash('Registro no encontrado para esta empresa.', 'warning')
        return redirect(url_for('checkpoints_slug.view_original_records', slug=slug))
    
    # Crear un formulario para editar el registro
    class EditOriginalRecordForm(FlaskForm):
        original_check_in_date = StringField('Fecha de entrada original', validators=[DataRequired()])
        original_check_in_time = TimeField('Hora de entrada original', validators=[DataRequired()])
        original_check_out_time = TimeField('Hora de salida original', validators=[Optional()])
        notes = TextAreaField('Notas', validators=[Optional(), Length(max=500)])
        submit = SubmitField('Guardar cambios')
    
    form = EditOriginalRecordForm()
    
    # Pre-llenar el formulario con los datos actuales
    if request.method == 'GET':
        form.original_check_in_date.data = original_record.original_check_in_time.strftime('%Y-%m-%d')
        form.original_check_in_time.data = original_record.original_check_in_time.time()
        if original_record.original_check_out_time:
            form.original_check_out_time.data = original_record.original_check_out_time.time()
        form.notes.data = original_record.original_notes
    
    # Procesar el formulario
    if form.validate_on_submit():
        try:
            # Obtener fecha y hora de entrada
            check_in_date = datetime.strptime(form.original_check_in_date.data, '%Y-%m-%d').date()
            original_record.original_check_in_time = datetime.combine(check_in_date, form.original_check_in_time.data)
            
            # Obtener hora de salida si está presente
            if form.original_check_out_time.data:
                # Si la hora de salida es menor que la de entrada, asumimos que es del día siguiente
                if form.original_check_out_time.data < form.original_check_in_time.data:
                    check_out_date = check_in_date + timedelta(days=1)
                else:
                    check_out_date = check_in_date
                    
                original_record.original_check_out_time = datetime.combine(check_out_date, form.original_check_out_time.data)
            else:
                original_record.original_check_out_time = None
            
            # Actualizar notas
            original_record.original_notes = form.notes.data
            
            # Guardar cambios
            db.session.commit()
            flash('Registro original actualizado con éxito.', 'success')
            return redirect(url_for('checkpoints_slug.view_original_records', slug=slug))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el registro: {str(e)}', 'danger')
    
    return render_template('checkpoints/edit_original_record.html', 
                          form=form, 
                          original_record=original_record,
                          record=record,
                          company=company,
                          company_id=company_id)

@checkpoints_bp.route('/company/<slug>/rrrrrr/restore/<int:id>', methods=['GET'])
@login_required
@admin_required
def restore_original_record(slug, id):
    """Restaura los valores originales en el registro actual"""
    from models_checkpoints import CheckPointOriginalRecord
    
    # Buscar la empresa por slug
    companies = Company.query.all()
    company = None
    company_id = None
    
    for comp in companies:
        if slugify(comp.name) == slug:
            company = comp
            company_id = comp.id
            break
    
    if not company:
        abort(404)
    
    # Obtener el registro original y el registro actual
    original_record = CheckPointOriginalRecord.query.get_or_404(id)
    record = CheckPointRecord.query.get_or_404(original_record.record_id)
    
    # Verificar que el registro pertenece a esta empresa
    if record.employee.company_id != company_id:
        flash('Registro no encontrado para esta empresa.', 'warning')
        return redirect(url_for('checkpoints_slug.view_original_records', slug=slug))
    
    try:
        # Restaurar valores originales
        record.check_in_time = original_record.original_check_in_time
        record.check_out_time = original_record.original_check_out_time
        record.signature_data = original_record.original_signature_data
        record.has_signature = original_record.original_has_signature
        record.notes = original_record.original_notes
        
        # Actualizar razón de ajuste
        record.adjustment_reason = "Restaurado a valores originales"
        
        # Guardar cambios
        db.session.commit()
        flash('Registro restaurado a valores originales con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al restaurar el registro: {str(e)}', 'danger')
    
    return redirect(url_for('checkpoints_slug.view_original_records', slug=slug))

@checkpoints_bp.route('/company/<slug>/rrrrrr/delete/<int:id>', methods=['GET'])
@login_required
@admin_required
def delete_original_record(slug, id):
    """Elimina un registro original"""
    from models_checkpoints import CheckPointOriginalRecord
    
    # Buscar la empresa por slug
    companies = Company.query.all()
    company = None
    company_id = None
    
    for comp in companies:
        if slugify(comp.name) == slug:
            company = comp
            company_id = comp.id
            break
    
    if not company:
        abort(404)
    
    # Obtener el registro original
    original_record = CheckPointOriginalRecord.query.get_or_404(id)
    record = CheckPointRecord.query.get_or_404(original_record.record_id)
    
    # Verificar que el registro pertenece a esta empresa
    if record.employee.company_id != company_id:
        flash('Registro no encontrado para esta empresa.', 'warning')
        return redirect(url_for('checkpoints_slug.view_original_records', slug=slug))
    
    try:
        # Eliminar el registro
        db.session.delete(original_record)
        db.session.commit()
        flash('Registro original eliminado con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el registro: {str(e)}', 'danger')
    
    return redirect(url_for('checkpoints_slug.view_original_records', slug=slug))

@checkpoints_bp.route('/company/<slug>/rrrrrr/export', methods=['GET'])
@login_required
@admin_required
def export_original_records(slug):
    """Exporta los registros originales a PDF"""
    from models_checkpoints import CheckPointOriginalRecord
    
    # Buscar la empresa por slug
    companies = Company.query.all()
    company = None
    company_id = None
    
    for comp in companies:
        if slugify(comp.name) == slug:
            company = comp
            company_id = comp.id
            break
    
    if not company:
        abort(404)
    
    # Obtener parámetros de filtro
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    employee_id = request.args.get('employee_id', type=int)
    
    # Construir la consulta con filtro de empresa
    query = db.session.query(
        CheckPointOriginalRecord, 
        CheckPointRecord, 
        Employee
    ).join(
        CheckPointRecord, 
        CheckPointOriginalRecord.record_id == CheckPointRecord.id
    ).join(
        Employee,
        CheckPointRecord.employee_id == Employee.id
    ).filter(
        Employee.company_id == company_id,
        # Filtrar solo registros completos (con hora de entrada y salida)
        CheckPointRecord.check_out_time.isnot(None),
        CheckPointOriginalRecord.original_check_out_time.isnot(None)
    )
    
    # Aplicar filtros
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(func.date(CheckPointOriginalRecord.original_check_in_time) >= start_date)
        except ValueError:
            start_date = None
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(func.date(CheckPointOriginalRecord.original_check_in_time) <= end_date)
        except ValueError:
            end_date = None
    
    if employee_id:
        query = query.filter(Employee.id == employee_id)
    
    # Ordenar por empleado y fecha
    records = query.order_by(
        Employee.last_name,
        Employee.first_name,
        CheckPointOriginalRecord.original_check_in_time
    ).all()
    
    if not records:
        flash('No se encontraron registros para los filtros seleccionados', 'warning')
        return redirect(url_for('checkpoints_slug.view_original_records', slug=slug))
    
    # Filtrar registros duplicados (mismo empleado, misma fecha, mismo periodo)
    # Esto elimina casos en los que un registro puede aparecer como parcial y completo
    filtered_records = []
    seen_records = set()  # Para rastrear registros ya procesados
    
    for original, record, employee in records:
        # Crear una clave única para identificar registros duplicados
        record_key = (
            employee.id,
            original.original_check_in_time.strftime('%Y-%m-%d'),
            original.original_check_in_time.strftime('%H:%M'),
            original.original_check_out_time.strftime('%H:%M') if original.original_check_out_time else None
        )
        
        # Solo incluir registros que no hemos visto antes
        if record_key not in seen_records:
            filtered_records.append((original, record, employee))
            seen_records.add(record_key)
    
    if not filtered_records:
        flash('No se encontraron registros completos para los filtros seleccionados', 'warning')
        return redirect(url_for('checkpoints_slug.view_original_records', slug=slug))
    
    # Generar PDF con los registros filtrados
    return export_original_records_pdf(filtered_records, start_date, end_date, company)

def export_original_records_pdf(records, start_date=None, end_date=None, company=None):
    """Genera un PDF con los registros originales agrupados por semanas (lunes a domingo)"""
    from fpdf import FPDF
    from tempfile import NamedTemporaryFile
    import os
    from datetime import datetime, timedelta
    
    # Crear un archivo temporal para guardar el PDF
    pdf_file = NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_file.close()
    
    # Función auxiliar para obtener el lunes de la semana de una fecha
    def get_week_start(date_obj):
        """Retorna la fecha del lunes de la semana a la que pertenece date_obj"""
        # weekday() retorna 0 para lunes, 6 para domingo
        days_to_subtract = date_obj.weekday()
        return date_obj - timedelta(days=days_to_subtract)
    
    # Función auxiliar para obtener el domingo de la semana de una fecha
    def get_week_end(date_obj):
        """Retorna la fecha del domingo de la semana a la que pertenece date_obj"""
        # weekday() retorna 0 para lunes, 6 para domingo
        days_to_add = 6 - date_obj.weekday()
        return date_obj + timedelta(days=days_to_add)
    
    # Crear un PDF personalizado
    class OriginalRecordsPDF(FPDF):
        def header(self):
            # Logo y título
            self.set_font('Arial', 'B', 15)
            title = 'Registro de Ajustes de Fichajes'
            if company:
                title = f'Registro de Ajustes de Fichajes - {company.name}'
            self.cell(0, 10, title, 0, 1, 'C')
            
            # Período
            if start_date and end_date:
                period = f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
            elif start_date:
                period = f"Desde {start_date.strftime('%d/%m/%Y')}"
            elif end_date:
                period = f"Hasta {end_date.strftime('%d/%m/%Y')}"
            else:
                period = "Todos los registros"
                
            self.set_font('Arial', '', 10)
            self.cell(0, 10, f'Período: {period}', 0, 1, 'C')
            
            # Encabezados de la tabla
            self.set_fill_color(200, 220, 255)
            self.set_font('Arial', 'B', 8)
            self.cell(40, 7, 'Empleado', 1, 0, 'C', True)
            self.cell(20, 7, 'Fecha', 1, 0, 'C', True)
            self.cell(15, 7, 'Ent. Orig.', 1, 0, 'C', True)
            self.cell(15, 7, 'Sal. Orig.', 1, 0, 'C', True)
            self.cell(15, 7, 'Ent. Mod.', 1, 0, 'C', True)
            self.cell(15, 7, 'Sal. Mod.', 1, 0, 'C', True)
            self.cell(20, 7, 'Ajustado Por', 1, 0, 'C', True)
            self.cell(50, 7, 'Motivo', 1, 1, 'C', True)
            
        def footer(self):
            # Posición a 1.5 cm del final
            self.set_y(-15)
            # Número de página
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')
    
    # Crear PDF
    pdf = OriginalRecordsPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Llenar el PDF con los datos
    pdf.set_font('Arial', '', 8)
    
    # Ordenar registros por empleado, fecha y hora
    sorted_records = sorted(records, key=lambda x: (
        x[2].id,  # employee.id
        x[0].original_check_in_time.date(),  # date
        x[0].original_check_in_time.time()  # time
    ))
    
    # Preparar diccionarios para acumular totales por empleado y semana
    current_employee = None
    current_week_start = None
    week_hours_original = 0
    week_hours_adjusted = 0
    total_hours_original = 0
    total_hours_adjusted = 0
    
    # Estructurar registros por empleado
    employee_records = {}
    for original, record, employee in sorted_records:
        if employee.id not in employee_records:
            employee_records[employee.id] = {
                'employee': employee,
                'weeks': {}
            }
        
        # Obtener fecha de inicio de la semana (lunes)
        week_start = get_week_start(original.original_check_in_time.date())
        week_end = get_week_end(original.original_check_in_time.date())
        week_key = week_start.strftime('%Y-%m-%d')
        
        if week_key not in employee_records[employee.id]['weeks']:
            employee_records[employee.id]['weeks'][week_key] = {
                'start_date': week_start,
                'end_date': week_end,
                'records': [],
                'original_hours': 0,
                'adjusted_hours': 0
            }
        
        # Calcular horas trabajadas
        hours_original = 0
        if original.original_check_out_time and original.original_check_in_time:
            hours_original = (original.original_check_out_time - original.original_check_in_time).total_seconds() / 3600
            employee_records[employee.id]['weeks'][week_key]['original_hours'] += hours_original
        
        hours_adjusted = 0
        if record.check_out_time and record.check_in_time:
            hours_adjusted = (record.check_out_time - record.check_in_time).total_seconds() / 3600
            employee_records[employee.id]['weeks'][week_key]['adjusted_hours'] += hours_adjusted
            
        # Guardar registro
        employee_records[employee.id]['weeks'][week_key]['records'].append((original, record, hours_original, hours_adjusted))
    
    # Generar PDF con los datos estructurados
    for emp_id, emp_data in employee_records.items():
        employee = emp_data['employee']
        employee_name = f"{employee.first_name} {employee.last_name}"
        
        # Imprimir nombre del empleado como encabezado
        pdf.set_font('Arial', 'B', 12)
        pdf.ln(5)
        pdf.cell(0, 10, f"Empleado: {employee_name}", 0, 1, 'L')
        pdf.set_font('Arial', '', 8)
        
        employee_total_original = 0
        employee_total_adjusted = 0
        
        # Procesar cada semana del empleado
        for week_key in sorted(emp_data['weeks'].keys()):
            week_data = emp_data['weeks'][week_key]
            
            # Imprimir encabezado de la semana
            week_header = f"Semana: {week_data['start_date'].strftime('%d/%m/%Y')} - {week_data['end_date'].strftime('%d/%m/%Y')}"
            pdf.set_font('Arial', 'B', 10)
            pdf.ln(3)
            pdf.cell(0, 7, week_header, 0, 1, 'L')
            pdf.set_font('Arial', '', 8)
            
            # Imprimir registros de la semana
            for original, record, hours_original, hours_adjusted in week_data['records']:
                date_str = original.original_check_in_time.strftime('%d/%m/%Y')
                
                in_time_orig = original.original_check_in_time.strftime('%H:%M')
                out_time_orig = original.original_check_out_time.strftime('%H:%M') if original.original_check_out_time else '-'
                
                in_time_mod = record.check_in_time.strftime('%H:%M')
                out_time_mod = record.check_out_time.strftime('%H:%M') if record.check_out_time else '-'
                
                adjusted_by = original.adjusted_by.username if original.adjusted_by else 'Sistema'
                
                # Imprimir fila
                pdf.cell(40, 7, "", 1, 0, 'L')  # Columna vacía para el empleado (ya está en el encabezado)
                pdf.cell(20, 7, date_str, 1, 0, 'C')
                pdf.cell(15, 7, in_time_orig, 1, 0, 'C')
                pdf.cell(15, 7, out_time_orig, 1, 0, 'C')
                pdf.cell(15, 7, in_time_mod, 1, 0, 'C')
                pdf.cell(15, 7, out_time_mod, 1, 0, 'C')
                pdf.cell(20, 7, adjusted_by, 1, 0, 'C')
                
                # Ajustar motivo para que quepa en una fila
                motivo = original.adjustment_reason
                if motivo and len(motivo) > 30:
                    motivo = motivo[:27] + '...'
                pdf.cell(50, 7, motivo or '', 1, 1, 'L')
            
            # Imprimir totales de la semana
            pdf.set_font('Arial', 'B', 8)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(90, 7, f'Total semana (horas originales): {week_data["original_hours"]:.2f}', 1, 0, 'R', True)
            pdf.cell(90, 7, f'Total semana (horas ajustadas): {week_data["adjusted_hours"]:.2f}', 1, 1, 'R', True)
            pdf.ln(5)
            
            # Acumular totales del empleado
            employee_total_original += week_data['original_hours']
            employee_total_adjusted += week_data['adjusted_hours']
        
        # Imprimir totales del empleado
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(90, 8, f'TOTAL EMPLEADO (horas originales): {employee_total_original:.2f}', 1, 0, 'R', True)
        pdf.cell(90, 8, f'TOTAL EMPLEADO (horas ajustadas): {employee_total_adjusted:.2f}', 1, 1, 'R', True)
        
        # Nueva página para cada empleado, excepto el último
        if list(employee_records.keys()).index(emp_id) < len(employee_records) - 1:
            pdf.add_page()
    
    # Guardar PDF
    pdf.output(pdf_file.name)
    
    # Enviar el archivo
    filename = f"registros_originales.pdf"
    return send_file(
        pdf_file.name,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

# Ruta para acceder directamente a un checkpoint específico por ID
@checkpoints_bp.route('/login/<int:checkpoint_id>', methods=['GET', 'POST'])
def login_to_checkpoint(checkpoint_id):
    """Acceso directo a un punto de fichaje específico por ID"""
    # Si ya hay una sesión activa, redirigir al dashboard
    if 'checkpoint_id' in session:
        return redirect(url_for('checkpoints_slug.checkpoint_dashboard'))
    
    # Buscar el checkpoint por ID
    checkpoint = CheckPoint.query.get_or_404(checkpoint_id)
    
    # Si el checkpoint no está activo, mostrar error
    if not checkpoint.is_active:
        flash('El punto de fichaje no está activo.', 'danger')
        return redirect(url_for('checkpoints_slug.select_company'))
    
    # Crear el formulario
    form = CheckPointLoginForm()
    
    # Procesar el formulario si es una solicitud POST y es válido
    if form.validate_on_submit():
        # Guardar la información del checkpoint en la sesión
        session['checkpoint_id'] = checkpoint.id
        session['company_id'] = checkpoint.company_id
        
        # Redirigir al formulario de ingreso de PIN
        return redirect(url_for('checkpoints_slug.employee_pin'))
    
    return render_template('checkpoints/login.html', form=form, checkpoint=checkpoint)

# Resto del código ...