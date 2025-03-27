"""
Rutas de la API para el módulo de tareas.
"""
from flask import Blueprint, jsonify, request, abort
from app import db
from api_models import APITask

# Crear el Blueprint para las rutas de la API
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Devuelve una lista de todas las tareas.
    
    Returns:
        JSON con lista de tareas
    """
    tasks = APITask.query.all()
    
    # Convertir tareas a diccionarios para la serialización JSON
    tasks_dict = [task.to_dict() for task in tasks]
    
    return jsonify({
        'status': 'success',
        'count': len(tasks_dict),
        'tasks': tasks_dict
    })


@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """
    Devuelve los detalles de una tarea específica.
    
    Args:
        task_id: ID de la tarea
        
    Returns:
        JSON con detalles de la tarea
        
    Raises:
        404: Si la tarea no existe
    """
    task = APITask.query.get_or_404(task_id, description=f"Tarea con ID {task_id} no encontrada")
    
    return jsonify({
        'status': 'success',
        'task': task.to_dict()
    })


@api_bp.errorhandler(404)
def resource_not_found(e):
    """Manejador de error 404"""
    return jsonify(error=str(e)), 404


@api_bp.errorhandler(500)
def internal_server_error(e):
    """Manejador de error 500"""
    return jsonify(error="Error interno del servidor"), 500