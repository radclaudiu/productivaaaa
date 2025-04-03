import os
import ast
import re
import shutil
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
    
    # Excluir los scripts de documentación
    exclude_files = ['extract_functions.py', 'generate_functions_documentation.py', 
                    'add_function_comments.py', 'comment_functions.py', 
                    'generate_functions_html.py']
    
    # Incluir sólo los archivos principales del proyecto y excluir los scripts de documentación
    for file_name in main_py_files:
        if file_name not in exclude_files:
            file_path = os.path.join(directory, file_name)
            if os.path.exists(file_path):
                py_files.append(file_path)
    
    return py_files

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

def extract_function_nodes(source_code):
    """
    Extrae los nodos AST de todas las funciones en el código fuente.
    
    Args:
        source_code: Código fuente Python
        
    Returns:
        Un diccionario de nodos de función indexados por línea de inicio
    """
    try:
        tree = ast.parse(source_code)
        functions = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions[node.lineno] = node
        
        return functions
    except Exception as e:
        print(f"Error al analizar el código: {e}")
        return {}

def has_docstring(node):
    """
    Verifica si un nodo de función tiene docstring.
    
    Args:
        node: Nodo AST de una función
        
    Returns:
        True si la función tiene docstring, False en caso contrario
    """
    return ast.get_docstring(node) is not None

def add_docstrings_to_file(file_path):
    """
    Añade docstrings a las funciones en un archivo que no los tienen.
    
    Args:
        file_path: Ruta al archivo a procesar
        
    Returns:
        Número de docstrings añadidos
    """
    print(f"Procesando {file_path}...")
    
    try:
        # Leer el contenido del archivo
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Extraer nodos de función
        function_nodes = extract_function_nodes(source_code)
        
        if not function_nodes:
            print(f"No se encontraron funciones en {file_path}")
            return 0
        
        # Crear una copia de seguridad
        backup_path = f"{file_path}.bak"
        shutil.copy2(file_path, backup_path)
        
        # Convertir el código a líneas para procesamiento
        lines = source_code.split('\n')
        result_lines = []
        
        i = 0
        docstrings_added = 0
        
        while i < len(lines):
            current_line = lines[i]
            result_lines.append(current_line)
            
            # Comprobar si esta línea es el inicio de una definición de función
            line_num = i + 1  # Ajustar a numeración de línea (base 1)
            
            if line_num in function_nodes:
                node = function_nodes[line_num]
                
                # Verificar si ya tiene docstring
                if not has_docstring(node):
                    # Obtener indentación de la línea actual
                    indent_match = re.match(r'^(\s*)', current_line)
                    indentation = indent_match.group(1) if indent_match else ''
                    
                    # Generar descripción para la función
                    func_description = generate_function_description(node.name)
                    
                    # Crear docstring
                    docstring_lines = [
                        f"{indentation}    \"\"\"",
                        f"{indentation}    {func_description}",
                        f"{indentation}    \"\"\"",
                    ]
                    
                    # Insertar docstring después de la definición de la función
                    i += 1
                    for doc_line in docstring_lines:
                        result_lines.append(doc_line)
                    
                    docstrings_added += 1
                    continue
            
            i += 1
        
        # Si se añadieron docstrings, guardar el archivo modificado
        if docstrings_added > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(result_lines))
            print(f"  ✓ Se añadieron {docstrings_added} docstrings en {file_path}")
        else:
            # Eliminar la copia de seguridad si no hubo cambios
            os.remove(backup_path)
            print(f"  - No fue necesario añadir docstrings en {file_path}")
        
        return docstrings_added
    
    except Exception as e:
        print(f"  ✗ Error al procesar {file_path}: {e}")
        return 0

def add_docstrings_to_all_files():
    """
    Añade docstrings a todas las funciones en todos los archivos Python
    que no los tienen.
    """
    # Crear un log
    log_file = "docstrings_added.log"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Log de adición de docstrings - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Encontrar todos los archivos Python
    py_files = find_all_py_files('.')
    
    total_docstrings_added = 0
    processed_files = 0
    
    print(f"Se encontraron {len(py_files)} archivos Python para procesar.")
    
    # Procesar cada archivo
    for file_path in py_files:
        docstrings_added = add_docstrings_to_file(file_path)
        total_docstrings_added += docstrings_added
        processed_files += 1
        
        # Actualizar el log
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{file_path}: {docstrings_added} docstrings añadidos\n")
    
    # Añadir resumen al log
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\nResumen:\n")
        f.write(f"- Total de archivos procesados: {processed_files}\n")
        f.write(f"- Total de docstrings añadidos: {total_docstrings_added}\n")
    
    print(f"\nProceso completado.")
    print(f"- Total de archivos procesados: {processed_files}")
    print(f"- Total de docstrings añadidos: {total_docstrings_added}")
    print(f"- Log guardado en: {log_file}")

if __name__ == "__main__":
    print("Este script añadirá docstrings a todas las funciones que no los tengan.")
    print("Se creará una copia de seguridad de cada archivo antes de modificarlo.")
    response = input("¿Desea continuar? (s/n): ")
    
    if response.lower() == 's':
        add_docstrings_to_all_files()
    else:
        print("Operación cancelada.")