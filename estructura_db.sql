-- Archivo estructura_db.sql
-- Script para actualizar las tablas con nuevas funciones

-- Añadir campos adicionales a la tabla de empleados si no existen
DO $$
BEGIN
    -- Campo para foto de perfil
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'employees' AND column_name = 'profile_photo_path') THEN
        ALTER TABLE employees ADD COLUMN profile_photo_path VARCHAR(256);
    END IF;
    
    -- Campo para horas laborales semanales
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'employees' AND column_name = 'weekly_hours') THEN
        ALTER TABLE employees ADD COLUMN weekly_hours DECIMAL(5,2) DEFAULT 40.00;
    END IF;
    
    -- Campo para salario base
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'employees' AND column_name = 'base_salary') THEN
        ALTER TABLE employees ADD COLUMN base_salary DECIMAL(10,2);
    END IF;
    
    -- Campo para departamento
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'employees' AND column_name = 'department') THEN
        ALTER TABLE employees ADD COLUMN department VARCHAR(64);
    END IF;
END
$$;

-- Crear tabla para gestión de vacaciones si no existe
CREATE TABLE IF NOT EXISTS employee_vacations (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'REGISTRADA',
    approved_by_id INTEGER REFERENCES users(id),
    approved_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    year INTEGER NOT NULL,
    days_count INTEGER NOT NULL
);

-- Crear tabla para registro de horas extras si no existe
CREATE TABLE IF NOT EXISTS overtime_records (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    hours DECIMAL(5,2) NOT NULL,
    reason TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    approved_by_id INTEGER REFERENCES users(id),
    approved_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla para departamentos si no existe
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    description TEXT,
    manager_id INTEGER REFERENCES employees(id),
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Crear tabla para ausencias (enfermedades, permisos, etc.) si no existe
CREATE TABLE IF NOT EXISTS employee_absences (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    type VARCHAR(30) NOT NULL, -- ENFERMEDAD, PERMISO, PERSONAL, etc.
    documentation_path VARCHAR(256),
    notes TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'REGISTRADA',
    approved_by_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla para gestión de documentos de empresa si no existe
CREATE TABLE IF NOT EXISTS company_documents (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name VARCHAR(128) NOT NULL,
    description TEXT,
    file_path VARCHAR(256) NOT NULL,
    file_type VARCHAR(64),
    file_size INTEGER,
    uploaded_by_id INTEGER REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Crear tabla para evaluaciones de desempeño si no existe
CREATE TABLE IF NOT EXISTS performance_reviews (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    reviewer_id INTEGER NOT NULL REFERENCES users(id),
    review_date DATE NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    score INTEGER,
    comments TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'BORRADOR',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla para objetivos de empleados si no existe
CREATE TABLE IF NOT EXISTS employee_goals (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    title VARCHAR(128) NOT NULL,
    description TEXT,
    start_date DATE,
    target_date DATE,
    completed_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    progress INTEGER DEFAULT 0,
    created_by_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear o reemplazar la función para calcular horas trabajadas
CREATE OR REPLACE FUNCTION calculate_employee_worked_hours(
    p_employee_id INTEGER,
    p_start_date DATE,
    p_end_date DATE
) RETURNS TABLE (
    date DATE,
    hours_worked DECIMAL(5,2),
    is_complete BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        DATE(ci.check_in_time) AS date,
        CASE 
            WHEN ci.check_out_time IS NOT NULL THEN
                ROUND(EXTRACT(EPOCH FROM (ci.check_out_time - ci.check_in_time))/3600, 2)
            ELSE
                0.00
        END AS hours_worked,
        ci.check_out_time IS NOT NULL AS is_complete
    FROM 
        employee_check_ins ci
    WHERE 
        ci.employee_id = p_employee_id AND
        DATE(ci.check_in_time) BETWEEN p_start_date AND p_end_date
    ORDER BY 
        date;
END;
$$ LANGUAGE plpgsql;

-- Crear o reemplazar función para obtener el total de horas trabajadas por mes
CREATE OR REPLACE FUNCTION get_monthly_hours(
    p_employee_id INTEGER,
    p_year INTEGER,
    p_month INTEGER
) RETURNS DECIMAL(5,2) AS $$
DECLARE
    total_hours DECIMAL(5,2) := 0;
    start_date DATE;
    end_date DATE;
BEGIN
    -- Establecer el rango de fechas para el mes
    start_date := make_date(p_year, p_month, 1);
    end_date := (start_date + INTERVAL '1 month' - INTERVAL '1 day')::DATE;
    
    -- Calcular el total de horas para ese mes
    SELECT COALESCE(SUM(hours_worked), 0)
    INTO total_hours
    FROM calculate_employee_worked_hours(p_employee_id, start_date, end_date);
    
    RETURN total_hours;
END;
$$ LANGUAGE plpgsql;

-- Crear o reemplazar función para verificar ausencias de empleados
CREATE OR REPLACE FUNCTION check_employee_absence(
    p_employee_id INTEGER,
    p_date DATE
) RETURNS BOOLEAN AS $$
DECLARE
    is_absent BOOLEAN := FALSE;
BEGIN
    -- Comprobar si hay registro de ausencia para esa fecha
    SELECT EXISTS(
        SELECT 1 
        FROM employee_absences 
        WHERE employee_id = p_employee_id 
        AND p_date BETWEEN start_date AND end_date
    ) INTO is_absent;
    
    -- Comprobar también si hay vacaciones registradas
    IF NOT is_absent THEN
        SELECT EXISTS(
            SELECT 1 
            FROM employee_vacations 
            WHERE employee_id = p_employee_id 
            AND p_date BETWEEN start_date AND end_date
            AND status = 'DISFRUTADA'
        ) INTO is_absent;
    END IF;
    
    RETURN is_absent;
END;
$$ LANGUAGE plpgsql;

-- Crear índices para optimizar consultas
DO $$
BEGIN
    -- Índice para búsquedas por fecha en check_ins
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_check_ins_date') THEN
        CREATE INDEX idx_check_ins_date ON employee_check_ins(check_in_time);
    END IF;
    
    -- Índice para búsquedas de empleados por empresa
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_employees_company') THEN
        CREATE INDEX idx_employees_company ON employees(company_id);
    END IF;
    
    -- Índice para búsquedas de vacaciones por empleado y año
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_vacations_employee_year') THEN
        CREATE INDEX idx_vacations_employee_year ON employee_vacations(employee_id, year);
    END IF;
END
$$;