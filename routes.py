import os
from datetime import datetime
from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

from app import db
from models import (User, Company, Employee, EmployeeDocument, EmployeeNote, UserRole, 
                   ContractType, EmployeeStatus, EmployeeSchedule, EmployeeCheckIn, 
                   EmployeeVacation, VacationStatus, WeekDay)
from forms import (LoginForm, RegistrationForm, UserUpdateForm, PasswordChangeForm, 
                  CompanyForm, EmployeeForm, EmployeeDocumentForm, EmployeeNoteForm, SearchForm,
                  EmployeeStatusForm, EmployeeScheduleForm, EmployeeCheckInForm, EmployeeVacationForm,
                  EmployeeVacationApprovalForm, GenerateCheckInsForm)
from utils import (save_file, log_employee_change, log_activity, can_manage_company, 
                  can_manage_employee, can_view_employee, get_dashboard_stats)

# Create blueprints
auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)
company_bp = Blueprint('company', __name__, url_prefix='/companies')
employee_bp = Blueprint('employee', __name__, url_prefix='/employees')
user_bp = Blueprint('user', __name__, url_prefix='/users')
schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedules')
checkin_bp = Blueprint('checkin', __name__, url_prefix='/checkins')
vacation_bp = Blueprint('vacation', __name__, url_prefix='/vacations')

# Decorator for admin-only routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator for manager-only routes
def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (not current_user.is_admin() and not current_user.is_gerente()):
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data) or not user.is_active:
            flash('Usuario o contraseña invalidos.', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        log_activity(f'Login exitoso: {user.username}', user.id)
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        
        flash(f'Bienvenido, {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('login.html', title='Iniciar Sesión', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    log_activity(f'Logout: {current_user.username}')
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@admin_required
def register():
    form = RegistrationForm()
    
    # Get list of companies for the dropdown
    companies = Company.query.all()
    form.company_id.choices = [(0, 'Ninguna')] + [(c.id, c.name) for c in companies]
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=UserRole(form.role.data),
            company_id=form.company_id.data if form.company_id.data != 0 else None
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        log_activity(f'Usuario registrado: {user.username}')
        flash('¡Usuario registrado correctamente!', 'success')
        return redirect(url_for('user.list_users'))
    
    return render_template('register.html', title='Registrar Usuario', form=form)

# Main routes
@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    stats = get_dashboard_stats()
    return render_template('dashboard.html', title='Dashboard', stats=stats, datetime=datetime)

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('La contraseña actual es incorrecta.', 'danger')
            return redirect(url_for('main.profile'))
            
        current_user.set_password(form.new_password.data)
        db.session.commit()
        log_activity('Cambio de contraseña')
        flash('Contraseña actualizada correctamente.', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('profile.html', title='Mi Perfil', form=form)

@main_bp.route('/search')
@login_required
def search():
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('main.dashboard'))
    
    # Search for companies (admin and gerentes only)
    companies = []
    if current_user.is_admin() or current_user.is_gerente():
        companies = Company.query.filter(
            (Company.name.ilike(f'%{query}%')) |
            (Company.tax_id.ilike(f'%{query}%'))
        ).all()
    
    # Search for employees based on user role
    employees = []
    if current_user.is_admin():
        employees = Employee.query.filter(
            (Employee.first_name.ilike(f'%{query}%')) |
            (Employee.last_name.ilike(f'%{query}%')) |
            (Employee.dni.ilike(f'%{query}%'))
        ).all()
    elif current_user.is_gerente() and current_user.company_id:
        employees = Employee.query.filter(
            Employee.company_id == current_user.company_id
        ).filter(
            (Employee.first_name.ilike(f'%{query}%')) |
            (Employee.last_name.ilike(f'%{query}%')) |
            (Employee.dni.ilike(f'%{query}%'))
        ).all()
    elif current_user.is_empleado() and current_user.employee:
        # Empleados can only see themselves in search results
        if (query.lower() in current_user.employee.first_name.lower() or
            query.lower() in current_user.employee.last_name.lower() or
            query.lower() in current_user.employee.dni.lower()):
            employees = [current_user.employee]
    
    return render_template('search_results.html', 
                          title='Resultados de Búsqueda',
                          query=query,
                          companies=companies,
                          employees=employees)

# Company routes
@company_bp.route('/')
@login_required
def list_companies():
    # Admin can see all companies
    if current_user.is_admin():
        companies = Company.query.all()
    # Gerente can only see their company
    elif current_user.is_gerente() and current_user.company_id:
        companies = [Company.query.get_or_404(current_user.company_id)]
    # Empleado can only see their company
    elif current_user.is_empleado() and current_user.company_id:
        companies = [Company.query.get_or_404(current_user.company_id)]
    else:
        companies = []
    
    return render_template('company_list.html', title='Empresas', companies=companies)

@company_bp.route('/<int:id>')
@login_required
def view_company(id):
    company = Company.query.get_or_404(id)
    
    # Check if user has permission to view this company
    if not current_user.is_admin() and current_user.company_id != company.id:
        flash('No tienes permiso para ver esta empresa.', 'danger')
        return redirect(url_for('company.list_companies'))
    
    return render_template('company_detail.html', title=company.name, company=company)

@company_bp.route('/new', methods=['GET', 'POST'])
@admin_required
def create_company():
    form = CompanyForm()
    
    if form.validate_on_submit():
        company = Company(
            name=form.name.data,
            address=form.address.data,
            city=form.city.data,
            postal_code=form.postal_code.data,
            country=form.country.data,
            sector=form.sector.data,
            tax_id=form.tax_id.data,
            phone=form.phone.data,
            email=form.email.data,
            website=form.website.data,
            is_active=form.is_active.data
        )
        db.session.add(company)
        db.session.commit()
        
        log_activity(f'Empresa creada: {company.name}')
        flash(f'Empresa "{company.name}" creada correctamente.', 'success')
        return redirect(url_for('company.view_company', id=company.id))
    
    return render_template('company_form.html', title='Nueva Empresa', form=form)

@company_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_company(id):
    company = Company.query.get_or_404(id)
    
    # Check if user has permission to edit this company
    if not can_manage_company(company.id):
        flash('No tienes permiso para editar esta empresa.', 'danger')
        return redirect(url_for('company.list_companies'))
    
    form = CompanyForm(obj=company)
    
    if form.validate_on_submit():
        company.name = form.name.data
        company.address = form.address.data
        company.city = form.city.data
        company.postal_code = form.postal_code.data
        company.country = form.country.data
        company.sector = form.sector.data
        company.tax_id = form.tax_id.data
        company.phone = form.phone.data
        company.email = form.email.data
        company.website = form.website.data
        company.is_active = form.is_active.data
        company.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_activity(f'Empresa actualizada: {company.name}')
        flash(f'Empresa "{company.name}" actualizada correctamente.', 'success')
        return redirect(url_for('company.view_company', id=company.id))
    
    return render_template('company_form.html', title=f'Editar {company.name}', form=form, company=company)

@company_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete_company(id):
    company = Company.query.get_or_404(id)
    
    # Check if company has employees
    if company.employees:
        flash('No se puede eliminar la empresa porque tiene empleados asociados.', 'danger')
        return redirect(url_for('company.view_company', id=company.id))
    
    company_name = company.name
    db.session.delete(company)
    db.session.commit()
    
    log_activity(f'Empresa eliminada: {company_name}')
    flash(f'Empresa "{company_name}" eliminada correctamente.', 'success')
    return redirect(url_for('company.list_companies'))

# Employee routes
@employee_bp.route('/')
@login_required
def list_employees():
    # Admin can see all employees
    if current_user.is_admin():
        employees = Employee.query.all()
    # Gerente can only see employees from their company
    elif current_user.is_gerente() and current_user.company_id:
        employees = Employee.query.filter_by(company_id=current_user.company_id).all()
    # Empleado can only see themselves
    elif current_user.is_empleado() and current_user.employee:
        employees = [current_user.employee]
    else:
        employees = []
    
    return render_template('employee_list.html', title='Empleados', employees=employees)

@employee_bp.route('/<int:id>')
@login_required
def view_employee(id):
    employee = Employee.query.get_or_404(id)
    
    # Check if user has permission to view this employee
    if not can_view_employee(employee):
        flash('No tienes permiso para ver este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    return render_template('employee_detail.html', title=f'{employee.first_name} {employee.last_name}', employee=employee)

@employee_bp.route('/new', methods=['GET', 'POST'])
@manager_required
def create_employee():
    form = EmployeeForm()
    
    # Get list of companies for the dropdown
    if current_user.is_admin():
        companies = Company.query.all()
        form.company_id.choices = [(c.id, c.name) for c in companies]
    else:
        # For gerentes, only show their company
        form.company_id.choices = [(current_user.company_id, current_user.company.name)]
        form.company_id.data = current_user.company_id
    
    if form.validate_on_submit():
        employee = Employee(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            dni=form.dni.data,
            position=form.position.data,
            contract_type=ContractType(form.contract_type.data) if form.contract_type.data else None,
            bank_account=form.bank_account.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            company_id=form.company_id.data,
            is_active=form.is_active.data,
            status=EmployeeStatus(form.status.data) if form.status.data else EmployeeStatus.ACTIVO,
            status_start_date=form.start_date.data  # Por defecto, la fecha de inicio de estado es la misma de contratación
        )
        db.session.add(employee)
        db.session.commit()
        
        log_activity(f'Empleado creado: {employee.first_name} {employee.last_name}')
        flash(f'Empleado "{employee.first_name} {employee.last_name}" creado correctamente.', 'success')
        return redirect(url_for('employee.view_employee', id=employee.id))
    
    return render_template('employee_form.html', title='Nuevo Empleado', form=form)

@employee_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    
    # Check if user has permission to edit this employee
    if not can_manage_employee(employee):
        flash('No tienes permiso para editar este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    form = EmployeeForm(obj=employee)
    
    # Get list of companies for the dropdown
    if current_user.is_admin():
        companies = Company.query.all()
        form.company_id.choices = [(c.id, c.name) for c in companies]
    else:
        # For gerentes, only show their company
        form.company_id.choices = [(current_user.company_id, current_user.company.name)]
        form.company_id.data = current_user.company_id
    
    if form.validate_on_submit():
        # Track changes for employee history
        if employee.first_name != form.first_name.data:
            log_employee_change(employee, 'first_name', employee.first_name, form.first_name.data)
            employee.first_name = form.first_name.data
            
        if employee.last_name != form.last_name.data:
            log_employee_change(employee, 'last_name', employee.last_name, form.last_name.data)
            employee.last_name = form.last_name.data
            
        if employee.dni != form.dni.data:
            log_employee_change(employee, 'dni', employee.dni, form.dni.data)
            employee.dni = form.dni.data
            
        if employee.position != form.position.data:
            log_employee_change(employee, 'position', employee.position, form.position.data)
            employee.position = form.position.data
            
        if str(employee.contract_type.value if employee.contract_type else None) != form.contract_type.data:
            log_employee_change(employee, 'contract_type', 
                              employee.contract_type.value if employee.contract_type else None, 
                              form.contract_type.data)
            employee.contract_type = ContractType(form.contract_type.data) if form.contract_type.data else None
            
        if employee.bank_account != form.bank_account.data:
            log_employee_change(employee, 'bank_account', employee.bank_account, form.bank_account.data)
            employee.bank_account = form.bank_account.data
            
        if employee.start_date != form.start_date.data:
            log_employee_change(employee, 'start_date', 
                              employee.start_date.isoformat() if employee.start_date else None, 
                              form.start_date.data.isoformat() if form.start_date.data else None)
            employee.start_date = form.start_date.data
            
        if employee.end_date != form.end_date.data:
            log_employee_change(employee, 'end_date', 
                              employee.end_date.isoformat() if employee.end_date else None, 
                              form.end_date.data.isoformat() if form.end_date.data else None)
            employee.end_date = form.end_date.data
            
        if employee.company_id != form.company_id.data:
            old_company = Company.query.get(employee.company_id).name if employee.company_id else 'Ninguna'
            new_company = Company.query.get(form.company_id.data).name
            log_employee_change(employee, 'company', old_company, new_company)
            employee.company_id = form.company_id.data
            
        if employee.is_active != form.is_active.data:
            log_employee_change(employee, 'is_active', str(employee.is_active), str(form.is_active.data))
            employee.is_active = form.is_active.data
            
        if str(employee.status.value if employee.status else 'activo') != form.status.data:
            log_employee_change(employee, 'status', 
                              employee.status.value if employee.status else 'activo', 
                              form.status.data)
            employee.status = EmployeeStatus(form.status.data)
            
        employee.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(f'Empleado actualizado: {employee.first_name} {employee.last_name}')
        flash(f'Empleado "{employee.first_name} {employee.last_name}" actualizado correctamente.', 'success')
        return redirect(url_for('employee.view_employee', id=employee.id))
    
    return render_template('employee_form.html', title=f'Editar {employee.first_name} {employee.last_name}', form=form, employee=employee)

@employee_bp.route('/<int:id>/delete', methods=['POST'])
@manager_required
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    
    # Check if user has permission to delete this employee
    if not can_manage_employee(employee):
        flash('No tienes permiso para eliminar este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    employee_name = f"{employee.first_name} {employee.last_name}"
    db.session.delete(employee)
    db.session.commit()
    
    log_activity(f'Empleado eliminado: {employee_name}')
    flash(f'Empleado "{employee_name}" eliminado correctamente.', 'success')
    return redirect(url_for('employee.list_employees'))
    
@employee_bp.route('/<int:id>/status', methods=['GET', 'POST'])
@login_required
def manage_status(id):
    employee = Employee.query.get_or_404(id)
    
    # Check if user has permission to manage this employee's status
    if not can_manage_employee(employee):
        flash('No tienes permiso para gestionar el estado de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    form = EmployeeStatusForm(obj=employee)
    
    if form.validate_on_submit():
        old_status = employee.status.value if employee.status else 'activo'
        new_status = form.status.data
        
        if old_status != new_status:
            log_employee_change(employee, 'status', old_status, new_status)
            employee.status = EmployeeStatus(new_status)
        
        # Log changes to dates and notes if they've changed
        if employee.status_start_date != form.status_start_date.data:
            log_employee_change(employee, 'status_start_date', 
                              employee.status_start_date.isoformat() if employee.status_start_date else None, 
                              form.status_start_date.data.isoformat() if form.status_start_date.data else None)
        
        if employee.status_end_date != form.status_end_date.data:
            log_employee_change(employee, 'status_end_date', 
                              employee.status_end_date.isoformat() if employee.status_end_date else None, 
                              form.status_end_date.data.isoformat() if form.status_end_date.data else None)
        
        if employee.status_notes != form.status_notes.data:
            log_employee_change(employee, 'status_notes', employee.status_notes, form.status_notes.data)
        
        # Update the employee record with the new status information
        employee.status = EmployeeStatus(form.status.data)
        employee.status_start_date = form.status_start_date.data
        employee.status_end_date = form.status_end_date.data
        employee.status_notes = form.status_notes.data
        employee.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_activity(f'Estado de empleado actualizado: {employee.first_name} {employee.last_name}')
        flash(f'Estado del empleado "{employee.first_name} {employee.last_name}" actualizado correctamente.', 'success')
        return redirect(url_for('employee.view_employee', id=employee.id))
    
    return render_template('employee_status.html', title=f'Gestionar Estado - {employee.first_name} {employee.last_name}', 
                          form=form, employee=employee)

@employee_bp.route('/<int:id>/documents')
@login_required
def list_documents(id):
    employee = Employee.query.get_or_404(id)
    
    # Check if user has permission to view this employee's documents
    if not can_view_employee(employee):
        flash('No tienes permiso para ver los documentos de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    documents = EmployeeDocument.query.filter_by(employee_id=employee.id).all()
    return render_template('employee_documents.html', 
                          title=f'Documentos de {employee.first_name} {employee.last_name}', 
                          employee=employee, 
                          documents=documents)

@employee_bp.route('/<int:id>/documents/upload', methods=['GET', 'POST'])
@login_required
def upload_document(id):
    employee = Employee.query.get_or_404(id)
    
    # Check if user has permission to upload documents for this employee
    if not can_manage_employee(employee):
        flash('No tienes permiso para subir documentos para este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    form = EmployeeDocumentForm()
    
    if form.validate_on_submit():
        file_data = save_file(form.file.data, form.description.data)
        if file_data:
            document = EmployeeDocument(
                employee_id=employee.id,
                filename=file_data['filename'],
                original_filename=file_data['original_filename'],
                file_path=file_data['file_path'],
                file_type=file_data['file_type'],
                file_size=file_data['file_size'],
                description=file_data['description']
            )
            db.session.add(document)
            db.session.commit()
            
            log_activity(f'Documento subido para {employee.first_name} {employee.last_name}: {file_data["original_filename"]}')
            flash(f'Documento "{file_data["original_filename"]}" subido correctamente.', 'success')
            return redirect(url_for('employee.list_documents', id=employee.id))
        else:
            flash('Error al subir el documento. Formato no permitido.', 'danger')
    
    return render_template('employee_document_upload.html', 
                          title=f'Subir Documento para {employee.first_name} {employee.last_name}', 
                          employee=employee, 
                          form=form)

@employee_bp.route('/documents/<int:doc_id>')
@login_required
def download_document(doc_id):
    document = EmployeeDocument.query.get_or_404(doc_id)
    employee = Employee.query.get_or_404(document.employee_id)
    
    # Check if user has permission to download this document
    if not can_view_employee(employee):
        flash('No tienes permiso para descargar este documento.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    log_activity(f'Documento descargado: {document.original_filename}')
    return send_from_directory(
        os.path.dirname(document.file_path),
        os.path.basename(document.file_path),
        as_attachment=True,
        download_name=document.original_filename
    )

@employee_bp.route('/documents/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_document(doc_id):
    document = EmployeeDocument.query.get_or_404(doc_id)
    employee = Employee.query.get_or_404(document.employee_id)
    
    # Check if user has permission to delete this document
    if not can_manage_employee(employee):
        flash('No tienes permiso para eliminar este documento.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    # Delete file from filesystem
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    document_name = document.original_filename
    db.session.delete(document)
    db.session.commit()
    
    log_activity(f'Documento eliminado: {document_name}')
    flash(f'Documento "{document_name}" eliminado correctamente.', 'success')
    return redirect(url_for('employee.list_documents', id=employee.id))

@employee_bp.route('/<int:id>/notes', methods=['GET', 'POST'])
@login_required
def manage_notes(id):
    employee = Employee.query.get_or_404(id)
    
    # Check if user has permission to manage notes for this employee
    if not can_manage_employee(employee):
        flash('No tienes permiso para gestionar notas de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    form = EmployeeNoteForm()
    
    if form.validate_on_submit():
        note = EmployeeNote(
            employee_id=employee.id,
            content=form.content.data,
            created_by_id=current_user.id
        )
        db.session.add(note)
        db.session.commit()
        
        log_activity(f'Nota añadida para {employee.first_name} {employee.last_name}')
        flash('Nota añadida correctamente.', 'success')
        return redirect(url_for('employee.manage_notes', id=employee.id))
    
    notes = EmployeeNote.query.filter_by(employee_id=employee.id).order_by(EmployeeNote.created_at.desc()).all()
    return render_template('employee_notes.html', 
                          title=f'Notas de {employee.first_name} {employee.last_name}', 
                          employee=employee, 
                          notes=notes, 
                          form=form)

@employee_bp.route('/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    note = EmployeeNote.query.get_or_404(note_id)
    employee = Employee.query.get_or_404(note.employee_id)
    
    # Check if user has permission to delete this note
    if not can_manage_employee(employee):
        flash('No tienes permiso para eliminar esta nota.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    db.session.delete(note)
    db.session.commit()
    
    log_activity(f'Nota eliminada para {employee.first_name} {employee.last_name}')
    flash('Nota eliminada correctamente.', 'success')
    return redirect(url_for('employee.manage_notes', id=employee.id))

@employee_bp.route('/<int:id>/history')
@login_required
def view_history(id):
    employee = Employee.query.get_or_404(id)
    
    # Check if user has permission to view this employee's history
    if not can_view_employee(employee):
        flash('No tienes permiso para ver el historial de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    history = employee.history
    return render_template('employee_history.html', 
                          title=f'Historial de {employee.first_name} {employee.last_name}', 
                          employee=employee, 
                          history=history)

# User routes
@user_bp.route('/')
@admin_required
def list_users():
    users = User.query.all()
    return render_template('user_management.html', title='Gestión de Usuarios', users=users)

@user_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserUpdateForm(user.username, user.email, obj=user)
    
    # Get list of companies for the dropdown
    companies = Company.query.all()
    form.company_id.choices = [(0, 'Ninguna')] + [(c.id, c.name) for c in companies]
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.role = UserRole(form.role.data)
        user.company_id = form.company_id.data if form.company_id.data != 0 else None
        user.is_active = form.is_active.data
        
        db.session.commit()
        
        log_activity(f'Usuario actualizado: {user.username}')
        flash(f'Usuario "{user.username}" actualizado correctamente.', 'success')
        return redirect(url_for('user.list_users'))
    
    return render_template('user_form.html', title=f'Editar Usuario {user.username}', form=form, user=user)

@user_bp.route('/<int:id>/reset-password', methods=['POST'])
@admin_required
def reset_password(id):
    user = User.query.get_or_404(id)
    
    # Generate a temporary password
    temp_password = f"temp{id}pwd{int(datetime.utcnow().timestamp())}"[:12]
    user.set_password(temp_password)
    db.session.commit()
    
    log_activity(f'Contraseña restablecida para: {user.username}')
    flash(f'Contraseña de "{user.username}" restablecida a: {temp_password}', 'success')
    return redirect(url_for('user.list_users'))

@user_bp.route('/<int:id>/activate', methods=['POST'])
@admin_required
def toggle_activation(id):
    user = User.query.get_or_404(id)
    
    # Don't allow deactivating own account
    if user.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta.', 'danger')
        return redirect(url_for('user.list_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activado' if user.is_active else 'desactivado'
    log_activity(f'Usuario {status}: {user.username}')
    flash(f'Usuario "{user.username}" {status} correctamente.', 'success')
    return redirect(url_for('user.list_users'))

@user_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    
    # Don't allow deleting own account
    if user.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta.', 'danger')
        return redirect(url_for('user.list_users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    log_activity(f'Usuario eliminado: {username}')
    flash(f'Usuario "{username}" eliminado correctamente.', 'success')
    return redirect(url_for('user.list_users'))

# Schedules routes
@schedule_bp.route('/employee/<int:employee_id>')
@login_required
def list_schedules(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    
    # Check if user has permission to view this employee
    if not can_view_employee(employee):
        flash('No tienes permiso para ver los horarios de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    schedules = EmployeeSchedule.query.filter_by(employee_id=employee_id).all()
    
    return render_template('schedule_list.html', 
                          title=f'Horarios de {employee.first_name} {employee.last_name}', 
                          employee=employee,
                          schedules=schedules)

@schedule_bp.route('/employee/<int:employee_id>/new', methods=['GET', 'POST'])
@manager_required
def create_schedule(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    
    # Check if user has permission to manage this employee
    if not can_manage_employee(employee):
        flash('No tienes permiso para gestionar los horarios de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    form = EmployeeScheduleForm()
    
    if form.validate_on_submit():
        schedule = EmployeeSchedule(
            day_of_week=WeekDay(form.day_of_week.data),
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            is_working_day=form.is_working_day.data,
            employee_id=employee_id
        )
        db.session.add(schedule)
        db.session.commit()
        
        log_activity(f'Horario creado para {employee.first_name} {employee.last_name}')
        flash('Horario creado correctamente.', 'success')
        return redirect(url_for('schedule.list_schedules', employee_id=employee_id))
    
    return render_template('schedule_form.html', 
                          title=f'Nuevo Horario para {employee.first_name} {employee.last_name}', 
                          form=form,
                          employee=employee)

@schedule_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@manager_required
def edit_schedule(id):
    schedule = EmployeeSchedule.query.get_or_404(id)
    employee = Employee.query.get_or_404(schedule.employee_id)
    
    # Check if user has permission to manage this employee
    if not can_manage_employee(employee):
        flash('No tienes permiso para editar los horarios de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    form = EmployeeScheduleForm(obj=schedule)
    
    if form.validate_on_submit():
        schedule.day_of_week = WeekDay(form.day_of_week.data)
        schedule.start_time = form.start_time.data
        schedule.end_time = form.end_time.data
        schedule.is_working_day = form.is_working_day.data
        schedule.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_activity(f'Horario actualizado para {employee.first_name} {employee.last_name}')
        flash('Horario actualizado correctamente.', 'success')
        return redirect(url_for('schedule.list_schedules', employee_id=schedule.employee_id))
    
    return render_template('schedule_form.html', 
                          title=f'Editar Horario de {employee.first_name} {employee.last_name}', 
                          form=form,
                          employee=employee,
                          schedule=schedule)

@schedule_bp.route('/<int:id>/delete', methods=['POST'])
@manager_required
def delete_schedule(id):
    schedule = EmployeeSchedule.query.get_or_404(id)
    employee = Employee.query.get_or_404(schedule.employee_id)
    
    # Check if user has permission to manage this employee
    if not can_manage_employee(employee):
        flash('No tienes permiso para eliminar los horarios de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    employee_id = schedule.employee_id
    db.session.delete(schedule)
    db.session.commit()
    
    log_activity(f'Horario eliminado para {employee.first_name} {employee.last_name}')
    flash('Horario eliminado correctamente.', 'success')
    return redirect(url_for('schedule.list_schedules', employee_id=employee_id))

# Check-ins routes
@checkin_bp.route('/employee/<int:employee_id>')
@login_required
def list_checkins(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    
    # Check if user has permission to view this employee
    if not can_view_employee(employee):
        flash('No tienes permiso para ver los fichajes de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    checkins = EmployeeCheckIn.query.filter_by(employee_id=employee_id).order_by(EmployeeCheckIn.check_in_time.desc()).all()
    
    return render_template('checkin_list.html', 
                          title=f'Fichajes de {employee.first_name} {employee.last_name}', 
                          employee=employee,
                          checkins=checkins)

@checkin_bp.route('/employee/<int:employee_id>/new', methods=['GET', 'POST'])
@manager_required
def create_checkin(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    
    # Check if user has permission to manage this employee
    if not can_manage_employee(employee):
        flash('No tienes permiso para gestionar los fichajes de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    form = EmployeeCheckInForm()
    
    if form.validate_on_submit():
        check_in_time = datetime.combine(form.check_in_time.data, datetime.min.time())
        check_out_time = datetime.combine(form.check_out_time.data, datetime.min.time()) if form.check_out_time.data else None
        
        checkin = EmployeeCheckIn(
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            notes=form.notes.data,
            employee_id=employee_id
        )
        db.session.add(checkin)
        db.session.commit()
        
        log_activity(f'Fichaje creado para {employee.first_name} {employee.last_name}')
        flash('Fichaje creado correctamente.', 'success')
        return redirect(url_for('checkin.list_checkins', employee_id=employee_id))
    
    return render_template('checkin_form.html', 
                          title=f'Nuevo Fichaje para {employee.first_name} {employee.last_name}', 
                          form=form,
                          employee=employee)

@checkin_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@manager_required
def edit_checkin(id):
    checkin = EmployeeCheckIn.query.get_or_404(id)
    employee = Employee.query.get_or_404(checkin.employee_id)
    
    # Check if user has permission to manage this employee
    if not can_manage_employee(employee):
        flash('No tienes permiso para editar los fichajes de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    form = EmployeeCheckInForm()
    
    if request.method == 'GET':
        form.check_in_time.data = checkin.check_in_time.date()
        form.check_out_time.data = checkin.check_out_time.date() if checkin.check_out_time else None
        form.notes.data = checkin.notes
    
    if form.validate_on_submit():
        check_in_time = datetime.combine(form.check_in_time.data, checkin.check_in_time.time())
        check_out_time = None
        if form.check_out_time.data:
            check_out_time = datetime.combine(form.check_out_time.data, 
                                            checkin.check_out_time.time() if checkin.check_out_time else datetime.min.time())
        
        checkin.check_in_time = check_in_time
        checkin.check_out_time = check_out_time
        checkin.notes = form.notes.data
        checkin.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_activity(f'Fichaje actualizado para {employee.first_name} {employee.last_name}')
        flash('Fichaje actualizado correctamente.', 'success')
        return redirect(url_for('checkin.list_checkins', employee_id=checkin.employee_id))
    
    return render_template('checkin_form.html', 
                          title=f'Editar Fichaje de {employee.first_name} {employee.last_name}', 
                          form=form,
                          employee=employee,
                          checkin=checkin)

@checkin_bp.route('/<int:id>/delete', methods=['POST'])
@manager_required
def delete_checkin(id):
    checkin = EmployeeCheckIn.query.get_or_404(id)
    employee = Employee.query.get_or_404(checkin.employee_id)
    
    # Check if user has permission to manage this employee
    if not can_manage_employee(employee):
        flash('No tienes permiso para eliminar los fichajes de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    employee_id = checkin.employee_id
    db.session.delete(checkin)
    db.session.commit()
    
    log_activity(f'Fichaje eliminado para {employee.first_name} {employee.last_name}')
    flash('Fichaje eliminado correctamente.', 'success')
    return redirect(url_for('checkin.list_checkins', employee_id=employee_id))

@checkin_bp.route('/employee/<int:employee_id>/generate', methods=['GET', 'POST'])
@manager_required
def generate_checkins(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    
    # Check if user has permission to manage this employee
    if not can_manage_employee(employee):
        flash('No tienes permiso para generar fichajes para este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    # Check if employee has schedules
    if not employee.schedules:
        flash('El empleado no tiene horarios definidos. Por favor, defina los horarios primero.', 'warning')
        return redirect(url_for('schedule.list_schedules', employee_id=employee_id))
    
    form = GenerateCheckInsForm()
    
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        
        # Generate check-ins
        check_ins = EmployeeCheckIn.generate_check_ins_for_schedule(employee, start_date, end_date)
        
        if not check_ins:
            flash('No se han podido generar fichajes para el periodo seleccionado.', 'warning')
        else:
            # Save check-ins to database
            for check_in in check_ins:
                db.session.add(check_in)
            db.session.commit()
            
            log_activity(f'Fichajes generados para {employee.first_name} {employee.last_name}')
            flash(f'Se han generado {len(check_ins)} fichajes correctamente.', 'success')
        
        return redirect(url_for('checkin.list_checkins', employee_id=employee_id))
    
    return render_template('generate_checkins_form.html', 
                          title=f'Generar Fichajes para {employee.first_name} {employee.last_name}', 
                          form=form,
                          employee=employee)

# Vacations routes
@vacation_bp.route('/employee/<int:employee_id>')
@login_required
def list_vacations(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    
    # Check if user has permission to view this employee
    if not can_view_employee(employee):
        flash('No tienes permiso para ver las vacaciones de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    vacations = EmployeeVacation.query.filter_by(employee_id=employee_id).order_by(EmployeeVacation.start_date.desc()).all()
    
    return render_template('vacation_list.html', 
                          title=f'Vacaciones de {employee.first_name} {employee.last_name}', 
                          employee=employee,
                          vacations=vacations)

@vacation_bp.route('/employee/<int:employee_id>/new', methods=['GET', 'POST'])
@login_required
def create_vacation(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    
    # Check if user has permission to view this employee
    if not (can_manage_employee(employee) or 
            (current_user.is_empleado() and current_user.employee and current_user.employee.id == employee_id)):
        flash('No tienes permiso para gestionar las vacaciones de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    form = EmployeeVacationForm()
    
    if form.validate_on_submit():
        # Check if the vacation period overlaps with existing vacations
        overlapping_vacations = EmployeeVacation.query.filter_by(employee_id=employee_id).all()
        for v in overlapping_vacations:
            if v.overlaps_with(form.start_date.data, form.end_date.data):
                flash('El periodo de vacaciones se solapa con otro existente.', 'danger')
                return render_template('vacation_form.html', 
                                      title=f'Nuevas Vacaciones para {employee.first_name} {employee.last_name}', 
                                      form=form,
                                      employee=employee)
        
        # If EMPLEADO role, status is always PENDIENTE
        status = VacationStatus.PENDIENTE
        if not current_user.is_empleado() and form.status.data:
            status = VacationStatus(form.status.data)
        
        vacation = EmployeeVacation(
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            status=status,
            notes=form.notes.data,
            employee_id=employee_id
        )
        
        # If GERENTE or ADMIN approves, set approved_by
        if not current_user.is_empleado() and status == VacationStatus.APROBADA:
            vacation.approved_by_id = current_user.id
        
        db.session.add(vacation)
        db.session.commit()
        
        log_activity(f'Vacaciones creadas para {employee.first_name} {employee.last_name}')
        flash('Vacaciones creadas correctamente.', 'success')
        return redirect(url_for('vacation.list_vacations', employee_id=employee_id))
    
    return render_template('vacation_form.html', 
                          title=f'Nuevas Vacaciones para {employee.first_name} {employee.last_name}', 
                          form=form,
                          employee=employee)

@vacation_bp.route('/<int:id>/approve', methods=['GET', 'POST'])
@manager_required
def approve_vacation(id):
    vacation = EmployeeVacation.query.get_or_404(id)
    employee = Employee.query.get_or_404(vacation.employee_id)
    
    # Check if user has permission to manage this employee
    if not can_manage_employee(employee):
        flash('No tienes permiso para aprobar vacaciones de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    form = EmployeeVacationApprovalForm()
    form.status.data = vacation.status.value
    
    if form.validate_on_submit():
        vacation.status = VacationStatus(form.status.data)
        
        if form.notes.data:
            vacation.notes = form.notes.data
            
        # Update approved_by if status is APROBADA
        if vacation.status == VacationStatus.APROBADA:
            vacation.approved_by_id = current_user.id
        else:
            vacation.approved_by_id = None
            
        vacation.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_activity(f'Vacaciones actualizadas para {employee.first_name} {employee.last_name}')
        flash('Estado de vacaciones actualizado correctamente.', 'success')
        return redirect(url_for('vacation.list_vacations', employee_id=vacation.employee_id))
    
    return render_template('vacation_approval_form.html', 
                          title=f'Aprobar Vacaciones de {employee.first_name} {employee.last_name}', 
                          form=form,
                          employee=employee,
                          vacation=vacation)

@vacation_bp.route('/<int:id>/delete', methods=['POST'])
@manager_required
def delete_vacation(id):
    vacation = EmployeeVacation.query.get_or_404(id)
    employee = Employee.query.get_or_404(vacation.employee_id)
    
    # Check if user has permission to manage this employee
    if not can_manage_employee(employee):
        flash('No tienes permiso para eliminar vacaciones de este empleado.', 'danger')
        return redirect(url_for('employee.list_employees'))
    
    employee_id = vacation.employee_id
    db.session.delete(vacation)
    db.session.commit()
    
    log_activity(f'Vacaciones eliminadas para {employee.first_name} {employee.last_name}')
    flash('Vacaciones eliminadas correctamente.', 'success')
    return redirect(url_for('vacation.list_vacations', employee_id=employee_id))
