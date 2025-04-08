# Documentación Técnica del Sistema de Backup y Restauración

## Arquitectura del Sistema

El Sistema de Backup y Restauración está diseñado como un módulo independiente que se integra con la aplicación principal. La arquitectura se compone de los siguientes componentes:

### Componentes Principales

1. **Módulo de Gestión de Backups (`backup_manager.py`)**: 
   - Núcleo del sistema que proporciona todas las funciones de backup y restauración
   - Interfaz para crear, listar, eliminar y restaurar backups
   - Gestión de metadatos y políticas de retención

2. **Rutas Web (`routes_backup.py`)**:
   - Endpoints HTTP para interactuar con el sistema a través de la interfaz web
   - Manejo de formularios y validación de datos
   - Controles de autenticación y autorización

3. **Formularios (`forms_backup.py`)**:
   - Definiciones de formularios WTForms para la interfaz de usuario
   - Validación de entrada de datos

4. **Plantillas HTML (`templates/backup/*.html`)**:
   - Interfaz de usuario para interactuar con el sistema
   - Visualización de datos y estadísticas

5. **Sistema de Programación (`scheduled_backup.py`)**:
   - Ejecuta backups automáticos según la programación configurada
   - Aplica políticas de retención para gestionar el espacio en disco

6. **Scripts de Servicio**:
   - `install_backup_service.sh`: Configura el servicio de backups automáticos
   - `check_backup_service.sh`: Verifica el estado del servicio

### Flujo de Datos

```
Usuario → Interfaz Web → Rutas → Módulo de Gestión → PostgreSQL
                                        ↑
                                        ↓
                                Sistema de Archivos
                                (almacenamiento de backups)
```

## Estructura de Directorios

```
/
├── backup_manager.py           # Módulo principal de gestión
├── routes_backup.py            # Rutas web para la interfaz
├── forms_backup.py             # Definiciones de formularios
├── scheduled_backup.py         # Sistema de programación
├── install_backup_service.sh   # Script de instalación
├── check_backup_service.sh     # Script de verificación
├── backup_schedule.json        # Configuración de programación
├── backups/                    # Directorio de almacenamiento
│   ├── backup_metadata.json    # Metadatos de backups
│   └── backup_*.sql[.gz]       # Archivos de backup
├── docs/                       # Documentación
│   ├── backup_manual.md        # Manual de usuario
│   └── backup_technical.md     # Documentación técnica
└── templates/backup/           # Plantillas HTML
    ├── dashboard.html          # Panel principal
    ├── create.html             # Creación de backups
    ├── view.html               # Detalles de backup
    └── restore.html            # Restauración de backup
```

## Formato de Archivos y Metadatos

### Archivos de Backup

Los archivos de backup siguen la siguiente convención de nombres:

```
backup_{tipo}_{fecha}_{hora}.sql[.gz]
```

Donde:
- `tipo`: "full" (completo) o "schema" (solo esquema)
- `fecha`: Formato YYYYMMDD
- `hora`: Formato HHMMSS
- `.gz`: Presente si el archivo está comprimido

### Metadatos

Los metadatos de los backups se almacenan en `backups/backup_metadata.json` con la siguiente estructura:

```json
{
  "backups": [
    {
      "id": "20250408_160000",
      "filename": "backup_full_20250408_160000.sql.gz",
      "path": "/path/to/backups/backup_full_20250408_160000.sql.gz",
      "type": "full",
      "compressed": true,
      "size": 12345678,
      "date": "2025-04-08 16:00:00",
      "description": "Backup completo creado el 2025-04-08 16:00:00",
      "database": "nombre_db"
    },
    // ... más backups
  ]
}
```

### Configuración de Programación

La configuración de backups programados se almacena en `backup_schedule.json`:

```json
{
  "enabled": true,
  "frequency": "daily",
  "time": "03:00",
  "retention": {
    "daily": 7,
    "weekly": 4,
    "monthly": 3
  },
  "last_run": "2025-04-08 03:00:00",
  "next_run": "2025-04-09 03:00:00"
}
```

## API del Módulo de Gestión

El módulo `backup_manager.py` proporciona las siguientes funciones principales:

### `create_backup(tipo='full', compress=True, description=None)`

Crea un nuevo backup de la base de datos.

- **Parámetros**:
  - `tipo` (str): Tipo de backup ('full' o 'schema')
  - `compress` (bool): Si se debe comprimir el backup
  - `description` (str): Descripción opcional del backup
  
- **Retorna**:
  - `dict`: Información sobre el backup creado o None si hubo error

### `get_all_backups()`

Obtiene la lista de todos los backups disponibles.

- **Retorna**:
  - `list`: Lista de metadatos de backups ordenados por fecha (más reciente primero)

### `restore_backup(backup_id)`

Restaura la base de datos desde un backup.

- **Parámetros**:
  - `backup_id` (str): ID del backup a restaurar
  
- **Retorna**:
  - `dict`: Resultado de la operación con los campos 'success' y 'message'

### `delete_backup(backup_id)`

Elimina un backup específico.

- **Parámetros**:
  - `backup_id` (str): ID del backup a eliminar
  
- **Retorna**:
  - `bool`: True si se eliminó correctamente, False en caso contrario

### `apply_retention_policy(daily_keep=7, weekly_keep=4, monthly_keep=3)`

Aplica la política de retención para eliminar backups antiguos.

- **Parámetros**:
  - `daily_keep` (int): Número de backups diarios a conservar
  - `weekly_keep` (int): Número de backups semanales a conservar
  - `monthly_keep` (int): Número de backups mensuales a conservar
  
- **Retorna**:
  - `int`: Número de backups eliminados

### `check_database_status()`

Verifica el estado de la base de datos.

- **Retorna**:
  - `dict`: Estado de la base de datos con información de versión, tamaño, etc.

## Flujos de Trabajo

### Creación de Backup

1. Usuario solicita crear un backup a través de la interfaz
2. Aplicación valida los parámetros de entrada
3. Se llama a `backup_manager.create_backup()`
4. Se ejecuta `pg_dump` para crear el archivo SQL
5. Si se solicita compresión, se comprime el archivo
6. Se guardan los metadatos en `backup_metadata.json`
7. Se muestra confirmación al usuario

### Restauración de Backup

1. Usuario solicita restaurar un backup a través de la interfaz
2. Aplicación muestra pantalla de confirmación y validación
3. Usuario confirma escribiendo "RESTAURAR" e ingresando contraseña
4. Se llama a `backup_manager.restore_backup()`
5. Se descomprime el archivo si es necesario
6. Se ejecuta `psql` para restaurar la base de datos
7. Se muestra resultado al usuario

### Backup Programado

1. Cron job ejecuta `scheduled_backup.py` según programación
2. Script verifica si debe ejecutarse según configuración
3. Se llama a `backup_manager.run_scheduled_backup()`
4. Se crea el backup y se guardan metadatos
5. Se aplica política de retención
6. Se actualiza `last_run` y `next_run` en la configuración

## Seguridad

El sistema implementa las siguientes medidas de seguridad:

1. **Control de Acceso**: Solo usuarios administradores pueden acceder al sistema
2. **Autenticación de Operaciones Críticas**: Se requiere contraseña para restaurar o eliminar backups
3. **Confirmación Explícita**: Para restaurar, se requiere escribir "RESTAURAR" para confirmar
4. **Logs Detallados**: Se registran todas las operaciones en archivos de log

## Extensibilidad

El sistema está diseñado para ser extensible:

1. **Nuevos Tipos de Backup**: Se pueden añadir nuevos tipos modificando `backup_manager.py`
2. **Destinos Alternativos**: El sistema podría extenderse para almacenar backups en servicios como AWS S3
3. **Programación Avanzada**: Se podría integrar APScheduler para una programación más flexible
4. **Notificaciones**: Se podría añadir un sistema de notificaciones por email o SMS

## Limitaciones Conocidas

1. **Tamaño de Base de Datos**: Para bases de datos muy grandes (>10GB), el proceso puede consumir mucha memoria
2. **Dependencia de PostgreSQL**: El sistema depende de las herramientas `pg_dump` y `psql`
3. **Sin Restauración Parcial**: Actualmente no se soporta restaurar solo tablas específicas
4. **Concurrencia**: No se manejan múltiples operaciones de backup/restauración simultáneas

## Guía de Solución de Problemas para Desarrolladores

### Error en la Creación de Backups

```python
# Verificar permisos y rutas
import os
backup_dir = os.path.join(os.getcwd(), 'backups')
print(f"Directorio existe: {os.path.exists(backup_dir)}")
print(f"Permisos de escritura: {os.access(backup_dir, os.W_OK)}")

# Verificar conexión a la base de datos
import psycopg2
from config import Config
db_url = Config.SQLALCHEMY_DATABASE_URI
try:
    conn = psycopg2.connect(db_url)
    print("Conexión exitosa")
    conn.close()
except Exception as e:
    print(f"Error de conexión: {str(e)}")
```

### Error en la Restauración

```python
# Verificar disponibilidad de archivos
import os
backup_path = "/path/to/backup.sql.gz"
print(f"Archivo existe: {os.path.exists(backup_path)}")
print(f"Tamaño: {os.path.getsize(backup_path) if os.path.exists(backup_path) else 'N/A'}")

# Verificar permisos de PostgreSQL
import subprocess
try:
    result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
    print(f"psql version: {result.stdout}")
except Exception as e:
    print(f"Error ejecutando psql: {str(e)}")
```

## Futuras Mejoras

1. **Restauración Selectiva**: Permitir restaurar solo tablas o esquemas específicos
2. **Cifrado de Backups**: Añadir cifrado para backups sensibles
3. **Interfaz de Programación Mejorada**: Añadir interfaz web para configurar backups programados
4. **Integración con Almacenamiento en la Nube**: Soporte para AWS S3, Google Cloud Storage, etc.
5. **Verificación de Integridad**: Validación automática de los backups después de crearlos