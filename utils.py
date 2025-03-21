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
        pdf = FPDF()
        pdf.add_page()
        
        # Set fonts
        pdf.set_font('Arial', 'B', 16)
        
        # Title
        pdf.cell(0, 10, 'Registro de fichajes', 0, 1, 'C')
        pdf.ln(5)
        
        # Date range information
        pdf.set_font('Arial', '', 10)
        date_range = ""
        if start_date and end_date:
            date_range = f"Periodo: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
        elif start_date:
            date_range = f"Desde: {start_date.strftime('%d/%m/%Y')}"
        elif end_date:
            date_range = f"Hasta: {end_date.strftime('%d/%m/%Y')}"
        
        if date_range:
            pdf.cell(0, 7, date_range, 0, 1, 'C')
            pdf.ln(3)
        
        # Company information
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f'Empresa: {employee.company.name}', 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 7, f'CIF: {employee.company.tax_id}', 0, 1)
        pdf.cell(0, 7, f'Dirección: {employee.company.address or ""}', 0, 1)
        pdf.cell(0, 7, f'CP: {employee.company.postal_code or ""}, Ciudad: {employee.company.city or ""}', 0, 1)
        pdf.ln(5)
        
        # Employee information
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f'Empleado: {employee.first_name} {employee.last_name}', 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 7, f'DNI: {employee.dni}', 0, 1)
        pdf.cell(0, 7, f'Posición: {employee.position or ""}', 0, 1)
        pdf.ln(10)
        
        # Check-ins table header
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(40, 10, 'Fecha', 1, 0, 'C')
        pdf.cell(30, 10, 'Entrada', 1, 0, 'C')
        pdf.cell(30, 10, 'Salida', 1, 0, 'C')
        pdf.cell(30, 10, 'Horas', 1, 0, 'C')
        pdf.cell(60, 10, 'Notas', 1, 1, 'C')
        
        # Check-ins data
        pdf.set_font('Arial', '', 10)
        total_hours = 0
        for checkin in check_ins:
            # Format date and times
            date_str = checkin.check_in_time.strftime('%d/%m/%Y')
            check_in_str = checkin.check_in_time.strftime('%H:%M')
            check_out_str = checkin.check_out_time.strftime('%H:%M') if checkin.check_out_time else '-'
            
            # Calculate hours
            hours = 0
            hours_str = '-'
            if checkin.check_out_time:
                hours = (checkin.check_out_time - checkin.check_in_time).total_seconds() / 3600
                hours_str = f"{hours:.2f}"
                total_hours += hours
            
            # Notes (truncated if too long)
            notes = checkin.notes if checkin.notes else ""
            if len(notes) > 25:
                notes = notes[:22] + "..."
            
            pdf.cell(40, 7, date_str, 1, 0, 'C')
            pdf.cell(30, 7, check_in_str, 1, 0, 'C')
            pdf.cell(30, 7, check_out_str, 1, 0, 'C')
            pdf.cell(30, 7, hours_str, 1, 0, 'C')
            pdf.cell(60, 7, notes, 1, 1, 'L')
        
        # Total hours
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(100, 7, 'Total Horas:', 1, 0, 'R')
        pdf.cell(30, 7, f"{total_hours:.2f}", 1, 0, 'C')
        pdf.cell(60, 7, '', 1, 1, 'L')
        
        pdf.ln(10)
        pdf.cell(0, 10, 'Estos fichajes han sido verificados y comprobados.', 0, 1)
        
        # Date and signature spaces
        pdf.ln(15)
        pdf.set_font('Arial', '', 10)
        current_date = datetime.now().strftime('%d/%m/%Y')
        pdf.cell(0, 7, f'Fecha: {current_date}', 0, 1)
        pdf.ln(10)
        
        pdf.cell(90, 7, 'Firma del empleado:', 0, 0)
        pdf.cell(90, 7, 'Firma del responsable:', 0, 1)
        pdf.ln(15)
        
        pdf.cell(90, 7, '_______________________', 0, 0)
        pdf.cell(90, 7, '_______________________', 0, 1)
        
        # Output PDF to BytesIO buffer
        pdf_output = pdf.output(dest='S').encode('latin1')
        pdf_buffer.write(pdf_output)
        pdf_buffer.seek(0)
        
        return pdf_buffer
    
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None


def get_dashboard_stats():
    """Get statistics for dashboard."""
    stats = {
        'total_companies': 0,
        'total_employees': 0,
        'active_employees': 0,
        'employees_by_contract': {},
        'employees_by_status': {},
        'recent_activities': []
    }
    
    # Get company stats
    if current_user.is_admin():
        from models import Company
        stats['total_companies'] = Company.query.count()
        stats['total_employees'] = Employee.query.count()
        stats['active_employees'] = Employee.query.filter_by(is_active=True).count()
        
        # Count employees by contract type
        from sqlalchemy import func
        contract_counts = db.session.query(
            Employee.contract_type, func.count(Employee.id)
        ).group_by(Employee.contract_type).all()
        
        for contract_type, count in contract_counts:
            if contract_type:
                stats['employees_by_contract'][contract_type.value] = count
        
        # Count employees by status
        status_counts = db.session.query(
            Employee.status, func.count(Employee.id)
        ).group_by(Employee.status).all()
        
        for status, count in status_counts:
            if status:
                stats['employees_by_status'][status.value] = count
        
        # Get recent activities
        stats['recent_activities'] = ActivityLog.query.order_by(
            ActivityLog.timestamp.desc()
        ).limit(10).all()
    
    elif current_user.is_gerente() and current_user.company_id:
        stats['total_employees'] = Employee.query.filter_by(company_id=current_user.company_id).count()
        stats['active_employees'] = Employee.query.filter_by(
            company_id=current_user.company_id, is_active=True
        ).count()
        
        # Count employees by contract type for this company
        from sqlalchemy import func
        contract_counts = db.session.query(
            Employee.contract_type, func.count(Employee.id)
        ).filter_by(company_id=current_user.company_id).group_by(Employee.contract_type).all()
        
        for contract_type, count in contract_counts:
            if contract_type:
                stats['employees_by_contract'][contract_type.value] = count
        
        # Count employees by status for this company
        status_counts = db.session.query(
            Employee.status, func.count(Employee.id)
        ).filter_by(company_id=current_user.company_id).group_by(Employee.status).all()
        
        for status, count in status_counts:
            if status:
                stats['employees_by_status'][status.value] = count
        
        # Get recent activities for this company
        company_user_ids = [user.id for user in User.query.filter_by(company_id=current_user.company_id).all()]
        stats['recent_activities'] = ActivityLog.query.filter(
            ActivityLog.user_id.in_(company_user_ids)
        ).order_by(ActivityLog.timestamp.desc()).limit(10).all()
    
    elif current_user.is_empleado() and current_user.employee:
        # For empleado, just get their own activities
        stats['recent_activities'] = ActivityLog.query.filter_by(
            user_id=current_user.id
        ).order_by(ActivityLog.timestamp.desc()).limit(10).all()
    
    return stats
