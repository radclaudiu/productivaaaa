import os
import ast
from datetime import datetime

def find_all_py_files(directory):
    """
    Encuentra todos los archivos Python en un directorio y sus subdirectorios,
    excluyendo directorios de cache y librerías.
    
    Args:
        directory: Directorio raíz para la búsqueda
        
    Returns:
        Lista de rutas a archivos Python
    """
    py_files = []
    
    # Lista de archivos principales del proyecto
    main_py_files = [
        'app.py', 'main.py', 'models.py', 'models_checkpoints.py', 'models_tasks.py',
        'forms.py', 'forms_checkpoints.py', 'forms_tasks.py', 'forms_tmp.py',
        'routes.py', 'routes_checkpoints.py', 'routes_checkpoints_new.py', 'routes_tasks.py',
        'utils.py', 'utils_checkpoints.py', 'utils_tasks.py',
        'config.py', 'close_operation_hours.py', 'timezone_config.py',
        'create_employees.py', 'create_remaining_employees.py',
        'run_checkpoint_closer.py', 'scheduled_checkpoints_closer.py', 'verify_checkpoint_closures.py',
        'test_close_operation_hours.py', 'reset_checkpoint_password.py',
        'migrate.py', 'migrate_auto_checkout_removal.py', 'migrate_checkpoints.py',
        'migrate_contract_hours_activation.py', 'migrate_employee_on_shift.py',
        'migrate_label_templates.py', 'migrate_operation_hours.py',
        'migrate_original_records.py', 'migrate_task_instances.py',
        'update_db.py'
    ]
    
    # Incluir sólo los archivos principales del proyecto
    for file_name in main_py_files:
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            py_files.append(file_path)
    
    return py_files

def extract_functions_from_file(file_path):
    """
    Extrae todas las funciones definidas en un archivo Python.
    
    Args:
        file_path: Ruta al archivo Python
        
    Returns:
        Una lista de tuplas que contienen (nombre_función, línea_inicio, docstring)
    """
    functions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Analizar el código usando AST
        tree = ast.parse(content)
        
        # Extraer funciones a nivel de módulo y de clases
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Extraer docstring si existe
                docstring = ast.get_docstring(node) or ""
                
                # Añadir la función a la lista
                functions.append((node.name, node.lineno, docstring))
                
        return functions
    except Exception as e:
        print(f"Error al analizar {file_path}: {e}")
        return []

def generate_function_description(func_name):
    """
    Genera una descripción sencilla para una función basada en su nombre.
    
    Args:
        func_name: Nombre de la función
        
    Returns:
        Una descripción generada automáticamente
    """
    # Diccionario de prefijos comunes y sus descripciones
    prefix_templates = {
        'get_': 'Obtiene ',
        'set_': 'Establece ',
        'update_': 'Actualiza ',
        'delete_': 'Elimina ',
        'create_': 'Crea ',
        'add_': 'Añade ',
        'remove_': 'Elimina ',
        'check_': 'Verifica ',
        'is_': 'Comprueba si ',
        'has_': 'Comprueba si tiene ',
        'validate_': 'Valida ',
        'process_': 'Procesa ',
        'calculate_': 'Calcula ',
        'generate_': 'Genera ',
        'convert_': 'Convierte ',
        'format_': 'Formatea ',
        'parse_': 'Analiza ',
        'load_': 'Carga ',
        'save_': 'Guarda ',
        'init_': 'Inicializa ',
        'handle_': 'Maneja ',
        'render_': 'Renderiza ',
        'find_': 'Encuentra ',
        'search_': 'Busca ',
        'extract_': 'Extrae ',
        'filter_': 'Filtra ',
        'sort_': 'Ordena ',
        'apply_': 'Aplica ',
        'auto_': 'Automáticamente ',
        'restart_': 'Reinicia ',
        'log_': 'Registra ',
        'print_': 'Imprime ',
        'verify_': 'Verifica ',
        'test_': 'Prueba ',
        'run_': 'Ejecuta ',
        'execute_': 'Ejecuta ',
        'start_': 'Inicia ',
        'stop_': 'Detiene ',
        'close_': 'Cierra ',
        'open_': 'Abre ',
        'read_': 'Lee ',
        'write_': 'Escribe ',
        'send_': 'Envía ',
        'receive_': 'Recibe ',
        'connect_': 'Conecta ',
        'disconnect_': 'Desconecta ',
        'register_': 'Registra ',
        'unregister_': 'Elimina registro de ',
        'build_': 'Construye ',
        'compile_': 'Compila ',
        'deploy_': 'Despliega ',
        'install_': 'Instala ',
        'uninstall_': 'Desinstala ',
        'configure_': 'Configura ',
        'setup_': 'Configura ',
        'reset_': 'Reinicia ',
        'clear_': 'Limpia ',
        'cleanup_': 'Limpia ',
        'import_': 'Importa ',
        'export_': 'Exporta ',
        'backup_': 'Realiza copia de seguridad de ',
        'restore_': 'Restaura ',
        'merge_': 'Fusiona ',
        'split_': 'Divide ',
        'join_': 'Une ',
        'combine_': 'Combina ',
        'transform_': 'Transforma ',
        'modify_': 'Modifica ',
        'change_': 'Cambia ',
        'alter_': 'Altera ',
    }
    
    # Palabras de especial significado en nombres de funciones
    special_function_templates = {
        'after_request': 'Procesa la respuesta después de una petición HTTP',
        'before_request': 'Procesa la petición HTTP antes de manejarla',
        'forbidden_page': 'Maneja las respuestas HTTP 403 (Prohibido)',
        'page_not_found': 'Maneja las respuestas HTTP 404 (No encontrado)',
        'server_error_page': 'Maneja las respuestas HTTP 500 (Error del servidor)',
        'login': 'Gestiona el inicio de sesión',
        'logout': 'Gestiona el cierre de sesión',
        'register': 'Gestiona el registro de nuevos usuarios',
        'authenticate': 'Autentica a un usuario',
        'authorize': 'Autoriza a un usuario para realizar una acción',
        'check_auth': 'Verifica la autenticación de un usuario',
        'check_permission': 'Verifica los permisos de un usuario',
        'upload_file': 'Sube un archivo al servidor',
        'download_file': 'Descarga un archivo del servidor',
        'stream_file': 'Transmite un archivo al cliente',
        'render_template': 'Renderiza una plantilla HTML',
        'json_response': 'Genera una respuesta JSON',
        'xml_response': 'Genera una respuesta XML',
        'csv_response': 'Genera una respuesta CSV',
        'pdf_response': 'Genera una respuesta PDF',
        'excel_response': 'Genera una respuesta Excel',
        'send_email': 'Envía un correo electrónico',
        'send_sms': 'Envía un mensaje SMS',
        'send_notification': 'Envía una notificación',
        'generate_report': 'Genera un informe',
        'generate_invoice': 'Genera una factura',
        'generate_pdf': 'Genera un documento PDF',
        'generate_excel': 'Genera un documento Excel',
        'generate_csv': 'Genera un archivo CSV',
        'generate_xml': 'Genera un archivo XML',
        'generate_json': 'Genera un archivo JSON',
        'generate_html': 'Genera un documento HTML',
        'generate_token': 'Genera un token de autenticación',
        'verify_token': 'Verifica un token de autenticación',
        'refresh_token': 'Actualiza un token de autenticación',
        'hash_password': 'Genera el hash de una contraseña',
        'verify_password': 'Verifica una contraseña contra su hash',
        'change_password': 'Cambia la contraseña de un usuario',
        'reset_password': 'Reinicia la contraseña de un usuario',
        'forgot_password': 'Gestiona el proceso de recuperación de contraseña',
        'send_password_reset': 'Envía un enlace para restablecer la contraseña',
    }
    
    # Caso especial para __init__
    if func_name == '__init__':
        return "Constructor de la clase"
    
    # Verificar si es una función especial completa
    if func_name in special_function_templates:
        return special_function_templates[func_name]
    
    # Buscar coincidencias con los prefijos conocidos
    for prefix, template in prefix_templates.items():
        if func_name.startswith(prefix):
            # Extraer el resto del nombre de la función y convertirlo a formato legible
            remainder = func_name[len(prefix):].replace('_', ' ')
            return f"{template}{remainder}"
    
    # Si no coincide con ningún prefijo conocido, devolver una descripción genérica
    readable_name = func_name.replace('_', ' ')
    return f"Función para {readable_name.lower()}"

def create_functions_documentation(output_file="funciones_documentadas.txt"):
    """
    Genera un archivo de texto con información sobre todas las funciones
    de la aplicación, incluyendo sus descripciones generadas automáticamente.
    
    Args:
        output_file: Ruta donde se guardará el archivo de salida
    """
    all_functions = []
    
    # Encontrar todos los archivos Python
    py_files = find_all_py_files('.')
    
    # Procesar cada archivo
    for file_path in py_files:
        relative_path = os.path.relpath(file_path, '.')
        
        # Extraer funciones de este archivo
        functions = extract_functions_from_file(file_path)
        
        # Añadir funciones a la lista global
        for func_name, line_num, docstring in functions:
            # Generar descripción si no hay docstring
            description = docstring.strip().split('\n')[0] if docstring else generate_function_description(func_name)
            
            all_functions.append((func_name, relative_path, line_num, description))
    
    # Ordenar por archivo y línea
    all_functions.sort(key=lambda x: (x[1], x[2]))
    
    # Escribir al archivo de salida
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Documentación de Funciones\n\n")
        f.write(f"Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        current_file = ""
        for func_name, file_path, line_num, description in all_functions:
            # Añadir encabezado de archivo cuando cambia
            if file_path != current_file:
                f.write(f"\n## {file_path}\n\n")
                current_file = file_path
            
            # Escribir información de la función
            f.write(f"### `{func_name}` (línea {line_num})\n\n")
            f.write(f"{description}\n\n")
    
    print(f"Documentación generada en {output_file}")

if __name__ == "__main__":
    create_functions_documentation()