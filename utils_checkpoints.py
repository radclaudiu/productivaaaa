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
    pdf = CheckPointPDF(title=f'Informe de Fichajes: {start_date.strftime("%d/%m/%Y")} - {end_date.strftime("%d/%m/%Y")}')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Para cada empleado
    for employee_id, data in employees_records.items():
        employee = data['employee']
        records = data['records']
        
        # Título empleado
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"{employee.first_name} {employee.last_name} - {employee.position}", 0, 1)
        
        # Tabla de registros
        pdf.set_font('Arial', 'B', 10)
        
        # Cabecera de tabla
        col_widths = [30, 30, 30, 25, 40, 25]
        header = ['Fecha', 'Entrada', 'Salida', 'Horas', 'Punto de Fichaje', 'Ajustado']
        
        # Dibujar cabecera
        pdf.set_fill_color(200, 200, 200)
        for i, col in enumerate(header):
            pdf.cell(col_widths[i], 10, col, 1, 0, 'C', True)
        pdf.ln()
        
        # Dibujar filas
        pdf.set_font('Arial', '', 10)
        
        total_hours = 0
        
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
                total_hours += duration
            else:
                hours_str = '-'
            pdf.cell(col_widths[3], 10, hours_str, 1, 0, 'C')
            
            # Punto de fichaje
            pdf.cell(col_widths[4], 10, record.checkpoint.name, 1, 0, 'C')
            
            # Ajustado
            pdf.cell(col_widths[5], 10, 'Sí' if record.adjusted else 'No', 1, 0, 'C')
            
            pdf.ln()
            
            # Si hay firma y se debe incluir, añadirla
            if include_signature and record.has_signature and record.signature_data:
                pdf.ln(5)
                pdf.set_font('Arial', 'I', 8)
                pdf.cell(0, 5, f"Firma del {record.check_in_time.strftime('%d/%m/%Y')}:", 0, 1)
                draw_signature(pdf, record.signature_data, 30, pdf.get_y(), 50, 20)
                pdf.ln(25)  # Espacio para la firma
        
        # Total de horas
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(sum(col_widths[0:3]), 10, 'Total Horas:', 1, 0, 'R')
        pdf.cell(col_widths[3], 10, f"{total_hours:.2f}h", 1, 0, 'C')
        pdf.cell(sum(col_widths[4:]), 10, '', 1, 0)
        
        pdf.ln(20)  # Espacio entre empleados
    
    # Crear un archivo en memoria
    pdf_file = BytesIO()
    pdf.output(pdf_file)
    pdf_file.seek(0)
    
    return pdf_file


def process_auto_checkouts():
    """Procesa los checkouts automáticos para fichajes pendientes"""
    from app import db
    from models_checkpoints import CheckPoint, CheckPointRecord, CheckPointIncident, CheckPointIncidentType
    
    # Obtener todos los puntos de fichaje activos
    checkpoints = CheckPoint.query.filter_by(status='active').all()
    
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
        
        for record in pending_records:
            # Registrar el checkout automático
            record.check_out_time = checkout_datetime
            
            # Crear incidencia
            incident = CheckPointIncident(
                record_id=record.id,
                incident_type=CheckPointIncidentType.MISSED_CHECKOUT,
                description=f"Checkout automático realizado a las {checkout_datetime.strftime('%H:%M')} por falta de registro de salida."
            )
            
            db.session.add(incident)
        
        # Guardar cambios
        if pending_records:
            db.session.commit()
    
    return len(pending_records) if 'pending_records' in locals() else 0