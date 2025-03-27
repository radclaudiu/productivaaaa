# Documentación de la API de Tareas

## Descripción General

Esta API proporciona acceso a los datos de tareas almacenados en una base de datos PostgreSQL.
La API está construida con Flask y utiliza SQLAlchemy como ORM para la interacción con la base de datos.

## Configuración de la Base de Datos PostgreSQL

La conexión a PostgreSQL se configura a través de la variable de entorno `DATABASE_URL` con el siguiente formato:

```
postgresql://usuario:contraseña@host:puerto/nombre_base_datos
```

En el archivo `config.py`, la conexión a la base de datos se configura así:

```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_recycle": 120,
    "pool_pre_ping": True,
    "pool_size": 20,
    "max_overflow": 15,
    "pool_timeout": 15,
    "connect_args": {
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
    "echo": False,
    "echo_pool": False,
}
```

Esta configuración asegura que:
- Las conexiones se reciclan cada 2 minutos
- Se verifica la conexión antes de usarla
- Se mantiene un pool de 20 conexiones
- Se establece un tiempo de espera para las conexiones
- Se activan los keepalives para mantener las conexiones abiertas

## Modelo de Datos

El modelo de datos para las tareas incluye los siguientes campos:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | Clave primaria |
| title | String | Título de la tarea |
| description | Text | Descripción detallada |
| priority | String | Prioridad (baja, media, alta, urgente) |
| frequency | String | Frecuencia (diaria, semanal, mensual, etc.) |
| status | String | Estado (pendiente, completada, vencida, cancelada) |
| start_date | Date | Fecha de inicio (puede ser nulo) |
| end_date | Date | Fecha de fin (puede ser nulo) |
| created_at | DateTime | Fecha y hora de creación |
| updated_at | DateTime | Fecha y hora de última actualización |

## Endpoints de la API

### 1. Listar todas las tareas

**Endpoint:** `/api/tasks`
**Método:** GET
**Descripción:** Devuelve una lista de todas las tareas.

**Ejemplo de respuesta:**
```json
{
  "status": "success",
  "count": 5,
  "tasks": [
    {
      "id": 1,
      "title": "Revisar inventario",
      "description": "Realizar un conteo completo del inventario de productos.",
      "priority": "alta",
      "frequency": "semanal",
      "status": "pendiente",
      "start_date": "2025-03-27",
      "end_date": "2025-04-26",
      "created_at": "2025-03-27T10:00:00",
      "updated_at": "2025-03-27T10:00:00"
    },
    // ... más tareas
  ]
}
```

### 2. Obtener una tarea específica

**Endpoint:** `/api/tasks/<id>`
**Método:** GET
**Descripción:** Devuelve los detalles de una tarea específica.

**Parámetros de ruta:**
- `id`: ID de la tarea (entero)

**Ejemplo de respuesta:**
```json
{
  "status": "success",
  "task": {
    "id": 1,
    "title": "Revisar inventario",
    "description": "Realizar un conteo completo del inventario de productos.",
    "priority": "alta",
    "frequency": "semanal",
    "status": "pendiente",
    "start_date": "2025-03-27",
    "end_date": "2025-04-26",
    "created_at": "2025-03-27T10:00:00",
    "updated_at": "2025-03-27T10:00:00"
  }
}
```

### 3. Obtener tareas de un portal externo

**Endpoint:** `/api/external/portal/<portal_id>`
**Método:** GET
**Descripción:** Obtiene tareas desde un portal externo específico como https://productiva.replit.app.

**Parámetros de ruta:**
- `portal_id`: ID del portal externo (entero)

**IMPORTANTE:** Para usar este endpoint desde tu aplicación Android, debes usar la URL completa con el nombre real de tu aplicación en Replit:

```
https://NOMBRE-DE-TU-REPL.replit.app/api/external/portal/1
```

Donde `NOMBRE-DE-TU-REPL` debe ser sustituido por el nombre real de tu aplicación en Replit.

**Ejemplo de respuesta (cuando el portal externo devuelve JSON):**
```json
{
  "status": "success",
  "source": "https://productiva.replit.app/tasks/portal/1",
  "data": {
    // Datos del portal externo en formato JSON
  }
}
```

**Ejemplo de respuesta (cuando el portal externo no devuelve JSON):**
```json
{
  "status": "success",
  "source": "https://productiva.replit.app/tasks/portal/1",
  "data": {
    "content": "...", // Contenido HTML/texto del portal externo
    "content_type": "text/html"
  }
}
```

**Ejemplo de respuesta (cuando hay un error):**
```json
{
  "status": "error",
  "source": "https://productiva.replit.app/tasks/portal/1",
  "code": 404,
  "message": "Error al conectar con el portal externo: Not Found"
}
```

## Manejo de Errores

La API devuelve los siguientes códigos de estado HTTP:

- `200 OK`: Solicitud exitosa
- `404 Not Found`: El recurso solicitado no existe
- `500 Internal Server Error`: Error del servidor

Ejemplo de respuesta de error:
```json
{
  "error": "Tarea con ID 999 no encontrada"
}
```

## Fechas y Horas

Todas las fechas y horas se formatean como cadenas ISO 8601:
- Fechas: `YYYY-MM-DD`
- Fechas y horas: `YYYY-MM-DDTHH:MM:SS`

## Datos de Ejemplo

Para crear datos de ejemplo, ejecute el script `create_sample_api_tasks.py`:

```bash
python create_sample_api_tasks.py
```

Este script creará 5 tareas de ejemplo en la base de datos si la tabla está vacía.