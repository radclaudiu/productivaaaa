from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, date
import os
from werkzeug.utils import secure_filename
from wtforms.validators import Optional

from app import db
from models import User, Company
from models_tasks import Location, LocalUser, Task, TaskSchedule, TaskCompletion, TaskPriority, TaskFrequency, TaskStatus, WeekDay
from forms_tasks import (LocationForm, LocalUserForm, TaskForm, DailyScheduleForm, WeeklyScheduleForm, 
                        MonthlyScheduleForm, BiweeklyScheduleForm, TaskCompletionForm, LocalUserLoginForm, 
                        LocalUserPinForm, SearchForm)
from utils import log_activity, can_manage_company, save_file

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
        'tasks_completed_today': TaskCompletion.query.filter(TaskCompletion.completion_date >= datetime.combine(today, datetime.min.time())).count()
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
            is_active=form.is_active.data
        )
        
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

@tasks_bp.route('/locations/<int:id>')
@login_required
def view_location(id):
    """Ver detalles de un local"""
    location = Location.query.get_or_404(id)
    
    # Verificar permisos (admin, gerente de la empresa, o empleado de la empresa)
    if not current_user.is_admin() and not (current_user.company_id == location.company_id):
        flash('No tienes permiso para ver este local.', 'danger')
        return redirect(url_for('tasks.index'))
    
    # Obtener tareas activas para hoy
    today = date.today()
    active_tasks = []
    pending_tasks = Task.query.filter_by(location_id=location.id, status=TaskStatus.PENDIENTE).all()
    
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
    
    return render_template('tasks/location_detail.html',
                          title=f'Local: {location.name}',
                          location=location,
                          active_tasks=active_tasks,
                          local_users=local_users,
                          recent_completions=recent_completions)

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
        user = LocalUser(
            name=form.name.data,
            username=form.username.data,
            location_id=location_id,
            is_active=form.is_active.data
        )
        
        # Establecer contraseña y PIN
        user.set_password(form.password.data)
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
    
    # Crear formulario sin los campos de contraseña y PIN
    form = LocalUserForm(obj=user)
    form.password.validators = []  # Hacer el campo de contraseña opcional
    form.confirm_password.validators = []
    form.pin.validators = [Optional()]  # Hacer el PIN opcional
    
    if form.validate_on_submit():
        user.name = form.name.data
        user.username = form.username.data
        user.is_active = form.is_active.data
        
        # Actualizar contraseña solo si se proporciona
        if form.password.data:
            user.set_password(form.password.data)
        
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
    
    # Eliminar valores de los campos sensibles
    form.password.data = ''
    form.confirm_password.data = ''
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
        
        db.session.add(task)
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
                          location=location)

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
    
    # Guardar la frecuencia original
    original_frequency = task.frequency
    
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.priority = TaskPriority(form.priority.data)
        task.frequency = TaskFrequency(form.frequency.data)
        task.start_date = form.start_date.data
        task.end_date = form.end_date.data
        
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
                          location=task.location)

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
@tasks_bp.route('/local-login', methods=['GET', 'POST'])
def local_login():
    """Página de login para usuarios locales"""
    form = LocalUserLoginForm()
    
    if form.validate_on_submit():
        user = LocalUser.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            # Almacenar ID de local en sesión para PIN
            session['location_id'] = user.location_id
            session['local_user_username'] = user.username
            
            log_activity(f'Acceso a portal de local: {user.location.name}')
            flash(f'Bienvenido al portal de {user.location.name}', 'success')
            return redirect(url_for('tasks.local_portal'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    
    return render_template('tasks/local_login.html',
                          title='Acceso a Portal de Local',
                          form=form)

@tasks_bp.route('/local-portal')
def local_portal():
    """Portal de acceso para un local"""
    if 'location_id' not in session:
        return redirect(url_for('tasks.local_login'))
    
    location_id = session['location_id']
    location = Location.query.get_or_404(location_id)
    
    # Obtener usuarios del local
    users = LocalUser.query.filter_by(location_id=location_id, is_active=True).all()
    
    return render_template('tasks/local_portal.html',
                          title=f'Portal de {location.name}',
                          location=location,
                          users=users)

@tasks_bp.route('/local-user-login/<int:user_id>', methods=['GET', 'POST'])
def local_user_login(user_id):
    """Login con PIN para empleado local"""
    if 'location_id' not in session:
        return redirect(url_for('tasks.local_login'))
    
    user = LocalUser.query.get_or_404(user_id)
    
    # Verificar que pertenece al local correcto
    if user.location_id != session['location_id']:
        flash('Usuario no válido para este local.', 'danger')
        return redirect(url_for('tasks.local_portal'))
    
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
    session.pop('local_user_id', None)
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('tasks.local_portal'))

@tasks_bp.route('/portal-logout')
def portal_logout():
    """Cerrar sesión de portal local"""
    session.pop('location_id', None)
    session.pop('local_user_username', None)
    session.pop('local_user_id', None)
    flash('Has cerrado sesión del portal correctamente.', 'success')
    return redirect(url_for('tasks.local_login'))

@tasks_bp.route('/local-user/tasks')
@local_user_required
def local_user_tasks():
    """Panel de tareas para usuario local"""
    user_id = session['local_user_id']
    user = LocalUser.query.get_or_404(user_id)
    location = user.location
    
    # Obtener tareas activas para hoy
    today = date.today()
    active_tasks = []
    pending_tasks = Task.query.filter_by(location_id=location.id, status=TaskStatus.PENDIENTE).all()
    
    for task in pending_tasks:
        if task.is_due_today():
            # Verificar si ya ha sido completada hoy por este usuario
            completion = TaskCompletion.query.filter_by(
                task_id=task.id,
                local_user_id=user_id
            ).filter(
                db.func.date(TaskCompletion.completion_date) == today
            ).first()
            
            task.completed_today = completion is not None
            active_tasks.append(task)
    
    return render_template('tasks/local_user_tasks.html',
                          title=f'Tareas de {user.name}',
                          user=user,
                          location=location,
                          active_tasks=active_tasks)

@tasks_bp.route('/local-user/tasks/<int:task_id>/complete', methods=['GET', 'POST'])
@local_user_required
def complete_task(task_id):
    """Marcar una tarea como completada"""
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