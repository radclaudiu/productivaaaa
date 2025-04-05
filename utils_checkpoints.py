import os
import tempfile
import base64
import logging
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image
from fpdf import FPDF
from sqlalchemy import and_, func
from app import db
from models_checkpoints import CheckPointRecord, CheckPointOriginalRecord
from timezone_config import get_current_time, datetime_to_madrid, TIMEZONE

logger = logging.getLogger(__name__)

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


def set_font_safely(pdf, family, style='', size=12):
    """
    Función auxiliar para establecer la fuente de manera segura en el PDF.
    Normaliza los valores de estilo para evitar errores de tipado.
    
    Args:
        pdf: Objeto FPDF
        family: Nombre de la familia de fuente (string)
        style: Estilo de la fuente ('', 'B', 'I', 'U', etc.)
        size: Tamaño de la fuente (integer)
    """
    # Mapa de estilos válidos
    style_map = {
        '': '', 
        'B': 'B', 
        'I': 'I', 
        'U': 'U', 
        'BU': 'BU', 
        'UB': 'UB', 
        'BI': 'BI', 
        'IB': 'BI', 
        'UI': 'UI', 
        'IU': 'UI', 
        'BUI': 'BUI', 
        'BIU': 'BUI', 
        'UBI': 'BUI', 
        'UIB': 'BUI', 
        'IBU': 'BUI', 
        'IUB': 'BUI'
    }
    
    # Normalizar el estilo
    normalized_style = style_map.get(str(style), '')
    
    # Asegurar que el tamaño sea un entero
    normalized_size = int(size)
    
    # Establecer la fuente
    pdf.set_font(family, normalized_style, normalized_size)


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
        
        return True  # Indicar que se dibujó la firma correctamente
    except Exception as e:
        print(f"Error al dibujar la firma: {str(e)}")
        return False  # Indicar que hubo un error al dibujar la firma


def get_iso_week_start_end(date_obj):
    """
    Obtiene el inicio (lunes) y fin (domingo) de la semana ISO para una fecha dada.
    
    Args:
        date_obj: Objeto datetime.date o datetime.datetime
        
    Returns:
        Tupla con (fecha_inicio_semana, fecha_fin_semana)
    """
    # Si es un datetime, convertir a date
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    # El día de la semana en formato ISO (1=lunes, 7=domingo)
    iso_day = date_obj.isoweekday()
    
    # Calcular el lunes de esa semana
    week_start = date_obj - timedelta(days=iso_day - 1)
    
    # El domingo es 6 días después del lunes
    week_end = week_start + timedelta(days=6)
    
    return (week_start, week_end)

def get_week_description(week_start):
    """
    Genera una descripción de la semana basada en su fecha de inicio.
    
    Args:
        week_start: Fecha de inicio de la semana (lunes)
        
    Returns:
        String con descripción de la semana (ej: "Semana 15 (10/04 - 16/04)")
    """
    week_end = week_start + timedelta(days=6)
    week_num = week_start.isocalendar()[1]
    return f"Semana {week_num} ({week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m')})"

def generate_simple_pdf_report(records, start_date, end_date, include_signature=True):
    """
    Genera un informe PDF simple de los registros de fichaje sin agrupar por semanas y sin sumar horas.
    Este formato es específico para la ruta 'fichajes/records/export' y es exactamente igual al
    que utilizaba la ruta original '/rrrrrr/export'.
    """
    # Importar librerías necesarias
    from fpdf import FPDF
    from tempfile import NamedTemporaryFile
    
    # Clase PDF personalizada igual a la utilizada en routes_checkpoints_new.py
    class WeeklyReportPDF(FPDF):
        def __init__(self):
            super().__init__()
            # Colores corporativos
            self.primary_color = (31, 79, 121)  # Azul oscuro
            self.secondary_color = (82, 125, 162)  # Azul medio
            self.accent_color = (236, 240, 245)  # Azul muy claro para fondos
            
        def header(self):
            # Fondo de cabecera
            self.set_fill_color(*self.primary_color)
            self.rect(0, 0, 210, 15, 'F')
            
            # Título con texto blanco
            self.set_font('Arial', 'B', 15)
            self.set_text_color(255, 255, 255)
            
            title = 'Registros Originales de Fichajes'
            
            # Si hay una empresa en el contexto (pasada por el método add_company)
            if hasattr(self, 'company') and self.company:
                title = f'Registros Originales de Fichajes - {self.company.name}'
            
            self.cell(0, 10, title, 0, 1, 'C')
            
            # Restaurar color de texto
            self.set_text_color(0, 0, 0)
            
            # Período
            self.set_font('Arial', '', 10)
            if hasattr(self, 'start_date') and hasattr(self, 'end_date'):
                if self.start_date and self.end_date:
                    period = f"Período: {self.start_date.strftime('%d/%m/%Y')} - {self.end_date.strftime('%d/%m/%Y')}"
                elif self.start_date:
                    period = f"Desde: {self.start_date.strftime('%d/%m/%Y')}"
                elif self.end_date:
                    period = f"Hasta: {self.end_date.strftime('%d/%m/%Y')}"
                else:
                    period = "Todos los registros"
                
                self.set_y(15)  # Posicionarse después de la barra
                self.cell(0, 10, period, 0, 1, 'C')
            
            # Fecha de generación
            self.set_font('Arial', 'I', 8)
            self.cell(0, 5, f'Generado el: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'R')
            self.ln(5)
            
        def footer(self):
            # Pie de página
            self.set_y(-15)
            
            # Línea divisoria
            self.set_draw_color(*self.secondary_color)
            self.line(10, self.get_y(), 200, self.get_y())
            
            # Número de página
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')
        
        def add_company(self, company):
            self.company = company
            
        def add_dates(self, start_date, end_date):
            self.start_date = start_date
            self.end_date = end_date
    
    # Agrupar registros por empleado
    employee_records = {}
    for record in records:
        if record.employee_id not in employee_records:
            employee_records[record.employee_id] = {
                'employee': record.employee,
                'records': []
            }
        employee_records[record.employee_id]['records'].append(record)
    
    # Crear PDF
    pdf = WeeklyReportPDF()
    pdf.alias_nb_pages()
    
    # Configurar información de fechas y empresa
    if employee_records:
        first_employee = next(iter(employee_records.values()))['employee']
        pdf.add_company(first_employee.company)
    pdf.add_dates(start_date, end_date)
    
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Generar el PDF para cada empleado
    for emp_id, data in employee_records.items():
        employee = data['employee']
        records_list = data['records']
        
        # Encabezado de empleado
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(*pdf.secondary_color)
        pdf.set_text_color(255, 255, 255)
        pdf.rect(10, pdf.get_y(), 190, 10, 'F')
        pdf.cell(0, 10, f"Empleado: {employee.first_name} {employee.last_name} (DNI: {employee.dni})", 0, 1, 'C')
        pdf.set_text_color(0, 0, 0)  # Restaurar color de texto
        pdf.ln(5)
        
        # Ordenar registros por fecha
        sorted_records = sorted(records_list, key=lambda x: x.check_in_time if x.check_in_time else datetime.min)
        
        # Encabezados de la tabla
        pdf.set_font('Arial', 'B', 9)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(40, 7, 'Fecha', 1, 0, 'C', True)
        pdf.cell(30, 7, 'Entrada', 1, 0, 'C', True)
        pdf.cell(30, 7, 'Salida', 1, 0, 'C', True)
        pdf.cell(30, 7, 'Horas', 1, 0, 'C', True)
        pdf.cell(60, 7, 'Observaciones', 1, 1, 'C', True)
        
        # Datos de la tabla
        pdf.set_font('Arial', '', 9)
        
        for record in sorted_records:
            # Fecha
            pdf.cell(40, 7, record.check_in_time.strftime('%d/%m/%Y') if record.check_in_time else '-', 1, 0, 'C')
            
            # Entrada
            pdf.cell(30, 7, record.check_in_time.strftime('%H:%M') if record.check_in_time else '-', 1, 0, 'C')
            
            # Salida
            pdf.cell(30, 7, record.check_out_time.strftime('%H:%M') if record.check_out_time else '-', 1, 0, 'C')
            
            # Horas
            if record.check_in_time and record.check_out_time:
                duration = (record.check_out_time - record.check_in_time).total_seconds() / 3600
                pdf.cell(30, 7, f'{duration:.2f}', 1, 0, 'C')
            else:
                pdf.cell(30, 7, '-', 1, 0, 'C')
            
            # Observaciones (firmado, notas, etc.)
            notes = ""
            if hasattr(record, 'has_signature') and record.has_signature and include_signature:
                notes += "Firmado. "
            if hasattr(record, 'notes') and record.notes:
                notes += record.notes[:50]  # Limitar longitud
            pdf.cell(60, 7, notes, 1, 1, 'L')
            
            # Nueva página si es necesario
            if pdf.get_y() > pdf.h - 20:
                pdf.add_page()
        
        # Añadir una nueva página para el siguiente empleado
        if emp_id != list(employee_records.keys())[-1]:
            pdf.add_page()
    
    # Guardar en un archivo temporal
    output_file = NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_path = output_file.name
    output_file.close()
    
    # Guardar el PDF
    pdf.output(pdf_path)
    
    return pdf_path

def delete_employee_records(employee_id, start_date, end_date):
    """
    Elimina todos los registros de fichaje de un empleado en un rango de fechas específico.
    También elimina los registros originales y las incidencias asociadas.
    
    Args:
        employee_id: ID del empleado
        start_date: Fecha de inicio del rango (inclusive)
        end_date: Fecha de fin del rango (inclusive)
        
    Returns:
        dict: Un diccionario con el resultado de la operación, conteniendo:
            - success: Boolean indicando si la operación fue exitosa
            - message: Mensaje descriptivo del resultado
            - records_deleted: Número de registros eliminados
            - original_records_deleted: Número de registros originales eliminados
            - incidents_deleted: Número de incidencias eliminadas
    """
    try:
        # Iniciar una transacción para asegurar atomicidad
        db.session.begin()
        
        # Obtener registros que coincidan con los criterios
        records = CheckPointRecord.query.filter(
            CheckPointRecord.employee_id == employee_id,
            func.date(CheckPointRecord.check_in_time) >= start_date,
            func.date(CheckPointRecord.check_in_time) <= end_date
        ).all()
        
        if not records:
            # No hay registros que eliminar
            db.session.rollback()
            return {
                "success": True,
                "message": "No se encontraron registros para eliminar",
                "records_deleted": 0,
                "original_records_deleted": 0,
                "incidents_deleted": 0
            }
        
        # Recopilar los IDs de los registros para eliminar incidencias y registros originales
        record_ids = [record.id for record in records]
        
        # Eliminar incidencias asociadas primero
        from models_checkpoints import CheckPointIncident
        incidents = CheckPointIncident.query.filter(
            CheckPointIncident.record_id.in_(record_ids)
        ).all()
        incidents_count = len(incidents)
        
        for incident in incidents:
            db.session.delete(incident)
        
        # Eliminar registros originales asociados
        original_records = CheckPointOriginalRecord.query.filter(
            CheckPointOriginalRecord.record_id.in_(record_ids)
        ).all()
        original_records_count = len(original_records)
        
        for original_record in original_records:
            db.session.delete(original_record)
        
        # Finalmente, eliminar los registros principales
        records_count = len(records)
        for record in records:
            db.session.delete(record)
        
        # Confirmar la transacción
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Se eliminaron {records_count} registros y {incidents_count} incidencias",
            "records_deleted": records_count,
            "original_records_deleted": original_records_count,
            "incidents_deleted": incidents_count
        }
    
    except Exception as e:
        # Rollback en caso de error
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": str(e),
            "records_deleted": 0,
            "original_records_deleted": 0,
            "incidents_deleted": 0
        }

def generate_pdf_report(records, start_date, end_date, include_signature=True):
    """Genera un informe PDF de los registros de fichaje agrupados por semanas"""
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
        
        # Añadir título de resumen semanal
        pdf.set_y(initial_y + 35)  # Saltar después de los bloques de datos
        
        # Ordenar los registros por fecha
        sorted_records = sorted(records, key=lambda r: r.check_in_time)
        
        # Agrupar registros por semana
        weeks_data = {}
        
        for record in sorted_records:
            # Obtener la fecha de inicio de la semana (lunes)
            week_start, _ = get_iso_week_start_end(record.check_in_time)
            week_key = week_start.strftime('%Y-%m-%d')
            
            if week_key not in weeks_data:
                weeks_data[week_key] = {
                    'start_date': week_start,
                    'records': [],
                    'total_hours': 0
                }
            
            weeks_data[week_key]['records'].append(record)
            
            # Sumar horas si el registro tiene check-out
            if record.check_out_time:
                duration = (record.check_out_time - record.check_in_time).total_seconds() / 3600
                weeks_data[week_key]['total_hours'] += duration
        
        # Ordenar las semanas cronológicamente
        sorted_weeks = sorted(weeks_data.items(), key=lambda x: x[1]['start_date'])
        
        # Título general
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, 'RESUMEN DE FICHAJES POR SEMANA', 1, 1, 'C', True)
        pdf.set_text_color(0, 0, 0)  # Restaurar color
        pdf.ln(5)
        
        # Contador de horas totales
        total_hours = 0
        
        # Para cada semana
        for week_key, week_data in sorted_weeks:
            week_start = week_data['start_date']
            week_records = week_data['records']
            week_total = week_data['total_hours']
            total_hours += week_total
            
            # Título de la semana
            pdf.set_font('Arial', 'B', 11)
            pdf.set_fill_color(*pdf.secondary_color)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 8, get_week_description(week_start), 1, 1, 'C', True)
            pdf.set_text_color(0, 0, 0)  # Restaurar color
            
            # Encabezado de la tabla
            pdf.set_font('Arial', 'B', 10)
            pdf.set_fill_color(240, 240, 240)
            
            col_widths = [25, 25, 25, 25, 50, 40]  # Día, Fecha, Entrada, Salida, Checkpoint, Firma
            
            # Encabezados de columna
            pdf.cell(col_widths[0], 8, 'Día', 1, 0, 'C', True)
            pdf.cell(col_widths[1], 8, 'Fecha', 1, 0, 'C', True)
            pdf.cell(col_widths[2], 8, 'Entrada', 1, 0, 'C', True)
            pdf.cell(col_widths[3], 8, 'Salida', 1, 0, 'C', True)
            pdf.cell(col_widths[4], 8, 'Checkpoint', 1, 0, 'C', True)
            if include_signature:
                pdf.cell(col_widths[5], 8, 'Firma', 1, 1, 'C', True)
            else:
                pdf.cell(col_widths[5], 8, 'Horas', 1, 1, 'C', True)
            
            # Agrupar registros por día
            days_records = {}
            
            for record in week_records:
                day_key = record.check_in_time.strftime('%Y-%m-%d')
                
                if day_key not in days_records:
                    days_records[day_key] = []
                    
                days_records[day_key].append(record)
            
            # Ordenar días cronológicamente
            sorted_days = sorted(days_records.items(), key=lambda x: x[0])
            
            # Colores alternados para las filas
            row_colors = [(255, 255, 255), pdf.accent_color]  # Blanco y azul claro alternados
            
            # Para cada día
            row_index = 0
            for day_key, day_records in sorted_days:
                day_date = datetime.strptime(day_key, '%Y-%m-%d').date()
                day_name = day_date.strftime('%A')  # Nombre del día en inglés
                
                # Traducir el nombre del día al español
                day_name_es = {
                    'Monday': 'Lunes',
                    'Tuesday': 'Martes',
                    'Wednesday': 'Miércoles',
                    'Thursday': 'Jueves',
                    'Friday': 'Viernes',
                    'Saturday': 'Sábado',
                    'Sunday': 'Domingo'
                }.get(day_name, day_name)
                
                # Ordenar registros del día
                day_records = sorted(day_records, key=lambda r: r.check_in_time)
                day_total_hours = 0
                
                # Para cada registro del día
                for i, record in enumerate(day_records):
                    # Colocarse al inicio de la fila
                    pdf.set_x(10)
                    
                    # Color de fondo alternado para mejorar legibilidad
                    row_color = row_colors[row_index % 2]
                    pdf.set_fill_color(*row_color)
                    
                    # Fuente para los datos
                    pdf.set_font('Arial', '', 9)
                    
                    # Día de la semana (solo para el primer registro del día)
                    if i == 0:
                        pdf.cell(col_widths[0], 8, day_name_es, 1, 0, 'C', True)
                    else:
                        pdf.cell(col_widths[0], 8, '', 1, 0, 'C', True)
                    
                    # Fecha (solo para el primer registro del día)
                    if i == 0:
                        pdf.cell(col_widths[1], 8, day_date.strftime('%d/%m/%Y'), 1, 0, 'C', True)
                    else:
                        pdf.cell(col_widths[1], 8, '', 1, 0, 'C', True)
                    
                    # Hora de entrada
                    pdf.cell(col_widths[2], 8, record.check_in_time.strftime('%H:%M'), 1, 0, 'C', True)
                    
                    # Hora de salida
                    if record.check_out_time:
                        pdf.cell(col_widths[3], 8, record.check_out_time.strftime('%H:%M'), 1, 0, 'C', True)
                        # Calcular horas de este registro
                        hours = (record.check_out_time - record.check_in_time).total_seconds() / 3600
                        day_total_hours += hours
                    else:
                        pdf.cell(col_widths[3], 8, '-', 1, 0, 'C', True)
                    
                    # Checkpoint
                    checkpoint_name = record.checkpoint.name if record.checkpoint else '-'
                    pdf.cell(col_widths[4], 8, checkpoint_name, 1, 0, 'L', True)
                    
                    # Firma o horas
                    if include_signature:
                        # Verificar si tiene firma
                        if hasattr(record, 'has_signature') and record.has_signature:
                            pdf.cell(col_widths[5], 8, 'Firmado', 1, 1, 'C', True)
                        else:
                            pdf.cell(col_widths[5], 8, 'No firmado', 1, 1, 'C', True)
                    else:
                        # Mostrar horas de este registro
                        if record.check_out_time:
                            hours_str = f"{hours:.2f}"
                            pdf.cell(col_widths[5], 8, hours_str, 1, 1, 'C', True)
                        else:
                            pdf.cell(col_widths[5], 8, '-', 1, 1, 'C', True)
                    
                    row_index += 1
                
                # Si hay más de un registro en el día, mostrar total del día
                if len(day_records) > 1:
                    # Verificar si hay espacio suficiente para el total
                    if pdf.get_y() > pdf.h - 15:
                        pdf.add_page()
                    
                    pdf.set_x(10)
                    pdf.set_font('Arial', 'B', 9)
                    fill_color = (245, 245, 245)  # Gris muy claro para el total del día
                    pdf.set_fill_color(*fill_color)
                    
                    # Celda que abarca desde Día hasta Checkpoint
                    combined_width = sum(col_widths[:5])
                    pdf.cell(combined_width, 8, f'Total del día {day_date.strftime("%d/%m/%Y")}:', 1, 0, 'R', True)
                    
                    # Celda de total de horas
                    pdf.cell(col_widths[5], 8, f'{day_total_hours:.2f}', 1, 1, 'C', True)
                    
                    row_index += 1
            
            # Total de la semana
            if pdf.get_y() > pdf.h - 15:
                pdf.add_page()
            
            pdf.set_x(10)
            pdf.set_font('Arial', 'B', 10)
            pdf.set_fill_color(*pdf.secondary_color)
            pdf.set_text_color(255, 255, 255)
            
            # Celda que abarca desde Día hasta Checkpoint
            combined_width = sum(col_widths[:5])
            pdf.cell(combined_width, 10, f'TOTAL SEMANA {get_week_description(week_start)}:', 1, 0, 'R', True)
            
            # Celda de total de horas de la semana
            pdf.cell(col_widths[5], 10, f'{week_total:.2f}', 1, 1, 'C', True)
            
            # Restaurar color de texto
            pdf.set_text_color(0, 0, 0)
            
            # Espacio entre semanas
            pdf.ln(5)
        
        # Total de todas las semanas
        if len(sorted_weeks) > 1:
            if pdf.get_y() > pdf.h - 20:
                pdf.add_page()
            
            pdf.set_font('Arial', 'B', 12)
            pdf.set_fill_color(*pdf.primary_color)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(150, 12, f'TOTAL HORAS DEL PERÍODO:', 1, 0, 'R', True)
            pdf.cell(40, 12, f'{total_hours:.2f}', 1, 1, 'C', True)
            pdf.set_text_color(0, 0, 0)  # Restaurar color
        
        # Espacio entre empleados
        pdf.ln(10)
    
    # Guardar PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)
    
    return temp_file.name