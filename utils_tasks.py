from datetime import datetime
from flask import session
from app import db
from models_tasks import LocalUser, Location

def create_default_local_user():
    """Crea un usuario local por defecto si no existe ninguno para la ubicación."""
    # Comprobamos si existen ubicaciones
    locations = Location.query.filter_by(is_active=True).all()
    if not locations:
        return None
    
    # Para cada ubicación, comprobamos si tiene usuarios locales
    for location in locations:
        local_users = LocalUser.query.filter_by(location_id=location.id).count()
        
        if local_users == 0:
            # Crear usuario admin por defecto para esta ubicación
            default_user = LocalUser(
                name="Admin",
                last_name="Local",
                username=f"admin_{location.id}",
                pin="1234",  # Se establecerá el hash más adelante
                is_active=True,
                location_id=location.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Establecer el PIN real
            default_user.set_pin("1234")
            
            db.session.add(default_user)
            db.session.commit()
            
            return default_user
    
    return None

def get_portal_session():
    """Obtiene información de la sesión del portal."""
    return {
        'location_id': session.get('portal_location_id'),
        'location_name': session.get('portal_location_name'),
        'user_id': session.get('local_user_id'),
        'user_name': session.get('local_user_name')
    }
    
def clear_portal_session():
    """Limpia la sesión del portal."""
    if 'portal_location_id' in session:
        session.pop('portal_location_id')
    if 'portal_location_name' in session:
        session.pop('portal_location_name')
    if 'local_user_id' in session:
        session.pop('local_user_id')
    if 'local_user_name' in session:
        session.pop('local_user_name')