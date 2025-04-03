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

def escape_html(text):
    """
    Escapa caracteres especiales para HTML.
    
    Args:
        text: Texto a escapar
        
    Returns:
        Texto escapado
    """
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def create_functions_html(output_file="funciones_app.html"):
    """
    Genera un archivo HTML interactivo con información sobre todas las funciones
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
            
            all_functions.append((func_name, relative_path, line_num, description, docstring))
    
    # Ordenar por archivo y línea
    all_functions.sort(key=lambda x: (x[1], x[2]))
    
    # Agrupar por archivo
    files_dict = {}
    for func_name, file_path, line_num, description, docstring in all_functions:
        if file_path not in files_dict:
            files_dict[file_path] = []
        files_dict[file_path].append((func_name, line_num, description, docstring))
    
    # Escribir el archivo HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentación de Funciones</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        h2 {
            color: #3498db;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
            margin-top: 40px;
        }
        h3 {
            color: #2980b9;
            margin-top: 20px;
        }
        .function {
            background-color: #f9f9f9;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 0 4px 4px 0;
        }
        .function:hover {
            background-color: #f1f1f1;
        }
        .function-name {
            font-family: monospace;
            font-weight: bold;
            color: #e74c3c;
        }
        .function-meta {
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 10px;
        }
        .function-description {
            margin-bottom: 10px;
        }
        .docstring {
            background-color: #f1f1f1;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            white-space: pre-wrap;
            margin-top: 10px;
            display: none;
        }
        .toggle-docstring {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
        }
        .toggle-docstring:hover {
            background-color: #2980b9;
        }
        .search-container {
            margin: 20px 0;
            text-align: center;
        }
        #searchInput {
            padding: 8px;
            width: 300px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .file-container {
            margin-bottom: 40px;
        }
        .file-header {
            cursor: pointer;
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .file-header:hover {
            background-color: #e9e9e9;
        }
        .file-functions {
            display: none;
        }
        .expand-all, .collapse-all {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }
        .expand-all:hover, .collapse-all:hover {
            background-color: #2980b9;
        }
        .count-badge {
            background-color: #e74c3c;
            color: white;
            border-radius: 50%;
            padding: 2px 8px;
            font-size: 0.8em;
            margin-left: 10px;
        }
        .timestamp {
            font-size: 0.8em;
            color: #7f8c8d;
            text-align: center;
            margin-top: 40px;
        }
        .toc {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 30px;
        }
        .toc h2 {
            margin-top: 0;
        }
        .toc ul {
            list-style-type: none;
            padding: 0;
        }
        .toc a {
            text-decoration: none;
            color: #3498db;
        }
        .toc a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>Documentación de Funciones de la Aplicación</h1>
    <p class="timestamp">Generado automáticamente el ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
    
    <div class="search-container">
        <input type="text" id="searchInput" placeholder="Buscar funciones...">
    </div>
    
    <div class="controls">
        <button class="expand-all">Expandir Todos</button>
        <button class="collapse-all">Colapsar Todos</button>
    </div>
    
    <div class="toc">
        <h2>Archivos</h2>
        <ul>''')
        
        # Generar tabla de contenidos
        for file_path in sorted(files_dict.keys()):
            f.write(f'<li><a href="#{file_path.replace(".", "_")}">{file_path}</a> <span class="count-badge">{len(files_dict[file_path])}</span></li>\n')
        
        f.write('''
        </ul>
    </div>
    ''')
        
        # Generar contenido para cada archivo
        for file_path, functions in sorted(files_dict.items()):
            file_id = file_path.replace(".", "_")
            f.write(f'''
    <div class="file-container">
        <div class="file-header" onclick="toggleFile('{file_id}')">
            <h2 id="{file_id}">{file_path} <span class="count-badge">{len(functions)}</span></h2>
        </div>
        <div class="file-functions" id="file_{file_id}">
        ''')
            
            # Escribir cada función
            for func_name, line_num, description, docstring in functions:
                docstring_html = ""
                if docstring:
                    docstring_html = f'''
            <div class="docstring" id="docstring_{file_id}_{line_num}">
{escape_html(docstring)}
            </div>
            <button class="toggle-docstring" onclick="toggleDocstring('{file_id}_{line_num}')">Ver Docstring</button>
                    '''
                
                f.write(f'''
            <div class="function">
                <h3 class="function-name">{escape_html(func_name)}</h3>
                <div class="function-meta">Línea: {line_num}</div>
                <div class="function-description">{escape_html(description)}</div>
                {docstring_html}
            </div>
                ''')
            
            f.write('''
        </div>
    </div>
            ''')
        
        # Añadir JavaScript para interactividad
        f.write('''
    <script>
        // Función para alternar la visibilidad de los docstrings
        function toggleDocstring(id) {
            const docstring = document.getElementById('docstring_' + id);
            const button = document.querySelector(`button[onclick="toggleDocstring('${id}')"]`);
            
            if (docstring.style.display === 'block') {
                docstring.style.display = 'none';
                button.textContent = 'Ver Docstring';
            } else {
                docstring.style.display = 'block';
                button.textContent = 'Ocultar Docstring';
            }
        }
        
        // Función para alternar la visibilidad de las funciones de un archivo
        function toggleFile(id) {
            const fileDiv = document.getElementById('file_' + id);
            
            if (fileDiv.style.display === 'block') {
                fileDiv.style.display = 'none';
            } else {
                fileDiv.style.display = 'block';
            }
        }
        
        // Evento de búsqueda
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const functions = document.querySelectorAll('.function');
            
            functions.forEach(function(func) {
                const functionName = func.querySelector('.function-name').textContent.toLowerCase();
                const description = func.querySelector('.function-description').textContent.toLowerCase();
                
                if (functionName.includes(searchTerm) || description.includes(searchTerm)) {
                    func.style.display = 'block';
                    // Mostrar el contenedor del archivo
                    const fileContainer = func.closest('.file-functions');
                    if (fileContainer) {
                        fileContainer.style.display = 'block';
                    }
                } else {
                    func.style.display = 'none';
                }
            });
            
            // Si el término de búsqueda está vacío, restaurar la visualización original
            if (searchTerm === '') {
                document.querySelectorAll('.file-functions').forEach(function(container) {
                    container.style.display = 'none';
                });
            }
        });
        
        // Botones para expandir/colapsar todos
        document.querySelector('.expand-all').addEventListener('click', function() {
            document.querySelectorAll('.file-functions').forEach(function(container) {
                container.style.display = 'block';
            });
        });
        
        document.querySelector('.collapse-all').addEventListener('click', function() {
            document.querySelectorAll('.file-functions').forEach(function(container) {
                container.style.display = 'none';
            });
        });
    </script>
</body>
</html>
        ''')
    
    print(f"Documentación HTML generada en {output_file}")

if __name__ == "__main__":
    create_functions_html()