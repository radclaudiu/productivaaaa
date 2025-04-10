"""
Formularios para la gestión de turnos y horarios.

Este módulo proporciona los formularios para:
- Crear y editar turnos
- Asignar turnos a empleados en fechas específicas
- Registrar ausencias
- Definir patrones de horarios
"""

from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField, DateField, TimeField, 
                   TextAreaField, HiddenField, IntegerField, BooleanField,
                   RadioField, SelectMultipleField, SubmitField)
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from datetime import date, datetime, timedelta
from models_turnos import TipoTurno, TipoAusencia

class TurnoForm(FlaskForm):
    """
    Formulario para crear y editar turnos.
    
    Permite definir los detalles de un turno como horarios,
    color, tipo, etc.
    """
    nombre = StringField('Nombre del Turno', 
                       validators=[DataRequired(), Length(min=2, max=50)])
    tipo = SelectField('Tipo de Turno', 
                     choices=[(tipo.name, tipo.value) for tipo in TipoTurno],
                     validators=[DataRequired()])
    hora_inicio = TimeField('Hora de Inicio', 
                          format='%H:%M',
                          validators=[DataRequired()])
    hora_fin = TimeField('Hora de Fin', 
                       format='%H:%M',
                       validators=[DataRequired()])
    color = StringField('Color (HEX)', 
                      default="#3498db",
                      validators=[DataRequired(), Length(min=4, max=7)])
    descanso_inicio = TimeField('Inicio de Descanso', 
                              format='%H:%M',
                              validators=[Optional()])
    descanso_fin = TimeField('Fin de Descanso', 
                           format='%H:%M',
                           validators=[Optional()])
    descripcion = TextAreaField('Descripción', 
                              validators=[Optional(), Length(max=500)])
    company_id = HiddenField('ID de Empresa', validators=[DataRequired()])
    
    def validate_descanso_fin(self, field):
        """Valida que el fin del descanso sea posterior al inicio."""
        if self.descanso_inicio.data and field.data:
            if field.data <= self.descanso_inicio.data:
                raise ValidationError('El fin del descanso debe ser posterior al inicio.')
    
    def validate_hora_fin(self, field):
        """
        Valida las horas de inicio y fin.
        
        Nota: No valida que hora_fin sea mayor que hora_inicio porque
        algunos turnos pueden pasar de un día a otro.
        """
        if not self.hora_inicio.data:
            return
        
        # Verificar que el turno no dure más de 24 horas
        inicio = datetime.combine(date.today(), self.hora_inicio.data)
        fin = datetime.combine(date.today(), field.data)
        
        if fin < inicio:  # Si el turno pasa al día siguiente
            fin += timedelta(days=1)
            
        duracion = (fin - inicio).total_seconds() / 3600  # Convertir a horas
        
        if duracion > 24:
            raise ValidationError('La duración del turno no puede exceder 24 horas.')

class HorarioForm(FlaskForm):
    """
    Formulario para asignar turnos a empleados.
    
    Permite seleccionar un empleado, un turno y una fecha.
    """
    fecha = DateField('Fecha', 
                    format='%Y-%m-%d',
                    validators=[DataRequired()])
    employee_id = SelectField('Empleado', 
                           coerce=int,
                           validators=[DataRequired()])
    turno_id = RadioField('Turno', 
                        coerce=int,
                        validators=[DataRequired()])
    notas = TextAreaField('Notas', 
                        validators=[Optional(), Length(max=200)])
    
    def validate_fecha(self, field):
        """Verifica que la fecha no sea anterior a hoy."""
        if field.data < date.today():
            raise ValidationError('No se pueden crear horarios para fechas pasadas.')

class AusenciaForm(FlaskForm):
    """
    Formulario para registrar ausencias de empleados.
    
    Permite seleccionar un empleado, un tipo de ausencia y un rango de fechas.
    """
    employee_id = SelectField('Empleado', 
                           coerce=int,
                           validators=[DataRequired()])
    fecha_inicio = DateField('Fecha de Inicio', 
                          format='%Y-%m-%d',
                          validators=[DataRequired()])
    fecha_fin = DateField('Fecha de Fin', 
                        format='%Y-%m-%d',
                        validators=[DataRequired()])
    tipo = SelectField('Tipo de Ausencia', 
                     choices=[(tipo.name, tipo.value) for tipo in TipoAusencia],
                     validators=[DataRequired()])
    motivo = TextAreaField('Motivo', 
                        validators=[Optional(), Length(max=500)])
    aprobado = BooleanField('Aprobado')
    
    def validate_fecha_fin(self, field):
        """Valida que la fecha de fin sea posterior o igual a la de inicio."""
        if self.fecha_inicio.data and field.data:
            if field.data < self.fecha_inicio.data:
                raise ValidationError('La fecha de fin debe ser posterior o igual a la fecha de inicio.')

class PlantillaHorarioForm(FlaskForm):
    """
    Formulario para crear plantillas de horarios semanales.
    
    Permite definir un patrón semanal de turnos que puede
    ser aplicado rápidamente a empleados.
    """
    nombre = StringField('Nombre de la Plantilla', 
                       validators=[DataRequired(), Length(min=2, max=100)])
    descripcion = TextAreaField('Descripción', 
                              validators=[Optional(), Length(max=500)])
    company_id = HiddenField('ID de Empresa', validators=[DataRequired()])

class DetallePlantillaForm(FlaskForm):
    """
    Formulario para definir los detalles de una plantilla de horario.
    
    Permite asignar turnos específicos a cada día de la semana
    en una plantilla.
    """
    plantilla_id = HiddenField('ID de Plantilla', validators=[DataRequired()])
    dia_semana = SelectField('Día de la Semana',
                          choices=[(0, 'Lunes'), 
                                  (1, 'Martes'), 
                                  (2, 'Miércoles'), 
                                  (3, 'Jueves'), 
                                  (4, 'Viernes'), 
                                  (5, 'Sábado'), 
                                  (6, 'Domingo')],
                          coerce=int,
                          validators=[DataRequired()])
    turno_id = SelectField('Turno', 
                        coerce=int,
                        validators=[DataRequired()])

class AsignacionPlantillaForm(FlaskForm):
    """
    Formulario para asignar una plantilla de horarios a un empleado.
    
    Permite aplicar un patrón semanal predefinido a un empleado
    a partir de una fecha específica.
    """
    plantilla_id = SelectField('Plantilla de Horario', 
                            coerce=int,
                            validators=[DataRequired()])
    employee_id = SelectField('Empleado', 
                           coerce=int,
                           validators=[DataRequired()])
    fecha_inicio = DateField('Fecha de Inicio', 
                          format='%Y-%m-%d',
                          validators=[DataRequired()])
    fecha_fin = DateField('Fecha de Fin (opcional)', 
                       format='%Y-%m-%d',
                       validators=[Optional()])
    
    def validate_fecha_fin(self, field):
        """Valida que la fecha de fin sea posterior a la de inicio."""
        if self.fecha_inicio.data and field.data:
            if field.data <= self.fecha_inicio.data:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')

class AsignacionMasivaForm(FlaskForm):
    """
    Formulario para asignar turnos a múltiples empleados o múltiples días.
    
    Permite una asignación eficiente de turnos a varios empleados
    o en un rango de fechas.
    """
    fecha_inicio = DateField('Fecha de Inicio', 
                          format='%Y-%m-%d',
                          validators=[DataRequired()])
    fecha_fin = DateField('Fecha de Fin', 
                       format='%Y-%m-%d',
                       validators=[DataRequired()])
    dias_semana = SelectMultipleField('Días de la Semana',
                                    choices=[(0, 'Lunes'), 
                                            (1, 'Martes'), 
                                            (2, 'Miércoles'), 
                                            (3, 'Jueves'), 
                                            (4, 'Viernes'), 
                                            (5, 'Sábado'), 
                                            (6, 'Domingo')],
                                    coerce=int,
                                    validators=[DataRequired()])
    turno_id = SelectField('Turno', 
                        coerce=int,
                        validators=[DataRequired()])
    employees = SelectMultipleField('Empleados', 
                                 coerce=int,
                                 validators=[DataRequired()])
    notas = TextAreaField('Notas para todos los horarios', 
                        validators=[Optional(), Length(max=200)])
    
    def validate_fecha_fin(self, field):
        """Valida que la fecha de fin sea posterior o igual a la de inicio."""
        if self.fecha_inicio.data and field.data:
            if field.data < self.fecha_inicio.data:
                raise ValidationError('La fecha de fin debe ser posterior o igual a la fecha de inicio.')
            
            # Verificar que el rango no sea demasiado grande (máximo 3 meses)
            delta = field.data - self.fecha_inicio.data
            if delta.days > 90:
                raise ValidationError('El rango de fechas no puede exceder 3 meses.')

class FiltroCalendarioForm(FlaskForm):
    """
    Formulario para filtrar la vista de calendario.
    
    Permite seleccionar qué empleados y turnos mostrar
    en la vista de calendario.
    """
    semana = DateField('Semana', 
                     format='%Y-%m-%d',
                     validators=[Optional()])
    employee_id = SelectField('Empleado', 
                           coerce=int,
                           validators=[Optional()])
    turno_id = SelectField('Turno', 
                        coerce=int,
                        validators=[Optional()])
    
class EliminarHorarioForm(FlaskForm):
    """
    Formulario para eliminar un horario.
    
    Simplicidad para eliminar asignaciones de turnos.
    """
    horario_id = HiddenField('ID de Horario', validators=[DataRequired()])

class PreferenciaDisponibilidadForm(FlaskForm):
    """
    Formulario para registrar preferencias de disponibilidad de un empleado.
    
    Permite a los empleados indicar en qué días y horarios prefieren trabajar.
    """
    employee_id = HiddenField('ID de Empleado', validators=[DataRequired()])
    dia_semana = SelectField('Día de la Semana',
                          choices=[(0, 'Lunes'), 
                                  (1, 'Martes'), 
                                  (2, 'Miércoles'), 
                                  (3, 'Jueves'), 
                                  (4, 'Viernes'), 
                                  (5, 'Sábado'), 
                                  (6, 'Domingo')],
                          coerce=int,
                          validators=[DataRequired()])
    hora_inicio = TimeField('Hora de Inicio', 
                          format='%H:%M',
                          validators=[DataRequired()])
    hora_fin = TimeField('Hora de Fin', 
                       format='%H:%M',
                       validators=[DataRequired()])
    preferencia = SelectField('Preferencia',
                           choices=[(-1, 'No disponible'), 
                                   (0, 'Neutro'), 
                                   (1, 'Preferido')],
                           coerce=int,
                           validators=[DataRequired()])
    
    def validate_hora_fin(self, field):
        """Valida que la hora de fin sea posterior a la de inicio."""
        if self.hora_inicio.data and field.data:
            if field.data <= self.hora_inicio.data:
                raise ValidationError('La hora de fin debe ser posterior a la hora de inicio.')

class RequisitoPersonalForm(FlaskForm):
    """
    Formulario para definir requisitos de personal por franja horaria.
    
    Permite especificar cuántos empleados se necesitan en cada
    día y hora específicos.
    """
    company_id = HiddenField('ID de Empresa', validators=[DataRequired()])
    dia_semana = SelectField('Día de la Semana',
                          choices=[(0, 'Lunes'), 
                                  (1, 'Martes'), 
                                  (2, 'Miércoles'), 
                                  (3, 'Jueves'), 
                                  (4, 'Viernes'), 
                                  (5, 'Sábado'), 
                                  (6, 'Domingo')],
                          coerce=int,
                          validators=[DataRequired()])
    hora_inicio = TimeField('Hora de Inicio', 
                          format='%H:%M',
                          validators=[DataRequired()])
    hora_fin = TimeField('Hora de Fin', 
                       format='%H:%M',
                       validators=[DataRequired()])
    num_empleados = IntegerField('Número de Empleados Requeridos',
                               default=1,
                               validators=[DataRequired()])
    notas = TextAreaField('Notas', 
                        validators=[Optional(), Length(max=200)])
    
    def validate_hora_fin(self, field):
        """Valida que la hora de fin sea posterior a la de inicio."""
        if self.hora_inicio.data and field.data:
            if field.data <= self.hora_inicio.data:
                raise ValidationError('La hora de fin debe ser posterior a la hora de inicio.')
                
    def validate_num_empleados(self, field):
        """Valida que el número de empleados sea positivo."""
        if field.data < 1:
            raise ValidationError('El número de empleados debe ser al menos 1.')