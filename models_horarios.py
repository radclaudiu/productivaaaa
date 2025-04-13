"""
Modelos de datos para el módulo de horarios.
Integra el sistema de horarios basado en React con los modelos existentes de SQLAlchemy.
"""

from datetime import datetime
from app import db
from models import Employee, Company, User

class Schedule(db.Model):
    """
    Modelo para almacenar los horarios semanales.
    Cada horario representa una semana de trabajo para una ubicación/empresa específica.
    """
    __tablename__ = 'schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con la empresa/ubicación
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = db.relationship('Company', backref=db.backref('schedules', lazy='dynamic'))
    
    # Relación con asignaciones de horario
    assignments = db.relationship('ScheduleAssignment', backref='schedule', lazy='dynamic', 
                                cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convierte el horario a un diccionario para la API JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'published': self.published,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ScheduleAssignment(db.Model):
    """
    Modelo para almacenar las asignaciones de horarios.
    Cada asignación representa un bloque de tiempo asignado a un empleado.
    """
    __tablename__ = 'schedule_assignment'
    
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date, nullable=False)  # Fecha específica para la asignación
    start_time = db.Column(db.String(5), nullable=False)  # Formato: "HH:MM"
    end_time = db.Column(db.String(5), nullable=False)    # Formato: "HH:MM"
    break_duration = db.Column(db.Integer, default=0)     # Duración del descanso en minutos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = db.relationship('Employee', backref=db.backref('schedule_assignments', lazy='dynamic'))
    
    def to_dict(self):
        """Convierte la asignación a un diccionario para la API JSON"""
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'employee_id': self.employee_id,
            'employee_name': f"{self.employee.first_name} {self.employee.last_name}" if self.employee else None,
            'day': self.day.isoformat() if self.day else None,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'break_duration': self.break_duration
        }

class ScheduleTemplate(db.Model):
    """
    Modelo para plantillas de horario.
    Las plantillas definen patrones de horario reutilizables para crear horarios semanales.
    """
    __tablename__ = 'schedule_template'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)
    start_hour = db.Column(db.Integer, default=8)
    end_hour = db.Column(db.Integer, default=20)
    time_increment = db.Column(db.Integer, default=15)  # Incrementos en minutos (15, 30, 60)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    company = db.relationship('Company', backref=db.backref('schedule_templates', lazy='dynamic'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    creator = db.relationship('User', backref=db.backref('created_templates', lazy='dynamic'))
    
    def to_dict(self):
        """Convierte la plantilla a un diccionario para la API JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_default': self.is_default,
            'start_hour': self.start_hour,
            'end_hour': self.end_hour,
            'time_increment': self.time_increment,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EmployeeAvailability(db.Model):
    """
    Modelo para almacenar la disponibilidad de los empleados.
    Define en qué días y horas está disponible cada empleado para trabajar.
    """
    __tablename__ = 'employee_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6 (Lunes a Domingo)
    start_time = db.Column(db.String(5), nullable=False)  # Formato: "HH:MM"
    end_time = db.Column(db.String(5), nullable=False)    # Formato: "HH:MM"
    is_available = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = db.relationship('Employee', backref=db.backref('availability', lazy='dynamic'))
    
    __table_args__ = (
        db.UniqueConstraint('employee_id', 'day_of_week', 'start_time', 'end_time', name='uq_employee_availability'),
    )
    
    def to_dict(self):
        """Convierte la disponibilidad a un diccionario para la API JSON"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': f"{self.employee.first_name} {self.employee.last_name}" if self.employee else None,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'is_available': self.is_available,
            'notes': self.notes
        }

class ScheduleRule(db.Model):
    """
    Modelo para reglas de horario.
    Define restricciones y políticas para la creación de horarios.
    """
    __tablename__ = 'schedule_rule'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    max_hours_per_day = db.Column(db.Integer, default=8)
    max_hours_per_week = db.Column(db.Integer, default=40)
    min_break_duration = db.Column(db.Integer, default=30)  # En minutos
    min_time_between_shifts = db.Column(db.Integer, default=720)  # En minutos (12 horas por defecto)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    company = db.relationship('Company', backref=db.backref('schedule_rules', lazy='dynamic'))
    
    def to_dict(self):
        """Convierte la regla a un diccionario para la API JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'max_hours_per_day': self.max_hours_per_day,
            'max_hours_per_week': self.max_hours_per_week,
            'min_break_duration': self.min_break_duration,
            'min_time_between_shifts': self.min_time_between_shifts,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None
        }

class ScheduleRequest(db.Model):
    """
    Modelo para solicitudes de cambio de horario.
    Permite a los empleados solicitar cambios en sus horarios asignados.
    """
    __tablename__ = 'schedule_request'
    
    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.String(20), nullable=False)  # 'time_off', 'shift_change', 'swap'
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    start_time = db.Column(db.String(5))
    end_time = db.Column(db.String(5))
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    reviewed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = db.relationship('Employee', backref=db.backref('schedule_requests', lazy='dynamic'))
    assignment_id = db.Column(db.Integer, db.ForeignKey('schedule_assignment.id'))
    assignment = db.relationship('ScheduleAssignment', backref=db.backref('change_requests', lazy='dynamic'))
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewer = db.relationship('User', backref=db.backref('reviewed_requests', lazy='dynamic'))
    
    def to_dict(self):
        """Convierte la solicitud a un diccionario para la API JSON"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': f"{self.employee.first_name} {self.employee.last_name}" if self.employee else None,
            'assignment_id': self.assignment_id,
            'request_type': self.request_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'reason': self.reason,
            'status': self.status,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }