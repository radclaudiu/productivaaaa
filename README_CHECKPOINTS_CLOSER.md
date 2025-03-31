# Sistema de Cierre Automático de Fichajes

## Versión 1.1.0

Este módulo implementa un sistema para cerrar automáticamente los registros de fichajes pendientes cuando se encuentra fuera del horario de operación configurado para cada punto de fichaje.

## Características principales

- Cierre automático de fichajes pendientes al finalizar el horario de operación
- Registro detallado de actividades y operaciones realizadas
- Verificación del estado del sistema al inicio
- Configuración flexible por punto de fichaje
- Servicio instalable como daemon de sistema
- Ejecución manual disponible para operaciones puntuales

## Componentes del Sistema

El sistema está compuesto por los siguientes archivos:

- `scheduled_checkpoints_closer.py`: Servicio principal que ejecuta el cierre automático cada 10 minutos
- `close_operation_hours.py`: Lógica central para cerrar registros pendientes
- `run_checkpoint_closer.py`: Herramienta para ejecución manual única
- `install_checkpoint_closer_service.sh`: Script para instalar el servicio en el sistema

## Requisitos

- Python 3.6+
- Flask y SQLAlchemy
- Base de datos PostgreSQL
- Permisos de administrador para la instalación del servicio

## Instalación como Servicio

Para instalar el sistema como un servicio que se ejecuta automáticamente:

```bash
sudo bash install_checkpoint_closer_service.sh
```

El script realizará las siguientes operaciones:
1. Verificación de requisitos y acceso a la base de datos
2. Creación del archivo de servicio systemd
3. Configuración de logs y permisos
4. Activación e inicio del servicio
5. Verificación del funcionamiento

## Ejecución Manual

Si desea realizar una verificación manual única, puede ejecutar:

```bash
python run_checkpoint_closer.py
```

Este comando ejecutará una única verificación de todos los puntos de fichaje y cerrará los registros pendientes que estén fuera de horario.

## Logs y Monitorización

El sistema genera logs detallados en dos ubicaciones:

- **Logs del servicio**: `/var/log/checkpoints-closer.log`
- **Logs internos**: `./checkpoints_closer.log`

Los logs incluyen:
- Hora de inicio y fin de cada barrido
- Estadísticas detalladas de operaciones
- Errores y advertencias
- Verificación del estado del sistema

## Configuración de Puntos de Fichaje

Para que un punto de fichaje utilice este sistema, debe configurarlo con:

1. Horario de fin de operación (campo `operation_end_time`)
2. Activar la aplicación de horarios (campo `enforce_operation_hours = True`)

Estas configuraciones pueden realizarse desde el panel de administración web.

## Resolución de Problemas

Si el servicio no funciona correctamente, verifique:

1. **Logs del Sistema**: `sudo journalctl -u checkpoints-closer.service`
2. **Estado del Servicio**: `sudo systemctl status checkpoints-closer.service`
3. **Conexión a la Base de Datos**: Asegúrese de que la aplicación puede conectarse a la BD
4. **Permisos**: El servicio debe ejecutarse como `www-data` o el usuario adecuado

## Comandos Útiles

- **Ver Estado**: `sudo systemctl status checkpoints-closer.service`
- **Iniciar Servicio**: `sudo systemctl start checkpoints-closer.service`
- **Detener Servicio**: `sudo systemctl stop checkpoints-closer.service`
- **Reiniciar Servicio**: `sudo systemctl restart checkpoints-closer.service`
- **Ver Logs**: `sudo tail -f /var/log/checkpoints-closer.log`

## Funcionamiento Interno

El sistema realiza las siguientes operaciones en cada ciclo:

1. Busca todos los puntos de fichaje con horario de operación configurado
2. Para cada punto fuera de horario, identifica registros pendientes
3. Cierra automáticamente esos registros estableciendo la hora de salida
4. Registra una incidencia por cada cierre automático
5. Genera estadísticas de la operación

## Notas de Seguridad

- El sistema preserva los registros originales en campos separados
- Marca claramente los registros que han sido modificados automáticamente
- Registra cada cambio como una incidencia para auditoría