-- Script para crear las tablas del sistema de turnos
-- Este script crea las tablas para el sistema de gestión de turnos y horarios de empleados

-- Tipo de turno (enum)
CREATE TYPE tipo_turno AS ENUM ('MANANA', 'TARDE', 'NOCHE', 'COMPLETO', 'PERSONALIZADO');

-- Tipo de ausencia (enum)
CREATE TYPE tipo_ausencia AS ENUM ('VACACIONES', 'BAJA_MEDICA', 'PERMISO', 'ASUNTOS_PROPIOS', 'OTRO');

-- Tabla de turnos
CREATE TABLE IF NOT EXISTS turnos_turno (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    tipo tipo_turno NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    color VARCHAR(7) NOT NULL DEFAULT '#3498db',
    descripcion TEXT,
    descanso_inicio TIME,
    descanso_fin TIME,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Tabla de horarios asignados
CREATE TABLE IF NOT EXISTS turnos_horario (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    notas TEXT,
    turno_id INTEGER NOT NULL REFERENCES turnos_turno(id),
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Tabla de ausencias
CREATE TABLE IF NOT EXISTS turnos_ausencia (
    id SERIAL PRIMARY KEY,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    tipo tipo_ausencia NOT NULL,
    motivo TEXT,
    aprobado BOOLEAN NOT NULL DEFAULT FALSE,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    aprobado_por_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Tabla de requisitos de personal
CREATE TABLE IF NOT EXISTS turnos_requisito_personal (
    id SERIAL PRIMARY KEY,
    dia_semana INTEGER NOT NULL, -- 0-6 (lunes a domingo)
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    num_empleados INTEGER NOT NULL DEFAULT 1,
    notas TEXT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Tabla de plantillas de horario
CREATE TABLE IF NOT EXISTS turnos_plantilla_horario (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Tabla de detalles de plantilla
CREATE TABLE IF NOT EXISTS turnos_detalle_plantilla (
    id SERIAL PRIMARY KEY,
    dia_semana INTEGER NOT NULL, -- 0-6 (lunes a domingo)
    plantilla_id INTEGER NOT NULL REFERENCES turnos_plantilla_horario(id),
    turno_id INTEGER NOT NULL REFERENCES turnos_turno(id)
);

-- Tabla de asignación de plantillas
CREATE TABLE IF NOT EXISTS turnos_asignacion_plantilla (
    id SERIAL PRIMARY KEY,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    plantilla_id INTEGER NOT NULL REFERENCES turnos_plantilla_horario(id),
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Tabla de preferencias de disponibilidad
CREATE TABLE IF NOT EXISTS turnos_preferencia_disponibilidad (
    id SERIAL PRIMARY KEY,
    dia_semana INTEGER NOT NULL, -- 0-6 (lunes a domingo)
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    preferencia INTEGER NOT NULL DEFAULT 0, -- -1: No disponible, 0: Neutro, 1: Preferido
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Tabla de historial de cambios
CREATE TABLE IF NOT EXISTS turnos_historial_cambios (
    id SERIAL PRIMARY KEY,
    fecha_cambio TIMESTAMP NOT NULL DEFAULT NOW(),
    tipo_cambio VARCHAR(50) NOT NULL, -- "creacion", "modificacion", "eliminacion"
    descripcion TEXT NOT NULL,
    horario_id INTEGER REFERENCES turnos_horario(id),
    user_id INTEGER NOT NULL REFERENCES users(id)
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_turno_company ON turnos_turno(company_id);
CREATE INDEX IF NOT EXISTS idx_horario_employee ON turnos_horario(employee_id);
CREATE INDEX IF NOT EXISTS idx_horario_turno ON turnos_horario(turno_id);
CREATE INDEX IF NOT EXISTS idx_horario_fecha ON turnos_horario(fecha);
CREATE INDEX IF NOT EXISTS idx_ausencia_employee ON turnos_ausencia(employee_id);
CREATE INDEX IF NOT EXISTS idx_ausencia_fechas ON turnos_ausencia(fecha_inicio, fecha_fin);
CREATE INDEX IF NOT EXISTS idx_plantilla_company ON turnos_plantilla_horario(company_id);
CREATE INDEX IF NOT EXISTS idx_detalle_plantilla ON turnos_detalle_plantilla(plantilla_id);
CREATE INDEX IF NOT EXISTS idx_asignacion_employee ON turnos_asignacion_plantilla(employee_id);
CREATE INDEX IF NOT EXISTS idx_preferencia_employee ON turnos_preferencia_disponibilidad(employee_id);
CREATE INDEX IF NOT EXISTS idx_historial_user ON turnos_historial_cambios(user_id);

-- Crear turnos de ejemplo para cada empresa
INSERT INTO turnos_turno (nombre, tipo, hora_inicio, hora_fin, color, descanso_inicio, descanso_fin, descripcion, company_id)
SELECT 'Mañana', 'MANANA', '08:00', '16:00', '#28a745', '13:00', '14:00', 'Turno de mañana con 1 hora de descanso', id
FROM companies
WHERE is_active = TRUE
AND NOT EXISTS (
    SELECT 1 FROM turnos_turno WHERE nombre = 'Mañana' AND company_id = companies.id
);

INSERT INTO turnos_turno (nombre, tipo, hora_inicio, hora_fin, color, descanso_inicio, descanso_fin, descripcion, company_id)
SELECT 'Tarde', 'TARDE', '16:00', '00:00', '#007bff', '20:00', '21:00', 'Turno de tarde con 1 hora de descanso', id
FROM companies
WHERE is_active = TRUE
AND NOT EXISTS (
    SELECT 1 FROM turnos_turno WHERE nombre = 'Tarde' AND company_id = companies.id
);

INSERT INTO turnos_turno (nombre, tipo, hora_inicio, hora_fin, color, descanso_inicio, descanso_fin, descripcion, company_id)
SELECT 'Noche', 'NOCHE', '00:00', '08:00', '#6f42c1', '04:00', '04:30', 'Turno de noche con 30 minutos de descanso', id
FROM companies
WHERE is_active = TRUE
AND NOT EXISTS (
    SELECT 1 FROM turnos_turno WHERE nombre = 'Noche' AND company_id = companies.id
);

INSERT INTO turnos_turno (nombre, tipo, hora_inicio, hora_fin, color, descripcion, company_id)
SELECT 'Media Jornada', 'PERSONALIZADO', '09:00', '13:00', '#fd7e14', 'Turno de media jornada sin descanso', id
FROM companies
WHERE is_active = TRUE
AND NOT EXISTS (
    SELECT 1 FROM turnos_turno WHERE nombre = 'Media Jornada' AND company_id = companies.id
);