
# Sistema de Control de Fichajes y Tareas

Sistema web para gestionar fichajes de empleados y tareas de mantenimiento, con las siguientes características:

- Gestión de fichajes de entrada/salida
- Control de horarios de operación
- Gestión de tareas y etiquetas
- Administración de empleados y locales
- Reportes y estadísticas

## Configuración Inicial

1. Crear usuario administrador:
```bash
python create_admin.py
```

2. Configurar la base de datos:
```bash
python migrate.py
```

3. Iniciar la aplicación:
```bash
python main.py
```

## Tecnologías

- Python/Flask
- PostgreSQL
- Bootstrap
- Gunicorn

## Licencia

MIT License
