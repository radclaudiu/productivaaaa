import os
import tempfile
import base64
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image
from fpdf import FPDF

class CheckPointPDF(FPDF):
    """Clase personalizada para generar PDFs de fichajes con cabecera y pie de página"""
    
    def __init__(self, title='Registro de Fichajes', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.set_title(title)
        self.set_author('Sistema de Fichajes')
        
    def header(self):
        # Logo (si existe)
        logo_path = os.path.join(os.getcwd(), 'static', 'img', 'logo.png')
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 33)
            
        # Título
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, self.title, 0, 1, 'C')
        
        # Fecha de generación
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'R')
        
        # Línea de separación
        self.line(10, 30, 200, 30)
        self.ln(10)
        
    def footer(self):
        # Posición a 1.5 cm desde el final
        self.set_y(-15)
        # Fuente Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Número de página centrado
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')


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
    pdf = CheckPointPDF(title='Informe de Fichajes')
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Para cada empleado
    for employee_id, data in employees_records.items():
        employee = data['employee']
        records = data['records']
        company = employee.company
        
        # Añadir una nueva página para cada empleado
        pdf.add_page()
        
        # Información del empleado (izquierda)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(95, 6, 'DATOS DEL EMPLEADO:', 0, 0)
        
        # Información de la empresa (derecha)
        pdf.cell(95, 6, 'DATOS DE LA EMPRESA:', 0, 1, 'R')
        
        # Datos del empleado
        pdf.set_font('Arial', '', 10)
        pdf.cell(95, 6, f"Nombre: {employee.first_name} {employee.last_name}", 0, 0)
        
        # Datos de la empresa
        pdf.cell(95, 6, f"Nombre: {company.name}", 0, 1, 'R')
        
        # DNI empleado
        pdf.cell(95, 6, f"DNI/NIE: {employee.dni}", 0, 0)
        
        # CIF empresa
        pdf.cell(95, 6, f"CIF: {company.tax_id}", 0, 1, 'R')
        
        # Puesto empleado (para completar info)
        pdf.cell(95, 6, f"Puesto: {employee.position or '-'}", 0, 0)
        
        # Dirección empresa
        empresa_direccion = f"{company.address or ''}, {company.city or ''}"
        if empresa_direccion.strip() == ',':
            empresa_direccion = '-'
        pdf.cell(95, 6, f"Dirección: {empresa_direccion}", 0, 1, 'R')
        
        pdf.ln(5)  # Espacio antes de la tabla
        
        # Título de la tabla
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'REGISTROS DE FICHAJE', 0, 1, 'C')
        
        # Tabla de registros
        pdf.set_font('Arial', 'B', 10)
        
        # Cabecera de tabla
        col_widths = [35, 30, 30, 30, 40]
        header = ['Fecha', 'Entrada', 'Salida', 'Horas', 'Firma']
        
        # Dibujar cabecera
        pdf.set_fill_color(200, 200, 200)
        for i, col in enumerate(header):
            pdf.cell(col_widths[i], 10, col, 1, 0, 'C', True)
        pdf.ln()
        
        # Dibujar filas
        pdf.set_font('Arial', '', 10)
        
        for record in records:
            # Fecha
            pdf.cell(col_widths[0], 10, record.check_in_time.strftime('%d/%m/%Y'), 1, 0, 'C')
            
            # Hora entrada
            pdf.cell(col_widths[1], 10, record.check_in_time.strftime('%H:%M'), 1, 0, 'C')
            
            # Hora salida
            if record.check_out_time:
                pdf.cell(col_widths[2], 10, record.check_out_time.strftime('%H:%M'), 1, 0, 'C')
            else:
                pdf.cell(col_widths[2], 10, '-', 1, 0, 'C')
            
            # Horas trabajadas
            duration = record.duration()
            if duration is not None:
                hours_str = f"{duration:.2f}h"
            else:
                hours_str = '-'
            pdf.cell(col_widths[3], 10, hours_str, 1, 0, 'C')
            
            # Celda para firma
            y_pos_before = pdf.get_y()
            pdf.cell(col_widths[4], 10, '', 1, 0, 'C')
            
            # Dibujar firma en la celda si existe
            if include_signature and record.has_signature and record.signature_data:
                # Guardar posición actual
                x_pos = pdf.get_x() - col_widths[4]
                # Dibujar la firma dentro de la celda
                draw_signature(pdf, record.signature_data, x_pos + 2, y_pos_before + 1, col_widths[4] - 4, 8)
            
            pdf.ln()
    
    # Crear un archivo temporal en disco
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_filename = temp_file.name
    temp_file.close()
    
    # Guardar el PDF en el archivo temporal
    pdf.output(temp_filename)
    
    return temp_filename


def process_auto_checkouts():
    """Procesa los checkouts automáticos para fichajes pendientes"""
    from app import db
    from models_checkpoints import CheckPoint, CheckPointRecord, CheckPointIncident, CheckPointIncidentType, EmployeeContractHours
    
    # Obtener todos los puntos de fichaje activos
    checkpoints = CheckPoint.query.filter_by(status='active').all()
    
    # Contador total de registros procesados
    total_processed = 0
    
    for checkpoint in checkpoints:
        # Solo procesar si tiene hora de checkout automático configurada
        if not checkpoint.auto_checkout_time:
            continue
            
        # Obtener la fecha/hora actual
        now = datetime.now()
        
        # Construir la fecha/hora de corte de hoy
        checkout_datetime = datetime.combine(now.date(), checkpoint.auto_checkout_time)
        
        # Solo procesar si ya pasó la hora de corte
        if now < checkout_datetime:
            continue
            
        # Buscar todos los fichajes de hoy sin checkout
        pending_records = CheckPointRecord.query.filter(
            CheckPointRecord.checkpoint_id == checkpoint.id,
            CheckPointRecord.check_out_time.is_(None),
            CheckPointRecord.check_in_time.between(
                datetime.combine(now.date(), datetime.min.time()),
                now
            )
        ).all()
        
        # Contar registros procesados para este checkpoint
        checkpoint_processed = 0
        
        for record in pending_records:
            # Registrar el checkout automático
            record.check_out_time = checkout_datetime
            
            # Crear incidencia por el checkout automático
            incident = CheckPointIncident(
                record_id=record.id,
                incident_type=CheckPointIncidentType.MISSED_CHECKOUT,
                description=f"Checkout automático realizado a las {checkout_datetime.strftime('%H:%M')} por falta de registro de salida."
            )
            db.session.add(incident)
            
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
                
            # Incrementar contador de este checkpoint
            checkpoint_processed += 1
        
        # Guardar cambios si se procesaron registros
        if checkpoint_processed > 0:
            db.session.commit()
            
        # Añadir al contador total
        total_processed += checkpoint_processed
            
    return total_processed