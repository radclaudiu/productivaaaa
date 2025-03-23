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
    
    # Credenciales de portal (solo contraseña)
    portal_password = PasswordField('Contraseña del Portal', validators=[Optional(), Length(min=4)],
                                   description='Contraseña para acceder al portal de tareas (opcional)')
    confirm_portal_password = PasswordField('Confirmar Contraseña', 
                                          validators=[Optional(), EqualTo('portal_password', 
                                                                        message='Las contraseñas deben coincidir')])
    
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
    group_id = SelectField('Grupo de tareas', coerce=int, validators=[Optional()])
    
    # Días de la semana para frecuencia personalizada
    monday = BooleanField('Lunes', default=False)
    tuesday = BooleanField('Martes', default=False)
    wednesday = BooleanField('Miércoles', default=False)
    thursday = BooleanField('Jueves', default=False)
    friday = BooleanField('Viernes', default=False)
    saturday = BooleanField('Sábado', default=False)
    sunday = BooleanField('Domingo', default=False)
    
    submit = SubmitField('Guardar Tarea')
    
    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        # Añadir opción para "Sin grupo"
        if self.group_id.choices and self.group_id.choices[0][0] != 0:
            self.group_id.choices.insert(0, (0, 'Sin grupo'))
    
    def validate_end_date(form, field):
        if field.data and form.start_date.data and field.data < form.start_date.data:
            raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio')
            
    def validate(self, **kwargs):
        if not super(TaskForm, self).validate(**kwargs):
            return False
            
        # Verificar que si la frecuencia es personalizada, al menos un día está marcado
        if self.frequency.data == TaskFrequency.PERSONALIZADA.value:
            if not (self.monday.data or self.tuesday.data or self.wednesday.data or 
                    self.thursday.data or self.friday.data or self.saturday.data or 
                    self.sunday.data):
                self.frequency.errors.append('Debes seleccionar al menos un día de la semana para tareas personalizadas')
                return False
                
        return True

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

class TaskGroupForm(FlaskForm):
    name = StringField('Nombre del grupo', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    color = StringField('Color (formato hex)', validators=[DataRequired(), Length(min=4, max=7)])
    location_id = SelectField('Local', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar Grupo')

class CustomWeekdaysForm(FlaskForm):
    weekdays = MultiCheckboxField('Días de la semana', choices=[
        (day.value, day.name.capitalize()) for day in WeekDay
    ], validators=[DataRequired(message='Debes seleccionar al menos un día de la semana')])
    start_time = TimeField('Hora de inicio', validators=[Optional()])
    end_time = TimeField('Hora de fin', validators=[Optional()])
    submit = SubmitField('Guardar Configuración')
    
    def validate_end_time(form, field):
        if field.data and form.start_time.data and field.data < form.start_time.data:
            raise ValidationError('La hora de fin debe ser posterior a la hora de inicio')

class SearchForm(FlaskForm):
    query = StringField('Buscar', validators=[DataRequired()])
    submit = SubmitField('Buscar')
    
class PortalLoginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Acceder al Portal')

# Formularios para el sistema de etiquetas

class ProductForm(FlaskForm):
    """Formulario para crear y editar productos"""
    name = StringField('Nombre del producto', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    shelf_life_days = IntegerField('Vida útil (días)', validators=[
        Optional(),
        NumberRange(min=0, max=365, message='La vida útil debe estar entre 0 y 365 días')
    ], default=0, description='Días hasta caducidad secundaria (0 = sin fecha secundaria)')
    is_active = BooleanField('Producto activo', default=True)
    location_id = SelectField('Local', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar Producto')

class ProductConservationForm(FlaskForm):
    """Formulario para asignar tiempos de conservación a un producto"""
    conservation_type = SelectField('Tipo de conservación', validators=[DataRequired()])
    hours_valid = IntegerField('Horas válidas', validators=[
        DataRequired(),
        NumberRange(min=1, max=2160, message='Las horas deben estar entre 1 y 2160 (90 días)')
    ])
    submit = SubmitField('Guardar Configuración')
    
    def __init__(self, *args, **kwargs):
        super(ProductConservationForm, self).__init__(*args, **kwargs)
        from models_tasks import ConservationType
        self.conservation_type.choices = [(ct.value, ct.name.capitalize()) for ct in ConservationType]

class GenerateLabelForm(FlaskForm):
    """Formulario para generar etiquetas de productos"""
    product_id = SelectField('Producto', coerce=int, validators=[DataRequired()])
    conservation_type = SelectField('Tipo de conservación', validators=[DataRequired()])
    quantity = IntegerField('Cantidad a imprimir', validators=[
        DataRequired(),
        NumberRange(min=1, max=100, message='La cantidad debe estar entre 1 y 100')
    ], default=1)
    submit = SubmitField('Generar Etiquetas')
    
    def __init__(self, *args, **kwargs):
        super(GenerateLabelForm, self).__init__(*args, **kwargs)
        from models_tasks import ConservationType
        self.conservation_type.choices = [(ct.value, ct.name.capitalize()) for ct in ConservationType]