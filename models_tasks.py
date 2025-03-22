from app import db
from datetime import datetime, date, time
import enum
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Company

class TaskPriority(enum.Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"

class TaskFrequency(enum.Enum):
    DIARIA = "diaria"
    SEMANAL = "semanal"
    QUINCENAL = "quincenal"
    MENSUAL = "mensual"
    PERSONALIZADA = "personalizada"

class TaskStatus(enum.Enum):
    PENDIENTE = "pendiente"
    COMPLETADA = "completada"
    VENCIDA = "vencida"
    CANCELADA = "cancelada"

class WeekDay(enum.Enum):
    LUNES = "lunes"
    MARTES = "martes"
    MIERCOLES = "miercoles"
    JUEVES = "jueves"
    VIERNES = "viernes"
    SABADO = "sabado"
    DOMINGO = "domingo"

class TaskGroup(db.Model):
    __tablename__ = 'task_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default="#17a2b8")  # Color para identificar visualmente el grupo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    location = db.relationship('Location', backref=db.backref('task_groups', lazy=True))
    
    # Tareas en este grupo
    tasks = db.relationship('Task', back_populates='group')
    
    def __repr__(self):
        return f'<TaskGroup {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'location_id': self.location_id,
            'location_name': self.location.name if self.location else None
        }
    
class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(256))
    city = db.Column(db.String(64))
    postal_code = db.Column(db.String(16))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Credenciales de acceso al portal
    portal_username = db.Column(db.String(64), unique=True)
    portal_password_hash = db.Column(db.String(256))
    
    # Relaciones
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = db.relationship('Company', backref=db.backref('locations', lazy=True))
    
    # Relación con las tareas
    tasks = db.relationship('Task', back_populates='location', cascade='all, delete-orphan')
    
    # Relación con usuarios locales
    local_users = db.relationship('LocalUser', back_populates='location', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Location {self.name}>'
    
    def set_portal_password(self, password):
        """Establece una contraseña encriptada para el portal"""
        self.portal_password_hash = generate_password_hash(password)
        
    def check_portal_password(self, password):
        """Verifica si la contraseña proporcionada coincide con la almacenada"""
        # Si hay hash de contraseña, verificamos contra esa
        if self.portal_password_hash:
            return check_password_hash(self.portal_password_hash, password)
        # Si no, comparamos con la contraseña fija
        return password == self.portal_fixed_password
    
    @property
    def portal_fixed_username(self):
        """Retorna el nombre de usuario para este local"""
        # Siempre usamos el formato predeterminado
        return f"portal_{self.id}"
        
    @property
    def portal_fixed_password(self):
        """Retorna la contraseña para este local"""
        # Si hay contraseña personalizada (hash), significará que el usuario ha establecido una contraseña personalizada
        if self.portal_password_hash:
            # No podemos recuperar la contraseña real (solo tenemos el hash)
            # Usaremos una función específica para validar la contraseña en lugar de mostrarla
            return None  # No podemos mostrar la contraseña real
        # Si no hay contraseña personalizada, usamos el formato predeterminado
        return f"Portal{self.id}2025!"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'postal_code': self.postal_code,
            'description': self.description,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'is_active': self.is_active,
            'has_portal_credentials': True  # Siempre tiene credenciales fijas
        }

class LocalUser(db.Model):
    __tablename__ = 'local_users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(128), nullable=False)  # Se generará automáticamente
    pin = db.Column(db.String(256), nullable=False)  # PIN de 4 dígitos (almacenado como hash)
    photo_path = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relaciones
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    location = db.relationship('Location', back_populates='local_users')
    
    # Relación con las tareas completadas
    completed_tasks = db.relationship('TaskCompletion', back_populates='local_user')
    
    def __repr__(self):
        return f'<LocalUser {self.name} {self.last_name}>'
    
    def set_pin(self, pin):
        # Almacenamos el PIN como hash por seguridad
        self.pin = generate_password_hash(pin)
        
    def check_pin(self, pin):
        return check_password_hash(self.pin, pin)
    
    def get_full_name(self):
        return f"{self.name} {self.last_name}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'photo_path': self.photo_path,
            'location_id': self.location_id,
            'location_name': self.location.name if self.location else None,
            'is_active': self.is_active
        }

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(Enum(TaskPriority), default=TaskPriority.MEDIA)
    frequency = db.Column(Enum(TaskFrequency), default=TaskFrequency.DIARIA)
    status = db.Column(Enum(TaskStatus), default=TaskStatus.PENDIENTE)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date)  # Fecha final para tareas recurrentes, NULL si no caduca
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    location = db.relationship('Location', back_populates='tasks')
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User')
    
    # Grupo de tareas
    group_id = db.Column(db.Integer, db.ForeignKey('task_groups.id'), nullable=True)
    group = db.relationship('TaskGroup', back_populates='tasks')
    
    # Programación
    schedule_details = db.relationship('TaskSchedule', back_populates='task', cascade='all, delete-orphan')
    weekdays = db.relationship('TaskWeekday', back_populates='task', cascade='all, delete-orphan')
    
    # Historial de completado
    completions = db.relationship('TaskCompletion', back_populates='task', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority.value if self.priority else None,
            'frequency': self.frequency.value if self.frequency else None,
            'status': self.status.value if self.status else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'location_id': self.location_id,
            'location_name': self.location.name if self.location else None
        }
    
    def is_due_today(self):
        """Comprueba si la tarea está programada para hoy según su programación."""
        today = date.today()
        today_weekday = today.weekday()  # 0 es lunes, 6 es domingo
        
        # Si la tarea tiene fecha de fin y ya ha pasado, no está activa
        if self.end_date and today > self.end_date:
            return False
        
        # Si la tarea tiene fecha de inicio y aún no ha llegado, no está activa
        if self.start_date and today < self.start_date:
            return False
        
        # Para tareas personalizadas con múltiples días, verificamos los días configurados
        if self.frequency == TaskFrequency.PERSONALIZADA and self.weekdays:
            for weekday_entry in self.weekdays:
                if TaskWeekday.day_matches_today(weekday_entry.day_of_week):
                    return True
            # Si llegamos aquí, es que hoy no es uno de los días configurados
            return False
            
        # Si no hay programación específica (schedule_details está vacío),
        # consideramos que la tarea está activa según su frecuencia
        if not self.schedule_details:
            # Para tareas diarias, siempre están activas
            if self.frequency == TaskFrequency.DIARIA:
                return True
                
            # Para tareas semanales, verificamos si today es el mismo día de la semana que start_date
            elif self.frequency == TaskFrequency.SEMANAL and self.start_date:
                return today.weekday() == self.start_date.weekday()
                
            # Para tareas mensuales, verificamos si today es el mismo día del mes que start_date
            elif self.frequency == TaskFrequency.MENSUAL and self.start_date:
                return today.day == self.start_date.day
                
            # Para tareas quincenales, verificamos si han pasado múltiplos de 15 días desde start_date
            elif self.frequency == TaskFrequency.QUINCENAL and self.start_date:
                delta = (today - self.start_date).days
                return delta % 15 == 0
            
            # Para cualquier otro caso, mostramos la tarea
            return True
        
        # Comprobamos la programación específica
        for schedule in self.schedule_details:
            if schedule.is_active_for_date(today):
                return True
                
        return False

class TaskSchedule(db.Model):
    __tablename__ = 'task_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(Enum(WeekDay), nullable=True)  # Día de la semana para tareas semanales
    day_of_month = db.Column(db.Integer, nullable=True)    # Día del mes para tareas mensuales
    start_time = db.Column(db.Time, nullable=True)         # Hora de inicio
    end_time = db.Column(db.Time, nullable=True)           # Hora de finalización
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    task = db.relationship('Task', back_populates='schedule_details')
    
    def __repr__(self):
        if self.day_of_week:
            return f'<TaskSchedule {self.task.title} - {self.day_of_week.value}>'
        elif self.day_of_month:
            return f'<TaskSchedule {self.task.title} - Day {self.day_of_month}>'
        else:
            return f'<TaskSchedule {self.task.title}>'
    
    def is_active_for_date(self, check_date):
        """Comprueba si este horario está activo para una fecha determinada."""
        # Si es una tarea diaria, siempre está activa
        if self.task.frequency == TaskFrequency.DIARIA:
            return True
            
        # Para tareas semanales, comprobamos el día de la semana
        if self.task.frequency == TaskFrequency.SEMANAL and self.day_of_week:
            day_map = {
                WeekDay.LUNES: 0,
                WeekDay.MARTES: 1,
                WeekDay.MIERCOLES: 2,
                WeekDay.JUEVES: 3,
                WeekDay.VIERNES: 4,
                WeekDay.SABADO: 5,
                WeekDay.DOMINGO: 6
            }
            return check_date.weekday() == day_map[self.day_of_week]
            
        # Para tareas mensuales, comprobamos el día del mes
        if self.task.frequency == TaskFrequency.MENSUAL and self.day_of_month:
            return check_date.day == self.day_of_month
            
        # Para tareas quincenales (cada 15 días)
        if self.task.frequency == TaskFrequency.QUINCENAL:
            if not self.task.start_date:
                return False
                
            delta = (check_date - self.task.start_date).days
            return delta % 15 == 0
            
        # Si llegamos aquí y no hemos retornado, no está activa
        return False
        
class TaskWeekday(db.Model):
    """Modelo para almacenar los días de la semana en los que una tarea debe ejecutarse"""
    __tablename__ = 'task_weekdays'
    
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(Enum(WeekDay), nullable=False)
    
    # Relaciones
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    task = db.relationship('Task', back_populates='weekdays')
    
    def __repr__(self):
        return f'<TaskWeekday {self.task.title} - {self.day_of_week.value}>'
        
    @classmethod
    def day_matches_today(cls, weekday):
        """Comprueba si el día de la semana corresponde al día actual"""
        day_map = {
            WeekDay.LUNES: 0,
            WeekDay.MARTES: 1,
            WeekDay.MIERCOLES: 2,
            WeekDay.JUEVES: 3,
            WeekDay.VIERNES: 4,
            WeekDay.SABADO: 5,
            WeekDay.DOMINGO: 6
        }
        return date.today().weekday() == day_map[weekday]

class TaskCompletion(db.Model):
    __tablename__ = 'task_completions'
    
    id = db.Column(db.Integer, primary_key=True)
    completion_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relaciones
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    task = db.relationship('Task', back_populates='completions')
    local_user_id = db.Column(db.Integer, db.ForeignKey('local_users.id'), nullable=False)
    local_user = db.relationship('LocalUser', back_populates='completed_tasks')
    
    def __repr__(self):
        return f'<TaskCompletion {self.task.title} by {self.local_user.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'task_title': self.task.title if self.task else None,
            'local_user_id': self.local_user_id,
            'local_user_name': self.local_user.name if self.local_user else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'notes': self.notes
        }