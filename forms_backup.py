"""
Formularios para la gestión de backups de la base de datos.

Este módulo define los formularios utilizados en las páginas de gestión de backups,
incluyendo la creación y restauración de backups.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

class CreateBackupForm(FlaskForm):
    """
    Formulario para crear un nuevo backup de la base de datos.
    """
    type = SelectField(
        'Tipo de Backup', 
        choices=[
            ('full', 'Completo (esquema y datos)'),
            ('schema', 'Solo esquema (sin datos)')
        ],
        validators=[DataRequired()]
    )
    
    compress = BooleanField('Comprimir backup', default=True)
    
    description = TextAreaField(
        'Descripción', 
        validators=[Length(max=200)],
        description='Descripción opcional para identificar este backup'
    )
    
    submit = SubmitField('Crear Backup')


class RestoreBackupForm(FlaskForm):
    """
    Formulario para restaurar un backup en la base de datos.
    """
    admin_password = PasswordField(
        'Contraseña de Administrador', 
        validators=[DataRequired()],
        description='Ingrese su contraseña de administrador para confirmar la restauración'
    )
    
    confirm = StringField(
        'Confirmación', 
        validators=[DataRequired()],
        description='Escriba RESTAURAR en mayúsculas para confirmar que entiende que esta acción sobrescribirá todos los datos actuales'
    )
    
    submit = SubmitField('Restaurar Backup')
    
    def validate_confirm(self, field):
        if field.data != 'RESTAURAR':
            raise ValidationError('Debe escribir RESTAURAR en mayúsculas para confirmar')


class DeleteBackupForm(FlaskForm):
    """
    Formulario para eliminar un backup.
    """
    admin_password = PasswordField(
        'Contraseña de Administrador', 
        validators=[DataRequired()],
        description='Ingrese su contraseña de administrador para confirmar la eliminación'
    )
    
    submit = SubmitField('Eliminar Backup')


class ScheduledBackupForm(FlaskForm):
    """
    Formulario para configurar backups programados.
    """
    enabled = BooleanField('Habilitar backups programados', default=True)
    
    frequency = SelectField(
        'Frecuencia', 
        choices=[
            ('daily', 'Diario'),
            ('weekly', 'Semanal'),
            ('monthly', 'Mensual')
        ],
        validators=[DataRequired()]
    )
    
    time = StringField(
        'Hora (HH:MM)', 
        validators=[DataRequired()],
        description='Hora en formato 24 horas (ejemplo: 03:00)'
    )
    
    retention_daily = SelectField(
        'Retención de backups diarios', 
        choices=[(str(i), str(i)) for i in range(1, 31)],
        default='7',
        validators=[DataRequired()]
    )
    
    retention_weekly = SelectField(
        'Retención de backups semanales', 
        choices=[(str(i), str(i)) for i in range(1, 13)],
        default='4',
        validators=[DataRequired()]
    )
    
    retention_monthly = SelectField(
        'Retención de backups mensuales', 
        choices=[(str(i), str(i)) for i in range(1, 13)],
        default='3',
        validators=[DataRequired()]
    )
    
    submit = SubmitField('Guardar Configuración')