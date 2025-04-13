"""
Modelos de datos para el módulo de horarios.
Integra el sistema de horarios basado en React con los modelos existentes de SQLAlchemy.
"""

from datetime import datetime
from app import db
from models import Employee, Company

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