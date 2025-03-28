from app import app
from models_checkpoints import CheckPoint
from app import db

def reset_checkpoint_password():
    """Resetea la contraseña del punto de fichaje con username 'movil' a 'movil'"""
    with app.app_context():
        checkpoint = CheckPoint.query.filter_by(username='movil').first()
        if checkpoint:
            checkpoint.set_password('movil')
            db.session.commit()
            print(f"Contraseña actualizada para el punto de fichaje '{checkpoint.name}'")
        else:
            print("No se encontró el punto de fichaje con username 'movil'")

if __name__ == "__main__":
    reset_checkpoint_password()