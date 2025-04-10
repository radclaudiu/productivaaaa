"""
Formularios para la gestión de turnos y horarios de empleados.

Este módulo proporciona formularios para:
- Crear y editar turnos
- Asignar turnos a empleados
- Gestionar ausencias
- Crear plantillas de horarios
"""

from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, SelectField, TimeField, 
                     DateField, IntegerField, BooleanField, HiddenField,
                     SelectMultipleField, SubmitField, FormField, FieldList)
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from models_turnos import TipoTurno, TipoAusencia
from datetime import datetime, time, date

class TurnoForm(FlaskForm):
    """Formulario para crear y editar turnos."""
    nombre = StringField('Nombre del turno', validators=[DataRequired(), Length(max=50)])
    tipo = SelectField('Tipo de turno', choices=[(t.name, t.value) for t in TipoTurno], validators=[DataRequired()])
    hora_inicio = TimeField('Hora de inicio', validators=[DataRequired()])
    hora_fin = TimeField('Hora de fin', validators=[DataRequired()])
    color = StringField('Color', validators=[DataRequired(), Length(max=7)], default="#3498db")
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    descanso_inicio = TimeField('Inicio del descanso', validators=[Optional()])
    descanso_fin = TimeField('Fin del descanso', validators=[Optional()])
    company_id = HiddenField('ID de empresa', validators=[DataRequired()])
    submit = SubmitField('Guardar')
    
    def validate_hora_fin(self, field):
        """Validar que la hora de fin sea posterior a la hora de inicio, o igual si cruza de día."""
        if self.hora_inicio.data and field.data:
            if field.data == self.hora_inicio.data:
                raise ValidationError('La hora de fin debe ser diferente a la hora de inicio.')
    
    def validate_descanso_fin(self, field):
        """Validar que el fin del descanso sea posterior al inicio del descanso."""
        if self.descanso_inicio.data and field.data:
            if field.data < self.descanso_inicio.data:
                raise ValidationError('El fin del descanso debe ser posterior al inicio del descanso.')

class HorarioForm(FlaskForm):
    """Formulario para asignar turnos a empleados."""
    fecha = DateField('Fecha', validators=[DataRequired()])
    turno_id = SelectField('Turno', validators=[DataRequired()], coerce=int)
    employee_id = SelectField('Empleado', validators=[DataRequired()], coerce=int)
    notas = TextAreaField('Notas', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Asignar turno')

class HorarioMasivoForm(FlaskForm):
    """Formulario para asignar turnos de forma masiva."""
    fecha_inicio = DateField('Fecha de inicio', validators=[DataRequired()])
    fecha_fin = DateField('Fecha de fin', validators=[DataRequired()])
    turno_id = SelectField('Turno', validators=[DataRequired()], coerce=int)
    employee_ids = SelectMultipleField('Empleados', validators=[DataRequired()], coerce=int)
    dias_semana = SelectMultipleField('Días de la semana', choices=[
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), 
        (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')
    ], coerce=int)
    notas = TextAreaField('Notas', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Asignar turnos masivamente')
    
    def validate_fecha_fin(self, field):
        """Validar que la fecha de fin sea posterior a la fecha de inicio."""
        if self.fecha_inicio.data and field.data:
            if field.data < self.fecha_inicio.data:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')

class EliminarHorarioForm(FlaskForm):
    """Formulario para eliminar asignaciones de horario."""
    horario_id = HiddenField('ID de horario', validators=[DataRequired()])
    submit = SubmitField('Eliminar asignación')

class AusenciaForm(FlaskForm):
    """Formulario para registrar ausencias de empleados."""
    fecha_inicio = DateField('Fecha de inicio', validators=[DataRequired()])
    fecha_fin = DateField('Fecha de fin', validators=[DataRequired()])
    tipo = SelectField('Tipo de ausencia', choices=[(t.name, t.value) for t in TipoAusencia], validators=[DataRequired()])
    motivo = TextAreaField('Motivo de la ausencia', validators=[Optional(), Length(max=500)])
    employee_id = SelectField('Empleado', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Registrar ausencia')
    
    def validate_fecha_fin(self, field):
        """Validar que la fecha de fin sea posterior o igual a la fecha de inicio."""
        if self.fecha_inicio.data and field.data:
            if field.data < self.fecha_inicio.data:
                raise ValidationError('La fecha de fin debe ser posterior o igual a la fecha de inicio.')

class AprobarAusenciaForm(FlaskForm):
    """Formulario para aprobar o rechazar ausencias."""
    ausencia_id = HiddenField('ID de ausencia', validators=[DataRequired()])
    aprobado = BooleanField('Aprobar ausencia')
    submit = SubmitField('Guardar decisión')

class RequisitoPersonalForm(FlaskForm):
    """Formulario para definir requisitos de personal."""
    dia_semana = SelectField('Día de la semana', choices=[
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), 
        (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')
    ], validators=[DataRequired()], coerce=int)
    hora_inicio = TimeField('Hora de inicio', validators=[DataRequired()])
    hora_fin = TimeField('Hora de fin', validators=[DataRequired()])
    num_empleados = IntegerField('Número de empleados necesarios', validators=[DataRequired()], default=1)
    notas = TextAreaField('Notas', validators=[Optional(), Length(max=500)])
    company_id = HiddenField('ID de empresa', validators=[DataRequired()])
    submit = SubmitField('Guardar requisito')
    
    def validate_hora_fin(self, field):
        """Validar que la hora de fin sea posterior a la hora de inicio."""
        if self.hora_inicio.data and field.data:
            if field.data <= self.hora_inicio.data:
                raise ValidationError('La hora de fin debe ser posterior a la hora de inicio.')
    
    def validate_num_empleados(self, field):
        """Validar que el número de empleados sea positivo."""
        if field.data < 1:
            raise ValidationError('Debe haber al menos un empleado requerido.')

class PlantillaHorarioForm(FlaskForm):
    """Formulario para crear plantillas de horarios."""
    nombre = StringField('Nombre de la plantilla', validators=[DataRequired(), Length(max=100)])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    company_id = HiddenField('ID de empresa', validators=[DataRequired()])
    submit = SubmitField('Guardar plantilla')

class DetallePlantillaForm(FlaskForm):
    """Formulario para agregar detalles a una plantilla de horario."""
    dia_semana = SelectField('Día de la semana', choices=[
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), 
        (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')
    ], validators=[DataRequired()], coerce=int)
    turno_id = SelectField('Turno', validators=[DataRequired()], coerce=int)
    plantilla_id = HiddenField('ID de plantilla', validators=[DataRequired()])
    submit = SubmitField('Agregar a plantilla')

class AsignacionPlantillaForm(FlaskForm):
    """Formulario para asignar plantillas de horario a empleados."""
    plantilla_id = SelectField('Plantilla de horario', validators=[DataRequired()], coerce=int)
    employee_id = SelectField('Empleado', validators=[DataRequired()], coerce=int)
    fecha_inicio = DateField('Fecha de inicio', validators=[DataRequired()])
    fecha_fin = DateField('Fecha de fin', validators=[Optional()])
    submit = SubmitField('Asignar plantilla')
    
    def validate_fecha_fin(self, field):
        """Validar que la fecha de fin sea posterior a la fecha de inicio si se proporciona."""
        if self.fecha_inicio.data and field.data:
            if field.data < self.fecha_inicio.data:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')

class PreferenciaDisponibilidadForm(FlaskForm):
    """Formulario para registrar preferencias de disponibilidad de empleados."""
    dia_semana = SelectField('Día de la semana', choices=[
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), 
        (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')
    ], validators=[DataRequired()], coerce=int)
    hora_inicio = TimeField('Hora de inicio', validators=[DataRequired()])
    hora_fin = TimeField('Hora de fin', validators=[DataRequired()])
    preferencia = SelectField('Preferencia', choices=[
        (-1, 'No disponible'), (0, 'Neutro'), (1, 'Preferido')
    ], validators=[DataRequired()], coerce=int)
    employee_id = HiddenField('ID de empleado', validators=[DataRequired()])
    submit = SubmitField('Guardar preferencia')
    
    def validate_hora_fin(self, field):
        """Validar que la hora de fin sea posterior a la hora de inicio."""
        if self.hora_inicio.data and field.data:
            if field.data <= self.hora_inicio.data:
                raise ValidationError('La hora de fin debe ser posterior a la hora de inicio.')

class FiltroHorarioForm(FlaskForm):
    """Formulario para filtrar la vista de horarios."""
    fecha_inicio = DateField('Desde', validators=[DataRequired()], default=date.today)
    fecha_fin = DateField('Hasta', validators=[Optional()])
    employee_id = SelectField('Empleado', validators=[Optional()], coerce=int)
    turno_id = SelectField('Turno', validators=[Optional()], coerce=int)
    company_id = SelectField('Empresa', validators=[Optional()], coerce=int)
    submit = SubmitField('Filtrar')
    
    def validate_fecha_fin(self, field):
        """Validar que la fecha de fin sea posterior a la fecha de inicio si se proporciona."""
        if self.fecha_inicio.data and field.data:
            if field.data < self.fecha_inicio.data:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')