"""
Script para actualizar la ventana horaria de los puntos de fichaje.
"""
from datetime import datetime, time
from app import create_app, db
from models_checkpoints import CheckPoint
from timezone_config import get_current_time

app = create_app()

def update_operation_hours(checkpoint_id, start_hour, start_minute, end_hour, end_minute):
    """
    Actualiza la ventana horaria de un punto de fichaje.
    
    Args:
        checkpoint_id: ID del punto de fichaje
        start_hour, start_minute: Hora y minuto de inicio de la ventana
        end_hour, end_minute: Hora y minuto de fin de la ventana
    """
    with app.app_context():
        checkpoint = CheckPoint.query.get(checkpoint_id)
        if not checkpoint:
            print(f"No se encontró el punto de fichaje con ID {checkpoint_id}")
            return False
        
        # Guardar configuración anterior
        old_start = checkpoint.operation_start_time
        old_end = checkpoint.operation_end_time
        old_enforce = checkpoint.enforce_operation_hours
        
        # Actualizar la ventana horaria
        checkpoint.operation_start_time = time(start_hour, start_minute)
        checkpoint.operation_end_time = time(end_hour, end_minute)
        checkpoint.enforce_operation_hours = True
        
        # Guardar cambios
        db.session.commit()
        
        print(f"Punto de fichaje {checkpoint.name} actualizado:")
        print(f"  Ventana horaria anterior: {old_start} - {old_end} (Activada: {old_enforce})")
        print(f"  Ventana horaria nueva: {checkpoint.operation_start_time} - {checkpoint.operation_end_time} (Activada: {checkpoint.enforce_operation_hours})")
        
        return True

if __name__ == "__main__":
    # Obtener la hora actual en Madrid para establecer la ventana horaria
    madrid_now = get_current_time()
    print(f"Hora actual en Madrid: {madrid_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    current_hour = madrid_now.hour
    current_minute = madrid_now.minute
    
    # Establecer la ventana horaria para que incluya la hora actual
    # Para asegurarnos de que el barrido funcione, usamos exactamente la misma hora 
    # que está utilizando el script de cierre (19:XX en Madrid)
    start_hour = current_hour
    start_minute = max(0, current_minute - 5)  # 5 minutos antes
    end_hour = current_hour
    end_minute = min(59, current_minute + 10)  # 10 minutos después
    
    print(f"Estableciendo ventana horaria: {start_hour:02d}:{start_minute:02d} - {end_hour:02d}:{end_minute:02d}")
    update_operation_hours(checkpoint_id=8, start_hour=start_hour, start_minute=start_minute, 
                          end_hour=end_hour, end_minute=end_minute)