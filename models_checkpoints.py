import enum
from datetime import datetime, date, time, timedelta
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import Employee, Company


class CheckPointStatus(enum.Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    MAINTENANCE = "maintenance"


class CheckPointIncidentType(enum.Enum):
    MISSED_CHECKOUT = "missed_checkout"
    LATE_CHECKIN = "late_checkin"
    EARLY_CHECKOUT = "early_checkout"
    OVERTIME = "overtime"
    MANUAL_ADJUSTMENT = "manual_adjustment"
    CONTRACT_HOURS_ADJUSTMENT = "contract_hours_adjustment"


class CheckPoint(db.Model):
    """Modelo para puntos de fichaje físicos (tablet, móvil, etc.)"""
    __tablename__ = 'checkpoints'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(256))
    status = db.Column(Enum(CheckPointStatus), default=CheckPointStatus.ACTIVE)
    
    # Credenciales para el punto de fichaje
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Configuración del punto de fichaje
    auto_checkout_time = db.Column(db.Time)  # Hora límite para checkout automático
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = db.relationship('Company', backref=db.backref('checkpoints', lazy=True))
    
    # Configuración de los ajustes automáticos
    enforce_contract_hours = db.Column(db.Boolean, default=False)
    auto_adjust_overtime = db.Column(db.Boolean, default=False)
    
    # Fichajes realizados desde este punto
    check_ins = db.relationship('CheckPointRecord', back_populates='checkpoint', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CheckPoint {self.name} ({self.company.name})>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class CheckPointRecord(db.Model):
    """Registro de fichajes realizados desde un punto de fichaje"""
    __tablename__ = 'checkpoint_records'
    
    id = db.Column(db.Integer, primary_key=True)
    check_in_time = db.Column(db.DateTime, nullable=False)
    check_out_time = db.Column(db.DateTime)
    
    # Fichaje original antes de ajustes
    original_check_in_time = db.Column(db.DateTime)
    original_check_out_time = db.Column(db.DateTime)
    
    # Ajustes aplicados
    adjusted = db.Column(db.Boolean, default=False)
    adjustment_reason = db.Column(db.String(256))
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = db.relationship('Employee', backref=db.backref('checkpoint_records', lazy=True))
    
    checkpoint_id = db.Column(db.Integer, db.ForeignKey('checkpoints.id'), nullable=False)
    checkpoint = db.relationship('CheckPoint', back_populates='check_ins')
    
    # Incidencias relacionadas con este fichaje
    incidents = db.relationship('CheckPointIncident', back_populates='record', cascade='all, delete-orphan')
    
    # Firma del empleado (si se requiere)
    signature_data = db.Column(db.Text)
    has_signature = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        status = "Completado" if self.check_out_time else "Pendiente de salida"
        return f'<Fichaje {self.employee.first_name} {self.check_in_time.strftime("%d/%m/%Y %H:%M")} - {status}>'
    
    def duration(self):
        """Calcula la duración del fichaje en horas"""
        if not self.check_out_time:
            return None
        
        delta = self.check_out_time - self.check_in_time
        return delta.total_seconds() / 3600  # Convertir a horas
    
    def to_dict(self):
        """Convierte el registro a un diccionario para serialización"""
        result = {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': f"{self.employee.first_name} {self.employee.last_name}",
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'duration': round(self.duration(), 2) if self.duration() is not None else None,
            'adjusted': self.adjusted,
            'has_signature': self.has_signature
        }
        
        if self.adjusted and self.original_check_in_time:
            result['original_check_in_time'] = self.original_check_in_time.isoformat()
            if self.original_check_out_time:
                result['original_check_out_time'] = self.original_check_out_time.isoformat()
                
        return result


class CheckPointIncident(db.Model):
    """Incidencias relacionadas con fichajes"""
    __tablename__ = 'checkpoint_incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_type = db.Column(Enum(CheckPointIncidentType))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    
    # Relaciones
    record_id = db.Column(db.Integer, db.ForeignKey('checkpoint_records.id'), nullable=False)
    record = db.relationship('CheckPointRecord', back_populates='incidents')
    
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_by = db.relationship('User')
    
    def __repr__(self):
        return f'<Incidencia {self.incident_type.value} - {self.created_at.strftime("%d/%m/%Y")}>'
    
    def resolve(self, user_id, notes=None):
        """Marca la incidencia como resuelta"""
        self.resolved = True
        self.resolved_at = datetime.utcnow()
        self.resolved_by_id = user_id
        if notes:
            self.resolution_notes = notes


class EmployeeContractHours(db.Model):
    """Configuración de horas por contrato para cada empleado"""
    __tablename__ = 'employee_contract_hours'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Horas diarias máximas según contrato
    daily_hours = db.Column(db.Float, default=8.0)
    weekly_hours = db.Column(db.Float, default=40.0)
    
    # Configuración de márgenes
    allow_overtime = db.Column(db.Boolean, default=False)
    max_overtime_daily = db.Column(db.Float, default=2.0)  # Horas extra máximas diarias permitidas
    
    # Horario normal de trabajo (para cálculo de retrasos)
    use_normal_schedule = db.Column(db.Boolean, default=False)  # Activar horario normal
    normal_start_time = db.Column(db.Time)
    normal_end_time = db.Column(db.Time)
    
    # Margen de flexibilidad (en minutos)
    use_flexibility = db.Column(db.Boolean, default=False)  # Activar margen de flexibilidad
    checkin_flexibility = db.Column(db.Integer, default=15)  # Minutos de flexibilidad en la entrada
    checkout_flexibility = db.Column(db.Integer, default=15)  # Minutos de flexibilidad en la salida
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, unique=True)
    employee = db.relationship('Employee', backref=db.backref('contract_hours', uselist=False))
    
    def __repr__(self):
        return f'<ContractHours {self.employee.first_name} - {self.daily_hours}h/día, {self.weekly_hours}h/semana>'
    
    def is_overtime(self, duration_hours):
        """Comprueba si una duración de horas supera el máximo diario"""
        return duration_hours > self.daily_hours
    
    def calculate_adjusted_hours(self, check_in_time, check_out_time):
        """Calcula el tiempo ajustado según el contrato"""
        if not check_out_time:
            return None, None
            
        # Calcular duración original
        duration = (check_out_time - check_in_time).total_seconds() / 3600
        
        # Si no excede las horas máximas, no se ajusta
        if duration <= self.daily_hours:
            return check_in_time, check_out_time
            
        # Si excede y no se permiten horas extra, ajustamos
        if not self.allow_overtime or (self.allow_overtime and duration > (self.daily_hours + self.max_overtime_daily)):
            # Ajustamos la hora de entrada para que la duración sea igual a las horas contratadas
            new_check_in_time = check_out_time - timedelta(hours=self.daily_hours)
            return new_check_in_time, check_out_time
            
        return check_in_time, check_out_time