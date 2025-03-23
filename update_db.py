from app import app, db
from flask_migrate import Migrate, upgrade
from sqlalchemy import text

def add_shelf_life_days_column():
    """Añade la columna shelf_life_days a la tabla products si no existe."""
    try:
        with app.app_context():
            # Verificar si la columna ya existe
            connection = db.engine.connect()
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'products' AND column_name = 'shelf_life_days';
            """))
            
            # Si la columna no existe, agregarla
            if result.fetchone() is None:
                print("Añadiendo columna shelf_life_days a la tabla products...")
                connection.execute(text("""
                    ALTER TABLE products
                    ADD COLUMN shelf_life_days INTEGER NOT NULL DEFAULT 0;
                """))
                print("Columna añadida correctamente.")
            else:
                print("La columna shelf_life_days ya existe en la tabla products.")
            
            connection.commit()
    except Exception as e:
        print(f"Error al añadir la columna: {str(e)}")
        raise

if __name__ == "__main__":
    add_shelf_life_days_column()
    print("Actualización completada.")