from datetime import datetime
from flask import session
from app import db
from models_tasks import LocalUser, Location
import random
import string
import os
import subprocess
import platform
import json

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
        
def get_system_printers():
    """Detecta las impresoras disponibles en el sistema.
    
    Esta función utiliza diferentes métodos según el sistema operativo:
    - En Windows: utiliza la API de wmic
    - En Linux: utiliza lpstat o CUPS
    - En macOS: utiliza la API de CUPS
    
    En entornos de desarrollo o cuando los comandos no están disponibles,
    utiliza el archivo dev_printers.json para obtener impresoras simuladas.
    
    Returns:
        Una lista de diccionarios con información sobre las impresoras o impresoras simuladas
    """
    printers = []
    system = platform.system().lower()
    
    # Primero comprobar si estamos en un entorno de desarrollo 
    # o si los comandos necesarios no están disponibles
    dev_printers_file = os.path.join(os.path.dirname(__file__), 'dev_printers.json')
    command_not_found = False
    
    try:
        # Para entornos Windows
        if system == "windows":
            try:
                output = subprocess.check_output("wmic printer list brief", shell=True)
                printer_lines = output.decode('utf-8', errors='ignore').strip().split('\n')[1:]
                
                for line in printer_lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            printer_name = ' '.join(parts[:-1])  # Todo menos el último elemento (estado)
                            printers.append({
                                'name': printer_name.strip(),
                                'state': parts[-1]
                            })
            except subprocess.CalledProcessError:
                print("Comando wmic no disponible")
                command_not_found = True
        
        # Para entornos Linux con CUPS
        elif system == "linux":
            command_not_found = True  # Asumimos que los comandos pueden no estar disponibles
            
            # Intentamos diferentes métodos para detectar impresoras
            # Primer intento con lpstat
            try:
                output = subprocess.check_output("lpstat -p", shell=True)
                command_not_found = False  # Si llegamos aquí, el comando está disponible
                printer_lines = output.decode('utf-8').strip().split('\n')
                
                for line in printer_lines:
                    if line.startswith("printer"):
                        parts = line.split(' ', 2)
                        if len(parts) >= 2:
                            printer_name = parts[1].strip(':')
                            printer_state = "unknown"
                            if len(parts) > 2:
                                printer_state = parts[2]
                            printers.append({
                                'name': printer_name,
                                'state': printer_state
                            })
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Comando lpstat no disponible")
                
                # Segundo intento con CUPS vía lpoptions
                try:
                    output = subprocess.check_output("lpoptions -l", shell=True)
                    command_not_found = False  # Si llegamos aquí, el comando está disponible
                    if output:
                        # Si hay salida, hay al menos una impresora predeterminada
                        default_printer = subprocess.check_output("lpstat -d", shell=True)
                        default_printer = default_printer.decode('utf-8').strip()
                        if "system default destination:" in default_printer:
                            printer_name = default_printer.split("system default destination:")[1].strip()
                            printers.append({
                                'name': printer_name,
                                'state': 'default'
                            })
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print("Comando lpoptions no disponible")
                    
                    # Tercer intento: buscar impresoras con lpinfo
                    try:
                        output = subprocess.check_output("lpinfo -v", shell=True)
                        command_not_found = False  # Si llegamos aquí, el comando está disponible
                        printer_lines = output.decode('utf-8').strip().split('\n')
                        
                        for line in printer_lines:
                            if ":" in line:
                                parts = line.split(':', 1)
                                if len(parts) >= 2:
                                    printer_name = parts[1].strip()
                                    printers.append({
                                        'name': printer_name,
                                        'state': 'available'
                                    })
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        print("Comando lpinfo no disponible")
        
        # Para entornos macOS
        elif system == "darwin":
            try:
                output = subprocess.check_output("lpstat -p", shell=True)
                printer_lines = output.decode('utf-8').strip().split('\n')
                
                for line in printer_lines:
                    if line.startswith("printer"):
                        parts = line.split(' ', 2)
                        if len(parts) >= 2:
                            printer_name = parts[1].strip(':')
                            printer_state = "unknown"
                            if len(parts) > 2:
                                printer_state = parts[2]
                            printers.append({
                                'name': printer_name,
                                'state': printer_state
                            })
            except subprocess.CalledProcessError:
                print("Comando lpstat no disponible en macOS")
                command_not_found = True
        
        # Si no se detectaron impresoras reales o los comandos no estaban disponibles
        if not printers or command_not_found:
            # Usar datos simulados para desarrollo cuando los comandos no están disponibles
            if os.path.exists(dev_printers_file):
                print("Usando impresoras simuladas desde dev_printers.json")
                with open(dev_printers_file, 'r') as f:
                    printers = json.load(f)
                # Asegurarse de que al menos hay una lista vacía
                if not isinstance(printers, list):
                    printers = []
    
    except Exception as e:
        print(f"Error al detectar impresoras: {str(e)}")
        # En caso de error, intentar usar el archivo de desarrollo
        if os.path.exists(dev_printers_file):
            try:
                with open(dev_printers_file, 'r') as f:
                    printers = json.load(f)
                print("Usando impresoras simuladas debido a un error")
            except:
                print("No se pudo leer el archivo de impresoras simuladas")
                printers = []
    
    # Si después de todo no hay impresoras, devolver al menos algunas predeterminadas
    if not printers:
        printers = [
            {"name": "Impresora Predeterminada", "state": "enabled"},
            {"name": "PDF Printer", "state": "enabled"}
        ]
        print("Usando impresoras predeterminadas de respaldo")
    
    return printers