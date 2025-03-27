from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from app import db
from models_tasks import LocalUser, Location, Task, TaskCompletion, TaskGroup
from models_tasks import TaskStatus, TaskPriority, TaskFrequency, Product, ProductConservation, LabelTemplate
from sqlalchemy import text
import logging

# Configurar blueprint para las rutas de API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Configuración de JWT
jwt = JWTManager()

def init_api(app):
    """Inicializa la configuración de JWT para la API"""
    jwt.init_app(app)
    
    # Comprobar si el blueprint ya está registrado
    if not any(bp.name == 'api' for bp in app.blueprints.values()):
        app.register_blueprint(api_bp)

# Función auxiliar para determinar si una tarea debe mostrarse en una fecha específica
def task_is_due_on_date(task, check_date):
    # Si la fecha está fuera del rango de fechas de la tarea, no es debido
    if task.start_date and check_date < task.start_date:
        return False
    if task.end_date and check_date > task.end_date:
        return False
    
    # Para tareas diarias, siempre están activas (si están dentro del rango de fechas)
    if task.frequency == TaskFrequency.DIARIA:
        return True
    
    # Para tareas personalizadas con múltiples días, verificamos los días configurados
    if task.frequency == TaskFrequency.PERSONALIZADA:
        if task.weekdays:
            check_weekday = check_date.weekday()
            days_map = {0: 'lunes', 1: 'martes', 2: 'miercoles', 3: 'jueves', 4: 'viernes', 5: 'sabado', 6: 'domingo'}
            weekday_value = days_map[check_weekday]
            for weekday_entry in task.weekdays:
                if weekday_entry.day_of_week.value == weekday_value:
                    return True
            # Si llegamos aquí, es que el día seleccionado no es uno de los días configurados
            return False
        else:
            # Si no tiene días específicos configurados, mostrar la tarea
            return True
    
    # Si no hay programación específica (schedule_details está vacío)
    if not task.schedule_details:
        # Para tareas semanales, verificamos si check_date es el mismo día de la semana que start_date
        if task.frequency == TaskFrequency.SEMANAL and task.start_date:
            return check_date.weekday() == task.start_date.weekday()
            
        # Para tareas mensuales, verificamos si check_date es el mismo día del mes que start_date
        elif task.frequency == TaskFrequency.MENSUAL and task.start_date:
            return check_date.day == task.start_date.day
            
        # Para tareas quincenales, verificamos si han pasado múltiplos de 14 días desde start_date
        elif task.frequency == TaskFrequency.QUINCENAL and task.start_date:
            delta = (check_date - task.start_date).days
            return delta % 14 == 0
        
        # Para cualquier otro caso, mostramos la tarea
        return True
    
    from models_tasks import WeekDay
    # Comprobamos la programación específica
    for schedule in task.schedule_details:
        # Para tareas semanales, comprobamos el día de la semana
        if task.frequency == TaskFrequency.SEMANAL and schedule.day_of_week:
            day_map = {
                WeekDay.LUNES: 0,
                WeekDay.MARTES: 1,
                WeekDay.MIERCOLES: 2,
                WeekDay.JUEVES: 3,
                WeekDay.VIERNES: 4,
                WeekDay.SABADO: 5,
                WeekDay.DOMINGO: 6
            }
            if check_date.weekday() == day_map[schedule.day_of_week]:
                return True
            
        # Para tareas mensuales, comprobamos el día del mes
        elif task.frequency == TaskFrequency.MENSUAL and schedule.day_of_month:
            if check_date.day == schedule.day_of_month:
                return True
            
        # Para tareas quincenales
        elif task.frequency == TaskFrequency.QUINCENAL and task.start_date:
            delta = (check_date - task.start_date).days
            if delta % 14 == 0:
                return True
                
    # Si no hay ninguna coincidencia, la tarea no está activa para la fecha seleccionada
    return False

# Rutas de autenticación
@api_bp.route('/auth/login', methods=['POST'])
def login():
    """
    Autentica a un usuario local y devuelve un token JWT
    ---
    Espera recibir:
    {
        "username": "nombre_usuario",
        "password": "contraseña"
    }
    ó
    {
        "location_id": 123,
        "password": "contraseña_portal"
    }
    """
    if not request.is_json:
        return jsonify({"error": "Se requiere datos en formato JSON"}), 400
    
    data = request.json
    
    # Autenticación mediante usuario/contraseña
    if 'username' in data and 'password' in data:
        username = data.get('username')
        password = data.get('password')
        
        user = LocalUser.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({"error": "Credenciales incorrectas"}), 401
        
        # Generar tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "last_name": user.last_name,
                "username": user.username,
                "location_id": user.location_id,
                "location_name": user.location.name if user.location else None
            },
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    
    # Autenticación mediante location_id/password
    elif 'location_id' in data and 'password' in data:
        location_id = data.get('location_id')
        password = data.get('password')
        
        location = Location.query.get(location_id)
        
        if not location:
            return jsonify({"error": "Local no encontrado"}), 404
        
        # Verificar contraseña
        if not location.check_password(password):
            return jsonify({"error": "Contraseña del portal incorrecta"}), 401
        
        # Crear un usuario temporal para la sesión
        # En este caso, generamos un token sin un usuario específico pero con el location_id
        access_token = create_access_token(identity=f"location_{location_id}")
        refresh_token = create_refresh_token(identity=f"location_{location_id}")
        
        return jsonify({
            "success": True,
            "location": {
                "id": location.id,
                "name": location.name,
                "company_id": location.company_id,
                "company_name": location.company.name if location.company else None
            },
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    
    else:
        return jsonify({"error": "Faltan datos de autenticación"}), 400

@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """
    Renueva el token de acceso usando el refresh_token
    """
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    
    return jsonify({
        "success": True,
        "access_token": new_access_token
    })

@api_bp.route('/auth/user', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Devuelve los datos del usuario autenticado
    """
    current_user_id = get_jwt_identity()
    
    # Si es un location_id (autenticación por local)
    if isinstance(current_user_id, str) and current_user_id.startswith("location_"):
        location_id = int(current_user_id.split("_")[1])
        location = Location.query.get(location_id)
        
        if not location:
            return jsonify({"error": "Local no encontrado"}), 404
        
        return jsonify({
            "success": True,
            "is_location": True,
            "location": {
                "id": location.id,
                "name": location.name,
                "company_id": location.company_id
            }
        })
    
    # Si es un usuario normal
    else:
        user = LocalUser.query.get(current_user_id)
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        return jsonify({
            "success": True,
            "is_location": False,
            "user": {
                "id": user.id,
                "name": user.name,
                "last_name": user.last_name,
                "username": user.username,
                "location_id": user.location_id
            }
        })

# Obtener información de una ubicación
@api_bp.route('/locations/<int:location_id>', methods=['GET'])
@jwt_required()
def get_location(location_id):
    """
    Devuelve los datos de una ubicación
    """
    location = Location.query.get_or_404(location_id)
    
    return jsonify({
        "success": True,
        "location": {
            "id": location.id,
            "name": location.name,
            "address": location.address,
            "city": location.city,
            "company_id": location.company_id,
            "company_name": location.company.name if location.company else None
        }
    })

# Rutas para las tareas
@api_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """
    Devuelve todas las tareas activas para el usuario autenticado
    """
    current_user_id = get_jwt_identity()
    
    # Determinar a qué local pertenece el usuario
    if isinstance(current_user_id, str) and current_user_id.startswith("location_"):
        location_id = int(current_user_id.split("_")[1])
    else:
        user = LocalUser.query.get_or_404(current_user_id)
        location_id = user.location_id
    
    # Verificar si el location_id existe
    if not location_id:
        return jsonify({"error": "No hay un local asociado a este usuario"}), 400
    
    # Obtener todas las tareas pendientes
    tasks = Task.query.filter_by(location_id=location_id, status=TaskStatus.PENDIENTE).all()
    
    # Obtener la fecha actual
    today = date.today()
    
    # Filtrar las tareas que son para hoy
    active_tasks = []
    for task in tasks:
        if task.is_due_today():
            active_tasks.append(task)
    
    # Obtener completados de hoy
    completions = TaskCompletion.query.filter(
        TaskCompletion.task_id.in_([t.id for t in active_tasks]),
        db.func.date(TaskCompletion.completion_date) == today
    ).all()
    
    # Crear un set de ids de tareas completadas
    completed_task_ids = {c.task_id for c in completions}
    
    # Convertir las tareas a formato JSON
    tasks_json = []
    for task in active_tasks:
        task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description or "",
            "priority": task.priority.value if task.priority else "baja",
            "frequency": task.frequency.value if task.frequency else "diaria",
            "start_date": task.start_date.isoformat() if task.start_date else None,
            "end_date": task.end_date.isoformat() if task.end_date else None,
            "group_id": task.group_id,
            "group_name": task.group.name if task.group else None,
            "group_color": task.group.color if task.group else "#CCCCCC",
            "completed_today": task.id in completed_task_ids
        }
        tasks_json.append(task_data)
    
    return jsonify({
        "success": True,
        "tasks": tasks_json,
        "date": today.isoformat()
    })

@api_bp.route('/tasks/date/<string:date_str>', methods=['GET'])
@jwt_required()
def get_tasks_by_date(date_str):
    """
    Devuelve las tareas para una fecha específica (formato ISO: YYYY-MM-DD)
    """
    current_user_id = get_jwt_identity()
    
    # Determinar a qué local pertenece el usuario
    if isinstance(current_user_id, str) and current_user_id.startswith("location_"):
        location_id = int(current_user_id.split("_")[1])
    else:
        user = LocalUser.query.get_or_404(current_user_id)
        location_id = user.location_id
    
    # Verificar si el location_id existe
    if not location_id:
        return jsonify({"error": "No hay un local asociado a este usuario"}), 400
    
    # Convertir string a fecha
    try:
        selected_date = date.fromisoformat(date_str)
    except ValueError:
        return jsonify({"error": "Formato de fecha incorrecto. Use ISO format (YYYY-MM-DD)"}), 400
    
    # Obtener todas las tareas pendientes
    tasks = Task.query.filter_by(location_id=location_id, status=TaskStatus.PENDIENTE).all()
    
    # Filtrar tareas para la fecha seleccionada
    active_tasks = []
    for task in tasks:
        if selected_date == date.today():
            # Para hoy, usar el método existente por compatibilidad
            task_due = task.is_due_today()
        else:
            # Para otras fechas, usar nuestra lógica específica
            task_due = task_is_due_on_date(task, selected_date)
            
        if task_due:
            active_tasks.append(task)
    
    # Obtener completados para esa fecha
    completions = TaskCompletion.query.filter(
        TaskCompletion.task_id.in_([t.id for t in active_tasks]),
        db.func.date(TaskCompletion.completion_date) == selected_date
    ).all()
    
    # Crear un set de ids de tareas completadas
    completed_task_ids = {c.task_id for c in completions}
    
    # Convertir las tareas a formato JSON
    tasks_json = []
    for task in active_tasks:
        task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description or "",
            "priority": task.priority.value if task.priority else "baja",
            "frequency": task.frequency.value if task.frequency else "diaria",
            "start_date": task.start_date.isoformat() if task.start_date else None,
            "end_date": task.end_date.isoformat() if task.end_date else None,
            "group_id": task.group_id,
            "group_name": task.group.name if task.group else None,
            "group_color": task.group.color if task.group else "#CCCCCC",
            "completed_today": task.id in completed_task_ids
        }
        tasks_json.append(task_data)
    
    return jsonify({
        "success": True,
        "tasks": tasks_json,
        "date": selected_date.isoformat()
    })

@api_bp.route('/tasks/<int:task_id>/complete', methods=['POST'])
@jwt_required()
def complete_task(task_id):
    """
    Marca una tarea como completada
    """
    current_user_id = get_jwt_identity()
    
    # Obtener notas (opcional)
    data = request.json or {}
    notes = data.get('notes', '')
    
    # Determinar el usuario que completa
    if isinstance(current_user_id, str) and current_user_id.startswith("location_"):
        location_id = int(current_user_id.split("_")[1])
        
        # Si se ha especificado un LocalUser específico del location
        local_user_id = data.get('local_user_id')
        if local_user_id:
            user = LocalUser.query.get_or_404(local_user_id)
            # Verificar que el usuario pertenece al location
            if user.location_id != location_id:
                return jsonify({"error": "El usuario no pertenece a este local"}), 403
        else:
            # Si no hay usuario específico, buscar un usuario cualquiera del location
            user = LocalUser.query.filter_by(location_id=location_id).first()
            if not user:
                return jsonify({"error": "No hay usuarios disponibles para este local"}), 404
    else:
        user = LocalUser.query.get_or_404(current_user_id)
    
    # Obtener la tarea
    task = Task.query.get_or_404(task_id)
    
    # Verificar que la tarea pertenece al local del usuario
    if task.location_id != user.location_id:
        return jsonify({"error": "Tarea no válida para este local"}), 403
    
    # Verificar si ya ha sido completada hoy por este usuario
    today = date.today()
    existing_completion = TaskCompletion.query.filter_by(
        task_id=task.id,
        local_user_id=user.id
    ).filter(
        db.func.date(TaskCompletion.completion_date) == today
    ).first()
    
    if existing_completion:
        return jsonify({"error": "Esta tarea ya ha sido completada hoy"}), 400
    
    # Crear registro de tarea completada
    completion = TaskCompletion(
        task_id=task.id,
        local_user_id=user.id,
        notes=notes
    )
    
    try:
        db.session.add(completion)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "taskId": task.id,
            "taskTitle": task.title,
            "completedBy": f"{user.name} {user.last_name}",
            "completedAt": datetime.now().strftime('%H:%M')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al completar la tarea: {str(e)}"}), 500

@api_bp.route('/tasks/groups', methods=['GET'])
@jwt_required()
def get_task_groups():
    """
    Devuelve todos los grupos de tareas para el local del usuario
    """
    current_user_id = get_jwt_identity()
    
    # Determinar a qué local pertenece el usuario
    if isinstance(current_user_id, str) and current_user_id.startswith("location_"):
        location_id = int(current_user_id.split("_")[1])
    else:
        user = LocalUser.query.get_or_404(current_user_id)
        location_id = user.location_id
    
    # Verificar si el location_id existe
    if not location_id:
        return jsonify({"error": "No hay un local asociado a este usuario"}), 400
    
    # Obtener grupos de tareas
    groups = TaskGroup.query.filter_by(location_id=location_id).all()
    
    groups_json = []
    for group in groups:
        group_data = {
            "id": group.id,
            "name": group.name,
            "color": group.color or "#CCCCCC",
            "description": group.description or ""
        }
        groups_json.append(group_data)
    
    return jsonify({
        "success": True,
        "groups": groups_json
    })

@api_bp.route('/tasks/stats', methods=['GET'])
@jwt_required()
def get_task_stats():
    """
    Devuelve estadísticas de tareas para el dashboard
    """
    current_user_id = get_jwt_identity()
    
    # Determinar a qué local pertenece el usuario
    if isinstance(current_user_id, str) and current_user_id.startswith("location_"):
        location_id = int(current_user_id.split("_")[1])
    else:
        user = LocalUser.query.get_or_404(current_user_id)
        location_id = user.location_id
    
    # Verificar si el location_id existe
    if not location_id:
        return jsonify({"error": "No hay un local asociado a este usuario"}), 400
    
    # Fecha actual
    today = date.today()
    
    # Obtener todas las tareas
    all_tasks = Task.query.filter_by(location_id=location_id, status=TaskStatus.PENDIENTE).all()
    
    # Filtrar tareas para hoy
    active_tasks = [task for task in all_tasks if task.is_due_today()]
    
    # Obtener completados de hoy
    completions = TaskCompletion.query.filter(
        TaskCompletion.task_id.in_([t.id for t in active_tasks]),
        db.func.date(TaskCompletion.completion_date) == today
    ).all()
    
    # Crear un set de ids de tareas completadas
    completed_task_ids = {c.task_id for c in completions}
    
    # Contar tareas urgentes
    urgent_tasks = sum(1 for task in active_tasks 
                     if task.priority == TaskPriority.URGENTE and task.id not in completed_task_ids)
    
    # Estadísticas
    total_tasks = len(active_tasks)
    completed_tasks = len(completed_task_ids)
    pending_tasks = total_tasks - completed_tasks
    
    # Calcular porcentaje completado
    completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return jsonify({
        "success": True,
        "date": today.isoformat(),
        "stats": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "urgent_tasks": urgent_tasks,
            "completion_percentage": round(completion_percentage, 1)
        }
    })

# Rutas para productos y etiquetas
@api_bp.route('/labels/products', methods=['GET'])
@jwt_required()
def get_products():
    """
    Devuelve todos los productos disponibles para el local del usuario
    """
    current_user_id = get_jwt_identity()
    
    # Determinar a qué local pertenece el usuario
    if isinstance(current_user_id, str) and current_user_id.startswith("location_"):
        location_id = int(current_user_id.split("_")[1])
    else:
        user = LocalUser.query.get_or_404(current_user_id)
        location_id = user.location_id
    
    # Verificar si el location_id existe
    if not location_id:
        return jsonify({"error": "No hay un local asociado a este usuario"}), 400
    
    # Obtener el location
    location = Location.query.get_or_404(location_id)
    
    # Obtener productos disponibles para la empresa del local
    products = Product.query.filter_by(company_id=location.company_id, is_active=True).all()
    
    products_json = []
    for product in products:
        product_data = {
            "id": product.id,
            "name": product.name,
            "code": product.code or "",
            "category": product.category or "",
            "has_barcode": bool(product.barcode)
        }
        products_json.append(product_data)
    
    return jsonify({
        "success": True,
        "products": products_json
    })

@api_bp.route('/labels/products/search', methods=['GET'])
@jwt_required()
def search_products():
    """
    Busca productos por nombre o código
    """
    current_user_id = get_jwt_identity()
    
    # Determinar a qué local pertenece el usuario
    if isinstance(current_user_id, str) and current_user_id.startswith("location_"):
        location_id = int(current_user_id.split("_")[1])
    else:
        user = LocalUser.query.get_or_404(current_user_id)
        location_id = user.location_id
    
    # Verificar si el location_id existe
    if not location_id:
        return jsonify({"error": "No hay un local asociado a este usuario"}), 400
    
    # Obtener el location
    location = Location.query.get_or_404(location_id)
    
    # Obtener término de búsqueda
    query = request.args.get('q', '')
    
    if not query or len(query) < 2:
        return jsonify({"error": "El término de búsqueda debe tener al menos 2 caracteres"}), 400
    
    # Buscar productos
    products = Product.query.filter(
        Product.company_id == location.company_id,
        Product.is_active == True,
        (
            Product.name.ilike(f'%{query}%') |
            Product.code.ilike(f'%{query}%') |
            Product.category.ilike(f'%{query}%')
        )
    ).all()
    
    products_json = []
    for product in products:
        product_data = {
            "id": product.id,
            "name": product.name,
            "code": product.code or "",
            "category": product.category or "",
            "has_barcode": bool(product.barcode)
        }
        products_json.append(product_data)
    
    return jsonify({
        "success": True,
        "products": products_json,
        "query": query
    })

@api_bp.route('/labels/conservation-types', methods=['GET'])
@jwt_required()
def get_conservation_types():
    """
    Devuelve los tipos de conservación disponibles para los productos
    """
    current_user_id = get_jwt_identity()
    
    # Determinar a qué local pertenece el usuario
    if isinstance(current_user_id, str) and current_user_id.startswith("location_"):
        location_id = int(current_user_id.split("_")[1])
    else:
        user = LocalUser.query.get_or_404(current_user_id)
        location_id = user.location_id
    
    # Verificar si el location_id existe
    if not location_id:
        return jsonify({"error": "No hay un local asociado a este usuario"}), 400
    
    # Obtener el location
    location = Location.query.get_or_404(location_id)
    
    # Tipos de conservación estándar
    conservation_types = [
        {"id": "descongelacion", "name": "Descongelación", "default_hours": 72, "description": "Productos descongelados"},
        {"id": "refrigeracion", "name": "Refrigeración", "default_hours": 24, "description": "Productos refrigerados"},
        {"id": "congelacion", "name": "Congelación", "default_hours": 720, "description": "Productos congelados"},
        {"id": "gastro", "name": "Gastro", "default_hours": 48, "description": "Productos gastronómicos"},
        {"id": "caliente", "name": "Caliente", "default_hours": 4, "description": "Productos calientes"},
        {"id": "seco", "name": "Seco", "default_hours": 168, "description": "Productos secos"}
    ]
    
    return jsonify({
        "success": True,
        "conservation_types": conservation_types
    })

@api_bp.route('/labels/product/<int:product_id>/conservation-types', methods=['GET'])
@jwt_required()
def get_product_conservation_types(product_id):
    """
    Devuelve los tipos de conservación específicos para un producto
    """
    # Obtener el producto
    product = Product.query.get_or_404(product_id)
    
    # Obtener tipos de conservación para el producto
    conservations = ProductConservation.query.filter_by(product_id=product_id).all()
    
    conservations_json = []
    for conservation in conservations:
        conservation_data = {
            "id": conservation.id,
            "type": conservation.conservation_type,
            "name": conservation.get_type_display(),
            "hours_valid": conservation.hours_valid,
            "description": conservation.description or ""
        }
        conservations_json.append(conservation_data)
    
    return jsonify({
        "success": True,
        "product": {
            "id": product.id,
            "name": product.name
        },
        "conservation_types": conservations_json
    })

@api_bp.route('/labels/generate', methods=['POST'])
@jwt_required()
def generate_label():
    """
    Genera los datos para una etiqueta
    """
    if not request.is_json:
        return jsonify({"error": "Se requiere datos en formato JSON"}), 400
    
    data = request.json
    
    product_id = data.get('product_id')
    conservation_type = data.get('conservation_type')
    
    if not product_id or not conservation_type:
        return jsonify({"error": "Se requiere product_id y conservation_type"}), 400
    
    # Obtener el producto
    product = Product.query.get_or_404(product_id)
    
    # Obtener la conservación específica del producto si existe
    product_conservation = ProductConservation.query.filter_by(
        product_id=product_id,
        conservation_type=conservation_type
    ).first()
    
    # Si no existe una conservación específica, usar valores predeterminados
    hours_valid = 24  # valor predeterminado
    if product_conservation:
        hours_valid = product_conservation.hours_valid
    else:
        # Valores predeterminados según el tipo de conservación
        if conservation_type == 'descongelacion':
            hours_valid = 72
        elif conservation_type == 'refrigeracion':
            hours_valid = 24
        elif conservation_type == 'congelacion':
            hours_valid = 720  # 30 días
        elif conservation_type == 'gastro':
            hours_valid = 48
        elif conservation_type == 'caliente':
            hours_valid = 4
        elif conservation_type == 'seco':
            hours_valid = 168  # 7 días
    
    # Calcular fechas
    elaboration_date = datetime.now()
    expiration_date = elaboration_date + timedelta(hours=hours_valid)
    
    # Devolver datos para la etiqueta
    return jsonify({
        "success": True,
        "label_data": {
            "product_name": product.name,
            "product_code": product.code,
            "conservation_type": conservation_type,
            "conservation_type_display": {
                "descongelacion": "Descongelación",
                "refrigeracion": "Refrigeración",
                "congelacion": "Congelación",
                "gastro": "Gastro",
                "caliente": "Caliente",
                "seco": "Seco"
            }.get(conservation_type, conservation_type),
            "elaboration_date": elaboration_date.isoformat(),
            "elaboration_date_display": elaboration_date.strftime("%d/%m/%Y %H:%M"),
            "expiration_date": expiration_date.isoformat(),
            "expiration_date_display": expiration_date.strftime("%d/%m/%Y %H:%M"),
            "hours_valid": hours_valid,
            "barcode": product.barcode or None
        }
    })

# Rutas para obtener datos de usuarios locales
@api_bp.route('/locations/<int:location_id>/users', methods=['GET'])
@jwt_required()
def get_location_users(location_id):
    """
    Devuelve los usuarios locales de una ubicación
    """
    # Verificar permisos
    current_user_id = get_jwt_identity()
    
    # Solo permitir acceso si el usuario es del mismo local o es una sesión de location
    if isinstance(current_user_id, str) and current_user_id.startswith("location_"):
        auth_location_id = int(current_user_id.split("_")[1])
        if auth_location_id != location_id:
            return jsonify({"error": "No tienes permisos para acceder a los usuarios de este local"}), 403
    else:
        user = LocalUser.query.get_or_404(current_user_id)
        if user.location_id != location_id:
            return jsonify({"error": "No tienes permisos para acceder a los usuarios de este local"}), 403
    
    # Obtener usuarios del local
    users = LocalUser.query.filter_by(location_id=location_id, is_active=True).all()
    
    users_json = []
    for user in users:
        user_data = {
            "id": user.id,
            "name": user.name,
            "last_name": user.last_name,
            "username": user.username
        }
        users_json.append(user_data)
    
    return jsonify({
        "success": True,
        "location_id": location_id,
        "users": users_json
    })