"""
Rutas para la gestión de backups de la base de datos.

Este módulo define las rutas web para gestionar los backups de la base de datos,
incluyendo la creación, visualización y restauración de backups.
"""

import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

import backup_manager
from models import User
from app import db

# Crear Blueprint
backup_bp = Blueprint('backup', __name__, url_prefix='/backup')

@backup_bp.route('/')
@login_required
def backup_dashboard():
    """
    Página principal de gestión de backups.
    
    Muestra una lista de los backups disponibles y opciones para crear nuevos.
    """
    # Verificar que el usuario sea administrador
    if not current_user.is_admin:
        flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
        return redirect(url_for('main_dashboard'))
    
    # Obtener todos los backups
    backups = backup_manager.get_all_backups()
    
    # Obtener estado de la base de datos
    db_status = backup_manager.check_database_status()
    
    return render_template(
        'backup/dashboard.html',
        backups=backups,
        db_status=db_status,
        title='Gestión de Backups',
        active_page='backup'
    )

@backup_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_backup():
    """
    Ruta para crear un nuevo backup.
    
    GET: Muestra el formulario de creación
    POST: Procesa la creación del backup
    """
    # Verificar que el usuario sea administrador
    if not current_user.is_admin:
        flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
        return redirect(url_for('main_dashboard'))
    
    if request.method == 'POST':
        # Obtener parámetros del formulario
        backup_type = request.form.get('type', 'full')
        compress = request.form.get('compress', 'true') == 'true'
        description = request.form.get('description', '')
        
        # Crear el backup
        backup = backup_manager.create_backup(
            tipo=backup_type,
            compress=compress,
            description=description
        )
        
        if backup:
            flash(f'Backup creado exitosamente: {backup["filename"]}', 'success')
            return redirect(url_for('backup.backup_dashboard'))
        else:
            flash('Error al crear el backup. Revise los logs para más detalles.', 'danger')
    
    return render_template(
        'backup/create.html',
        title='Crear Backup',
        active_page='backup'
    )

@backup_bp.route('/view/<backup_id>')
@login_required
def view_backup(backup_id):
    """
    Muestra información detallada sobre un backup específico.
    """
    # Verificar que el usuario sea administrador
    if not current_user.is_admin:
        flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
        return redirect(url_for('main_dashboard'))
    
    # Obtener el backup por ID
    backup = backup_manager.get_backup_by_id(backup_id)
    
    if not backup:
        flash('Backup no encontrado.', 'danger')
        return redirect(url_for('backup.backup_dashboard'))
    
    return render_template(
        'backup/view.html',
        backup=backup,
        title=f'Backup {backup["filename"]}',
        active_page='backup'
    )

@backup_bp.route('/download/<backup_id>')
@login_required
def download_backup(backup_id):
    """
    Descarga un archivo de backup específico.
    """
    # Verificar que el usuario sea administrador
    if not current_user.is_admin:
        flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
        return redirect(url_for('main_dashboard'))
    
    # Obtener el backup por ID
    backup = backup_manager.get_backup_by_id(backup_id)
    
    if not backup or not os.path.exists(backup['path']):
        flash('Archivo de backup no encontrado.', 'danger')
        return redirect(url_for('backup.backup_dashboard'))
    
    # Enviar el archivo para descarga
    return send_file(
        backup['path'],
        as_attachment=True,
        download_name=backup['filename']
    )

@backup_bp.route('/delete/<backup_id>', methods=['POST'])
@login_required
def delete_backup(backup_id):
    """
    Elimina un backup específico.
    """
    # Verificar que el usuario sea administrador
    if not current_user.is_admin:
        flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
        return redirect(url_for('main_dashboard'))
    
    # Verificar contraseña del administrador para confirmar
    password = request.form.get('admin_password', '')
    if not password or not check_password_hash(current_user.password_hash, password):
        flash('Contraseña incorrecta. Por seguridad, debe proporcionar su contraseña para confirmar la eliminación.', 'danger')
        return redirect(url_for('backup.view_backup', backup_id=backup_id))
    
    # Eliminar el backup
    if backup_manager.delete_backup(backup_id):
        flash('Backup eliminado exitosamente.', 'success')
    else:
        flash('Error al eliminar el backup. Revise los logs para más detalles.', 'danger')
    
    return redirect(url_for('backup.backup_dashboard'))

@backup_bp.route('/restore/<backup_id>', methods=['GET', 'POST'])
@login_required
def restore_backup(backup_id):
    """
    Restaura la base de datos desde un backup específico.
    
    GET: Muestra la página de confirmación
    POST: Procesa la restauración
    """
    # Verificar que el usuario sea administrador
    if not current_user.is_admin:
        flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
        return redirect(url_for('main_dashboard'))
    
    # Obtener el backup por ID
    backup = backup_manager.get_backup_by_id(backup_id)
    
    if not backup:
        flash('Backup no encontrado.', 'danger')
        return redirect(url_for('backup.backup_dashboard'))
    
    if request.method == 'POST':
        # Verificar contraseña del administrador para confirmar
        password = request.form.get('admin_password', '')
        if not password or not check_password_hash(current_user.password_hash, password):
            flash('Contraseña incorrecta. Por seguridad, debe proporcionar su contraseña para confirmar la restauración.', 'danger')
            return redirect(url_for('backup.restore_backup', backup_id=backup_id))
        
        # Confirmar que el usuario entiende las consecuencias
        confirmation = request.form.get('confirm', '')
        if confirmation != 'RESTAURAR':
            flash('Debe escribir RESTAURAR en mayúsculas para confirmar que entiende las consecuencias.', 'danger')
            return redirect(url_for('backup.restore_backup', backup_id=backup_id))
        
        # Restaurar el backup
        result = backup_manager.restore_backup(backup_id)
        
        if result['success']:
            flash(f'Restauración completada exitosamente: {result["message"]}', 'success')
            return redirect(url_for('backup.backup_dashboard'))
        else:
            flash(f'Error al restaurar: {result["message"]}', 'danger')
    
    return render_template(
        'backup/restore.html',
        backup=backup,
        title=f'Restaurar Backup {backup["filename"]}',
        active_page='backup'
    )

@backup_bp.route('/run-scheduled', methods=['POST'])
@login_required
def run_scheduled_backup():
    """
    Ejecuta un backup programado manualmente.
    """
    # Verificar que el usuario sea administrador
    if not current_user.is_admin:
        flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
        return redirect(url_for('main_dashboard'))
    
    # Ejecutar el backup programado
    result = backup_manager.run_scheduled_backup()
    
    if result['success']:
        flash(f'Backup programado ejecutado exitosamente: {result["message"]}', 'success')
    else:
        flash(f'Error al ejecutar backup programado: {result["message"]}', 'danger')
    
    return redirect(url_for('backup.backup_dashboard'))

@backup_bp.route('/api/status', methods=['GET'])
@login_required
def api_database_status():
    """
    API para obtener el estado actual de la base de datos.
    """
    # Verificar que el usuario sea administrador
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado. Se requieren permisos de administrador.'}), 403
    
    # Obtener estado de la base de datos
    db_status = backup_manager.check_database_status()
    
    return jsonify(db_status)

@backup_bp.route('/api/list', methods=['GET'])
@login_required
def api_list_backups():
    """
    API para obtener la lista de backups disponibles.
    """
    # Verificar que el usuario sea administrador
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado. Se requieren permisos de administrador.'}), 403
    
    # Obtener todos los backups
    backups = backup_manager.get_all_backups()
    
    return jsonify({'backups': backups})

@backup_bp.route('/api/create', methods=['POST'])
@login_required
def api_create_backup():
    """
    API para crear un nuevo backup.
    """
    # Verificar que el usuario sea administrador
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado. Se requieren permisos de administrador.'}), 403
    
    # Obtener parámetros de la solicitud
    data = request.get_json()
    backup_type = data.get('type', 'full')
    compress = data.get('compress', True)
    description = data.get('description', '')
    
    # Crear el backup
    backup = backup_manager.create_backup(
        tipo=backup_type,
        compress=compress,
        description=description
    )
    
    if backup:
        return jsonify({'success': True, 'backup': backup})
    else:
        return jsonify({'success': False, 'message': 'Error al crear el backup'}), 500

# Registrar el blueprint
def register_blueprint(app):
    app.register_blueprint(backup_bp)
    return app