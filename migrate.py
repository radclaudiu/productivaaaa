from flask_migrate import Migrate, MigrateCommand, upgrade
from app import app, db

migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        # Importar todos los modelos para asegurar que estén registrados
        from models import *
        from models_tasks import *
        
        # Crear tablas que no existen
        db.create_all()
        
        print("Migración completada.")