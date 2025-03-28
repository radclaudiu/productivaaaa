from flask_migrate import Migrate, upgrade
from app import app, db

migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        # Importar todos los modelos para asegurar que estén registrados
        from models import *
        from models_tasks import *
        from models_checkpoints import *
        
        # Aplicar las migraciones Alembic
        upgrade()
        
        # Para mayor seguridad, asegurarse de que todas las tablas existan
        db.create_all()
        
        print("Migración completada.")