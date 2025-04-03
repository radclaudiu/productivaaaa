#!/usr/bin/env python3
"""
PgAdmin - Una interfaz web simple para administrar bases de datos PostgreSQL.
"""

import os
import re
import psycopg2
import psycopg2.extras
from functools import wraps
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, g, flash, jsonify, Response
from datetime import datetime

# Configuración
DATABASE_URL = os.environ.get('DATABASE_URL')

def create_app():
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__, template_folder='templates')
    app.secret_key = os.environ.get('SESSION_SECRET', 'pgadmin-dev-key')
    
    # Registrar los manejadores before_request y teardown_request
    app.before_request(before_request)
    app.teardown_request(teardown_request)
    
    # Registrar las rutas
    app.add_url_rule('/', 'index', index)
    app.add_url_rule('/tables/<table_name>', 'view_table', view_table, methods=['GET'])
    app.add_url_rule('/query', 'execute_query', execute_query, methods=['GET', 'POST'])
    app.add_url_rule('/jinja_templates', 'jinja_templates', jinja_templates)
    
    # Template para pgAdmin
    @app.context_processor
    def inject_globals():
        return {'app_name': 'PgAdmin', 'current_year': datetime.now().year}
    
    return app

def get_db_connection():
    """Create a connection to the PostgreSQL database."""
    if DATABASE_URL is None:
        raise Exception("DATABASE_URL environment variable is not set.")
    
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False  # We'll manage transactions explicitly
    return conn

def before_request():
    """Set up a database connection before each request."""
    try:
        # Establecer la conexión a la base de datos
        g.db = get_db_connection()
        g.cursor = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
    except Exception as e:
        # Si hay un error al conectar, almacenarlo en g para mostrarlo en la plantilla
        g.db_error = str(e)
        g.db = None
        g.cursor = None

def teardown_request(exception):
    """Close the database connection after each request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def index():
    """Display the main dashboard with database information."""
    # Verificar si hay un error de conexión
    if hasattr(g, 'db_error'):
        return render_template('pgadmin/error.html', error=g.db_error)
    
    # Lista de tablas
    tables = []
    try:
        # Consulta para obtener todas las tablas públicas
        g.cursor.execute("""
            SELECT 
                table_name, 
                pg_catalog.obj_description(pgc.oid, 'pg_class') as table_comment,
                (SELECT count(*) FROM information_schema.columns WHERE table_name=t.table_name) as column_count,
                (SELECT count(*) FROM pg_indexes WHERE tablename=t.table_name) as index_count,
                (SELECT count(*) FROM pg_constraint WHERE conrelid = (SELECT oid FROM pg_class WHERE relname=t.table_name)) as constraint_count
            FROM information_schema.tables t
            JOIN pg_catalog.pg_class pgc ON pgc.relname=t.table_name
            WHERE table_schema='public' 
            AND table_type='BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = g.cursor.fetchall()
        
        # Para cada tabla, obtener el conteo aproximado de filas
        for i, table in enumerate(tables):
            try:
                # Usamos una consulta rápida para estimar el conteo de filas
                g.cursor.execute(f"SELECT count(*) FROM {table['table_name']}")
                row_count = g.cursor.fetchone()[0]
                tables[i] = dict(table)
                tables[i]['row_count'] = row_count
            except Exception as e:
                tables[i] = dict(table)
                tables[i]['row_count'] = f"Error: {str(e)}"
        
        # Obtener información del sistema
        g.cursor.execute("""
            SELECT 
                version() as version,
                current_database() as database,
                current_user as user,
                (SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE') as table_count,
                pg_size_pretty(pg_database_size(current_database())) as database_size
        """)
        system_info = g.cursor.fetchone()
        
        return render_template('pgadmin/index.html', 
                              tables=tables, 
                              system_info=system_info)
    
    except Exception as e:
        return render_template('pgadmin/error.html', error=str(e))

def view_table(table_name):
    """Display the contents of a table."""
    try:
        # Validar el nombre de la tabla para evitar inyección SQL
        if not re.match(r'^[a-zA-Z0-9_]+$', table_name):
            raise Exception("Nombre de tabla inválido")
        
        # Obtener información de las columnas
        g.cursor.execute(f"""
            SELECT column_name, data_type, is_nullable, column_default,
                   pg_catalog.col_description(pgc.oid, cols.ordinal_position) as column_comment
            FROM information_schema.columns cols
            JOIN pg_catalog.pg_class pgc ON pgc.relname=cols.table_name
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = g.cursor.fetchall()
        
        # Convertir los resultados a listas para ser más manejables en la plantilla
        column_names = [col['column_name'] for col in columns]
        
        # Obtener datos de la tabla (primeras 100 filas)
        g.cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
        rows = g.cursor.fetchall()
        
        # Obtener estadísticas de la tabla
        g.cursor.execute(f"""
            SELECT 
                (SELECT count(*) FROM {table_name}) as row_count,
                pg_size_pretty(pg_total_relation_size('{table_name}')) as table_size,
                pg_catalog.obj_description(pgc.oid, 'pg_class') as table_comment
            FROM pg_catalog.pg_class pgc
            WHERE pgc.relname = %s
        """, (table_name,))
        
        stats = g.cursor.fetchone()
        
        return render_template('pgadmin/table.html',
                              table_name=table_name,
                              columns=columns,
                              column_names=column_names,
                              rows=rows,
                              stats=stats)
        
    except Exception as e:
        return render_template('pgadmin/error.html', error=str(e), table_name=table_name)

def execute_query():
    """Execute a custom SQL query."""
    results = None
    error = None
    query = request.form.get('query', '')
    affected_rows = None
    
    if request.method == 'POST':
        try:
            # Ejecutar la consulta
            g.cursor.execute(query)
            
            # Si la consulta devolvió resultados (como un SELECT)
            if g.cursor.description:
                results = g.cursor.fetchall()
                # Convertir los objetos Row a diccionarios
                column_names = [desc[0] for desc in g.cursor.description]
            else:
                # Si la consulta fue un INSERT, UPDATE, DELETE, etc.
                g.db.commit()
                affected_rows = g.cursor.rowcount
        
        except Exception as e:
            g.db.rollback()
            error = str(e)
    
    return render_template('pgadmin/query.html',
                          query=query,
                          results=results,
                          error=error,
                          affected_rows=affected_rows)

def jinja_templates():
    """Return Jinja2 templates to be used on the client side."""
    import jinja2
    
    # Template para la página de inicio
    index_template = """
    {% extends 'pgadmin/base.html' %}
    
    {% block title %}Dashboard{% endblock %}
    
    {% block content %}
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-md-12 mb-4">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">Información del Sistema</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3 mb-3">
                                <div class="card h-100">
                                    <div class="card-body text-center">
                                        <h3 class="mb-0">{{ system_info.database }}</h3>
                                        <p class="text-muted">Base de Datos</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3 mb-3">
                                <div class="card h-100">
                                    <div class="card-body text-center">
                                        <h3 class="mb-0">{{ system_info.table_count }}</h3>
                                        <p class="text-muted">Tablas</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3 mb-3">
                                <div class="card h-100">
                                    <div class="card-body text-center">
                                        <h3 class="mb-0">{{ system_info.user }}</h3>
                                        <p class="text-muted">Usuario</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3 mb-3">
                                <div class="card h-100">
                                    <div class="card-body text-center">
                                        <h3 class="mb-0">{{ system_info.database_size }}</h3>
                                        <p class="text-muted">Tamaño</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="mt-3">
                            <small class="text-muted">Versión: {{ system_info.version }}</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-12">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Tablas</h5>
                        <a href="{{ url_for('execute_query') }}" class="btn btn-light btn-sm">
                            <i class="fas fa-terminal"></i> Consulta SQL
                        </a>
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th>Nombre</th>
                                        <th>Columnas</th>
                                        <th>Filas</th>
                                        <th>Índices</th>
                                        <th>Restricciones</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for table in tables %}
                                    <tr>
                                        <td>
                                            <a href="{{ url_for('view_table', table_name=table.table_name) }}">
                                                {{ table.table_name }}
                                            </a>
                                            {% if table.table_comment %}
                                            <br><small class="text-muted">{{ table.table_comment }}</small>
                                            {% endif %}
                                        </td>
                                        <td>{{ table.column_count }}</td>
                                        <td>{{ table.row_count }}</td>
                                        <td>{{ table.index_count }}</td>
                                        <td>{{ table.constraint_count }}</td>
                                        <td>
                                            <div class="btn-group btn-group-sm">
                                                <a href="{{ url_for('view_table', table_name=table.table_name) }}" class="btn btn-outline-primary">
                                                    <i class="fas fa-table"></i> Ver
                                                </a>
                                            </div>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    """
    
    # Template para la página de tabla
    table_template = """
    {% extends 'pgadmin/base.html' %}
    
    {% block title %}Tabla: {{ table_name }}{% endblock %}
    
    {% block content %}
    <div class="container-fluid mt-4">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="{{ url_for('index') }}">Tablas</a></li>
                <li class="breadcrumb-item active">{{ table_name }}</li>
            </ol>
        </nav>
        
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Tabla: {{ table_name }}</h5>
                        <div>
                            <a href="{{ url_for('execute_query') }}?query=SELECT * FROM {{ table_name }} LIMIT 100" class="btn btn-light btn-sm me-2">
                                <i class="fas fa-edit"></i> Consulta
                            </a>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="card mb-3">
                                    <div class="card-body text-center">
                                        <h4 class="mb-0">{{ stats.row_count }}</h4>
                                        <p class="text-muted">Filas</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card mb-3">
                                    <div class="card-body text-center">
                                        <h4 class="mb-0">{{ stats.table_size }}</h4>
                                        <p class="text-muted">Tamaño</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card mb-3">
                                    <div class="card-body text-center">
                                        <h4 class="mb-0">{{ columns|length }}</h4>
                                        <p class="text-muted">Columnas</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        {% if stats.table_comment %}
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle"></i> {{ stats.table_comment }}
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">Estructura</h5>
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th>Columna</th>
                                        <th>Tipo</th>
                                        <th>Nulo</th>
                                        <th>Predeterminado</th>
                                        <th>Comentario</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for column in columns %}
                                    <tr>
                                        <td><code>{{ column.column_name }}</code></td>
                                        <td><code>{{ column.data_type }}</code></td>
                                        <td>{{ 'Sí' if column.is_nullable == 'YES' else 'No' }}</td>
                                        <td><code>{{ column.column_default or '' }}</code></td>
                                        <td>{{ column.column_comment or '' }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-12">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">Datos (primeras 100 filas)</h5>
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover table-sm mb-0">
                                <thead class="table-light">
                                    <tr>
                                        {% for column_name in column_names %}
                                        <th>{{ column_name }}</th>
                                        {% endfor %}
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for row in rows %}
                                    <tr>
                                        {% for column_name in column_names %}
                                        <td>
                                            {% if row[column_name] is none %}
                                            <span class="text-muted">NULL</span>
                                            {% elif row[column_name] is boolean %}
                                            <span class="badge bg-{{ 'success' if row[column_name] else 'danger' }}">
                                                {{ 'Verdadero' if row[column_name] else 'Falso' }}
                                            </span>
                                            {% else %}
                                            {{ row[column_name] }}
                                            {% endif %}
                                        </td>
                                        {% endfor %}
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    """
    
    # Template para la página de consulta
    query_template = """
    {% extends 'pgadmin/base.html' %}
    
    {% block title %}Consulta SQL{% endblock %}
    
    {% block content %}
    <div class="container-fluid mt-4">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="{{ url_for('index') }}">Tablas</a></li>
                <li class="breadcrumb-item active">Consulta SQL</li>
            </ol>
        </nav>
        
        <div class="card shadow mb-4">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Consulta SQL</h5>
            </div>
            <div class="card-body">
                <form action="{{ url_for('execute_query') }}" method="post">
                    <div class="form-group mb-3">
                        <label for="query">Consulta SQL:</label>
                        <textarea class="form-control font-monospace" id="query" name="query" rows="6" style="font-family: monospace;">{{ query }}</textarea>
                        <small class="form-text text-muted">Introduzca una consulta SQL válida.</small>
                    </div>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-play"></i> Ejecutar
                    </button>
                </form>
            </div>
        </div>
        
        {% if error %}
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle"></i> <strong>Error:</strong> {{ error }}
        </div>
        {% endif %}
        
        {% if affected_rows is not none %}
        <div class="alert alert-success">
            <i class="fas fa-check-circle"></i> Consulta ejecutada correctamente. {{ affected_rows }} filas afectadas.
        </div>
        {% endif %}
        
        {% if results %}
        <div class="card shadow">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Resultados</h5>
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-hover table-sm mb-0">
                        <thead class="table-light">
                            <tr>
                                {% for key in results[0].keys() %}
                                <th>{{ key }}</th>
                                {% endfor %}
                            </tr>
                        </thead>
                        <tbody>
                            {% for row in results %}
                            <tr>
                                {% for key, value in row.items() %}
                                <td>
                                    {% if value is none %}
                                    <span class="text-muted">NULL</span>
                                    {% elif value is boolean %}
                                    <span class="badge bg-{{ 'success' if value else 'danger' }}">
                                        {{ 'Verdadero' if value else 'Falso' }}
                                    </span>
                                    {% else %}
                                    {{ value }}
                                    {% endif %}
                                </td>
                                {% endfor %}
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                <div class="card-footer text-muted">
                    {{ results|length }} filas encontradas
                </div>
            </div>
        </div>
        {% endif %}
    </div>
    {% endblock %}
    """
    
    # Template para la página de error
    error_template = """
    {% extends 'pgadmin/base.html' %}
    
    {% block title %}Error{% endblock %}
    
    {% block content %}
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card shadow">
                    <div class="card-header bg-danger text-white">
                        <h5 class="mb-0"><i class="fas fa-exclamation-triangle"></i> Error</h5>
                    </div>
                    <div class="card-body">
                        <p class="mb-0">{{ error }}</p>
                        
                        {% if table_name %}
                        <hr>
                        <p>Error al acceder a la tabla <strong>{{ table_name }}</strong>.</p>
                        {% endif %}
                        
                        <div class="mt-4">
                            <a href="{{ url_for('index') }}" class="btn btn-primary">
                                <i class="fas fa-home"></i> Volver al Inicio
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    """
    
    # Template base
    base_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{% block title %}PgAdmin{% endblock %} - {{ app_name }}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            .navbar-brand i {
                color: #13b5ea;
                margin-right: 0.5rem;
            }
            .bg-primary {
                background-color: #336791 !important;
            }
            .btn-primary {
                background-color: #336791;
                border-color: #336791;
            }
            .btn-primary:hover {
                background-color: #254a6a;
                border-color: #254a6a;
            }
            .navbar {
                background-color: #336791;
            }
            .table th {
                white-space: nowrap;
            }
            .bd-highlight {
                background-color: rgba(86, 61, 124, 0.05);
                border: 1px solid rgba(86, 61, 124, 0.15);
            }
            .icon-dashboard {
                font-size: 2rem;
                margin-bottom: 0.5rem;
            }
        </style>
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container-fluid">
                <a class="navbar-brand" href="{{ url_for('index') }}">
                    <i class="fas fa-database"></i> {{ app_name }}
                </a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('index') }}">
                                <i class="fas fa-table"></i> Tablas
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('execute_query') }}">
                                <i class="fas fa-terminal"></i> Consulta SQL
                            </a>
                        </li>
                    </ul>
                    
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item">
                            <a class="nav-link" href="/" target="_blank">
                                <i class="fas fa-arrow-left"></i> Volver a la Aplicación
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>

        <main>
            {% block content %}{% endblock %}
        </main>

        <footer class="mt-5 py-3 bg-white border-top">
            <div class="container text-center">
                <p class="text-muted mb-0">
                    <small>{{ app_name }} &copy; {{ current_year }}</small>
                </p>
            </div>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    templates = {
        'base.html': base_template,
        'index.html': index_template,
        'table.html': table_template,
        'query.html': query_template,
        'error.html': error_template
    }
    
    return jsonify(templates)

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5050, debug=True)