-- SQL Script para adaptar la estructura de horarios al sistema existente
-- Este script es compatible con los modelos ya creados en models_horarios.py

-- Verificar si las tablas ya existen
DO $$
BEGIN
    -- Evitamos crear tablas si ya existen
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'schedule') THEN
        -- Tabla de horarios (compatible con Schedule en models_horarios.py)
        CREATE TABLE schedule (
            id SERIAL PRIMARY KEY,
            name VARCHAR(128) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            published BOOLEAN DEFAULT FALSE,
            company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
        );
        
        -- Índice para búsquedas de horarios por empresa
        CREATE INDEX idx_schedule_company ON schedule(company_id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'schedule_assignment') THEN
        -- Tabla de asignaciones de horario (compatible con ScheduleAssignment en models_horarios.py)
        CREATE TABLE schedule_assignment (
            id SERIAL PRIMARY KEY,
            schedule_id INTEGER NOT NULL REFERENCES schedule(id) ON DELETE CASCADE,
            employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            day DATE NOT NULL,
            start_time VARCHAR(5) NOT NULL, -- Formato "HH:MM"
            end_time VARCHAR(5) NOT NULL,   -- Formato "HH:MM"
            break_duration INTEGER DEFAULT 0, -- Duración del descanso en minutos
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
        );
        
        -- Índices para búsquedas de asignaciones
        CREATE INDEX idx_assignment_schedule ON schedule_assignment(schedule_id);
        CREATE INDEX idx_assignment_employee ON schedule_assignment(employee_id);
        CREATE INDEX idx_assignment_day ON schedule_assignment(day);
    END IF;

    -- Tablas adicionales para funcionalidades extendidas de horarios

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'schedule_template') THEN
        -- Tabla de plantillas de horario
        CREATE TABLE schedule_template (
            id SERIAL PRIMARY KEY,
            name VARCHAR(128) NOT NULL,
            description TEXT,
            is_default BOOLEAN DEFAULT FALSE,
            start_hour INTEGER NOT NULL DEFAULT 8,
            end_hour INTEGER NOT NULL DEFAULT 20,
            time_increment INTEGER NOT NULL DEFAULT 15, -- Incrementos en minutos (15, 30, 60)
            company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
        );
        
        -- Índice para plantillas por empresa
        CREATE INDEX idx_template_company ON schedule_template(company_id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'employee_availability') THEN
        -- Tabla de disponibilidad de empleados
        CREATE TABLE employee_availability (
            id SERIAL PRIMARY KEY,
            employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            day_of_week INTEGER NOT NULL, -- 0-6 (Lunes a Domingo)
            start_time VARCHAR(5) NOT NULL, -- Formato "HH:MM"
            end_time VARCHAR(5) NOT NULL,   -- Formato "HH:MM"
            is_available BOOLEAN DEFAULT TRUE,
            notes TEXT,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
            UNIQUE(employee_id, day_of_week, start_time, end_time)
        );
        
        -- Índice para búsquedas de disponibilidad
        CREATE INDEX idx_availability_employee ON employee_availability(employee_id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'schedule_rule') THEN
        -- Tabla de reglas para horarios (horas máximas, descansos mínimos, etc.)
        CREATE TABLE schedule_rule (
            id SERIAL PRIMARY KEY,
            name VARCHAR(128) NOT NULL,
            description TEXT,
            company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
            max_hours_per_day INTEGER DEFAULT 8,
            max_hours_per_week INTEGER DEFAULT 40,
            min_break_duration INTEGER DEFAULT 30, -- En minutos
            min_time_between_shifts INTEGER DEFAULT 720, -- En minutos (12 horas por defecto)
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
        );
        
        -- Índice para reglas por empresa
        CREATE INDEX idx_rule_company ON schedule_rule(company_id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'schedule_request') THEN
        -- Tabla de solicitudes de cambio de horario
        CREATE TABLE schedule_request (
            id SERIAL PRIMARY KEY,
            employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            assignment_id INTEGER REFERENCES schedule_assignment(id) ON DELETE SET NULL,
            request_type VARCHAR(20) NOT NULL, -- 'time_off', 'shift_change', 'swap'
            start_date DATE NOT NULL,
            end_date DATE,
            start_time VARCHAR(5),
            end_time VARCHAR(5),
            reason TEXT,
            status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
            reviewed_by INTEGER REFERENCES users(id),
            reviewed_at TIMESTAMP WITHOUT TIME ZONE,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
        );
        
        -- Índices para solicitudes
        CREATE INDEX idx_request_employee ON schedule_request(employee_id);
        CREATE INDEX idx_request_status ON schedule_request(status);
    END IF;

    RAISE NOTICE 'Estructura de tablas para el módulo de horarios creada o verificada correctamente.';
END;
$$;