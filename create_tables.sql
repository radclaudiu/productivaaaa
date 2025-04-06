
-- Tabla de usuarios
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'empleado',
    first_name VARCHAR(64),
    last_name VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabla de empresas
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    address VARCHAR(256),
    city VARCHAR(64),
    postal_code VARCHAR(16),
    country VARCHAR(64),
    sector VARCHAR(64),
    tax_id VARCHAR(32) UNIQUE,
    phone VARCHAR(13),
    email VARCHAR(120),
    website VARCHAR(128),
    bank_account VARCHAR(24),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabla de relación usuarios-empresas
CREATE TABLE user_companies (
    user_id INTEGER REFERENCES users(id),
    company_id INTEGER REFERENCES companies(id),
    PRIMARY KEY (user_id, company_id)
);

-- Tabla de empleados
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    dni VARCHAR(16) UNIQUE NOT NULL,
    social_security_number VARCHAR(20),
    email VARCHAR(120),
    address VARCHAR(200),
    phone VARCHAR(20),
    position VARCHAR(64),
    contract_type VARCHAR(20) DEFAULT 'INDEFINIDO',
    bank_account VARCHAR(64),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'activo',
    company_id INTEGER REFERENCES companies(id) NOT NULL,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    is_on_shift BOOLEAN DEFAULT FALSE
);

-- Tabla de horarios de empleados
CREATE TABLE employee_schedules (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) NOT NULL,
    day_of_week VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_working_day BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de fichajes
CREATE TABLE employee_check_ins (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) NOT NULL,
    check_in_time TIMESTAMP NOT NULL,
    check_out_time TIMESTAMP,
    is_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);
