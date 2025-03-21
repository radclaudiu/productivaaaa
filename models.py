from datetime import datetime
import enum
from flask_login import UserMixin
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

class UserRole(enum.Enum):
    ADMIN = "admin"
    GERENTE = "gerente"
    EMPLEADO = "empleado"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(Enum(UserRole), default=UserRole.EMPLEADO, nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    company = db.relationship('Company', back_populates='users')
    employee = db.relationship('Employee', back_populates='user', uselist=False)
    activity_logs = db.relationship('ActivityLog', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == UserRole.ADMIN
        
    def is_gerente(self):
        return self.role == UserRole.GERENTE
        
    def is_empleado(self):
        return self.role == UserRole.EMPLEADO
    
    def __repr__(self):
        return f'<User {self.username}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'full_name': f"{self.first_name} {self.last_name}",
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'company_id': self.company_id
        }
        
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(256))
    city = db.Column(db.String(64))
    postal_code = db.Column(db.String(16))
    country = db.Column(db.String(64))
    sector = db.Column(db.String(64))
    tax_id = db.Column(db.String(32), unique=True)
    phone = db.Column(db.String(32))
    email = db.Column(db.String(120))
    website = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    employees = db.relationship('Employee', back_populates='company', cascade='all, delete-orphan')
    users = db.relationship('User', back_populates='company')
    
    def __repr__(self):
        return f'<Company {self.name}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'postal_code': self.postal_code,
            'country': self.country,
            'sector': self.sector,
            'tax_id': self.tax_id,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'is_active': self.is_active,
            'employee_count': len(self.employees)
        }

class ContractType(enum.Enum):
    INDEFINIDO = "indefinido"
    TEMPORAL = "temporal"
    PRACTICAS = "practicas"
    FORMACION = "formacion"
    OBRA = "obra"
    TIEMPO_PARCIAL = "tiempo_parcial"
    RELEVO = "relevo"
    AUTONOMO = "autonomo"
    MERCANTIL = "mercantil"

class EmployeeStatus(enum.Enum):
    ACTIVO = "activo"
    BAJA_MEDICA = "baja_medica"
    EXCEDENCIA = "excedencia"
    VACACIONES = "vacaciones"
    INACTIVO = "inactivo"

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    dni = db.Column(db.String(16), unique=True, nullable=False)
    position = db.Column(db.String(64))
    contract_type = db.Column(Enum(ContractType), default=ContractType.INDEFINIDO)
    bank_account = db.Column(db.String(64))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(Enum(EmployeeStatus), default=EmployeeStatus.ACTIVO)
    status_start_date = db.Column(db.Date)
    status_end_date = db.Column(db.Date)
    status_notes = db.Column(db.Text)
    
    # Relationships
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = db.relationship('Company', back_populates='employees')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    user = db.relationship('User', back_populates='employee')
    documents = db.relationship('EmployeeDocument', back_populates='employee', cascade='all, delete-orphan')
    notes = db.relationship('EmployeeNote', back_populates='employee', cascade='all, delete-orphan')
    history = db.relationship('EmployeeHistory', back_populates='employee', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'dni': self.dni,
            'position': self.position,
            'contract_type': self.contract_type.value if self.contract_type else None,
            'bank_account': self.bank_account,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'status': self.status.value if self.status else 'activo',
            'status_start_date': self.status_start_date.isoformat() if self.status_start_date else None,
            'status_end_date': self.status_end_date.isoformat() if self.status_end_date else None,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None
        }

class EmployeeDocument(db.Model):
    __tablename__ = 'employee_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    original_filename = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(64))
    file_size = db.Column(db.Integer)  # Size in bytes
    description = db.Column(db.String(256))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = db.relationship('Employee', back_populates='documents')
    
    def __repr__(self):
        return f'<EmployeeDocument {self.original_filename}>'

class EmployeeNote(db.Model):
    __tablename__ = 'employee_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = db.relationship('Employee', back_populates='notes')
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User')
    
    def __repr__(self):
        return f'<EmployeeNote {self.id}>'

class EmployeeHistory(db.Model):
    __tablename__ = 'employee_history'
    
    id = db.Column(db.Integer, primary_key=True)
    field_name = db.Column(db.String(64), nullable=False)
    old_value = db.Column(db.String(256))
    new_value = db.Column(db.String(256))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = db.relationship('Employee', back_populates='history')
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    changed_by = db.relationship('User')
    
    def __repr__(self):
        return f'<EmployeeHistory {self.field_name}>'

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(256), nullable=False)
    ip_address = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='activity_logs')
    
    def __repr__(self):
        return f'<ActivityLog {self.action}>'
