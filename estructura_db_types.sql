-- Crear tipos enumerados para la aplicación
-- Tipos de usuario
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
        CREATE TYPE userrole AS ENUM ('ADMIN', 'GERENTE', 'EMPLEADO');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE user_role AS ENUM ('admin', 'gerente', 'empleado');
    END IF;
    
    -- Tipos de contrato
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contracttype') THEN
        CREATE TYPE contracttype AS ENUM ('INDEFINIDO', 'TEMPORAL', 'PRACTICAS', 'FORMACION', 'OBRA');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contract_type') THEN
        CREATE TYPE contract_type AS ENUM ('INDEFINIDO', 'TEMPORAL', 'PRACTICAS', 'FORMACION', 'OBRA');
    END IF;
    
    -- Estado de empleado
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'employeestatus') THEN
        CREATE TYPE employeestatus AS ENUM ('ACTIVO', 'BAJA_MEDICA', 'EXCEDENCIA', 'VACACIONES', 'INACTIVO');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'employee_status') THEN
        CREATE TYPE employee_status AS ENUM ('activo', 'baja_medica', 'excedencia', 'vacaciones', 'inactivo');
    END IF;
    
    -- Días de la semana
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'weekday') THEN
        CREATE TYPE weekday AS ENUM ('LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'week_day') THEN
        CREATE TYPE week_day AS ENUM ('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo');
    END IF;
    
    -- Estado de vacaciones
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'vacationstatus') THEN
        CREATE TYPE vacationstatus AS ENUM ('REGISTRADA', 'DISFRUTADA');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'vacation_status') THEN
        CREATE TYPE vacation_status AS ENUM ('REGISTRADA', 'DISFRUTADA');
    END IF;
    
    -- Tipos de tareas
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'taskpriority') THEN
        CREATE TYPE taskpriority AS ENUM ('BAJA', 'MEDIA', 'ALTA', 'URGENTE');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_priority') THEN
        CREATE TYPE task_priority AS ENUM ('alta', 'media', 'baja');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'taskstatus') THEN
        CREATE TYPE taskstatus AS ENUM ('PENDIENTE', 'COMPLETADA', 'VENCIDA', 'CANCELADA');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_status') THEN
        CREATE TYPE task_status AS ENUM ('pendiente', 'completada', 'cancelada');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'taskfrequency') THEN
        CREATE TYPE taskfrequency AS ENUM ('DIARIA', 'SEMANAL', 'QUINCENAL', 'MENSUAL', 'PERSONALIZADA');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_frequency') THEN
        CREATE TYPE task_frequency AS ENUM ('diaria', 'semanal', 'mensual', 'unica');
    END IF;
    
    -- Tipos para puntos de fichaje
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'checkpointstatus') THEN
        CREATE TYPE checkpointstatus AS ENUM ('ACTIVE', 'DISABLED', 'MAINTENANCE');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'checkpoint_status') THEN
        CREATE TYPE checkpoint_status AS ENUM ('active', 'disabled', 'maintenance');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'checkpointincidenttype') THEN
        CREATE TYPE checkpointincidenttype AS ENUM ('MISSED_CHECKOUT', 'LATE_CHECKIN', 'EARLY_CHECKOUT', 'OVERTIME', 'MANUAL_ADJUSTMENT', 'CONTRACT_HOURS_ADJUSTMENT');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'checkpoint_incident_type') THEN
        CREATE TYPE checkpoint_incident_type AS ENUM ('missed_checkout', 'late_checkin', 'early_checkout', 'overtime', 'manual_adjustment', 'contract_hours_adjustment');
    END IF;
    
    -- Tipo de conservación
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'conservationtype') THEN
        CREATE TYPE conservationtype AS ENUM ('DESCONGELACION', 'REFRIGERACION', 'GASTRO', 'CALIENTE', 'SECO');
    END IF;
    
END $$;