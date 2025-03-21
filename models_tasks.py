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
    
    # Relaciones
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = db.relationship('Company', backref=db.backref('locations', lazy=True))
    
    # Relación con las tareas
    tasks = db.relationship('Task', back_populates='location', cascade='all, delete-orphan')
    
    # Relación con usuarios locales
    local_users = db.relationship('LocalUser', back_populates='location', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Location {self.name}>'
    
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
            'is_active': self.is_active
        }

class LocalUser(db.Model):
    __tablename__ = 'local_users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    pin = db.Column(db.String(10), nullable=False)  # PIN de 4 dígitos
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
        return f'<LocalUser {self.name}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_pin(self, pin):
        # Almacenamos el PIN como hash por seguridad
        self.pin = generate_password_hash(pin)
        
    def check_pin(self, pin):
        return check_password_hash(self.pin, pin)
    
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
    
    # Programación
    schedule_details = db.relationship('TaskSchedule', back_populates='task', cascade='all, delete-orphan')
    
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