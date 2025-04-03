import os
import re
import ast
import shutil

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
    
    exclude_dirs = ['.cache', '__pycache__', '.pythonlibs', 'migrations', 'env']
    
    for root, dirs, files in os.walk(directory):
        # Excluir directorios no deseados
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    
    return py_files

def extract_functions_info(file_path):
    """
    Extrae información sobre todas las funciones definidas en un archivo Python.
    
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

def add_function_comments(file_path, functions_info):
    """
    Añade o actualiza comentarios docstring a las funciones en un archivo Python.
    
    Args:
        file_path: Ruta al archivo Python
        functions_info: Lista de tuplas (nombre_función, línea_inicio, docstring_actual)
    
    Returns:
        True si se realizaron cambios, False en caso contrario
    """
    try:
        # Leer el contenido del archivo
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Crear una copia de seguridad
        backup_path = file_path + '.bak'
        shutil.copy2(file_path, backup_path)
        
        changes_made = False
        
        # Crear un diccionario para facilitar la búsqueda por línea
        functions_by_line = {line: (name, docstring) for name, line, docstring in functions_info}
        
        # Procesar cada línea del archivo
        result_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            result_lines.append(line)
            
            # Verificar si esta línea contiene el inicio de una definición de función
            line_num = i + 1  # Ajustar a numeración basada en 1
            if line_num in functions_by_line:
                func_name, existing_docstring = functions_by_line[line_num]
                
                # Obtener la indentación de la definición de la función
                match = re.match(r'^(\s*)', line)
                indent = match.group(1) if match else ""
                
                # Verificar si la siguiente línea ya contiene un docstring
                has_docstring = False
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('"""') or next_line.startswith("'''"):
                        has_docstring = True
                
                # Si no hay docstring, añadir uno
                if not has_docstring and not existing_docstring:
                    # Generar una descripción basada en el nombre de la función
                    func_description = generate_function_description(func_name)
                    docstring_lines = [
                        f'{indent}    """\n',
                        f'{indent}    {func_description}\n',
                        f'{indent}    """\n'
                    ]
                    
                    # Insertar el docstring después de la definición de la función
                    result_lines.extend(docstring_lines)
                    changes_made = True
                # Si ya existe un docstring pero está vacío, podríamos actualizarlo en el futuro
            
            i += 1
        
        # Si se realizaron cambios, escribir el nuevo contenido al archivo
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(result_lines)
            print(f"Se añadieron comentarios a las funciones en {file_path}")
            return True
        else:
            # Eliminar la copia de seguridad si no hubo cambios
            os.remove(backup_path)
            return False
            
    except Exception as e:
        print(f"Error al procesar {file_path}: {e}")
        return False

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
    }
    
    # Buscar coincidencias con los prefijos conocidos
    for prefix, template in prefix_templates.items():
        if func_name.startswith(prefix):
            # Extraer el resto del nombre de la función y convertirlo a formato legible
            remainder = func_name[len(prefix):].replace('_', ' ')
            return f"{template}{remainder}"
    
    # Caso especial para __init__
    if func_name == '__init__':
        return "Constructor de la clase"
    
    # Si no coincide con ningún prefijo conocido, devolver una descripción genérica
    readable_name = func_name.replace('_', ' ')
    return f"Función que {readable_name.lower()}"

def comment_all_py_files(directory='.'):
    """
    Añade comentarios a todas las funciones en todos los archivos Python
    del directorio especificado y sus subdirectorios.
    
    Args:
        directory: Directorio raíz donde comenzar la búsqueda
    """
    # Encontrar todos los archivos Python
    py_files = find_all_py_files(directory)
    
    # Procesar cada archivo
    for file_path in py_files:
        print(f"Procesando: {file_path}")
        
        # Extraer información de las funciones
        functions_info = extract_functions_info(file_path)
        
        if functions_info:
            # Añadir comentarios a las funciones
            add_function_comments(file_path, functions_info)
        else:
            print(f"No se encontraron funciones en {file_path}")

if __name__ == "__main__":
    print("Este script añadirá comentarios a todas las funciones en los archivos Python.")
    response = input("¿Desea continuar? (s/n): ")
    
    if response.lower() == 's':
        comment_all_py_files()
        print("Proceso completado.")
    else:
        print("Operación cancelada.")