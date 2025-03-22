from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, date, timedelta
import os
from werkzeug.utils import secure_filename
from wtforms.validators import Optional

from app import db
from models import User, Company
from models_tasks import Location, LocalUser, Task, TaskSchedule, TaskCompletion, TaskPriority, TaskFrequency, TaskStatus, WeekDay, TaskGroup, TaskWeekday
from forms_tasks import (LocationForm, LocalUserForm, TaskForm, DailyScheduleForm, WeeklyScheduleForm, 
                        MonthlyScheduleForm, BiweeklyScheduleForm, TaskCompletionForm, 
                        LocalUserPinForm, SearchForm, TaskGroupForm, CustomWeekdaysForm, PortalLoginForm)
from utils import log_activity, can_manage_company, save_file
from utils_tasks import create_default_local_user, regenerate_portal_password

# Crear el Blueprint para las tareas
tasks_bp = Blueprint('tasks', __name__)

# Decorador para proteger rutas y asegurar que el usuario es admin o gerente
def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        if not (current_user.is_admin() or current_user.is_gerente()):
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('index'))
            
        return f(*args, **kwargs)
    return decorated_function

# Decorador para proteger rutas de usuario local
def local_user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'local_user_id' not in session:
            return redirect(url_for('tasks.local_login'))
            
        return f(*args, **kwargs)
    return decorated_function

# Rutas para el dashboard principal de tareas
@tasks_bp.route('/')
@login_required
def index():
    """Dashboard principal del módulo de tareas"""
    # Determinar qué información mostrar según el rol del usuario
    if current_user.is_admin():
        # Los administradores ven estadísticas globales
        locations = Location.query.all()
        total_tasks = Task.query.count()
        pending_tasks = Task.query.filter_by(status=TaskStatus.PENDIENTE).count()
        completed_tasks = Task.query.filter_by(status=TaskStatus.COMPLETADA).count()
        
        # Obtener tareas completadas recientemente
        recent_completions = (db.session.query(TaskCompletion, Task, LocalUser)
                             .join(Task, TaskCompletion.task_id == Task.id)
                             .join(LocalUser, TaskCompletion.local_user_id == LocalUser.id)
                             .order_by(TaskCompletion.completion_date.desc())
                             .limit(10)
                             .all())
        
    elif current_user.is_gerente() and current_user.company_id:
        # Los gerentes ven solo su empresa
        locations = Location.query.filter_by(company_id=current_user.company_id).all()
        
        # Subconsulta para obtener tareas de los locales de su empresa
        location_ids = [loc.id for loc in locations]
        
        # Si no hay locales, los conteos serán 0
        if location_ids:
            total_tasks = Task.query.filter(Task.location_id.in_(location_ids)).count()
            pending_tasks = Task.query.filter(Task.location_id.in_(location_ids), 
                                             Task.status==TaskStatus.PENDIENTE).count()
            completed_tasks = Task.query.filter(Task.location_id.in_(location_ids), 
                                              Task.status==TaskStatus.COMPLETADA).count()
            
            # Obtener completados recientes
            recent_completions = (db.session.query(TaskCompletion, Task, LocalUser)
                                .join(Task, TaskCompletion.task_id == Task.id)
                                .join(LocalUser, TaskCompletion.local_user_id == LocalUser.id)
                                .filter(Task.location_id.in_(location_ids))
                                .order_by(TaskCompletion.completion_date.desc())
                                .limit(10)
                                .all())
        else:
            total_tasks = 0
            pending_tasks = 0
            completed_tasks = 0
            recent_completions = []
    else:
        # Otros usuarios no tendrían acceso, pero por si acaso
        locations = []
        total_tasks = 0
        pending_tasks = 0
        completed_tasks = 0
        recent_completions = []
    
    # Calcular porcentaje de tareas completadas
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Preparar datos para los gráficos
    location_names = [loc.name for loc in locations]
    pending_tasks_by_location = []
    completed_tasks_by_location = []
    
    for loc in locations:
        pending_count = Task.query.filter_by(location_id=loc.id, status=TaskStatus.PENDIENTE).count()
        completed_count = Task.query.filter_by(location_id=loc.id, status=TaskStatus.COMPLETADA).count()
        pending_tasks_by_location.append(pending_count)
        completed_tasks_by_location.append(completed_count)
    
    # Contar tareas por estado
    task_status_counts = [
        Task.query.filter_by(status=TaskStatus.PENDIENTE).count(),
        Task.query.filter_by(status=TaskStatus.COMPLETADA).count(),
        Task.query.filter_by(status=TaskStatus.VENCIDA).count(),
        Task.query.filter_by(status=TaskStatus.CANCELADA).count()
    ]
    
    # Obtener tareas pendientes para hoy
    today = date.today()
    today_tasks = []
    for loc in locations:
        tasks = Task.query.filter_by(location_id=loc.id, status=TaskStatus.PENDIENTE).all()
        for task in tasks:
            if task.is_due_today():
                today_tasks.append(task)
    
    # Preparar estadísticas
    stats = {
        'total_locations': len(locations),
        'total_local_users': LocalUser.query.filter(LocalUser.location_id.in_([loc.id for loc in locations])).count() if locations else 0,
        'total_tasks': total_tasks,
        'tasks_pending': pending_tasks,
        'tasks_completed': completed_tasks,
        'tasks_completed_today': TaskCompletion.query.filter(TaskCompletion.completion_date >= datetime.combine(today, datetime.min.time())).count(),
        'tasks_today': len(today_tasks),
        'tasks_expired': Task.query.filter_by(status=TaskStatus.VENCIDA).count()
    }
    
    return render_template('tasks/dashboard.html',
                          title='Dashboard de Tareas',
                          stats=stats,
                          locations=locations,
                          pending_tasks=today_tasks,
                          completion_rate=completion_rate,
                          recent_completions=recent_completions,
                          location_names=location_names,
                          pending_tasks_by_location=pending_tasks_by_location,
                          completed_tasks_by_location=completed_tasks_by_location,
                          task_status_counts=task_status_counts)

# Rutas para gestión de locales
@tasks_bp.route('/locations')
@login_required
@manager_required
def list_locations():
    """Lista de locales disponibles"""
    if current_user.is_admin():
        locations = Location.query.all()
    elif current_user.is_gerente() and current_user.company_id:
        locations = Location.query.filter_by(company_id=current_user.company_id).all()
    else:
        locations = []
    
    return render_template('tasks/location_list.html',
                          title='Gestión de Locales',
                          locations=locations)

@tasks_bp.route('/locations/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_location():
    """Crear un nuevo local"""
    form = LocationForm()
    
    # Cargar empresas disponibles según el rol
    if current_user.is_admin():
        form.company_id.choices = [(c.id, c.name) for c in Company.query.all()]
    elif current_user.is_gerente() and current_user.company_id:
        company = Company.query.get(current_user.company_id)
        if company:
            form.company_id.choices = [(company.id, company.name)]
        else:
            form.company_id.choices = []
    else:
        form.company_id.choices = []
    
    if form.validate_on_submit():
        location = Location(
            name=form.name.data,
            address=form.address.data,
            city=form.city.data,
            postal_code=form.postal_code.data,
            description=form.description.data,
            company_id=form.company_id.data,
            is_active=form.is_active.data,
            portal_username=form.portal_username.data
        )
        
        # Si se proporcionó contraseña, establecerla de forma segura
        if form.portal_password.data:
            location.set_portal_password(form.portal_password.data)
        
        db.session.add(location)
        db.session.commit()
        
        log_activity(f'Local creado: {location.name}')
        flash(f'Local "{location.name}" creado correctamente.', 'success')
        return redirect(url_for('tasks.list_locations'))
    
    return render_template('tasks/location_form.html',
                          title='Crear Nuevo Local',
                          form=form)

@tasks_bp.route('/locations/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_location(id):
    """Editar un local existente"""
    location = Location.query.get_or_404(id)
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != location.company_id):
        flash('No tienes permiso para editar este local.', 'danger')
        return redirect(url_for('tasks.list_locations'))
    
    form = LocationForm(obj=location)
    
    # No cargar contraseña del portal, ya que la tenemos como hash
    form.portal_password.data = None
    form.confirm_portal_password.data = None
    
    # Cargar empresas disponibles según el rol
    if current_user.is_admin():
        form.company_id.choices = [(c.id, c.name) for c in Company.query.all()]
    elif current_user.is_gerente() and current_user.company_id:
        company = Company.query.get(current_user.company_id)
        if company:
            form.company_id.choices = [(company.id, company.name)]
        else:
            form.company_id.choices = []
    else:
        form.company_id.choices = []
    
    if form.validate_on_submit():
        location.name = form.name.data
        location.address = form.address.data
        location.city = form.city.data
        location.postal_code = form.postal_code.data
        location.description = form.description.data
        location.company_id = form.company_id.data
        location.is_active = form.is_active.data
        location.portal_username = form.portal_username.data
        
        # Si se proporcionó una nueva contraseña, actualizarla
        if form.portal_password.data:
            location.set_portal_password(form.portal_password.data)
        
        db.session.commit()
        
        log_activity(f'Local actualizado: {location.name}')
        flash(f'Local "{location.name}" actualizado correctamente.', 'success')
        return redirect(url_for('tasks.list_locations'))
    
    return render_template('tasks/location_form.html',
                          title=f'Editar Local: {location.name}',
                          form=form,
                          location=location)

@tasks_bp.route('/locations/delete/<int:id>', methods=['POST'])
@login_required
@manager_required
def delete_location(id):
    """Eliminar un local"""
    location = Location.query.get_or_404(id)
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != location.company_id):
        flash('No tienes permiso para eliminar este local.', 'danger')
        return redirect(url_for('tasks.list_locations'))
    
    # Verificar si tiene tareas o usuarios asociados
    if location.tasks or location.local_users:
        flash('No se puede eliminar este local porque tiene tareas o usuarios asociados.', 'warning')
        return redirect(url_for('tasks.list_locations'))
    
    name = location.name
    db.session.delete(location)
    db.session.commit()
    
    log_activity(f'Local eliminado: {name}')
    flash(f'Local "{name}" eliminado correctamente.', 'success')
    return redirect(url_for('tasks.list_locations'))

@tasks_bp.route('/locations/<int:id>/groups')
@login_required
@manager_required
def list_task_groups(id):
    """Lista de grupos de tareas para un local"""
    location = Location.query.get_or_404(id)
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != location.company_id):
        flash('No tienes permiso para ver los grupos de este local.', 'danger')
        return redirect(url_for('tasks.list_locations'))
    
    # Obtener todos los grupos para este local
    groups = TaskGroup.query.filter_by(location_id=id).all()
    
    return render_template('tasks/task_group_list.html',
                          title=f'Grupos de Tareas - {location.name}',
                          location=location,
                          groups=groups)

@tasks_bp.route('/locations/<int:location_id>/groups/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_task_group(location_id):
    """Crear un nuevo grupo de tareas"""
    location = Location.query.get_or_404(location_id)
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != location.company_id):
        flash('No tienes permiso para crear grupos en este local.', 'danger')
        return redirect(url_for('tasks.list_locations'))
    
    form = TaskGroupForm()
    form.location_id.choices = [(location.id, location.name)]
    form.location_id.data = location.id
    
    if form.validate_on_submit():
        group = TaskGroup(
            name=form.name.data,
            description=form.description.data,
            color=form.color.data,
            location_id=location.id
        )
        
        db.session.add(group)
        db.session.commit()
        
        log_activity(f'Grupo de tareas creado: {group.name} para local {location.name}')
        flash(f'Grupo "{group.name}" creado correctamente.', 'success')
        return redirect(url_for('tasks.list_task_groups', id=location.id))
    
    return render_template('tasks/task_group_form.html',
                          title='Crear Nuevo Grupo de Tareas',
                          form=form,
                          location=location)

@tasks_bp.route('/task-groups/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_task_group(id):
    """Editar un grupo de tareas existente"""
    group = TaskGroup.query.get_or_404(id)
    location = group.location
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != location.company_id):
        flash('No tienes permiso para editar este grupo.', 'danger')
        return redirect(url_for('tasks.list_locations'))
    
    form = TaskGroupForm(obj=group)
    form.location_id.choices = [(location.id, location.name)]
    
    if form.validate_on_submit():
        group.name = form.name.data
        group.description = form.description.data
        group.color = form.color.data
        
        db.session.commit()
        
        log_activity(f'Grupo de tareas actualizado: {group.name}')
        flash(f'Grupo "{group.name}" actualizado correctamente.', 'success')
        return redirect(url_for('tasks.list_task_groups', id=location.id))
    
    return render_template('tasks/task_group_form.html',
                          title=f'Editar Grupo: {group.name}',
                          form=form,
                          group=group,
                          location=location)

@tasks_bp.route('/task-groups/<int:id>/delete', methods=['POST'])
@login_required
@manager_required
def delete_task_group(id):
    """Eliminar un grupo de tareas"""
    group = TaskGroup.query.get_or_404(id)
    location = group.location
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != location.company_id):
        flash('No tienes permiso para eliminar este grupo.', 'danger')
        return redirect(url_for('tasks.list_locations'))
    
    # Verificar si hay tareas asignadas al grupo
    tasks = Task.query.filter_by(group_id=id).all()
    if tasks:
        # Actualizar las tareas para desasociarlas del grupo
        for task in tasks:
            task.group_id = None
        db.session.commit()
    
    name = group.name
    location_id = location.id
    db.session.delete(group)
    db.session.commit()
    
    log_activity(f'Grupo de tareas eliminado: {name}')
    flash(f'Grupo "{name}" eliminado correctamente.', 'success')
    return redirect(url_for('tasks.list_task_groups', id=location_id))

@tasks_bp.route('/locations/<int:id>')
@login_required
def view_location(id):
    """Ver detalles de un local"""
    location = Location.query.get_or_404(id)
    
    # Verificar permisos (admin, gerente de la empresa, o empleado de la empresa)
    if not current_user.is_admin() and not (current_user.company_id == location.company_id):
        flash('No tienes permiso para ver este local.', 'danger')
        return redirect(url_for('tasks.index'))
    
    # Obtener tareas para hoy
    today = date.today()
    active_tasks = []
    pending_tasks = Task.query.filter_by(location_id=location.id, status=TaskStatus.PENDIENTE).all()
    completed_tasks = Task.query.filter_by(location_id=location.id, status=TaskStatus.COMPLETADA).all()
    
    for task in pending_tasks:
        if task.is_due_today():
            active_tasks.append(task)
    
    # Obtener usuarios locales
    local_users = LocalUser.query.filter_by(location_id=location.id).all()
    
    # Obtener tareas recientes completadas
    recent_completions = (db.session.query(TaskCompletion, Task, LocalUser)
                         .join(Task, TaskCompletion.task_id == Task.id)
                         .join(LocalUser, TaskCompletion.local_user_id == LocalUser.id)
                         .filter(Task.location_id == location.id)
                         .order_by(TaskCompletion.completion_date.desc())
                         .limit(10)
                         .all())
    
    # Generar datos para el gráfico de completados mensuales
    last_6_months = []
    monthly_counts = []
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    for i in range(5, -1, -1):
        month = (current_month - i) % 12
        if month == 0:
            month = 12
        year = current_year if month <= current_month else current_year - 1
        
        month_start = datetime(year, month, 1)
        if month == 12:
            next_month_start = datetime(year + 1, 1, 1)
        else:
            next_month_start = datetime(year, month + 1, 1)
            
        # Obtener completados de este mes
        month_count = TaskCompletion.query\
            .join(Task, TaskCompletion.task_id == Task.id)\
            .filter(Task.location_id == location.id)\
            .filter(TaskCompletion.completion_date >= month_start)\
            .filter(TaskCompletion.completion_date < next_month_start)\
            .count()
            
        # Formato del mes en español
        month_names = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        month_label = f"{month_names[month-1]} {year}"
        
        last_6_months.append(month_label)
        monthly_counts.append(month_count)
    
    # Obtener el enlace directo al portal
    portal_url = url_for('tasks.local_portal', location_id=location.id, _external=True)
    
    return render_template('tasks/location_detail.html',
                          title=f'Local: {location.name}',
                          location=location,
                          active_tasks=active_tasks,
                          pending_tasks=pending_tasks,
                          completed_tasks=completed_tasks,
                          local_users=local_users,
                          recent_completions=recent_completions,
                          monthly_labels=last_6_months,
                          monthly_counts=monthly_counts,
                          portal_url=portal_url)

# Rutas para gestión de usuarios locales
@tasks_bp.route('/locations/<int:location_id>/users')
@login_required
@manager_required
def list_local_users(location_id):
    """Lista de usuarios de un local"""
    location = Location.query.get_or_404(location_id)
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != location.company_id):
        flash('No tienes permiso para ver los usuarios de este local.', 'danger')
        return redirect(url_for('tasks.list_locations'))
    
    users = LocalUser.query.filter_by(location_id=location_id).all()
    
    return render_template('tasks/local_user_list.html',
                          title=f'Usuarios del Local: {location.name}',
                          location=location,
                          users=users)

@tasks_bp.route('/locations/<int:location_id>/users/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_local_user(location_id):
    """Crear un nuevo usuario local"""
    location = Location.query.get_or_404(location_id)
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != location.company_id):
        flash('No tienes permiso para crear usuarios en este local.', 'danger')
        return redirect(url_for('tasks.list_locations'))
    
    form = LocalUserForm()
    
    if form.validate_on_submit():
        # Generar nombre de usuario automáticamente (nombre + apellido + timestamp)
        timestamp = datetime.now().strftime('%y%m%d%H%M%S')
        username = f"{form.name.data.lower()}_{form.last_name.data.lower()}_{timestamp}"
        
        user = LocalUser(
            name=form.name.data,
            last_name=form.last_name.data,
            username=username,
            location_id=location_id,
            is_active=form.is_active.data
        )
        
        # Establecer PIN de acceso
        user.set_pin(form.pin.data)
        
        # Guardar foto si se proporciona
        if form.photo.data:
            filename = secure_filename(form.photo.data.filename)
            # Generar nombre único para evitar colisiones
            unique_filename = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'local_users', unique_filename)
            
            # Asegurar que existe el directorio
            os.makedirs(os.path.dirname(photo_path), exist_ok=True)
            
            # Guardar archivo
            form.photo.data.save(photo_path)
            user.photo_path = os.path.join('local_users', unique_filename)
        
        db.session.add(user)
        db.session.commit()
        
        log_activity(f'Usuario local creado: {user.name} en {location.name}')
        flash(f'Usuario "{user.name}" creado correctamente.', 'success')
        return redirect(url_for('tasks.list_local_users', location_id=location_id))
    
    return render_template('tasks/local_user_form.html',
                          title=f'Crear Usuario en {location.name}',
                          form=form,
                          location=location)

@tasks_bp.route('/locations/<int:location_id>/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_local_user(location_id, id):
    """Editar un usuario local existente"""
    location = Location.query.get_or_404(location_id)
    user = LocalUser.query.get_or_404(id)
    
    # Verificar que el usuario pertenece al local
    if user.location_id != location_id:
        flash('El usuario no pertenece a este local.', 'danger')
        return redirect(url_for('tasks.list_local_users', location_id=location_id))
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != location.company_id):
        flash('No tienes permiso para editar usuarios en este local.', 'danger')
        return redirect(url_for('tasks.list_locations'))
    
    # Crear formulario, PIN opcional para editarlo
    form = LocalUserForm(obj=user)
    form.pin.validators = [Optional()]  # Hacer el PIN opcional
    
    if form.validate_on_submit():
        user.name = form.name.data
        user.last_name = form.last_name.data
        user.is_active = form.is_active.data
        
        # Actualizar PIN solo si se proporciona
        if form.pin.data:
            user.set_pin(form.pin.data)
        
        # Actualizar foto si se proporciona
        if form.photo.data:
            # Eliminar foto anterior si existe
            if user.photo_path:
                old_photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user.photo_path)
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)
            
            filename = secure_filename(form.photo.data.filename)
            # Generar nombre único para evitar colisiones
            unique_filename = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'local_users', unique_filename)
            
            # Asegurar que existe el directorio
            os.makedirs(os.path.dirname(photo_path), exist_ok=True)
            
            # Guardar archivo
            form.photo.data.save(photo_path)
            user.photo_path = os.path.join('local_users', unique_filename)
        
        db.session.commit()
        
        log_activity(f'Usuario local actualizado: {user.name} en {location.name}')
        flash(f'Usuario "{user.name}" actualizado correctamente.', 'success')
        return redirect(url_for('tasks.list_local_users', location_id=location_id))
    
    # Eliminar valores del campo PIN para seguridad
    form.pin.data = ''
    
    return render_template('tasks/local_user_form.html',
                          title=f'Editar Usuario: {user.name}',
                          form=form,
                          location=location,
                          user=user)

@tasks_bp.route('/locations/<int:location_id>/users/delete/<int:id>', methods=['POST'])
@login_required
@manager_required
def delete_local_user(location_id, id):
    """Eliminar un usuario local"""
    location = Location.query.get_or_404(location_id)
    user = LocalUser.query.get_or_404(id)
    
    # Verificar que el usuario pertenece al local
    if user.location_id != location_id:
        flash('El usuario no pertenece a este local.', 'danger')
        return redirect(url_for('tasks.list_local_users', location_id=location_id))
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != location.company_id):
        flash('No tienes permiso para eliminar usuarios en este local.', 'danger')
        return redirect(url_for('tasks.list_locations'))
    
    # Verificar si tiene tareas completadas asociadas
    if user.completed_tasks:
        flash('No se puede eliminar este usuario porque tiene tareas completadas asociadas.', 'warning')
        return redirect(url_for('tasks.list_local_users', location_id=location_id))
    
    # Eliminar foto si existe
    if user.photo_path:
        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user.photo_path)
        if os.path.exists(photo_path):
            os.remove(photo_path)
    
    name = user.name
    db.session.delete(user)
    db.session.commit()
    
    log_activity(f'Usuario local eliminado: {name} de {location.name}')
    flash(f'Usuario "{name}" eliminado correctamente.', 'success')
    return redirect(url_for('tasks.list_local_users', location_id=location_id))

# Rutas para gestión de tareas
@tasks_bp.route('/locations/<int:location_id>/tasks')
@login_required
def list_tasks(location_id):
    """Lista de tareas de un local"""
    location = Location.query.get_or_404(location_id)
    
    # Verificar permisos (admin, gerente o empleado de la empresa)
    if not current_user.is_admin() and not (current_user.company_id == location.company_id):
        flash('No tienes permiso para ver las tareas de este local.', 'danger')
        return redirect(url_for('tasks.index'))
    
    # Filtrar por estado si se especifica
    status_filter = request.args.get('status')
    if status_filter and status_filter in [s.value for s in TaskStatus]:
        tasks = Task.query.filter_by(location_id=location_id, status=TaskStatus(status_filter)).all()
    else:
        tasks = Task.query.filter_by(location_id=location_id).all()
    
    # Agrupar tareas por estado
    tasks_by_status = {
        'pendiente': [],
        'completada': [],
        'vencida': [],
        'cancelada': []
    }
    
    for task in tasks:
        if task.status:
            tasks_by_status[task.status.value].append(task)
    
    return render_template('tasks/task_list.html',
                          title=f'Tareas del Local: {location.name}',
                          location=location,
                          tasks=tasks,
                          tasks_by_status=tasks_by_status)

@tasks_bp.route('/locations/<int:location_id>/tasks/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_task(location_id):
    """Crear una nueva tarea"""
    location = Location.query.get_or_404(location_id)
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != location.company_id):
        flash('No tienes permiso para crear tareas en este local.', 'danger')
        return redirect(url_for('tasks.list_locations'))
    
    form = TaskForm()
    form.location_id.choices = [(location.id, location.name)]
    
    # Cargar grupos de tareas disponibles para este local
    groups = TaskGroup.query.filter_by(location_id=location_id).all()
    group_choices = [(0, 'Ningún grupo')] + [(g.id, g.name) for g in groups]
    form.group_id.choices = group_choices
    
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            priority=TaskPriority(form.priority.data),
            frequency=TaskFrequency(form.frequency.data),
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            location_id=form.location_id.data,
            created_by_id=current_user.id,
            status=TaskStatus.PENDIENTE
        )
        
        # Asignar grupo de tareas si se seleccionó uno
        if form.group_id.data and form.group_id.data != 0:
            task.group_id = form.group_id.data
        
        db.session.add(task)
        db.session.commit()
        
        # Para tareas personalizadas, guardar los días seleccionados
        if task.frequency == TaskFrequency.PERSONALIZADA:
            # Crear registros de días seleccionados
            if form.monday.data:
                db.session.add(TaskWeekday(task_id=task.id, day_of_week=WeekDay.LUNES))
            if form.tuesday.data:
                db.session.add(TaskWeekday(task_id=task.id, day_of_week=WeekDay.MARTES))
            if form.wednesday.data:
                db.session.add(TaskWeekday(task_id=task.id, day_of_week=WeekDay.MIERCOLES))
            if form.thursday.data:
                db.session.add(TaskWeekday(task_id=task.id, day_of_week=WeekDay.JUEVES))
            if form.friday.data:
                db.session.add(TaskWeekday(task_id=task.id, day_of_week=WeekDay.VIERNES))
            if form.saturday.data:
                db.session.add(TaskWeekday(task_id=task.id, day_of_week=WeekDay.SABADO))
            if form.sunday.data:
                db.session.add(TaskWeekday(task_id=task.id, day_of_week=WeekDay.DOMINGO))
            
            db.session.commit()
        
        # Redirigir a la página de programación según la frecuencia
        log_activity(f'Tarea creada: {task.title} en {location.name}')
        flash(f'Tarea "{task.title}" creada correctamente. Ahora debes configurar su programación.', 'success')
        
        if task.frequency == TaskFrequency.DIARIA:
            return redirect(url_for('tasks.configure_daily_schedule', task_id=task.id))
        elif task.frequency == TaskFrequency.SEMANAL:
            return redirect(url_for('tasks.configure_weekly_schedule', task_id=task.id))
        elif task.frequency == TaskFrequency.MENSUAL:
            return redirect(url_for('tasks.configure_monthly_schedule', task_id=task.id))
        elif task.frequency == TaskFrequency.QUINCENAL:
            return redirect(url_for('tasks.configure_biweekly_schedule', task_id=task.id))
        else:
            return redirect(url_for('tasks.list_tasks', location_id=location_id))
    
    return render_template('tasks/task_form.html',
                          title=f'Crear Tarea en {location.name}',
                          form=form,
                          location=location,
                          location_id=location_id)

@tasks_bp.route('/tasks/<int:task_id>/daily-schedule', methods=['GET', 'POST'])
@login_required
@manager_required
def configure_daily_schedule(task_id):
    """Configurar horario diario para una tarea"""
    task = Task.query.get_or_404(task_id)
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != task.location.company_id):
        flash('No tienes permiso para configurar esta tarea.', 'danger')
        return redirect(url_for('tasks.list_tasks', location_id=task.location_id))
    
    # Verificar que sea una tarea diaria
    if task.frequency != TaskFrequency.DIARIA:
        flash('Esta tarea no es de frecuencia diaria.', 'warning')
        return redirect(url_for('tasks.list_tasks', location_id=task.location_id))
    
    # Buscar si ya existe un horario
    schedule = TaskSchedule.query.filter_by(task_id=task.id).first()
    
    form = DailyScheduleForm(obj=schedule)
    
    if form.validate_on_submit():
        if schedule:
            # Actualizar horario existente
            schedule.start_time = form.start_time.data
            schedule.end_time = form.end_time.data
        else:
            # Crear nuevo horario
            schedule = TaskSchedule(
                task_id=task.id,
                start_time=form.start_time.data,
                end_time=form.end_time.data
            )
            db.session.add(schedule)
        
        db.session.commit()
        
        log_activity(f'Horario diario configurado para tarea: {task.title}')
        flash('Horario configurado correctamente.', 'success')
        return redirect(url_for('tasks.list_tasks', location_id=task.location_id))
    
    return render_template('tasks/schedule_form.html',
                          title=f'Configurar Horario Diario: {task.title}',
                          form=form,
                          task=task,
                          schedule_type='diario')

@tasks_bp.route('/tasks/<int:task_id>/weekly-schedule', methods=['GET', 'POST'])
@login_required
@manager_required
def configure_weekly_schedule(task_id):
    """Configurar horario semanal para una tarea"""
    task = Task.query.get_or_404(task_id)
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != task.location.company_id):
        flash('No tienes permiso para configurar esta tarea.', 'danger')
        return redirect(url_for('tasks.list_tasks', location_id=task.location_id))
    
    # Verificar que sea una tarea semanal
    if task.frequency != TaskFrequency.SEMANAL:
        flash('Esta tarea no es de frecuencia semanal.', 'warning')
        return redirect(url_for('tasks.list_tasks', location_id=task.location_id))
    
    # Buscar si ya existe un horario
    schedule = TaskSchedule.query.filter_by(task_id=task.id).first()
    
    form = WeeklyScheduleForm(obj=schedule)
    
    if form.validate_on_submit():
        if schedule:
            # Actualizar horario existente
            schedule.day_of_week = WeekDay(form.day_of_week.data)
            schedule.start_time = form.start_time.data
            schedule.end_time = form.end_time.data
        else:
            # Crear nuevo horario
            schedule = TaskSchedule(
                task_id=task.id,
                day_of_week=WeekDay(form.day_of_week.data),
                start_time=form.start_time.data,
                end_time=form.end_time.data
            )
            db.session.add(schedule)
        
        db.session.commit()
        
        log_activity(f'Horario semanal configurado para tarea: {task.title}')
        flash('Horario configurado correctamente.', 'success')
        return redirect(url_for('tasks.list_tasks', location_id=task.location_id))
    
    return render_template('tasks/schedule_form.html',
                          title=f'Configurar Horario Semanal: {task.title}',
                          form=form,
                          task=task,
                          schedule_type='semanal')

@tasks_bp.route('/tasks/<int:task_id>/monthly-schedule', methods=['GET', 'POST'])
@login_required
@manager_required
def configure_monthly_schedule(task_id):
    """Configurar horario mensual para una tarea"""
    task = Task.query.get_or_404(task_id)
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != task.location.company_id):
        flash('No tienes permiso para configurar esta tarea.', 'danger')
        return redirect(url_for('tasks.list_tasks', location_id=task.location_id))
    
    # Verificar que sea una tarea mensual
    if task.frequency != TaskFrequency.MENSUAL:
        flash('Esta tarea no es de frecuencia mensual.', 'warning')
        return redirect(url_for('tasks.list_tasks', location_id=task.location_id))
    
    # Buscar si ya existe un horario
    schedule = TaskSchedule.query.filter_by(task_id=task.id).first()
    
    form = MonthlyScheduleForm(obj=schedule)
    
    if form.validate_on_submit():
        if schedule:
            # Actualizar horario existente
            schedule.day_of_month = form.day_of_month.data
            schedule.start_time = form.start_time.data
            schedule.end_time = form.end_time.data
        else:
            # Crear nuevo horario
            schedule = TaskSchedule(
                task_id=task.id,
                day_of_month=form.day_of_month.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data
            )
            db.session.add(schedule)
        
        db.session.commit()
        
        log_activity(f'Horario mensual configurado para tarea: {task.title}')
        flash('Horario configurado correctamente.', 'success')
        return redirect(url_for('tasks.list_tasks', location_id=task.location_id))
    
    return render_template('tasks/schedule_form.html',
                          title=f'Configurar Horario Mensual: {task.title}',
                          form=form,
                          task=task,
                          schedule_type='mensual')

@tasks_bp.route('/tasks/<int:task_id>/biweekly-schedule', methods=['GET', 'POST'])
@login_required
@manager_required
def configure_biweekly_schedule(task_id):
    """Configurar horario quincenal para una tarea"""
    task = Task.query.get_or_404(task_id)
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != task.location.company_id):
        flash('No tienes permiso para configurar esta tarea.', 'danger')
        return redirect(url_for('tasks.list_tasks', location_id=task.location_id))
    
    # Verificar que sea una tarea quincenal
    if task.frequency != TaskFrequency.QUINCENAL:
        flash('Esta tarea no es de frecuencia quincenal.', 'warning')
        return redirect(url_for('tasks.list_tasks', location_id=task.location_id))
    
    # Buscar si ya existe un horario
    schedule = TaskSchedule.query.filter_by(task_id=task.id).first()
    
    form = BiweeklyScheduleForm(obj=schedule)
    
    if form.validate_on_submit():
        if schedule:
            # Actualizar horario existente
            schedule.start_time = form.start_time.data
            schedule.end_time = form.end_time.data
        else:
            # Crear nuevo horario
            schedule = TaskSchedule(
                task_id=task.id,
                start_time=form.start_time.data,
                end_time=form.end_time.data
            )
            db.session.add(schedule)
        
        db.session.commit()
        
        log_activity(f'Horario quincenal configurado para tarea: {task.title}')
        flash('Horario configurado correctamente.', 'success')
        return redirect(url_for('tasks.list_tasks', location_id=task.location_id))
    
    return render_template('tasks/schedule_form.html',
                          title=f'Configurar Horario Quincenal: {task.title}',
                          form=form,
                          task=task,
                          schedule_type='quincenal')

@tasks_bp.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_task(task_id):
    """Editar una tarea existente"""
    task = Task.query.get_or_404(task_id)
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != task.location.company_id):
        flash('No tienes permiso para editar esta tarea.', 'danger')
        return redirect(url_for('tasks.list_tasks', location_id=task.location_id))
    
    form = TaskForm(obj=task)
    form.location_id.choices = [(task.location.id, task.location.name)]
    
    # Cargar grupos de tareas disponibles para este local
    groups = TaskGroup.query.filter_by(location_id=task.location_id).all()
    group_choices = [(0, 'Ningún grupo')] + [(g.id, g.name) for g in groups]
    form.group_id.choices = group_choices
    
    # Establecer el grupo seleccionado actualmente
    if task.group_id:
        form.group_id.data = task.group_id
    else:
        form.group_id.data = 0
    
    # Si es una tarea personalizada, marcar los días seleccionados
    if task.frequency == TaskFrequency.PERSONALIZADA:
        # Obtener los días de la semana configurados
        weekdays = TaskWeekday.query.filter_by(task_id=task.id).all()
        days_of_week = [day.day_of_week for day in weekdays]
        
        # Marcar los checkboxes correspondientes
        form.monday.data = WeekDay.LUNES in days_of_week
        form.tuesday.data = WeekDay.MARTES in days_of_week
        form.wednesday.data = WeekDay.MIERCOLES in days_of_week
        form.thursday.data = WeekDay.JUEVES in days_of_week
        form.friday.data = WeekDay.VIERNES in days_of_week
        form.saturday.data = WeekDay.SABADO in days_of_week
        form.sunday.data = WeekDay.DOMINGO in days_of_week
    
    # Guardar la frecuencia original
    original_frequency = task.frequency
    
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.priority = TaskPriority(form.priority.data)
        task.frequency = TaskFrequency(form.frequency.data)
        task.start_date = form.start_date.data
        task.end_date = form.end_date.data
        
        # Actualizar grupo de tareas
        if form.group_id.data and form.group_id.data != 0:
            task.group_id = form.group_id.data
        else:
            task.group_id = None
            
        db.session.commit()
        
        # Si la frecuencia es personalizada, actualizar los días de la semana
        if task.frequency == TaskFrequency.PERSONALIZADA:
            # Eliminar días existentes
            TaskWeekday.query.filter_by(task_id=task.id).delete()
            
            # Crear nuevos registros de días seleccionados
            if form.monday.data:
                db.session.add(TaskWeekday(task_id=task.id, day_of_week=WeekDay.LUNES))
            if form.tuesday.data:
                db.session.add(TaskWeekday(task_id=task.id, day_of_week=WeekDay.MARTES))
            if form.wednesday.data:
                db.session.add(TaskWeekday(task_id=task.id, day_of_week=WeekDay.MIERCOLES))
            if form.thursday.data:
                db.session.add(TaskWeekday(task_id=task.id, day_of_week=WeekDay.JUEVES))
            if form.friday.data:
                db.session.add(TaskWeekday(task_id=task.id, day_of_week=WeekDay.VIERNES))
            if form.saturday.data:
                db.session.add(TaskWeekday(task_id=task.id, day_of_week=WeekDay.SABADO))
            if form.sunday.data:
                db.session.add(TaskWeekday(task_id=task.id, day_of_week=WeekDay.DOMINGO))
            
            db.session.commit()
        
        log_activity(f'Tarea actualizada: {task.title}')
        
        # Si cambió la frecuencia, redirigir a configurar el horario
        if original_frequency != task.frequency:
            # Eliminar horarios anteriores
            TaskSchedule.query.filter_by(task_id=task.id).delete()
            db.session.commit()
            
            flash(f'Tarea "{task.title}" actualizada. La frecuencia ha cambiado, configura el nuevo horario.', 'success')
            
            if task.frequency == TaskFrequency.DIARIA:
                return redirect(url_for('tasks.configure_daily_schedule', task_id=task.id))
            elif task.frequency == TaskFrequency.SEMANAL:
                return redirect(url_for('tasks.configure_weekly_schedule', task_id=task.id))
            elif task.frequency == TaskFrequency.MENSUAL:
                return redirect(url_for('tasks.configure_monthly_schedule', task_id=task.id))
            elif task.frequency == TaskFrequency.QUINCENAL:
                return redirect(url_for('tasks.configure_biweekly_schedule', task_id=task.id))
        else:
            flash(f'Tarea "{task.title}" actualizada correctamente.', 'success')
            return redirect(url_for('tasks.list_tasks', location_id=task.location_id))
    
    return render_template('tasks/task_form.html',
                          title=f'Editar Tarea: {task.title}',
                          form=form,
                          task=task,
                          location=task.location,
                          location_id=task.location_id)

@tasks_bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
@manager_required
def delete_task(task_id):
    """Eliminar una tarea"""
    task = Task.query.get_or_404(task_id)
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != task.location.company_id):
        flash('No tienes permiso para eliminar esta tarea.', 'danger')
        return redirect(url_for('tasks.list_tasks', location_id=task.location_id))
    
    location_id = task.location_id
    title = task.title
    
    # Eliminar primero las programaciones y completados
    TaskSchedule.query.filter_by(task_id=task.id).delete()
    TaskCompletion.query.filter_by(task_id=task.id).delete()
    
    db.session.delete(task)
    db.session.commit()
    
    log_activity(f'Tarea eliminada: {title}')
    flash(f'Tarea "{title}" eliminada correctamente.', 'success')
    return redirect(url_for('tasks.list_tasks', location_id=location_id))

@tasks_bp.route('/tasks/<int:task_id>')
@login_required
def view_task(task_id):
    """Ver detalles de una tarea"""
    task = Task.query.get_or_404(task_id)
    
    # Verificar permisos (admin, gerente o empleado de la empresa)
    if not current_user.is_admin() and not (current_user.company_id == task.location.company_id):
        flash('No tienes permiso para ver esta tarea.', 'danger')
        return redirect(url_for('tasks.index'))
    
    # Obtener programación
    schedule = TaskSchedule.query.filter_by(task_id=task.id).first()
    
    # Obtener historial de completados
    completions = (db.session.query(TaskCompletion, LocalUser)
                  .join(LocalUser, TaskCompletion.local_user_id == LocalUser.id)
                  .filter(TaskCompletion.task_id == task.id)
                  .order_by(TaskCompletion.completion_date.desc())
                  .all())
    
    return render_template('tasks/task_detail.html',
                          title=f'Tarea: {task.title}',
                          task=task,
                          schedule=schedule,
                          completions=completions)

# Portal de acceso para usuarios locales
@tasks_bp.route('/portal')
def portal_selection():
    """Página de selección de portal"""
    # Añadir logging para diagnóstico
    print("[DEBUG] Accediendo a la selección de portal")
    try:
        # Obtener todos los locations disponibles
        locations = Location.query.filter_by(is_active=True).all()
        print(f"[DEBUG] Locales encontrados: {len(locations)}")
        return render_template('tasks/portal_selection.html',
                            title='Selección de Portal',
                            locations=locations)
    except Exception as e:
        print(f"[ERROR] Error en portal_selection: {str(e)}")
        # Devolver una respuesta mínima para evitar 500
        return f"Error: {str(e)}", 500

@tasks_bp.route('/portal-test')
def portal_test():
    """Ruta de prueba para diagnóstico"""
    try:
        # Intentamos primero una consulta simple sin usar los campos nuevos
        locations = db.session.query(Location.id, Location.name).filter_by(is_active=True).all()
        location_count = len(locations)
        location_names = [loc[1] for loc in locations]
        
        # Ahora verificamos los campos nuevos
        has_new_columns = True
        try:
            test_query = db.session.query(Location.id, Location.portal_username).first()
        except Exception as e:
            has_new_columns = False
            column_error = str(e)
        
        # Generar respuesta informativa
        result = {
            "status": "ok",
            "locations_count": location_count,
            "locations": location_names,
            "has_new_columns": has_new_columns
        }
        
        if not has_new_columns:
            result["column_error"] = column_error
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@tasks_bp.route('/portal/<int:location_id>', methods=['GET', 'POST'])
def portal_login(location_id):
    """Página de login para acceder al portal de un local"""
    location = Location.query.get_or_404(location_id)
    
    # Verificar si el portal tiene credenciales configuradas
    if not location.portal_username or not location.portal_password_hash:
        # Si no tiene credenciales, asignar unas por defecto
        if not location.portal_username:
            location.portal_username = f"portal_{location.id}"
        if not location.portal_password_hash:
            location.set_portal_password("1234")
        db.session.commit()
        flash("Se han configurado credenciales por defecto para este portal. Usuario: " + 
             f"{location.portal_username}, Contraseña: 1234", "info")
    
    form = PortalLoginForm()
    
    if form.validate_on_submit():
        print(f"Login attempt - Username: {form.username.data}, Location username: {location.portal_username}")
        print(f"Password check result: {location.check_portal_password(form.password.data)}")
        
        # Verificar las credenciales
        if form.username.data == location.portal_username and location.check_portal_password(form.password.data):
            # Guardar en sesión que estamos autenticados en este portal
            session['portal_authenticated'] = True
            session['portal_location_id'] = location.id
            
            # Redireccionar al portal real
            return redirect(url_for('tasks.local_portal', location_id=location.id))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    
    return render_template('tasks/portal_login.html',
                          title=f'Acceso al Portal {location.name}',
                          location=location,
                          form=form)

# Route removed to fix duplicate endpoint

@tasks_bp.route('/local-login', methods=['GET', 'POST'])
def local_login():
    """Redirigir a la página de login para usuarios locales (obsoleta)"""
    return redirect(url_for('tasks.portal_selection'))

@tasks_bp.route('/local-portal/<int:location_id>')
def local_portal(location_id):
    """Portal de acceso para un local"""
    location = Location.query.get_or_404(location_id)
    
    # Verificar si el usuario está autenticado en el portal
    if not session.get('portal_authenticated') or session.get('portal_location_id') != location.id:
        # Si no está autenticado, redireccionar al login del portal
        return redirect(url_for('tasks.portal_login', location_id=location.id))
    
    # Guardar ID del local en la sesión
    session['location_id'] = location_id
    
    # Obtener usuarios activos del local
    local_users = LocalUser.query.filter_by(location_id=location_id, is_active=True).all()
    
    # Si no hay usuarios, crear un admin por defecto
    if not local_users:
        try:
            # Crear usuario admin por defecto
            admin_user = LocalUser(
                name="Admin",
                last_name="Local",
                username=f"admin_{location_id}",
                is_active=True,
                location_id=location_id
            )
            
            # Establecer PIN 1234
            admin_user.set_pin("1234")
            
            db.session.add(admin_user)
            db.session.commit()
            
            # Refrescar la lista de usuarios
            local_users = [admin_user]
            
            # Mostrar mensaje informativo 
            flash("Se ha creado un usuario administrador por defecto con PIN: 1234", "info")
            
        except Exception as e:
            flash(f"No se pudo crear el usuario por defecto: {str(e)}", "warning")
    
    return render_template('tasks/local_portal.html',
                          title=f'Portal de {location.name}',
                          location=location,
                          local_users=local_users)

@tasks_bp.route('/local-user-login/<int:user_id>', methods=['GET', 'POST'])
def local_user_login(user_id):
    """Login con PIN para empleado local"""
    if 'location_id' not in session:
        return redirect(url_for('tasks.index'))
    
    user = LocalUser.query.get_or_404(user_id)
    
    # Verificar que pertenece al local correcto
    if user.location_id != session['location_id']:
        flash('Usuario no válido para este local.', 'danger')
        return redirect(url_for('tasks.local_portal', location_id=session['location_id']))
    
    form = LocalUserPinForm()
    
    if form.validate_on_submit():
        if user.check_pin(form.pin.data):
            # Guardar usuario en sesión
            session['local_user_id'] = user.id
            
            log_activity(f'Acceso de usuario local: {user.name} en {user.location.name}')
            flash(f'Bienvenido, {user.name}!', 'success')
            return redirect(url_for('tasks.local_user_tasks'))
        else:
            flash('PIN incorrecto.', 'danger')
    
    return render_template('tasks/local_user_pin.html',
                          title=f'Acceso de {user.name}',
                          form=form,
                          user=user)

@tasks_bp.route('/local-logout')
def local_logout():
    """Cerrar sesión de usuario local"""
    location_id = session.get('location_id')
    session.pop('local_user_id', None)
    flash('Has cerrado sesión correctamente.', 'success')
    
    if location_id:
        return redirect(url_for('tasks.local_portal', location_id=location_id))
    else:
        return redirect(url_for('tasks.index'))

@tasks_bp.route('/portal-logout')
def portal_logout():
    """Cerrar sesión de portal local"""
    # Limpiar todas las variables de sesión relacionadas con el portal
    session.pop('location_id', None)
    session.pop('local_user_username', None)
    session.pop('local_user_id', None)
    session.pop('portal_authenticated', None)
    session.pop('portal_location_id', None)
    
    flash('Has cerrado sesión del portal correctamente.', 'success')
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/local-user/tasks')
@tasks_bp.route('/local-user/tasks/<string:date_str>')
@local_user_required
def local_user_tasks(date_str=None):
    """Panel de tareas para usuario local"""
    user_id = session['local_user_id']
    user = LocalUser.query.get_or_404(user_id)
    location = user.location
    
    # Determinar la fecha de las tareas (hoy por defecto, o la especificada)
    today = date.today()
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today
    
    # Calcular fechas para el carrusel (día anterior, actual, siguiente)
    prev_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)
    
    # Determinar los nombres de los días en español
    days_map = {
        0: 'LUN',
        1: 'MAR',
        2: 'MIÉ',
        3: 'JUE',
        4: 'VIE', 
        5: 'SÁB',
        6: 'DOM'
    }
    
    # Configurar el carrusel de fechas
    date_carousel = [
        {
            'date': prev_date,
            'day_name': days_map[prev_date.weekday()],
            'day': prev_date.day,
            'url': url_for('tasks.local_user_tasks', date_str=prev_date.strftime('%Y-%m-%d')),
            'active': False
        },
        {
            'date': selected_date,
            'day_name': days_map[selected_date.weekday()],
            'day': selected_date.day,
            'url': url_for('tasks.local_user_tasks', date_str=selected_date.strftime('%Y-%m-%d')),
            'active': True
        },
        {
            'date': next_date, 
            'day_name': days_map[next_date.weekday()],
            'day': next_date.day,
            'url': url_for('tasks.local_user_tasks', date_str=next_date.strftime('%Y-%m-%d')),
            'active': False
        }
    ]
    
    # Inicializar colecciones
    active_tasks = []
    grouped_tasks = {}  # Diccionario para agrupar tareas por grupo
    ungrouped_tasks = [] # Lista para tareas sin grupo
    pending_tasks = Task.query.filter_by(location_id=location.id, status=TaskStatus.PENDIENTE).all()
    
    # Obtener grupos de tareas para esta ubicación
    task_groups = TaskGroup.query.filter_by(location_id=location.id).all()
    group_dict = {group.id: group for group in task_groups}
    
    # Obtener todas las completadas de la fecha seleccionada
    all_completions = db.session.query(
        TaskCompletion, LocalUser
    ).join(
        LocalUser, TaskCompletion.local_user_id == LocalUser.id
    ).filter(
        TaskCompletion.task_id.in_([t.id for t in pending_tasks]),
        db.func.date(TaskCompletion.completion_date) == selected_date
    ).order_by(
        TaskCompletion.completion_date.desc()
    ).all()
    
    # Crear un diccionario de información de completado por tarea
    completion_info = {}
    for completion, local_user in all_completions:
        completion_info[completion.task_id] = {
            'user': f"{local_user.name} {local_user.last_name}",
            'time': completion.completion_date.strftime('%H:%M'),
            'completed_by_me': local_user.id == user_id
        }
    
    # Completiones específicas para este usuario en la fecha seleccionada
    user_completions = TaskCompletion.query.filter_by(
        local_user_id=user_id
    ).filter(
        db.func.date(TaskCompletion.completion_date) == selected_date
    ).order_by(
        TaskCompletion.completion_date.desc()
    ).all()
    
    # Lista de IDs de tareas completadas en la fecha seleccionada
    completed_task_ids = [c.task_id for c, _ in all_completions]
    
    # Función auxiliar para comprobar si una tarea debe aparecer en la fecha seleccionada
    def task_is_due_on_date(task, check_date):
        # Si la fecha está fuera del rango de fechas de la tarea, no es debido
        if task.start_date and check_date < task.start_date:
            return False
        if task.end_date and check_date > task.end_date:
            return False
        
        # Verificar frecuencia
        if task.frequency == TaskFrequency.DIARIA:
            return True
        
        # Para tareas semanales, verificar día de la semana
        if task.frequency == TaskFrequency.SEMANAL:
            weekday_name = WeekDay(days_map[check_date.weekday()].lower())
            for schedule in task.schedule_details:
                if schedule.day_of_week and schedule.day_of_week.value == weekday_name.value:
                    return True
            return False
        
        # Para tareas quincenales, verificar quincena
        if task.frequency == TaskFrequency.QUINCENAL:
            start_date = task.start_date or task.created_at.date()
            days_diff = (check_date - start_date).days
            return days_diff % 14 == 0
        
        # Para tareas mensuales, verificar día del mes
        if task.frequency == TaskFrequency.MENSUAL:
            # Si hay horario mensual definido, verificar día del mes
            schedules = [s for s in task.schedule_details if s.day_of_month]
            if schedules:
                return any(s.day_of_month == check_date.day for s in schedules)
            # Si no hay horario específico, usar el día de inicio como referencia
            start_date = task.start_date or task.created_at.date()
            return start_date.day == check_date.day
        
        # Para tareas personalizadas, verificar días específicos
        if task.frequency == TaskFrequency.PERSONALIZADA:
            # Verificar si alguno de los días de la semana coincide
            weekday_value = days_map[check_date.weekday()].lower()
            for weekday in task.weekdays:
                if weekday.day_of_week.value == weekday_value:
                    return True
            return False
        
        return False
    
    for task in pending_tasks:
        # Usar la nueva función para verificar tareas en fechas específicas
        task_due = False
        if selected_date == today:
            # Para hoy, usar el método existente por compatibilidad
            task_due = task.is_due_today()
        else:
            # Para otras fechas, usar nuestra nueva lógica
            task_due = task_is_due_on_date(task, selected_date)
            
        if task_due:
            # Verificar si ya ha sido completada
            task.completed_today = task.id in completed_task_ids
            
            # Agregar información de quién completó la tarea
            if task.id in completion_info:
                task.completion_info = completion_info[task.id]
            
            active_tasks.append(task)
            
            # Agrupar por grupo si tiene uno
            if task.group_id and task.group_id in group_dict:
                group_id = task.group_id
                if group_id not in grouped_tasks:
                    grouped_tasks[group_id] = {
                        'group': group_dict[group_id],
                        'tasks': []
                    }
                grouped_tasks[group_id]['tasks'].append(task)
            else:
                ungrouped_tasks.append(task)
    
    return render_template('tasks/local_user_tasks.html',
                          title=f'Tareas de {user.name}',
                          user=user,
                          local_user=user,
                          location=location,
                          active_tasks=active_tasks,
                          ungrouped_tasks=ungrouped_tasks,
                          grouped_tasks=grouped_tasks,
                          task_groups=task_groups,
                          completed_tasks=user_completions,
                          selected_date=selected_date,
                          today=today, 
                          date_carousel=date_carousel)

@tasks_bp.route('/local-user/tasks/<int:task_id>/complete', methods=['GET', 'POST'])
@local_user_required
def complete_task(task_id):
    """Marcar una tarea como completada (versión con formulario)"""
    user_id = session['local_user_id']
    user = LocalUser.query.get_or_404(user_id)
    task = Task.query.get_or_404(task_id)
    
    # Verificar que la tarea pertenece al local del usuario
    if task.location_id != user.location_id:
        flash('Tarea no válida para este local.', 'danger')
        return redirect(url_for('tasks.local_user_tasks'))
    
    # Verificar si ya ha sido completada hoy por este usuario
    today = date.today()
    completion = TaskCompletion.query.filter_by(
        task_id=task.id,
        local_user_id=user_id
    ).filter(
        db.func.date(TaskCompletion.completion_date) == today
    ).first()
    
    if completion:
        flash('Ya has completado esta tarea hoy.', 'warning')
        return redirect(url_for('tasks.local_user_tasks'))
    
    form = TaskCompletionForm()
    
    if form.validate_on_submit():
        completion = TaskCompletion(
            task_id=task.id,
            local_user_id=user_id,
            notes=form.notes.data
        )
        
        db.session.add(completion)
        db.session.commit()
        
        log_activity(f'Tarea completada: {task.title} por {user.name}')
        flash('¡Tarea completada correctamente!', 'success')
        return redirect(url_for('tasks.local_user_tasks'))
    
    return render_template('tasks/complete_task.html',
                          title=f'Completar Tarea: {task.title}',
                          form=form,
                          task=task,
                          user=user)

@tasks_bp.route('/local-user/tasks/<int:task_id>/ajax-complete', methods=['POST'])
@local_user_required
def ajax_complete_task(task_id):
    """Marcar una tarea como completada (versión AJAX)"""
    user_id = session['local_user_id']
    user = LocalUser.query.get_or_404(user_id)
    task = Task.query.get_or_404(task_id)
    
    # Verificar que la solicitud es AJAX
    if not request.is_json:
        return jsonify({'error': 'Se requiere petición JSON'}), 400
    
    # Verificar que la tarea pertenece al local del usuario
    if task.location_id != user.location_id:
        return jsonify({'error': 'Tarea no válida para este local'}), 403
    
    # Verificar si ya ha sido completada hoy por este usuario
    today = date.today()
    existing_completion = TaskCompletion.query.filter_by(
        task_id=task.id,
        local_user_id=user_id
    ).filter(
        db.func.date(TaskCompletion.completion_date) == today
    ).first()
    
    if existing_completion:
        return jsonify({'error': 'Ya has completado esta tarea hoy'}), 400
    
    # Obtener notas (opcional)
    data = request.json
    notes = data.get('notes', '')
    
    # Crear registro de tarea completada
    completion = TaskCompletion(
        task_id=task.id,
        local_user_id=user_id,
        notes=notes
    )
    
    db.session.add(completion)
    db.session.commit()
    
    log_activity(f'Tarea completada (AJAX): {task.title} por {user.name}')
    
    # Devolver información para actualizar la UI
    return jsonify({
        'success': True,
        'taskId': task.id,
        'taskTitle': task.title,
        'completedBy': f"{user.name} {user.last_name}",
        'completedAt': datetime.now().strftime('%H:%M')
    })

# API para regenerar contraseña del portal
@tasks_bp.route('/api/regenerate-password/<int:location_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def regenerate_password(location_id):
    """Regenera la contraseña del portal de un local y la devuelve"""
    location = Location.query.get_or_404(location_id)
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != location.company_id):
        return jsonify({'error': 'No tienes permiso para regenerar la contraseña de este local'}), 403
    
    # Si es GET con show_only=true, solo devuelve la contraseña actual sin regenerarla
    if request.method == 'GET' and request.args.get('show_only') == 'true':
        # Obtener la contraseña actual usando la misma función pero sin actualizar
        current_password = regenerate_portal_password(location_id, only_return=True)
        if not current_password:
            return jsonify({'error': 'Error al obtener la contraseña'}), 500
        
        return jsonify({'success': True, 'password': current_password})
    
    # Si es POST, regenera la contraseña
    new_password = regenerate_portal_password(location_id)
    if not new_password:
        return jsonify({'error': 'Error al regenerar la contraseña'}), 500
    
    log_activity(f'Contraseña de portal regenerada para el local: {location.name}')
    return jsonify({'success': True, 'password': new_password})

# API para obtener credenciales del portal
@tasks_bp.route('/api/get-portal-credentials/<int:location_id>', methods=['GET'])
@login_required
@manager_required
def get_portal_credentials(location_id):
    """Obtiene las credenciales del portal (solo el username)"""
    location = Location.query.get_or_404(location_id)
    
    # Verificar permisos (admin o gerente de la empresa)
    if not current_user.is_admin() and (not current_user.is_gerente() or current_user.company_id != location.company_id):
        return jsonify({'error': 'No tienes permiso para obtener las credenciales de este local'}), 403
    
    return jsonify({
        'success': True,
        'username': location.portal_username
    })

# API para estadísticas en tiempo real
@tasks_bp.route('/api/task-stats')
@login_required
def task_stats():
    """API para obtener estadísticas de tareas"""
    if current_user.is_admin():
        # Administradores ven estadísticas globales
        locations = Location.query.all()
        location_ids = [loc.id for loc in locations]
    elif current_user.is_gerente() and current_user.company_id:
        # Gerentes ven solo su empresa
        locations = Location.query.filter_by(company_id=current_user.company_id).all()
        location_ids = [loc.id for loc in locations]
    else:
        # Otros usuarios no ven nada
        return jsonify({'error': 'No autorizado'}), 403
    
    # Si no hay locales, devolver valores vacíos
    if not location_ids:
        return jsonify({
            'total_tasks': 0,
            'pending_tasks': 0,
            'completed_tasks': 0,
            'completion_rate': 0,
            'tasks_by_priority': {},
            'tasks_by_location': {}
        })
    
    # Contar tareas
    total_tasks = Task.query.filter(Task.location_id.in_(location_ids)).count()
    pending_tasks = Task.query.filter(Task.location_id.in_(location_ids), 
                                     Task.status==TaskStatus.PENDIENTE).count()
    completed_tasks = Task.query.filter(Task.location_id.in_(location_ids), 
                                       Task.status==TaskStatus.COMPLETADA).count()
    
    # Calcular tasa de completado
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Tareas por prioridad
    tasks_by_priority_query = db.session.query(
        Task.priority,
        db.func.count(Task.id)
    ).filter(
        Task.location_id.in_(location_ids)
    ).group_by(Task.priority).all()
    
    tasks_by_priority = {}
    for priority, count in tasks_by_priority_query:
        if priority:
            tasks_by_priority[priority.value] = count
    
    # Tareas por local
    tasks_by_location_query = db.session.query(
        Location.name,
        db.func.count(Task.id)
    ).join(
        Task, Location.id == Task.location_id
    ).filter(
        Location.id.in_(location_ids)
    ).group_by(Location.name).all()
    
    tasks_by_location = {}
    for location_name, count in tasks_by_location_query:
        tasks_by_location[location_name] = count
    
    return jsonify({
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'completion_rate': completion_rate,
        'tasks_by_priority': tasks_by_priority,
        'tasks_by_location': tasks_by_location
    })