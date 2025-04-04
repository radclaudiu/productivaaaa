"""
Script para generar registros de fichaje aleatorios para los empleados de DNLN,
incluyendo algunos fichajes que se extiendan de un día a otro.
"""
import random
from datetime import datetime, timedelta
from app import create_app, db
from models import Employee, Company
from models_checkpoints import CheckPoint, CheckPointRecord, CheckPointOriginalRecord

def random_date(start_date, end_date):
    """Genera una fecha aleatoria entre start_date y end_date"""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def random_time(min_hour=7, max_hour=23, min_minute=0, max_minute=59):
    """Genera una hora aleatoria entre min_hour y max_hour"""
    hour = random.randint(min_hour, max_hour)
    minute = random.randint(min_minute, max_minute)
    return datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)

def generate_random_records(company_name='DNLN', num_records=30, start_date=None, end_date=None):
    """
    Genera registros aleatorios de fichaje para empleados de una empresa.
    
    Args:
        company_name: Nombre de la empresa (busca empresas que contengan este nombre)
        num_records: Número de registros a generar
        start_date: Fecha de inicio para los registros (por defecto, 30 días atrás)
        end_date: Fecha fin para los registros (por defecto, hoy)
    """
    app = create_app()
    
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    with app.app_context():
        # Buscar la empresa
        company = Company.query.filter(Company.name.like(f'%{company_name}%')).first()
        if not company:
            print(f"No se encontró ninguna empresa con el nombre: {company_name}")
            return
        
        # Buscar empleados de esa empresa
        employees = Employee.query.filter_by(company_id=company.id).all()
        if not employees:
            print(f"No se encontraron empleados para la empresa: {company.name}")
            return
        
        # Buscar puntos de fichaje de esa empresa
        checkpoints = CheckPoint.query.filter_by(company_id=company.id).all()
        if not checkpoints:
            print(f"No se encontraron puntos de fichaje para la empresa: {company.name}")
            return
        
        print(f"Generando {num_records} registros aleatorios para {len(employees)} empleados de {company.name}")
        
        records_created = 0
        
        for _ in range(num_records):
            # Elegir un empleado aleatorio
            employee = random.choice(employees)
            
            # Elegir un punto de fichaje aleatorio
            checkpoint = random.choice(checkpoints)
            
            # Generar fecha aleatoria
            random_day = random_date(start_date, end_date)
            
            # Decidir si será un turno que se extiende al día siguiente (20% de probabilidad)
            cross_day_shift = random.random() < 0.2
            
            if cross_day_shift:
                # Para turnos que cruzan el día, la entrada será entre las 18:00 y las 23:00
                check_in_time = random_day.replace(
                    hour=random.randint(18, 23),
                    minute=random.randint(0, 59),
                    second=0,
                    microsecond=0
                )
                
                # La salida será entre las 0:00 y las 8:00 del día siguiente
                next_day = check_in_time + timedelta(days=1)
                check_out_time = next_day.replace(
                    hour=random.randint(0, 8),
                    minute=random.randint(0, 59),
                    second=0,
                    microsecond=0
                )
            else:
                # Para turnos normales, la entrada será entre las 7:00 y las 10:00
                check_in_time = random_day.replace(
                    hour=random.randint(7, 10),
                    minute=random.randint(0, 59),
                    second=0,
                    microsecond=0
                )
                
                # La salida será entre 6 y 10 horas después
                hours_later = random.randint(6, 10)
                check_out_time = check_in_time + timedelta(hours=hours_later)
            
            # Crear el registro de fichaje
            record = CheckPointRecord(
                employee_id=employee.id,
                checkpoint_id=checkpoint.id,
                check_in_time=check_in_time,
                check_out_time=check_out_time,
                
                # Guardar también en los campos de registro original
                original_check_in_time=check_in_time,
                original_check_out_time=check_out_time
            )
            
            # Crear también el registro original (para mantener coherencia en la base de datos)
            original_record = CheckPointOriginalRecord(
                record=record,
                original_check_in_time=check_in_time,
                original_check_out_time=check_out_time
            )
            
            db.session.add(record)
            db.session.add(original_record)
            records_created += 1
            
            # Guardar cada 10 registros para evitar problemas de memoria
            if records_created % 10 == 0:
                db.session.commit()
                print(f"Creados {records_created} registros...")
        
        # Guardar todos los cambios pendientes
        db.session.commit()
        print(f"Se han creado {records_created} registros de fichaje aleatorios.")

if __name__ == "__main__":
    generate_random_records(company_name="DNLN", num_records=50)