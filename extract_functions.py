import os
import re
import ast

def extract_functions_from_file(file_path):
    """
    Extrae todas las funciones definidas en un archivo Python, junto con sus docstrings.
    
    Args:
        file_path: Ruta al archivo Python
        
    Returns:
        Una lista de tuplas que contienen (nombre_función, línea_inicio, docstring, código_completo)
    """
    functions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            source_lines = content.split('\n')
        
        # Analizar el código usando AST
        tree = ast.parse(content)
        
        # Extraer funciones a nivel de módulo y de clases
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Extraer docstring si existe
                docstring = ast.get_docstring(node) or ""
                
                # Obtener línea de inicio
                start_line = node.lineno
                
                # Estimamos la línea de fin usando el source_code
                # Esto es una simplificación, pero funcionará para nuestra necesidad
                # de documentación básica
                
                # Buscamos la definición de la función
                func_lines = []
                indentation = None
                i = start_line - 1  # Ajustar a índice base 0
                
                # Obtener la indentación de la línea de definición
                if i < len(source_lines):
                    line = source_lines[i]
                    # Encontrar la indentación inicial
                    spaces = len(line) - len(line.lstrip())
                    indentation = spaces
                    func_lines.append(line)
                    i += 1
                
                # Seguir leyendo líneas mientras tengan la misma o mayor indentación
                # hasta encontrar otra definición de función o clase
                while i < len(source_lines):
                    line = source_lines[i]
                    if line.strip() == '':
                        func_lines.append(line)
                        i += 1
                        continue
                    
                    current_spaces = len(line) - len(line.lstrip())
                    
                    # Si encontramos una línea con menor indentación, hemos salido de la función
                    if indentation is not None and current_spaces <= indentation and line.lstrip().startswith(('def ', 'class ')):
                        break
                    
                    # Verificar si todavía estamos dentro de la función
                    if indentation is not None and current_spaces < indentation and not line.lstrip().startswith('#'):
                        break
                    
                    func_lines.append(line)
                    i += 1
                
                # Unir las líneas para obtener el código completo de la función
                func_code = '\n'.join(func_lines)
                
                # Añadir a la lista de funciones
                functions.append((node.name, start_line, docstring, func_code))
                
        return functions
    except Exception as e:
        print(f"Error al analizar {file_path}: {e}")
        return []

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
    
    exclude_dirs = ['.cache', '__pycache__', '.pythonlibs']
    
    for root, dirs, files in os.walk(directory):
        # Excluir directorios no deseados
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    
    return py_files

def create_functions_table(output_file="funciones_app.md"):
    """
    Genera un archivo markdown con una tabla que contiene información sobre todas las funciones
    de la aplicación, incluyendo el nombre de la función, el archivo donde está definida,
    la línea de inicio y una descripción basada en su docstring.
    
    Args:
        output_file: Ruta donde se guardará el archivo de salida
    """
    function_data = []
    
    # Encontrar todos los archivos Python
    py_files = find_all_py_files('.')
    
    # Extraer funciones de cada archivo
    for file_path in py_files:
        # Convertir la ruta a un formato más legible
        relative_path = os.path.relpath(file_path, '.')
        
        # Extraer funciones de este archivo
        functions = extract_functions_from_file(file_path)
        
        for func_name, line_num, docstring, func_code in functions:
            # Preparar una descripción basada en el docstring
            description = ""
            if docstring:
                # Tomar solo la primera línea del docstring como descripción breve
                first_line = docstring.strip().split('\n')[0]
                description = first_line.strip()
            
            function_data.append((func_name, relative_path, line_num, description, docstring, func_code))
    
    # Ordenar la información por nombre de archivo y luego por línea
    function_data.sort(key=lambda x: (x[1], x[2]))
    
    # Generar el archivo markdown con la tabla principal
    with open(output_file, 'w', encoding='utf-8') as out_file:
        out_file.write("# Funciones de la Aplicación\n\n")
        out_file.write("Esta tabla contiene todas las funciones definidas en la aplicación, junto con su ubicación y una breve descripción.\n\n")
        out_file.write("| Función | Archivo | Línea | Descripción |\n")
        out_file.write("|---------|---------|-------|-------------|\n")
        
        for func_name, file_path, line_num, description, _, _ in function_data:
            # Escapar posibles pipes en la descripción para no romper la tabla markdown
            if description:
                description = description.replace('|', '\\|')
            
            # Añadir cada función a la tabla
            out_file.write(f"| `{func_name}` | {file_path} | {line_num} | {description} |\n")
        
        # Añadir sección detallada con código fuente y docstrings completos
        out_file.write("\n\n## Detalles de las Funciones\n\n")
        
        current_file = ""
        for func_name, file_path, line_num, _, docstring, func_code in function_data:
            # Añadir separadores de archivos para mayor claridad
            if file_path != current_file:
                out_file.write(f"\n### {file_path}\n\n")
                current_file = file_path
            
            # Escribir detalles de la función
            out_file.write(f"#### `{func_name}` (línea {line_num})\n\n")
            
            if docstring:
                out_file.write("**Docstring:**\n")
                out_file.write("```\n")
                out_file.write(docstring)
                out_file.write("\n```\n\n")
            
            out_file.write("**Código:**\n")
            out_file.write("```python\n")
            out_file.write(func_code)
            out_file.write("\n```\n\n")
    
    print(f"Archivo generado: {output_file}")

if __name__ == "__main__":
    create_functions_table()