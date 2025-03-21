import os
import uuid
import io
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app, flash, request, send_file
from flask_login import current_user
from fpdf import FPDF

from app import db
from models import User, Employee, EmployeeHistory, UserRole, ActivityLog

def create_admin_user():
    """Create admin user if not exists."""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            role=UserRole.ADMIN,
            first_name='Admin',
            last_name='User',
            is_active=True
        )
        admin.set_password('admin12345')
        db.session.add(admin)
        db.session.commit()
        current_app.logger.info('Created admin user')

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file, description=None):
    """Save uploaded file to filesystem and return path."""
    if file and allowed_file(file.filename):
        # Get secure filename and add unique identifier
        original_filename = secure_filename(file.filename)
        file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}" if file_ext else f"{uuid.uuid4().hex}"
        
        # Create path for file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file to disk
        file.save(file_path)
        
        return {
            'filename': unique_filename,
            'original_filename': original_filename,
            'file_path': file_path,
            'file_type': file.content_type if hasattr(file, 'content_type') else None,
            'file_size': os.path.getsize(file_path),
            'description': description
        }
    return None

def log_employee_change(employee, field_name, old_value, new_value):
    """Log changes to employee data."""
    history = EmployeeHistory(
        employee_id=employee.id,
        field_name=field_name,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        changed_by_id=current_user.id if current_user.is_authenticated else None,
        changed_at=datetime.utcnow()
    )
    db.session.add(history)

def log_activity(action, user_id=None):
    """Log user activity."""
    log = ActivityLog(
        user_id=user_id or (current_user.id if current_user.is_authenticated else None),
        action=action,
        ip_address=request.remote_addr if 'request' in globals() else None,
        timestamp=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()

def can_manage_company(company_id):
    """Check if current user can manage the company."""
    if not current_user.is_authenticated:
        return False
    
    if current_user.is_admin():
        return True
        
    if current_user.is_gerente() and current_user.company_id == company_id:
        return True
        
    return False

def can_manage_employee(employee):
    """Check if current user can manage the employee."""
    if not current_user.is_authenticated:
        return False
    
    if current_user.is_admin():
        return True
        
    if current_user.is_gerente() and current_user.company_id == employee.company_id:
        return True
        
    if current_user.is_empleado() and current_user.id == employee.user_id:
        return True
        
    return False

def can_view_employee(employee):
    """Check if current user can view the employee."""
    if not current_user.is_authenticated:
        return False
    
    if current_user.is_admin():
        return True
        
    if current_user.is_gerente() and current_user.company_id == employee.company_id:
        return True
        
    if current_user.is_empleado() and current_user.id == employee.user_id:
        return True
        
    return False

def generate_checkins_pdf(employee, start_date=None, end_date=None):
    """Generate a PDF with employee check-ins between dates."""
    from models import EmployeeCheckIn
    import io
    from fpdf import FPDF
    from datetime import datetime
    
    # Get employee check-ins filtered by date if provided
    query = EmployeeCheckIn.query.filter_by(employee_id=employee.id)
    
    if start_date:
        query = query.filter(EmployeeCheckIn.check_in_time >= start_date)
    if end_date:
        query = query.filter(EmployeeCheckIn.check_in_time <= end_date)
    
    check_ins = query.order_by(EmployeeCheckIn.check_in_time).all()
    
    # Create PDF with direct BytesIO output
    pdf_buffer = io.BytesIO()
    
    try:
        # Create PDF
        class PDF(FPDF):
            def header(self):
                # Título centrado, con línea de separación
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, 'Registro de fichajes', 0, 1, 'C')
                
                # Información de empresa y empleado
                self.set_font('Arial', 'B', 11)
                self.cell(0, 8, f'Empresa: {employee.company.name}', 0, 1)
                self.set_font('Arial', '', 10)
                self.cell(0, 6, f'CIF: {employee.company.tax_id}', 0, 1)
                self.cell(0, 6, f'Dirección: {employee.company.address or ""}', 0, 1)
                self.cell(0, 6, f'CP: {employee.company.postal_code or ""}, Ciudad: {employee.company.city or ""}', 0, 1)
                
                self.ln(5)
                self.set_font('Arial', 'B', 11)
                self.cell(0, 8, f'Empleado: {employee.first_name} {employee.last_name}', 0, 1)
                self.set_font('Arial', '', 10)
                self.cell(0, 6, f'DNI: {employee.dni}', 0, 1)
                
                # Mostrar el número de la seguridad social (si existe)
                if hasattr(employee, 'social_security_number') and employee.social_security_number:
                    self.cell(0, 6, f'NSS: {employee.social_security_number}', 0, 1)
                
                self.ln(5)
                
                # Línea decorativa
                self.set_draw_color(100, 100, 100)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(10)
        
        # Inicializar PDF
        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Date range information
        date_range = ""
        if start_date and end_date:
            date_range = f"Periodo: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
        elif start_date:
            date_range = f"Desde: {start_date.strftime('%d/%m/%Y')}"
        elif end_date:
            date_range = f"Hasta: {end_date.strftime('%d/%m/%Y')}"
        
        if date_range:
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 6, date_range, 0, 1, 'C')
            pdf.ln(5)
        
        # Check-ins table header - More centrado y con mejor formato
        table_width = 160
        date_width = 50
        time_width = 55
        
        # Ajustar márgenes para centrar la tabla
        margin_left = (210 - table_width) / 2
        pdf.set_left_margin(margin_left)
        
        # Cabecera de tabla
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(date_width, 10, 'Fecha', 0, 0, 'C')
        pdf.cell(time_width, 10, 'Entrada', 0, 0, 'C')
        pdf.cell(time_width, 10, 'Salida', 0, 1, 'C')
        
        # Línea separadora debajo de la cabecera
        pdf.set_draw_color(100, 100, 100)
        pdf.line(margin_left, pdf.get_y(), margin_left + table_width, pdf.get_y())
        pdf.ln(2)
        
        # Check-ins data
        pdf.set_font('Arial', '', 10)
        
        # Ajustar para más entradas por página
        max_rows_per_page = 22
        row_count = 0
        
        for checkin in check_ins:
            # Add a new page if necessary
            if row_count >= max_rows_per_page:
                pdf.add_page()
                
                # Add header again on new page
                pdf.set_left_margin(margin_left)
                pdf.set_font('Arial', 'B', 11)
                pdf.cell(date_width, 10, 'Fecha', 0, 0, 'C')
                pdf.cell(time_width, 10, 'Entrada', 0, 0, 'C')
                pdf.cell(time_width, 10, 'Salida', 0, 1, 'C')
                
                # Línea separadora debajo de la cabecera
                pdf.set_draw_color(100, 100, 100)
                pdf.line(margin_left, pdf.get_y(), margin_left + table_width, pdf.get_y())
                pdf.ln(2)
                
                pdf.set_font('Arial', '', 10)
                row_count = 0
            
            # Format date and times
            date_str = checkin.check_in_time.strftime('%d-%m-%Y')
            check_in_str = checkin.check_in_time.strftime('%H:%M:%S')
            check_out_str = checkin.check_out_time.strftime('%H:%M:%S') if checkin.check_out_time else ''
            
            # Draw row 
            pdf.cell(date_width, 10, date_str, 0, 0, 'C')
            pdf.cell(time_width, 10, check_in_str, 0, 0, 'C')
            pdf.cell(time_width, 10, check_out_str, 0, 1, 'C')
            
            row_count += 1
        
        # Restaurar margen izquierdo
        pdf.set_left_margin(10)
        
        # Texto final y espacio para firma
        pdf.ln(15)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, 'Estos fichajes han sido comprobados por el empleado.', 0, 1)
        
        pdf.ln(20)
        pdf.cell(0, 6, 'Firma :', 0, 1)
        
        # Output PDF to BytesIO buffer
        pdf_output = pdf.output(dest='S').encode('latin1')
        pdf_buffer.write(pdf_output)
        pdf_buffer.seek(0)
        
        return pdf_buffer
    
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None


def get_dashboard_stats():
    """Get statistics for dashboard (optimizado)."""
    import time
    import logging
    from flask_login import current_user
    from app import db
    from models import Employee, ActivityLog, User, Company
    from sqlalchemy import func, case, text
    
    # Iniciar temporizador para medir rendimiento
    start_time = time.time()
    logger = logging.getLogger(__name__)
    
    # Initialize stats
    stats = {
        'total_companies': 0,
        'total_employees': 0,
        'active_employees': 0,
        'employees_by_contract': {},
        'employees_by_status': {},
        'recent_activities': []
    }
    
    try:
        if current_user.is_admin():
            # Optimización: obtener conteos en una sola consulta en lugar de múltiples
            # esto evita varios viajes a la base de datos
            stats['total_companies'] = db.session.query(func.count(Company.id)).scalar() or 0
            
            # Optimizar la consulta de empleados
            employee_counts = db.session.query(
                func.count(Employee.id).label('total'),
                func.sum(case((Employee.is_active == True, 1), else_=0)).label('active')
            ).first()
            
            stats['total_employees'] = employee_counts.total or 0 
            stats['active_employees'] = employee_counts.active or 0
            
            # Optimización: reducir el número de consultas para los tipos de contrato y estados
            contract_counts = db.session.query(
                Employee.contract_type, func.count(Employee.id)
            ).group_by(Employee.contract_type).all()
            
            status_counts = db.session.query(
                Employee.status, func.count(Employee.id)
            ).group_by(Employee.status).all()
            
            # Procesar resultados
            for contract_type, count in contract_counts:
                if contract_type:
                    stats['employees_by_contract'][contract_type.value] = count
            
            for status, count in status_counts:
                if status:
                    stats['employees_by_status'][status.value] = count
            
            # Optimización: reducir el límite para mejorar rendimiento
            stats['recent_activities'] = ActivityLog.query.order_by(
                ActivityLog.timestamp.desc()
            ).limit(5).all()
            
        elif current_user.is_gerente() and current_user.company_id:
            company_id = current_user.company_id
            
            # Optimización: realizar una sola consulta para contar empleados
            employee_counts = db.session.query(
                func.count(Employee.id).label('total'),
                func.sum(case((Employee.is_active == True, 1), else_=0)).label('active')
            ).filter(Employee.company_id == company_id).first()
            
            stats['total_employees'] = employee_counts.total or 0
            stats['active_employees'] = employee_counts.active or 0
            
            # Optimización: consultamos tipo contrato y estado en una única operación
            contract_counts = db.session.query(
                Employee.contract_type, func.count(Employee.id)
            ).filter(Employee.company_id == company_id).group_by(Employee.contract_type).all()
            
            status_counts = db.session.query(
                Employee.status, func.count(Employee.id)
            ).filter(Employee.company_id == company_id).group_by(Employee.status).all()
            
            for contract_type, count in contract_counts:
                if contract_type:
                    stats['employees_by_contract'][contract_type.value] = count
            
            for status, count in status_counts:
                if status:
                    stats['employees_by_status'][status.value] = count
            
            # Optimización: evitar subconsulta ineficiente usando JOIN
            # en lugar de obtener todos los user_ids y luego filtrar
            stats['recent_activities'] = db.session.query(ActivityLog).join(
                User, ActivityLog.user_id == User.id
            ).filter(
                User.company_id == company_id
            ).order_by(ActivityLog.timestamp.desc()).limit(5).all()
        
        elif current_user.is_empleado() and current_user.employee:
            # Optimización: para empleados, solo obtener sus propias actividades
            # y limitar a 5 en lugar de 10 para mayor velocidad
            stats['recent_activities'] = ActivityLog.query.filter_by(
                user_id=current_user.id
            ).order_by(ActivityLog.timestamp.desc()).limit(5).all()
    
    except Exception as e:
        logger.error(f"Error al obtener estadísticas del dashboard: {str(e)}")
    
    # Registrar tiempo de ejecución para diagnóstico
    elapsed = time.time() - start_time
    logger.info(f"Dashboard stats completado en {elapsed:.3f} segundos")
    
    return stats
