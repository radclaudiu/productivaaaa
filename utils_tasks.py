from datetime import datetime
from flask import session
from app import db
from models_tasks import LocalUser, Location
import random
import string

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
        
def generate_secure_password(location_id=None):
    """Genera una contraseña segura con el formato estandarizado 'Portal[ID]2025!'."""
    if location_id:
        # Utilizamos un formato estándar para facilitar recordar la contraseña
        # Formato: Portal[ID]2025!
        return f"Portal{location_id}2025!"
    else:
        # Si no se proporciona ID, generamos una contraseña aleatoria más compleja
        # Asegurarnos de incluir al menos: una mayúscula, una minúscula, un número y un carácter especial
        uppercase = random.choice(string.ascii_uppercase)
        lowercase = random.choice(string.ascii_lowercase)
        digit = random.choice(string.digits)
        special = random.choice("!@#$%&*")
        
        # El resto de caracteres aleatorios
        remaining_length = 8  # Longitud total 12
        all_chars = string.ascii_letters + string.digits + "!@#$%&*"
        rest = ''.join(random.choice(all_chars) for _ in range(remaining_length))
        
        # Combinar todos los caracteres y mezclar
        password = uppercase + lowercase + digit + special + rest
        password_list = list(password)
        random.shuffle(password_list)
        
        return ''.join(password_list)

def regenerate_portal_password(location_id, only_return=False):
    """Regenera y actualiza la contraseña del portal de una ubicación.
    
    Args:
        location_id: ID de la ubicación
        only_return: Si es True, solo devuelve la contraseña actual sin regenerarla
    
    Returns:
        La contraseña actual o la nueva contraseña regenerada
    """
    try:
        location = Location.query.get(location_id)
        if not location:
            return None
            
        # Utilizamos un formato fijo para las contraseñas del portal
        # Formato estandarizado: Portal[ID]2025!
        # Esto permite que siempre podamos recuperar la contraseña sin almacenarla en texto plano
        fixed_password = generate_secure_password(location_id)
            
        if only_return:
            # Solo devolvemos la contraseña actual sin cambiar nada
            # Como usamos un formato fijo, siempre podemos reconstruirla
            return fixed_password
            
        # Actualizamos la contraseña en la base de datos
        location.set_portal_password(fixed_password)
        
        db.session.commit()
        return fixed_password
    except Exception as e:
        if not only_return:  # Solo hacemos rollback si estábamos modificando la BD
            db.session.rollback()
        print(f"Error al manipular contraseña: {str(e)}")
        return None