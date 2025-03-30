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

# La ruta '/company/<slug>/rrrrrr' ha sido eliminada
# def view_original_records(slug):
    """Página secreta para ver los registros originales antes de ajustes de una empresa específica - ELIMINADA"""
    # Esta función ha sido eliminada
    abort(404)

# La ruta '/company/<slug>/rrrrrr/edit/<int:id>' ha sido eliminada
# def edit_original_record(slug, id):
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

# La ruta '/company/<slug>/rrrrrr/restore/<int:id>' ha sido eliminada
# def restore_original_record(slug, id):
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

# La ruta '/company/<slug>/rrrrrr/delete/<int:id>' ha sido eliminada
# def delete_original_record(slug, id):
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

# La ruta '/company/<slug>/rrrrrr/export' ha sido eliminada
# def export_original_records(slug):
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
        Employee.company_id == company_id
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
    
    # Generar PDF
    return export_original_records_pdf(records, start_date, end_date, company)

# Esta función ha sido eliminada
# def export_original_records_pdf(records, start_date=None, end_date=None, company=None):
    """Genera un PDF con los registros originales"""
    from fpdf import FPDF
    from tempfile import NamedTemporaryFile
    import os
    
    # Crear un archivo temporal para guardar el PDF
    pdf_file = NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_file.close()
    
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
    
    current_employee = None
    total_hours_original = 0
    total_hours_adjusted = 0
    
    for original, record, employee in records:
        # Si cambia el empleado, agregar totales y reiniciar
        if current_employee and current_employee != employee.id:
            # Agregar fila de totales
            pdf.set_font('Arial', 'B', 8)
            pdf.cell(90, 7, f'Total horas originales: {total_hours_original:.2f}', 1, 0, 'R')
            pdf.cell(90, 7, f'Total horas ajustadas: {total_hours_adjusted:.2f}', 1, 1, 'R')
            pdf.ln(5)
            
            # Reiniciar totales
            total_hours_original = 0
            total_hours_adjusted = 0
            
            # Nueva página para cada empleado
            pdf.add_page()
            
        # Actualizar empleado actual
        current_employee = employee.id
        
        # Calcular horas trabajadas (original y ajustado)
        if original.original_check_out_time and original.original_check_in_time:
            hours_original = (original.original_check_out_time - original.original_check_in_time).total_seconds() / 3600
            total_hours_original += hours_original
        
        if record.check_out_time and record.check_in_time:
            hours_adjusted = (record.check_out_time - record.check_in_time).total_seconds() / 3600
            total_hours_adjusted += hours_adjusted
        
        # Formatear datos
        employee_name = f"{employee.first_name} {employee.last_name}"
        date_str = original.original_check_in_time.strftime('%d/%m/%Y')
        
        in_time_orig = original.original_check_in_time.strftime('%H:%M')
        out_time_orig = original.original_check_out_time.strftime('%H:%M') if original.original_check_out_time else '-'
        
        in_time_mod = record.check_in_time.strftime('%H:%M')
        out_time_mod = record.check_out_time.strftime('%H:%M') if record.check_out_time else '-'
        
        adjusted_by = original.adjusted_by.username if original.adjusted_by else 'Sistema'
        
        # Imprimir fila
        pdf.set_font('Arial', '', 8)
        pdf.cell(40, 7, employee_name, 1, 0, 'L')
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
    
    # Agregar totales del último empleado
    if current_employee:
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(90, 7, f'Total horas originales: {total_hours_original:.2f}', 1, 0, 'R')
        pdf.cell(90, 7, f'Total horas ajustadas: {total_hours_adjusted:.2f}', 1, 1, 'R')
    
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

# Resto del código ...