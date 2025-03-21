from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms import BooleanField, DateField, HiddenField, EmailField, TelField, URLField, TimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from datetime import date

from models import User, ContractType, UserRole, EmployeeStatus, WeekDay, VacationStatus

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repetir Contraseña', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Apellidos', validators=[DataRequired(), Length(max=64)])
    role = SelectField('Rol', choices=[(role.value, role.name.capitalize()) for role in UserRole])
    company_id = SelectField('Empresa', coerce=int)
    submit = SubmitField('Registrar')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Por favor, usa un nombre de usuario diferente.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Por favor, usa un email diferente.')

class UserUpdateForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Apellidos', validators=[DataRequired(), Length(max=64)])
    role = SelectField('Rol', choices=[(role.value, role.name.capitalize()) for role in UserRole])
    company_id = SelectField('Empresa', coerce=int)
    is_active = BooleanField('Usuario Activo')
    submit = SubmitField('Actualizar Usuario')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
        
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Por favor, usa un nombre de usuario diferente.')
                
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Por favor, usa un email diferente.')

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Contraseña Actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva Contraseña', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(), EqualTo('new_password', message='Las contraseñas deben coincidir')
    ])
    submit = SubmitField('Cambiar Contraseña')

class CompanyForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=128)])
    address = StringField('Dirección', validators=[Length(max=256)])
    city = StringField('Ciudad', validators=[Length(max=64)])
    postal_code = StringField('Código Postal', validators=[Length(max=16)])
    country = StringField('País', validators=[Length(max=64)])
    sector = StringField('Sector', validators=[Length(max=64)])
    tax_id = StringField('CIF/NIF', validators=[DataRequired(), Length(max=32)])
    phone = TelField('Teléfono', validators=[Length(max=32)])
    email = EmailField('Email', validators=[Email(), Length(max=120)])
    website = URLField('Sitio Web', validators=[Length(max=128)])
    is_active = BooleanField('Empresa Activa')
    submit = SubmitField('Guardar')

class EmployeeForm(FlaskForm):
    first_name = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Apellidos', validators=[DataRequired(), Length(max=64)])
    dni = StringField('DNI/NIE', validators=[DataRequired(), Length(max=16)])
    position = StringField('Puesto', validators=[Length(max=64)])
    contract_type = SelectField('Tipo de Contrato', 
                               choices=[(ct.value, ct.name.capitalize()) for ct in ContractType])
    bank_account = StringField('Cuenta Bancaria', validators=[Length(max=64)])
    start_date = DateField('Fecha de Inicio', validators=[Optional()], default=date.today)
    end_date = DateField('Fecha de Fin', validators=[Optional()])
    company_id = SelectField('Empresa', coerce=int, validators=[DataRequired()])
    is_active = BooleanField('Empleado Activo')
    status = SelectField('Estado', choices=[(status.value, status.name.capitalize()) for status in EmployeeStatus], 
                        default=EmployeeStatus.ACTIVO.value)
    submit = SubmitField('Guardar')
    
    def validate_end_date(form, field):
        if field.data and form.start_date.data and field.data < form.start_date.data:
            raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')

class EmployeeDocumentForm(FlaskForm):
    file = FileField('Documento', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'], 'Solo se permiten archivos PDF, DOC, DOCX, JPG, JPEG y PNG')
    ])
    description = StringField('Descripción', validators=[Length(max=256)])
    submit = SubmitField('Subir')

class EmployeeNoteForm(FlaskForm):
    content = TextAreaField('Nota', validators=[DataRequired()])
    submit = SubmitField('Guardar')

class EmployeeStatusForm(FlaskForm):
    status = SelectField('Estado', choices=[(status.value, status.name.capitalize()) for status in EmployeeStatus])
    status_start_date = DateField('Fecha de Inicio', validators=[DataRequired()], default=date.today)
    status_end_date = DateField('Fecha de Fin Prevista', validators=[Optional()])
    status_notes = TextAreaField('Notas', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Actualizar Estado')
    
    def validate_status_end_date(form, field):
        if field.data and form.status_start_date.data and field.data < form.status_start_date.data:
            raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')

class SearchForm(FlaskForm):
    query = StringField('Buscar', validators=[DataRequired()])
    submit = SubmitField('Buscar')

class EmployeeScheduleForm(FlaskForm):
    day_of_week = SelectField('Día de la Semana', choices=[(day.value, day.name.capitalize()) for day in WeekDay])
    start_time = TimeField('Hora de Entrada', validators=[DataRequired()])
    end_time = TimeField('Hora de Salida', validators=[DataRequired()])
    is_working_day = BooleanField('Día Laborable', default=True)
    submit = SubmitField('Guardar Horario')
    
    def validate_end_time(form, field):
        if form.start_time.data and field.data and field.data <= form.start_time.data:
            raise ValidationError('La hora de salida debe ser posterior a la hora de entrada.')

class EmployeeCheckInForm(FlaskForm):
    check_in_time = DateField('Fecha de Entrada', validators=[DataRequired()], default=date.today)
    check_out_time = DateField('Fecha de Salida', validators=[Optional()])
    notes = TextAreaField('Notas', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Registrar Fichaje')
    
    def validate_check_out_time(form, field):
        if field.data and form.check_in_time.data and field.data < form.check_in_time.data:
            raise ValidationError('La fecha de salida debe ser posterior a la fecha de entrada.')

class EmployeeVacationForm(FlaskForm):
    start_date = DateField('Fecha de Inicio', validators=[DataRequired()], default=date.today)
    end_date = DateField('Fecha de Fin', validators=[DataRequired()])
    status = SelectField('Estado', choices=[(status.value, status.name.capitalize()) for status in VacationStatus],
                        default=VacationStatus.PENDIENTE.value)
    notes = TextAreaField('Notas', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Solicitar Vacaciones')
    
    def validate_end_date(form, field):
        if field.data and form.start_date.data and field.data < form.start_date.data:
            raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')

class EmployeeVacationApprovalForm(FlaskForm):
    status = SelectField('Estado', choices=[
        (VacationStatus.PENDIENTE.value, 'Pendiente'),
        (VacationStatus.APROBADA.value, 'Aprobada'),
        (VacationStatus.DENEGADA.value, 'Denegada'),
    ])
    notes = TextAreaField('Notas', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Actualizar Estado')

class GenerateCheckInsForm(FlaskForm):
    start_date = DateField('Fecha de Inicio', validators=[DataRequired()], default=date.today)
    end_date = DateField('Fecha de Fin', validators=[DataRequired()])
    submit = SubmitField('Generar Fichajes')
    
    def validate_end_date(form, field):
        if field.data and form.start_date.data and field.data < form.start_date.data:
            raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
