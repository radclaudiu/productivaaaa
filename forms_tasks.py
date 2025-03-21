from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, IntegerField, PasswordField, BooleanField, SubmitField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError, EqualTo
from datetime import date, datetime
from models_tasks import TaskPriority, TaskFrequency, WeekDay

# Widget personalizado para checkboxes con mejor visualización
class MultiCheckboxField(SelectMultipleField):
    """Campo personalizado para mostrar múltiples opciones como checkboxes."""
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class LocationForm(FlaskForm):
    name = StringField('Nombre del local', validators=[DataRequired(), Length(max=128)])
    address = StringField('Dirección', validators=[Length(max=256)])
    city = StringField('Ciudad', validators=[Length(max=64)])
    postal_code = StringField('Código Postal', validators=[Length(max=16)])
    description = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    company_id = SelectField('Empresa', coerce=int, validators=[DataRequired()])
    is_active = BooleanField('Local Activo', default=True)
    submit = SubmitField('Guardar')

class LocalUserForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Apellidos', validators=[DataRequired(), Length(max=64)])
    pin = StringField('PIN (4 dígitos)', validators=[
        DataRequired(), 
        Length(min=4, max=4, message='El PIN debe tener exactamente 4 dígitos'),
    ])
    photo = FileField('Foto', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Solo se permiten imágenes (jpg, jpeg, png)')
    ])
    is_active = BooleanField('Usuario Activo', default=True)
    submit = SubmitField('Guardar')
    
    def validate_pin(form, field):
        if not field.data.isdigit():
            raise ValidationError('El PIN debe contener solo números')

class TaskForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    priority = SelectField('Prioridad', choices=[(p.value, p.name.capitalize()) for p in TaskPriority])
    frequency = SelectField('Frecuencia', choices=[(f.value, f.name.capitalize()) for f in TaskFrequency])
    start_date = DateField('Fecha de inicio', validators=[DataRequired()], default=date.today)
    end_date = DateField('Fecha de fin', validators=[Optional()])
    location_id = SelectField('Local', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar Tarea')
    
    def validate_end_date(form, field):
        if field.data and form.start_date.data and field.data < form.start_date.data:
            raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio')

class DailyScheduleForm(FlaskForm):
    start_time = TimeField('Hora de inicio', validators=[Optional()])
    end_time = TimeField('Hora de fin', validators=[Optional()])
    submit = SubmitField('Guardar Horario')
    
    def validate_end_time(form, field):
        if field.data and form.start_time.data and field.data < form.start_time.data:
            raise ValidationError('La hora de fin debe ser posterior a la hora de inicio')

class WeeklyScheduleForm(FlaskForm):
    day_of_week = SelectField('Día de la semana', choices=[(day.value, day.name.capitalize()) for day in WeekDay])
    start_time = TimeField('Hora de inicio', validators=[Optional()])
    end_time = TimeField('Hora de fin', validators=[Optional()])
    submit = SubmitField('Guardar Horario')
    
    def validate_end_time(form, field):
        if field.data and form.start_time.data and field.data < form.start_time.data:
            raise ValidationError('La hora de fin debe ser posterior a la hora de inicio')

class MonthlyScheduleForm(FlaskForm):
    day_of_month = IntegerField('Día del mes', validators=[
        DataRequired(),
        NumberRange(min=1, max=31, message='El día debe estar entre 1 y 31')
    ])
    start_time = TimeField('Hora de inicio', validators=[Optional()])
    end_time = TimeField('Hora de fin', validators=[Optional()])
    submit = SubmitField('Guardar Horario')
    
    def validate_end_time(form, field):
        if field.data and form.start_time.data and field.data < form.start_time.data:
            raise ValidationError('La hora de fin debe ser posterior a la hora de inicio')

class BiweeklyScheduleForm(FlaskForm):
    start_time = TimeField('Hora de inicio', validators=[Optional()])
    end_time = TimeField('Hora de fin', validators=[Optional()])
    submit = SubmitField('Guardar Horario')
    
    def validate_end_time(form, field):
        if field.data and form.start_time.data and field.data < form.start_time.data:
            raise ValidationError('La hora de fin debe ser posterior a la hora de inicio')

class TaskCompletionForm(FlaskForm):
    notes = TextAreaField('Notas', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Marcar como Completada')

# Eliminada la clase LocalUserLoginForm ya que no se usará más

class LocalUserPinForm(FlaskForm):
    pin = StringField('PIN (4 dígitos)', validators=[
        DataRequired(), 
        Length(min=4, max=4, message='El PIN debe tener exactamente 4 dígitos')
    ])
    submit = SubmitField('Acceder')
    
    def validate_pin(form, field):
        if not field.data.isdigit():
            raise ValidationError('El PIN debe contener solo números')

class SearchForm(FlaskForm):
    query = StringField('Buscar', validators=[DataRequired()])
    submit = SubmitField('Buscar')