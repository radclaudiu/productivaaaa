"""
Script para cerrar automáticamente los fichajes pendientes cuando llega
la hora de fin de funcionamiento configurada en cada punto de fichaje.

Este script debería ejecutarse periódicamente, por ejemplo, cada 5 minutos,
para verificar si algún punto de fichaje debe cerrar sus registros pendientes.
"""
import sys
from datetime import datetime, timedelta
from sqlalchemy import func

from app import db, create_app
from models_checkpoints import CheckPoint, CheckPointRecord, CheckPointIncident, CheckPointIncidentType, CheckPointStatus
from timezone_config import get_current_time, datetime_to_madrid, TIMEZONE

def auto_close_pending_records():
    """
    Cierra automáticamente todos los registros pendientes de los puntos de fichaje 
    que han llegado a su hora de fin de funcionamiento configurada.
    """
    timestamp = datetime.now()
    print(f"\n{'*' * 100}")
    print(f"* INICIANDO FUNCIÓN DE BARRIDO AUTOMÁTICO")
    print(f"* Fecha/hora: {timestamp}")
    print(f"* Versión: 1.1.0")
    print(f"{'*' * 100}\n")
    
    print(f"========== INICIO BARRIDO DE CIERRE AUTOMÁTICO: {timestamp} ==========")
    print(f"Ejecutando verificación de cierre automático por fin de horario de funcionamiento: {timestamp}")
    
    try:
        # Obtener hora actual en la zona horaria configurada
        current_time = get_current_time()
        current_hour = current_time.time()
        
        print(f"Hora actual (Madrid): {current_hour}")
        
        # Buscar todos los puntos de fichaje con horario de funcionamiento activado
        checkpoints = CheckPoint.query.filter(
            CheckPoint.enforce_operation_hours == True,  # Tiene configuración de horario activada
            CheckPoint.operation_end_time.isnot(None),   # Tiene hora de fin configurada
            CheckPoint.status == CheckPointStatus.ACTIVE  # Está activo
        ).all()
        
        if not checkpoints:
            print("No hay puntos de fichaje con horario de funcionamiento configurado.")
            print(f"========== FIN BARRIDO DE CIERRE AUTOMÁTICO (sin puntos configurados) ==========")
            return True
            
        print(f"Encontrados {len(checkpoints)} puntos de fichaje con horario configurado.")
        
        # Inicializamos contadores para el resumen final
        total_checkpoints_processed = 0
        total_records_closed = 0
        
        # Para cada punto de fichaje, verificar si es hora de cerrar sus registros
        for checkpoint in checkpoints:
            # Si la hora actual es mayor o igual a la hora de fin configurada, cerrar registros
            if current_hour >= checkpoint.operation_end_time:
                print(f"Procesando punto de fichaje: {checkpoint.name} (ID: {checkpoint.id}) - Hora de fin: {checkpoint.operation_end_time}")
                total_checkpoints_processed += 1
                
                # Buscar registros pendientes de este punto de fichaje
                pending_records = CheckPointRecord.query.filter(
                    CheckPointRecord.checkpoint_id == checkpoint.id,
                    CheckPointRecord.check_out_time.is_(None)
                ).all()
                
                if not pending_records:
                    print(f"No hay registros pendientes en el punto de fichaje {checkpoint.name}")
                    continue
                    
                print(f"Encontrados {len(pending_records)} registros pendientes para cerrar.")
                
                # Cerrar cada registro pendiente
                for record in pending_records:
                    # Crear una copia del registro original si es la primera modificación
                    if not record.original_check_in_time:
                        record.original_check_in_time = record.check_in_time
                    
                    # Asegurarse de que la fecha de entrada tenga información de zona horaria
                    check_in_time = record.check_in_time
                    if check_in_time.tzinfo is None:
                        check_in_time = datetime_to_madrid(check_in_time)
                    
                    # Establecer la hora de salida como la hora de fin de funcionamiento
                    check_in_date = check_in_time.date()
                    check_out_time = datetime.combine(check_in_date, checkpoint.operation_end_time)
                    check_out_time = TIMEZONE.localize(check_out_time)
                    
                    # Si la salida queda antes que la entrada (lo cual sería un error), 
                    # establecer la salida para el día siguiente
                    if check_out_time < check_in_time:
                        check_out_date = check_in_date + timedelta(days=1)
                        check_out_time = datetime.combine(check_out_date, checkpoint.operation_end_time)
                        check_out_time = TIMEZONE.localize(check_out_time)
                    
                    # Asignar la hora de salida calculada
                    record.check_out_time = check_out_time
                    
                    # Marcar que fue cerrado automáticamente
                    record.notes = (record.notes or "") + " [Cerrado automáticamente por fin de horario de funcionamiento]"
                    record.adjusted = True
                    
                    # Crear una incidencia
                    incident = CheckPointIncident(
                        record_id=record.id,
                        incident_type=CheckPointIncidentType.MISSED_CHECKOUT,
                        description=f"Salida automática por fin de horario de funcionamiento ({checkpoint.operation_end_time})"
                    )
                    db.session.add(incident)
                
                # Guardar todos los cambios para este punto de fichaje
                try:
                    records_closed = len(pending_records)
                    db.session.commit()
                    total_records_closed += records_closed
                    print(f"✓ {records_closed} registros cerrados correctamente para el punto {checkpoint.name}")
                except Exception as e:
                    db.session.rollback()
                    print(f"✗ Error al cerrar registros para el punto {checkpoint.name}: {e}")
            else:
                print(f"• No es hora de cerrar los registros para {checkpoint.name}. Hora actual: {current_hour}, Hora fin: {checkpoint.operation_end_time}")
        
        # Mostrar resumen final del barrido
        end_timestamp = datetime.now()
        duration = (end_timestamp - timestamp).total_seconds()
        print(f"\n========== RESUMEN DEL BARRIDO DE CIERRE AUTOMÁTICO ==========")
        print(f"Fecha y hora de inicio: {timestamp}")
        print(f"Fecha y hora de fin: {end_timestamp}")
        print(f"Duración: {duration:.2f} segundos")
        print(f"Puntos de fichaje procesados: {total_checkpoints_processed} de {len(checkpoints)}")
        print(f"Registros cerrados: {total_records_closed}")
        print(f"========== FIN BARRIDO DE CIERRE AUTOMÁTICO ==========\n")
        
        return True
        
    except Exception as e:
        end_timestamp = datetime.now()
        print(f"\n========== ERROR EN BARRIDO DE CIERRE AUTOMÁTICO ==========")
        print(f"Fecha y hora de inicio: {timestamp}")
        print(f"Fecha y hora de error: {end_timestamp}")
        print(f"Error general durante el proceso: {e}")
        print(f"========== FIN BARRIDO CON ERROR ==========\n")
        return False


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        success = auto_close_pending_records()
    
    sys.exit(0 if success else 1)