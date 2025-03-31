import os
import tempfile
import base64
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image
from fpdf import FPDF
from timezone_config import get_current_time, datetime_to_madrid, TIMEZONE

class CheckPointPDF(FPDF):
    """Clase personalizada para generar PDFs de fichajes con cabecera y pie de página"""
    
    def __init__(self, title='Registro de Fichajes', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.set_title(title)
        self.set_author('Sistema de Fichajes')
        
        # Colores corporativos
        self.primary_color = (31, 79, 121)  # Azul corporativo oscuro
        self.secondary_color = (82, 125, 162)  # Azul corporativo medio
        self.accent_color = (236, 240, 245)  # Azul muy claro para fondos
        
    def header(self):
        # Rectángulo superior de color
        self.set_fill_color(*self.primary_color)
        self.rect(0, 0, 210, 20, 'F')
        
        # Logo (si existe)
        logo_path = os.path.join(os.getcwd(), 'static', 'img', 'logo.png')
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 3, 15)
        
        # Título con texto blanco (centrado verticalmente)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.set_y(7)  # Centrar verticalmente el texto en la barra de 20mm
        self.cell(0, 6, self.title, 0, 1, 'C')
        
        # Restablecer color de texto
        self.set_text_color(0, 0, 0)
        
        # Línea de separación con color corporativo
        self.set_draw_color(*self.secondary_color)
        self.set_line_width(0.5)
        self.line(10, 25, 200, 25)
        
        # Restablecer color de texto
        self.set_text_color(0, 0, 0)
        self.ln(5)
        
    def footer(self):
        # Posición a 2 cm desde el final
        self.set_y(-20)
        
        # Línea de separación con color corporativo
        self.set_draw_color(*self.secondary_color)
        self.line(10, self.get_y(), 200, self.get_y())
        
        # Rectángulo inferior de color
        self.set_fill_color(*self.primary_color)
        self.rect(0, self.h - 12, 210, 12, 'F')
        
        # Número de página con texto blanco (centrado verticalmente)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(255, 255, 255)
        self.set_y(self.h - 8)  # Centrar verticalmente en la barra de 12mm
        self.cell(0, 4, f'Página {self.page_no()}', 0, 0, 'C')


def draw_signature(pdf, signature_data, x, y, width=50, height=20):
    """Dibuja la firma en el PDF desde datos base64"""
    if not signature_data:
        return
    
    try:
        # Procesar los datos base64
        if 'data:image/png;base64,' in signature_data:
            signature_data = signature_data.split('data:image/png;base64,')[1]
        
        # Decodificar los datos
        decoded_data = base64.b64decode(signature_data)
        
        # Crear una imagen temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(decoded_data)
            temp_file_path = temp_file.name
        
        # Dibujar la imagen en el PDF
        pdf.image(temp_file_path, x, y, width, height)
        
        # Eliminar el archivo temporal
        os.unlink(temp_file_path)
        
    except Exception as e:
        print(f"Error al dibujar la firma: {str(e)}")


def generate_pdf_report(records, start_date, end_date, include_signature=True):
    """Genera un informe PDF de los registros de fichaje"""
    # Agrupar registros por empleado
    employees_records = {}
    
    for record in records:
        employee_id = record.employee_id
        
        if employee_id not in employees_records:
            employees_records[employee_id] = {
                'employee': record.employee,
                'records': []
            }
            
        employees_records[employee_id]['records'].append(record)
    
    # Crear PDF
    pdf = CheckPointPDF(title=f'Informe de Fichajes: {start_date.strftime("%d/%m/%Y")} - {end_date.strftime("%d/%m/%Y")}')
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Para cada empleado
    for employee_id, data in employees_records.items():
        employee = data['employee']
        records = data['records']
        company = employee.company
        
        # Añadir una nueva página para cada empleado
        pdf.add_page()
        
        # Añadir espacio adicional después del encabezado para evitar solapamiento con la barra
        pdf.ln(8)  # 8mm de espacio adicional
        
        # Calcular posiciones centradas (el ancho de la página es 210mm)
        # Usaremos un margen de 20mm a cada lado
        left_margin = 20
        right_margin = 20
        usable_width = 210 - left_margin - right_margin
        block_width = 85  # Cada bloque tendrá 85mm de ancho
        gap = 10          # 10mm de separación entre bloques
        
        # Posición X del primer bloque
        block1_x = left_margin
        # Posición X del segundo bloque
        block2_x = block1_x + block_width + gap
        
        # Crear fondos de color para los bloques de información
        # Bloque empleado (izquierda)
        pdf.set_fill_color(*pdf.accent_color)
        pdf.rect(block1_x, pdf.get_y(), block_width, 30, 'F')
        
        # Bloque empresa (derecha)
        pdf.rect(block2_x, pdf.get_y(), block_width, 30, 'F')
        
        # Líneas de contorno con color corporativo
        pdf.set_draw_color(*pdf.secondary_color)
        pdf.rect(block1_x, pdf.get_y(), block_width, 30, 'D')
        pdf.rect(block2_x, pdf.get_y(), block_width, 30, 'D')
        
        initial_y = pdf.get_y()
        
        # Títulos con fondo de color primario
        pdf.set_fill_color(*pdf.secondary_color)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 10)
        
        # Título empleado
        pdf.rect(block1_x, pdf.get_y(), block_width, 6, 'F')
        pdf.set_xy(block1_x, pdf.get_y())
        pdf.cell(block_width, 6, 'DATOS DEL EMPLEADO', 0, 0, 'C')
        
        # Título empresa
        pdf.rect(block2_x, pdf.get_y(), block_width, 6, 'F')
        pdf.set_xy(block2_x, pdf.get_y())
        pdf.cell(block_width, 6, 'DATOS DE LA EMPRESA', 0, 1, 'C')
        
        # Restaurar color de texto
        pdf.set_text_color(0, 0, 0)
        
        # Espacio para etiquetas y valores
        label_width = 25
        value_width = block_width - label_width - 5  # 5mm de margen interno
        label_x1 = block1_x + 2  # 2mm de margen interno
        value_x1 = label_x1 + label_width
        label_x2 = block2_x + 2
        value_x2 = label_x2 + label_width
        
        # Etiquetas en negrita
        pdf.set_font('Arial', 'B', 9)
        pdf.set_xy(label_x1, pdf.get_y() + 2)
        pdf.cell(label_width, 5, 'Nombre:', 0, 0)
        
        pdf.set_xy(label_x2, pdf.get_y())
        pdf.cell(label_width, 5, 'Nombre:', 0, 1)
        
        # Datos en texto normal
        pdf.set_font('Arial', '', 9)
        pdf.set_xy(value_x1, pdf.get_y() - 5)
        pdf.cell(value_width, 5, f"{employee.first_name} {employee.last_name}", 0, 0)
        
        pdf.set_xy(value_x2, pdf.get_y())
        pdf.cell(value_width, 5, f"{company.name}", 0, 1)
        
        # DNI
        pdf.set_font('Arial', 'B', 9)
        pdf.set_xy(label_x1, pdf.get_y() + 2)
        pdf.cell(label_width, 5, 'DNI/NIE:', 0, 0)
        
        # CIF
        pdf.set_xy(label_x2, pdf.get_y())
        pdf.cell(label_width, 5, 'CIF:', 0, 1)
        
        pdf.set_font('Arial', '', 9)
        pdf.set_xy(value_x1, pdf.get_y() - 5)
        pdf.cell(value_width, 5, f"{employee.dni}", 0, 0)
        
        pdf.set_xy(value_x2, pdf.get_y())
        pdf.cell(value_width, 5, f"{company.tax_id}", 0, 1)
        
        # Puesto
        pdf.set_font('Arial', 'B', 9)
        pdf.set_xy(label_x1, pdf.get_y() + 2)
        pdf.cell(label_width, 5, 'Puesto:', 0, 0)
        
        # Dirección
        pdf.set_xy(label_x2, pdf.get_y())
        pdf.cell(label_width, 5, 'Dirección:', 0, 1)
        
        pdf.set_font('Arial', '', 9)
        pdf.set_xy(value_x1, pdf.get_y() - 5)
        pdf.cell(value_width, 5, f"{employee.position or '-'}", 0, 0)
        
        empresa_direccion = f"{company.address or ''}, {company.city or ''}"
        if empresa_direccion.strip() == ',':
            empresa_direccion = '-'
        pdf.set_xy(value_x2, pdf.get_y())
        pdf.cell(value_width, 5, empresa_direccion, 0, 1)
        
        # Asegurar que avanzamos correctamente después de los bloques
        pdf.set_y(initial_y + 35)  # Espacio antes de la tabla
        
        # Título de la tabla con fondo corporativo
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 12)
        
        # Centrar el título de la tabla usando los mismos márgenes
        title_width = 170  # Ancho del título
        title_x = (210 - title_width) / 2  # Centrado en la página
        
        # Dibujar el rectángulo para el título
        pdf.rect(title_x, pdf.get_y(), title_width, 10, 'F')
        
        # Guardar la posición Y actual
        current_y = pdf.get_y()
        
        # Posicionar el texto verticalmente centrado dentro de la barra (subir un poco)
        pdf.set_y(current_y + 2.5)  # 2.5mm para centrar el texto en la barra de 10mm de alto
        pdf.cell(0, 5, 'REGISTROS DE FICHAJE', 0, 1, 'C')
        
        # Volver a la posición después del rectángulo y añadir espacio
        pdf.set_y(current_y + 10 + 5)  # 5mm de espacio adicional entre la barra y la tabla
        
        # Restaurar color de texto
        pdf.set_text_color(0, 0, 0)
        
        # Tabla de registros
        pdf.set_font('Arial', 'B', 10)
        
        # Cabecera de tabla
        col_widths = [35, 30, 30, 30, 40]
        header = ['Fecha', 'Entrada', 'Salida', 'Horas', 'Firma']
        table_width = sum(col_widths)
        
        # Calcular posición X para centrar la tabla
        table_x = (210 - table_width) / 2
        pdf.set_x(table_x)
        
        # Dibujar cabecera con color corporativo
        pdf.set_fill_color(*pdf.secondary_color)
        pdf.set_text_color(255, 255, 255)
        pdf.set_draw_color(*pdf.primary_color)
        pdf.set_line_width(0.3)
        
        for i, col in enumerate(header):
            pdf.cell(col_widths[i], 10, col, 1, 0, 'C', True)
        pdf.ln()
        
        # Restaurar color de texto para las filas
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 10)
        
        # Color alternado para las filas (efecto cebra)
        row_count = 0
        
        for record in records:
            # Posicionar al inicio de la fila, centrado
            pdf.set_x(table_x)
            
            # Cambiar color de fondo según fila par/impar
            if row_count % 2 == 0:
                pdf.set_fill_color(255, 255, 255)  # Blanco
            else:
                pdf.set_fill_color(*pdf.accent_color)  # Color claro
            
            # Fecha
            pdf.cell(col_widths[0], 10, record.check_in_time.strftime('%d/%m/%Y'), 1, 0, 'C', True)
            
            # Hora entrada
            pdf.cell(col_widths[1], 10, record.check_in_time.strftime('%H:%M'), 1, 0, 'C', True)
            
            # Hora salida
            if record.check_out_time:
                pdf.cell(col_widths[2], 10, record.check_out_time.strftime('%H:%M'), 1, 0, 'C', True)
            else:
                pdf.cell(col_widths[2], 10, '-', 1, 0, 'C', True)
            
            # Horas trabajadas
            duration = record.duration()
            if duration is not None:
                hours_str = f"{duration:.2f}h"
            else:
                hours_str = '-'
            pdf.cell(col_widths[3], 10, hours_str, 1, 0, 'C', True)
            
            # Celda para firma
            y_pos_before = pdf.get_y()
            pdf.cell(col_widths[4], 10, '', 1, 0, 'C', True)
            
            # Dibujar firma en la celda si existe
            if include_signature and record.has_signature and record.signature_data:
                # Guardar posición actual
                x_pos = pdf.get_x() - col_widths[4]
                # Dibujar la firma dentro de la celda
                draw_signature(pdf, record.signature_data, x_pos + 2, y_pos_before + 1, col_widths[4] - 4, 8)
            
            pdf.ln()
            row_count += 1
    
    # Crear un archivo temporal en disco
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_filename = temp_file.name
    temp_file.close()
    
    # Guardar el PDF en el archivo temporal
    pdf.output(temp_filename)
    
    return temp_filename


def process_auto_checkouts(force=False):
    """
    Procesa los checkouts automáticos para fichajes pendientes
    
    Args:
        force (bool): Si es True, procesará todos los checkouts sin importar la hora configurada.
                     Útil para ejecuciones manuales desde el dashboard.
    """
    
    # Importamos las dependencias al inicio para evitar problemas
    from app import db
    from models_checkpoints import CheckPoint, CheckPointRecord, CheckPointIncident, CheckPointIncidentType, EmployeeContractHours
    from models import EmployeeSchedule, Employee
    from models import WeekDay as ModelWeekDay
    import enum
    from models_checkpoints import CheckPointStatus, CheckPointOriginalRecord
    
    # Contador total de registros procesados
    total_processed = 0
    
    try:
        # Obtener todos los puntos de fichaje activos
        checkpoints = CheckPoint.query.filter_by(status=CheckPointStatus.ACTIVE).all()
        
        # Obtener la fecha/hora actual en la zona horaria de Madrid
        now = get_current_time()
        
        # Determinar el día de la semana actual (1-7, donde 1 es lunes)
        today_weekday = now.isoweekday()
        print(f"🕒 Auto-checkouts: El día de la semana actual es {today_weekday} (1=Lunes, 7=Domingo)")
        
        # Crear mapeo de días de la semana (1-7) a la enumeración WeekDay
        # En vez de usar los objetos de enumeración, usamos el mapeo al valor de enumeración PostgreSQL en mayúsculas
        day_mapping = {
            1: "LUNES",
            2: "MARTES",
            3: "MIERCOLES",
            4: "JUEVES", 
            5: "VIERNES",
            6: "SABADO",
            7: "DOMINGO"
        }
        weekday_value = day_mapping.get(today_weekday)
        if not weekday_value:
            raise ValueError(f"No se pudo mapear el día de la semana {today_weekday} a una enumeración WeekDay")
            
        print(f"🔄 Auto-checkouts: Usando valor '{weekday_value}' para el día {today_weekday}")
        
        # Modo forzado para ejecuciones manuales
        if force:
            print(f"⚠️ Auto-checkout en modo forzado: se procesarán todos los registros independientemente de la hora")
        
        # Para cada punto de fichaje activo
        for checkpoint in checkpoints:
            try:
                # 1. Procesamiento basado en auto_checkout_time (configuración global)
                if checkpoint.auto_checkout_time:
                    # Construir la fecha/hora de corte de hoy usando la configuración del punto de fichaje
                    global_checkout_datetime = datetime.combine(now.date(), checkpoint.auto_checkout_time)
                    global_checkout_datetime = global_checkout_datetime.replace(tzinfo=TIMEZONE)
                    
                    # Imprimir valores para depuración
                    print(f"⏰ Comprobando auto-checkout para punto: {checkpoint.name}")
                    print(f"   Hora actual (Madrid): {now.strftime('%H:%M:%S')} ({now.tzinfo})")
                    print(f"   Hora auto-checkout (original): {checkpoint.auto_checkout_time.strftime('%H:%M:%S')} (Sin zona horaria)")
                    print(f"   Hora auto-checkout (Madrid): {global_checkout_datetime.strftime('%H:%M:%S')} ({global_checkout_datetime.tzinfo})")
                    
                    # Solo procesar si ya pasó la hora de corte global o si se fuerza el procesamiento
                    if force or now >= global_checkout_datetime:
                        print(f"⏰ Procesando checkouts automáticos (hora global) para checkpoint: {checkpoint.name}")
                        print(f"   Hora actual: {now.strftime('%H:%M:%S')}")
                        print(f"   Hora de auto-checkout: {checkpoint.auto_checkout_time.strftime('%H:%M:%S')}")
                        
                        # Buscar todos los fichajes de hoy sin checkout
                        start_of_day = datetime.combine(now.date(), datetime.min.time())
                        start_of_day = start_of_day.replace(tzinfo=TIMEZONE)
                        
                        pending_records = CheckPointRecord.query.filter(
                            CheckPointRecord.checkpoint_id == checkpoint.id,
                            CheckPointRecord.check_out_time.is_(None),
                            CheckPointRecord.check_in_time.between(
                                start_of_day,
                                now
                            )
                        ).all()
                        
                        # Procesar los registros pendientes
                        for record in pending_records:
                            # Registrar el checkout automático
                            record.check_out_time = global_checkout_datetime
                            record.notes = (record.notes or "") + f" [AUTO] Checkout automático a las {global_checkout_datetime.strftime('%H:%M')}"
                            
                            # Crear incidencia por el checkout automático
                            incident = CheckPointIncident(
                                record_id=record.id,
                                incident_type=CheckPointIncidentType.MISSED_CHECKOUT,
                                description=f"Checkout automático realizado a las {global_checkout_datetime.strftime('%H:%M')} por falta de registro de salida."
                            )
                            db.session.add(incident)
                            
                            # Crear un registro del estado original con las horas reales
                            original_record = CheckPointOriginalRecord(
                                record_id=record.id,
                                original_check_in_time=record.check_in_time,
                                original_check_out_time=global_checkout_datetime,
                                original_signature_data=record.signature_data,
                                original_has_signature=record.has_signature,
                                original_notes=record.notes,
                                adjustment_reason="Registro original creado en checkout automático"
                            )
                            db.session.add(original_record)
                            
                            # Aplicar restricciones de horario de contrato si corresponde
                            if checkpoint.enforce_contract_hours:
                                # Buscar configuración de horas de contrato del empleado
                                contract_hours = EmployeeContractHours.query.filter_by(employee_id=record.employee_id).first()
                                if contract_hours:
                                    # Guardar los valores originales para reporte
                                    original_checkin = record.check_in_time
                                    original_checkout = record.check_out_time
                                    
                                    # Aplicar ajustes según configuración
                                    adjusted_checkin, adjusted_checkout = contract_hours.calculate_adjusted_hours(
                                        original_checkin, original_checkout
                                    )
                                    
                                    # Si hay cambios, aplicarlos y marcar con R
                                    if adjusted_checkin and adjusted_checkin != original_checkin:
                                        record.check_in_time = adjusted_checkin
                                        # Marcar con R en lugar de crear incidencia
                                        record.notes = (record.notes or "") + f" [R] Hora entrada ajustada de {original_checkin.strftime('%H:%M')} a {adjusted_checkin.strftime('%H:%M')}"
                                        
                                    if adjusted_checkout and adjusted_checkout != original_checkout:
                                        record.check_out_time = adjusted_checkout
                                        # Marcar con R en lugar de crear incidencia
                                        record.notes = (record.notes or "") + f" [R] Hora salida ajustada de {original_checkout.strftime('%H:%M')} a {adjusted_checkout.strftime('%H:%M')}"
                                    
                                    # Verificar si hay horas extra
                                    duration = (record.check_out_time - record.check_in_time).total_seconds() / 3600
                                    if contract_hours.is_overtime(duration):
                                        overtime_hours = duration - contract_hours.daily_hours
                                        overtime_incident = CheckPointIncident(
                                            record_id=record.id,
                                            incident_type=CheckPointIncidentType.OVERTIME,
                                            description=f"Jornada con {overtime_hours:.2f} horas extra sobre el límite diario de {contract_hours.daily_hours} horas"
                                        )
                                        db.session.add(overtime_incident)
                            
                            # Actualizar el estado del empleado
                            employee = record.employee
                            if employee.is_on_shift:
                                employee.is_on_shift = False
                                db.session.add(employee)
                                
                            # Incrementar contador 
                            total_processed += 1
                
                # 2. Procesamiento basado en horarios individuales de los empleados
                employees_on_shift = Employee.query.filter_by(
                    company_id=checkpoint.company_id,
                    is_on_shift=True
                ).all()
                
                for employee in employees_on_shift:
                    # Verificar si hay un registro pendiente para este empleado
                    pending_record = CheckPointRecord.query.filter(
                        CheckPointRecord.employee_id == employee.id, 
                        CheckPointRecord.check_out_time.is_(None)
                    ).order_by(CheckPointRecord.check_in_time.desc()).first()
                    
                    if not pending_record:
                        # El empleado está marcado como en turno pero no tiene registro pendiente
                        # Corregir inconsistencia
                        employee.is_on_shift = False
                        db.session.add(employee)
                        print(f"⚠️ Corrigiendo inconsistencia: Empleado {employee.id} marcado en turno sin registro pendiente")
                        continue
                    
                    # Usamos el valor en mayúsculas para la base de datos PostgreSQL
                    schedule = EmployeeSchedule.query.filter_by(
                        employee_id=employee.id,
                        day_of_week=weekday_value
                    ).first()
                    
                    if schedule and schedule.is_working_day and schedule.end_time:
                        # Construir fecha/hora de fin de turno programado
                        scheduled_end_datetime = datetime.combine(now.date(), schedule.end_time)
                        scheduled_end_datetime = scheduled_end_datetime.replace(tzinfo=TIMEZONE)
                        
                        # Verificar si ya pasó la hora de fin de turno (con margen de 15 minutos)
                        # o si estamos en modo forzado
                        margin = timedelta(minutes=15)
                        if force or now > (scheduled_end_datetime + margin):
                            # Crear checkout automático basado en horario programado
                            pending_record.check_out_time = scheduled_end_datetime
                            pending_record.notes = (pending_record.notes or "") + f" [AUTO-S] Checkout automático basado en horario programado ({schedule.end_time.strftime('%H:%M')})"
                            
                            # Crear un registro del estado original con las horas reales
                            original_record = CheckPointOriginalRecord(
                                record_id=pending_record.id,
                                original_check_in_time=pending_record.check_in_time,
                                original_check_out_time=scheduled_end_datetime,
                                original_signature_data=pending_record.signature_data,
                                original_has_signature=pending_record.has_signature,
                                original_notes=pending_record.notes,
                                adjustment_reason="Registro original creado en checkout automático basado en horario"
                            )
                            db.session.add(original_record)
                            
                            # Crear incidencia
                            incident = CheckPointIncident(
                                record_id=pending_record.id,
                                incident_type=CheckPointIncidentType.MISSED_CHECKOUT,
                                description=f"Checkout automático realizado a las {scheduled_end_datetime.strftime('%H:%M')} basado en horario programado."
                            )
                            db.session.add(incident)
                            
                            # Actualizar estado del empleado
                            employee.is_on_shift = False
                            db.session.add(employee)
                            
                            # Log para depuración
                            print(f"⏰ Auto-checkout por horario programado: Empleado {employee.id}, Hora programada: {schedule.end_time}")
                            
                            # Incrementar contador
                            total_processed += 1
            
            except Exception as e:
                print(f"Error procesando checkpoint {checkpoint.id}: {e}")
                import traceback
                traceback.print_exc()
                # No interrumpir el proceso para otros checkpoints
                continue
        
        # Guardar todos los cambios
        if total_processed > 0:
            # Commit final de todos los cambios
            db.session.commit()
            print(f"✅ Total de registros procesados con checkout automático: {total_processed}")
        
    except Exception as e:
        print(f"Error al procesar auto-checkouts: {e}")
        import traceback
        traceback.print_exc()
        # Asegurar que se deshagan todos los cambios en caso de error
        db.session.rollback()
    
    return total_processed