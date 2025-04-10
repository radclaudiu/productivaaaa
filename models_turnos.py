"""
Módulo para la gestión de turnos y horarios de empleados.

Este módulo proporciona los modelos para:
- Definir tipos de turnos (mañana, tarde, noche)
- Crear y gestionar horarios semanales para empleados
- Registrar ausencias, vacaciones y bajas
- Definir requisitos de personal por franja horaria
"""

import enum
from datetime import datetime, timedelta
from app import db
from models import Employee, Company

class TipoTurno(enum.Enum):
    """Tipos de turnos disponibles."""
    MANANA = "Mañana"
    TARDE = "Tarde"
    NOCHE = "Noche"
    COMPLETO = "Completo"
    PERSONALIZADO = "Personalizado"

class TipoAusencia(enum.Enum):
    """Tipos de ausencias disponibles."""
    VACACIONES = "Vacaciones"
    BAJA_MEDICA = "Baja médica"
    PERMISO = "Permiso"
    ASUNTOS_PROPIOS = "Asuntos propios"
    OTRO = "Otro"

class Turno(db.Model):
    """
    Modelo para definir los tipos de turnos y sus características.
    
    Un turno define un patrón horario que puede ser asignado a empleados
    en diferentes días.
    """
    __tablename__ = 'turnos_turno'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.Enum(TipoTurno), nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    color = db.Column(db.String(7), nullable=False, default="#3498db")  # Color en formato HEX
    descripcion = db.Column(db.Text)
    descanso_inicio = db.Column(db.Time, nullable=True)
    descanso_fin = db.Column(db.Time, nullable=True)
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = db.relationship('Company', backref=db.backref('turnos', lazy=True))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f"<Turno '{self.nombre}' ({self.tipo.value})>"
    
    @property
    def duracion_total(self):
        """Retorna la duración total del turno en horas."""
        inicio = timedelta(hours=self.hora_inicio.hour, minutes=self.hora_inicio.minute)
        fin = timedelta(hours=self.hora_fin.hour, minutes=self.hora_fin.minute)
        
        # Si el turno pasa de un día a otro
        if fin < inicio:
            fin += timedelta(days=1)
            
        return (fin - inicio).total_seconds() / 3600  # Convertir a horas

    @property
    def duracion_descanso(self):
        """Retorna la duración del descanso en horas (si existe)."""
        if not self.descanso_inicio or not self.descanso_fin:
            return 0
            
        inicio = timedelta(hours=self.descanso_inicio.hour, minutes=self.descanso_inicio.minute)
        fin = timedelta(hours=self.descanso_fin.hour, minutes=self.descanso_fin.minute)
        
        # Si el descanso pasa de un día a otro
        if fin < inicio:
            fin += timedelta(days=1)
            
        return (fin - inicio).total_seconds() / 3600  # Convertir a horas
    
    @property
    def horas_efectivas(self):
        """Retorna las horas efectivas de trabajo (total - descanso)."""
        return self.duracion_total - self.duracion_descanso

class Horario(db.Model):
    """
    Modelo para asignar turnos a empleados en días específicos.
    
    Un horario representa la asignación de un empleado a un turno
    en una fecha específica.
    """
    __tablename__ = 'turnos_horario'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    notas = db.Column(db.Text)
    
    turno_id = db.Column(db.Integer, db.ForeignKey('turnos_turno.id'), nullable=False)
    turno = db.relationship('Turno', backref=db.backref('asignaciones', lazy=True))
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = db.relationship('Employee', backref=db.backref('horarios', lazy=True))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f"<Horario: {self.employee.nombre} - {self.fecha} - {self.turno.nombre}>"

class Ausencia(db.Model):
    """
    Modelo para registrar ausencias de empleados (vacaciones, bajas, etc.)
    
    Una ausencia representa un período en el que un empleado no está
    disponible para asignarle turnos.
    """
    __tablename__ = 'turnos_ausencia'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.Enum(TipoAusencia), nullable=False)
    motivo = db.Column(db.Text)
    aprobado = db.Column(db.Boolean, default=False)
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = db.relationship('Employee', backref=db.backref('ausencias', lazy=True))
    
    aprobado_por_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    aprobado_por = db.relationship('User')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Ausencia: {self.employee.nombre} - {self.tipo.value} ({self.fecha_inicio} a {self.fecha_fin})>"
    
    @property
    def dias_totales(self):
        """Retorna el número total de días de ausencia."""
        delta = self.fecha_fin - self.fecha_inicio
        return delta.days + 1  # Incluimos ambos días

class RequisitoPersonal(db.Model):
    """
    Modelo para definir requisitos de personal por día y franja horaria.
    
    Permite especificar cuántos empleados se necesitan en cada franja
    horaria para cada día de la semana.
    """
    __tablename__ = 'turnos_requisito_personal'
    
    id = db.Column(db.Integer, primary_key=True)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0-6 (lunes a domingo)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    num_empleados = db.Column(db.Integer, nullable=False, default=1)
    notas = db.Column(db.Text)
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = db.relationship('Company', backref=db.backref('requisitos_personal', lazy=True))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        return f"<Requisito: {dias[self.dia_semana]} {self.hora_inicio}-{self.hora_fin}, {self.num_empleados} empleados>"

class PlantillaHorario(db.Model):
    """
    Modelo para almacenar plantillas de horarios semanales.
    
    Permite definir patrones semanales que pueden ser aplicados
    para generar horarios rápidamente.
    """
    __tablename__ = 'turnos_plantilla_horario'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = db.relationship('Company', backref=db.backref('plantillas_horario', lazy=True))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f"<Plantilla: {self.nombre}>"

class DetallePlantilla(db.Model):
    """
    Modelo para almacenar los detalles de una plantilla de horario.
    
    Define qué turnos aplican a qué días de la semana en una plantilla.
    """
    __tablename__ = 'turnos_detalle_plantilla'
    
    id = db.Column(db.Integer, primary_key=True)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0-6 (lunes a domingo)
    
    plantilla_id = db.Column(db.Integer, db.ForeignKey('turnos_plantilla_horario.id'), nullable=False)
    plantilla = db.relationship('PlantillaHorario', backref=db.backref('detalles', lazy=True))
    
    turno_id = db.Column(db.Integer, db.ForeignKey('turnos_turno.id'), nullable=False)
    turno = db.relationship('Turno')
    
    def __repr__(self):
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        return f"<Detalle: {self.plantilla.nombre} - {dias[self.dia_semana]} - {self.turno.nombre}>"

class AsignacionPlantilla(db.Model):
    """
    Modelo para asignar plantillas de horario a empleados.
    
    Permite aplicar una plantilla de horario a un empleado específico.
    """
    __tablename__ = 'turnos_asignacion_plantilla'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=True)  # Null significa indefinido
    
    plantilla_id = db.Column(db.Integer, db.ForeignKey('turnos_plantilla_horario.id'), nullable=False)
    plantilla = db.relationship('PlantillaHorario')
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = db.relationship('Employee', backref=db.backref('asignaciones_plantilla', lazy=True))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f"<Asignación: {self.employee.nombre} - {self.plantilla.nombre}>"

class PreferenciaDisponibilidad(db.Model):
    """
    Modelo para registrar las preferencias de disponibilidad de un empleado.
    
    Permite a los empleados indicar en qué días y horarios prefieren trabajar.
    """
    __tablename__ = 'turnos_preferencia_disponibilidad'
    
    id = db.Column(db.Integer, primary_key=True)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0-6 (lunes a domingo)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    preferencia = db.Column(db.Integer, nullable=False, default=0)  # -1: No disponible, 0: Neutro, 1: Preferido
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = db.relationship('Employee', backref=db.backref('preferencias_disponibilidad', lazy=True))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        preferencias = {-1: "No disponible", 0: "Neutro", 1: "Preferido"}
        return f"<Preferencia: {self.employee.nombre} - {dias[self.dia_semana]} {self.hora_inicio}-{self.hora_fin}, {preferencias[self.preferencia]}>"

class HistorialCambios(db.Model):
    """
    Modelo para registrar el historial de cambios en los horarios.
    
    Permite llevar un registro de quién realizó cambios en los horarios y cuándo.
    """
    __tablename__ = 'turnos_historial_cambios'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_cambio = db.Column(db.DateTime, default=datetime.utcnow)
    tipo_cambio = db.Column(db.String(50), nullable=False)  # "creacion", "modificacion", "eliminacion"
    descripcion = db.Column(db.Text, nullable=False)
    
    horario_id = db.Column(db.Integer, db.ForeignKey('turnos_horario.id'), nullable=True)
    horario = db.relationship('Horario')
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User')
    
    def __repr__(self):
        return f"<Cambio: {self.tipo_cambio} - {self.fecha_cambio} por {self.user.username}>"