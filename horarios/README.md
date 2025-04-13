# Módulo de Horarios

Este módulo proporciona una aplicación moderna para gestionar horarios de empleados con una interfaz visual de cuadrícula semanal.

## Estructura del Proyecto

```
horarios/
├── client/                   # Frontend en React/TypeScript
│   ├── public/               # Archivos estáticos
│   └── src/                  # Código fuente React
│       └── components/       # Componentes React
├── server/                   # Lógica del servidor
└── shared/                   # Definiciones compartidas
    └── schema.ts             # Modelos y tipos
```

## Características Principales

- **Vista de Cuadrícula Semanal**: Interfaz visual que muestra días en columnas y empleados en filas.
- **Selección con Click/Drag**: Permite seleccionar múltiples slots horarios mediante arrastre.
- **Horarios Publicados/Borradores**: Los horarios pueden estar en estado borrador o publicados.
- **Validación de Reglas**: Control de horas contratadas, descansos y turnos máximos.
- **Plantillas de Horarios**: Reutilización de patrones de horarios comunes.
- **Notificaciones**: Avisos a empleados sobre cambios en los horarios.

## Integración con el Sistema Principal

El módulo de horarios se integra con el sistema principal mediante:

1. Blueprint de Flask que sirve la aplicación y expone API REST
2. Puntos de conexión para sincronizar datos de empleados
3. Sistema de autenticación compartido con el módulo principal

## Próximas Mejoras

- Implementación de la visualización de disponibilidad de empleados
- Sistema de solicitud de cambios por parte de los empleados
- Estadísticas y reportes de cumplimiento de horarios
- Exportación a Excel/PDF de los horarios semanales
- Vista móvil optimizada para consulta de horarios personales

## Desarrollo

### Frontend

El frontend está desarrollado con:

- React 18
- TypeScript
- React Router
- Bootstrap 5

### Backend 

El backend utiliza:

- Flask como framework web
- SQLAlchemy para la capa de acceso a datos
- PostgreSQL como base de datos