# Manual del Sistema de Backup y Restauración

## Introducción

El Sistema de Backup y Restauración proporciona una solución completa para gestionar copias de seguridad de la base de datos PostgreSQL de la aplicación. Este manual explica cómo usar el sistema, desde la creación de backups hasta la restauración de los mismos en caso de necesidad.

## Índice

1. [Acceso al Sistema](#acceso-al-sistema)
2. [Panel de Control](#panel-de-control)
3. [Creación de Backups](#creación-de-backups)
4. [Gestión de Backups](#gestión-de-backups)
5. [Restauración de Backups](#restauración-de-backups)
6. [Backups Programados](#backups-programados)
7. [Política de Retención](#política-de-retención)
8. [Solución de Problemas](#solución-de-problemas)

## Acceso al Sistema

Para acceder al Sistema de Backup y Restauración:

1. Inicie sesión en la aplicación con una cuenta de administrador
2. En el menú principal, haga clic en "Administración"
3. Seleccione "Gestión de Backups"

**Nota**: Solo los usuarios con permisos de administrador pueden acceder a esta funcionalidad.

## Panel de Control

El Panel de Control muestra una visión general del sistema de backup:

- **Estado de la Base de Datos**: Muestra información sobre la base de datos, incluyendo tamaño, versión de PostgreSQL y tablas más grandes.
- **Backups Disponibles**: Lista todos los backups existentes con información detallada.
- **Documentación**: Proporciona información útil sobre el funcionamiento del sistema.

## Creación de Backups

Para crear un nuevo backup:

1. Haga clic en el botón "Crear Backup" en el Panel de Control
2. Seleccione el tipo de backup:
   - **Completo**: Incluye estructura y datos (recomendado para restauraciones completas)
   - **Solo Esquema**: Incluye solo la estructura de la base de datos sin datos
3. Elija si desea comprimir el backup (recomendado para ahorrar espacio)
4. Añada una descripción opcional para identificar el backup
5. Haga clic en "Crear Backup"

El proceso puede tardar desde unos segundos hasta varios minutos, dependiendo del tamaño de la base de datos. Una vez completado, el backup aparecerá en la lista de backups disponibles.

## Gestión de Backups

Para cada backup disponible, puede realizar las siguientes acciones:

- **Ver Detalles**: Muestra información detallada sobre el backup
- **Descargar**: Descarga el archivo de backup a su dispositivo
- **Restaurar**: Inicia el proceso de restauración de la base de datos desde este backup
- **Eliminar**: Elimina permanentemente el archivo de backup

Para ver detalles o realizar estas acciones, haga clic en los botones correspondientes en la lista de backups.

## Restauración de Backups

**¡Advertencia!**: La restauración de un backup sobrescribirá todos los datos actuales en la base de datos. Esta acción no se puede deshacer.

Para restaurar un backup:

1. Localice el backup que desea restaurar en la lista de backups disponibles
2. Haga clic en el botón "Restaurar"
3. Lea cuidadosamente la información sobre las consecuencias de la restauración
4. Para confirmar, escriba "RESTAURAR" (en mayúsculas) en el campo de confirmación
5. Ingrese su contraseña de administrador para autorizar la operación
6. Haga clic en "Restaurar Backup"

El proceso de restauración puede tardar varios minutos. Durante este tiempo, la aplicación puede no estar disponible. Una vez completado, la base de datos contendrá los datos del backup seleccionado.

## Backups Programados

El sistema incluye la capacidad de realizar backups automáticos según una programación:

- Por defecto, los backups programados se ejecutan diariamente a las 3:00 AM
- Puede ejecutar un backup programado manualmente en cualquier momento haciendo clic en el botón "Ejecutar Backup Programado" en el Panel de Control

Para configurar o modificar la programación de backups:

1. Edite el archivo `backup_schedule.json` en el directorio raíz de la aplicación
2. Configure los parámetros según sus necesidades:
   - `enabled`: true/false para habilitar/deshabilitar backups programados
   - `frequency`: "daily", "weekly" o "monthly"
   - `time`: Hora de ejecución en formato HH:MM
   - `retention`: Configuración de retención para cada tipo de backup

Alternativamente, puede ejecutar el script de instalación del servicio:

```bash
./install_backup_service.sh
```

Este script configurará un cron job para ejecutar backups diarios automáticamente.

## Política de Retención

Para evitar un consumo excesivo de espacio en disco, el sistema aplica automáticamente una política de retención que conserva:

- Los últimos 7 backups diarios
- Los últimos 4 backups semanales
- Los últimos 3 backups mensuales

Los backups más antiguos se eliminan automáticamente cuando se alcanza el límite configurado.

Puede ajustar esta política modificando el archivo `backup_schedule.json` o los parámetros en el código de `backup_manager.py`.

## Solución de Problemas

### El backup tarda demasiado en crearse

Para bases de datos grandes, es normal que el proceso de backup tarde varios minutos. Si el proceso tarda excesivamente:

1. Verifique el espacio disponible en disco
2. Considere realizar el backup durante horas de baja actividad
3. Revise los logs en `backup_manager.log` para identificar posibles problemas

### Error al restaurar un backup

Si encuentra errores durante la restauración:

1. Verifique que el archivo de backup existe y no está corrupto
2. Asegúrese de que no hay conexiones activas a la base de datos durante la restauración
3. Revise los logs en `backup_manager.log` para obtener más detalles sobre el error

### Los backups programados no se ejecutan

Si los backups programados no se ejecutan automáticamente:

1. Ejecute `./check_backup_service.sh` para verificar el estado del servicio
2. Verifique que el cron job está correctamente configurado
3. Asegúrese de que el script tiene permisos de ejecución
4. Revise los logs en `scheduled_backup.log` para identificar posibles problemas

Para cualquier otro problema, contacte al administrador del sistema o consulte la documentación técnica del sistema de backup.