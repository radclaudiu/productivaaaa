"""
Rutas de la API para el módulo de tareas.
"""
from flask import Blueprint, jsonify, request, abort
import requests
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


@api_bp.route('/external/portal/<int:portal_id>', methods=['GET'])
def get_external_portal_tasks(portal_id):
    """
    Obtiene tareas desde un portal externo.
    
    Args:
        portal_id: ID del portal externo
        
    Returns:
        JSON con las tareas del portal externo
        
    Raises:
        404: Si el portal no existe
        500: Si hay un error de conexión
    """
    try:
        # URL del portal externo
        external_url = f"https://productiva.replit.app/tasks/portal/{portal_id}"
        
        # Realizar la solicitud al portal externo
        response = requests.get(external_url, timeout=10)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Intentar parsear la respuesta como JSON
            try:
                data = response.json()
                return jsonify({
                    'status': 'success',
                    'source': external_url,
                    'data': data
                })
            except ValueError:
                # Si la respuesta no es JSON válido, devolvemos el contenido como texto
                return jsonify({
                    'status': 'success',
                    'source': external_url,
                    'data': {
                        'content': response.text,
                        'content_type': response.headers.get('Content-Type', 'text/html')
                    }
                })
        else:
            # Si la solicitud no fue exitosa, devolvemos el código de estado
            return jsonify({
                'status': 'error',
                'source': external_url,
                'code': response.status_code,
                'message': f"Error al conectar con el portal externo: {response.reason}"
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        # Si hay un error de conexión, devolvemos un error 500
        return jsonify({
            'status': 'error',
            'source': f"https://productiva.replit.app/tasks/portal/{portal_id}",
            'message': f"Error al conectar con el portal externo: {str(e)}"
        }), 500