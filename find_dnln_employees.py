from app import create_app, db
from models import Employee, Company

app = create_app()

with app.app_context():
    # Buscar la empresa DNLN
    company = Company.query.filter(Company.name.like('%DNLN%')).first()
    print(f'Empresa encontrada: {company.name if company else "No encontrada"}')
    
    if company:
        # Buscar empleados de esa empresa
        employees = Employee.query.filter_by(company_id=company.id).all()
        print(f'Total empleados: {len(employees)}')
        
        # Mostrar los primeros 5 empleados
        for e in employees[:5]:
            print(f'{e.id}. {e.first_name} {e.last_name} - Fecha inicio: {e.start_date}')