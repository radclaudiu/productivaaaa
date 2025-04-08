--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8
-- Dumped by pg_dump version 16.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: checkpointincidenttype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.checkpointincidenttype AS ENUM (
    'MISSED_CHECKOUT',
    'LATE_CHECKIN',
    'EARLY_CHECKOUT',
    'OVERTIME',
    'MANUAL_ADJUSTMENT',
    'CONTRACT_HOURS_ADJUSTMENT'
);


--
-- Name: checkpointstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.checkpointstatus AS ENUM (
    'ACTIVE',
    'DISABLED',
    'MAINTENANCE'
);


--
-- Name: conservationtype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.conservationtype AS ENUM (
    'DESCONGELACION',
    'REFRIGERACION',
    'GASTRO',
    'CALIENTE',
    'SECO'
);


--
-- Name: contracttype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.contracttype AS ENUM (
    'INDEFINIDO',
    'TEMPORAL',
    'PRACTICAS',
    'FORMACION',
    'OBRA'
);


--
-- Name: employeestatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.employeestatus AS ENUM (
    'ACTIVO',
    'BAJA_MEDICA',
    'EXCEDENCIA',
    'VACACIONES',
    'INACTIVO'
);


--
-- Name: taskfrequency; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.taskfrequency AS ENUM (
    'DIARIA',
    'SEMANAL',
    'QUINCENAL',
    'MENSUAL',
    'PERSONALIZADA'
);


--
-- Name: taskpriority; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.taskpriority AS ENUM (
    'BAJA',
    'MEDIA',
    'ALTA',
    'URGENTE'
);


--
-- Name: taskstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.taskstatus AS ENUM (
    'PENDIENTE',
    'COMPLETADA',
    'VENCIDA',
    'CANCELADA'
);


--
-- Name: userrole; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.userrole AS ENUM (
    'ADMIN',
    'GERENTE',
    'EMPLEADO'
);


--
-- Name: vacationstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.vacationstatus AS ENUM (
    'PENDIENTE',
    'APROBADA',
    'DENEGADA',
    'DISFRUTADA',
    'REGISTRADA'
);


--
-- Name: weekday; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.weekday AS ENUM (
    'LUNES',
    'MARTES',
    'MIERCOLES',
    'JUEVES',
    'VIERNES',
    'SABADO',
    'DOMINGO'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activity_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.activity_logs (
    id integer NOT NULL,
    action character varying(256) NOT NULL,
    ip_address character varying(64),
    "timestamp" timestamp without time zone,
    user_id integer
);


--
-- Name: activity_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.activity_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: activity_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.activity_logs_id_seq OWNED BY public.activity_logs.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: api_tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.api_tasks (
    id integer NOT NULL,
    title character varying(128) NOT NULL,
    description text,
    priority character varying(20),
    frequency character varying(20),
    status character varying(20),
    start_date date,
    end_date date,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: api_tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.api_tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: api_tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.api_tasks_id_seq OWNED BY public.api_tasks.id;


--
-- Name: checkpoint_incidents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checkpoint_incidents (
    id integer NOT NULL,
    incident_type public.checkpointincidenttype,
    description text,
    created_at timestamp without time zone,
    resolved boolean,
    resolved_at timestamp without time zone,
    resolution_notes text,
    record_id integer NOT NULL,
    resolved_by_id integer
);


--
-- Name: checkpoint_incidents_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.checkpoint_incidents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: checkpoint_incidents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.checkpoint_incidents_id_seq OWNED BY public.checkpoint_incidents.id;


--
-- Name: checkpoint_original_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checkpoint_original_records (
    id integer NOT NULL,
    record_id integer NOT NULL,
    original_check_in_time timestamp without time zone NOT NULL,
    original_check_out_time timestamp without time zone,
    original_signature_data text,
    original_has_signature boolean,
    original_notes text,
    adjusted_at timestamp without time zone,
    adjusted_by_id integer,
    adjustment_reason character varying(256),
    created_at timestamp without time zone
);


--
-- Name: checkpoint_original_records_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.checkpoint_original_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: checkpoint_original_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.checkpoint_original_records_id_seq OWNED BY public.checkpoint_original_records.id;


--
-- Name: checkpoint_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checkpoint_records (
    id integer NOT NULL,
    check_in_time timestamp without time zone NOT NULL,
    check_out_time timestamp without time zone,
    original_check_in_time timestamp without time zone,
    original_check_out_time timestamp without time zone,
    adjusted boolean,
    adjustment_reason character varying(256),
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    employee_id integer NOT NULL,
    checkpoint_id integer NOT NULL,
    signature_data text,
    has_signature boolean
);


--
-- Name: checkpoint_records_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.checkpoint_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: checkpoint_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.checkpoint_records_id_seq OWNED BY public.checkpoint_records.id;


--
-- Name: checkpoints; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checkpoints (
    id integer NOT NULL,
    name character varying(128) NOT NULL,
    description text,
    location character varying(256),
    status public.checkpointstatus,
    username character varying(64) NOT NULL,
    password_hash character varying(256) NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    company_id integer NOT NULL,
    enforce_contract_hours boolean,
    auto_adjust_overtime boolean,
    require_signature boolean DEFAULT true NOT NULL,
    operation_start_time time without time zone,
    operation_end_time time without time zone,
    enforce_operation_hours boolean DEFAULT false NOT NULL
);


--
-- Name: checkpoints_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.checkpoints_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: checkpoints_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.checkpoints_id_seq OWNED BY public.checkpoints.id;


--
-- Name: companies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.companies (
    id integer NOT NULL,
    name character varying(128) NOT NULL,
    address character varying(256),
    city character varying(64),
    postal_code character varying(16),
    country character varying(64),
    sector character varying(64),
    tax_id character varying(32),
    phone character varying(13),
    email character varying(120),
    website character varying(128),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    is_active boolean,
    bank_account character varying(24)
);


--
-- Name: companies_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.companies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.companies_id_seq OWNED BY public.companies.id;


--
-- Name: employee_check_ins; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee_check_ins (
    id integer NOT NULL,
    check_in_time timestamp without time zone NOT NULL,
    check_out_time timestamp without time zone,
    is_generated boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    notes text,
    employee_id integer NOT NULL
);


--
-- Name: employee_check_ins_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.employee_check_ins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: employee_check_ins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.employee_check_ins_id_seq OWNED BY public.employee_check_ins.id;


--
-- Name: employee_contract_hours; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee_contract_hours (
    id integer NOT NULL,
    daily_hours double precision,
    weekly_hours double precision,
    allow_overtime boolean,
    max_overtime_daily double precision,
    normal_start_time time without time zone,
    normal_end_time time without time zone,
    checkin_flexibility integer,
    checkout_flexibility integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    employee_id integer NOT NULL,
    use_normal_schedule boolean DEFAULT false,
    use_flexibility boolean DEFAULT false
);


--
-- Name: employee_contract_hours_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.employee_contract_hours_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: employee_contract_hours_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.employee_contract_hours_id_seq OWNED BY public.employee_contract_hours.id;


--
-- Name: employee_documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee_documents (
    id integer NOT NULL,
    filename character varying(256) NOT NULL,
    original_filename character varying(256) NOT NULL,
    file_path character varying(512) NOT NULL,
    file_type character varying(64),
    file_size integer,
    description character varying(256),
    uploaded_at timestamp without time zone,
    employee_id integer NOT NULL
);


--
-- Name: employee_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.employee_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: employee_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.employee_documents_id_seq OWNED BY public.employee_documents.id;


--
-- Name: employee_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee_history (
    id integer NOT NULL,
    field_name character varying(64) NOT NULL,
    old_value character varying(256),
    new_value character varying(256),
    changed_at timestamp without time zone,
    employee_id integer NOT NULL,
    changed_by_id integer
);


--
-- Name: employee_history_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.employee_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: employee_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.employee_history_id_seq OWNED BY public.employee_history.id;


--
-- Name: employee_notes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee_notes (
    id integer NOT NULL,
    content text NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    employee_id integer NOT NULL,
    created_by_id integer
);


--
-- Name: employee_notes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.employee_notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: employee_notes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.employee_notes_id_seq OWNED BY public.employee_notes.id;


--
-- Name: employee_schedules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee_schedules (
    id integer NOT NULL,
    day_of_week public.weekday NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    is_working_day boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    employee_id integer NOT NULL
);


--
-- Name: employee_schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.employee_schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: employee_schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.employee_schedules_id_seq OWNED BY public.employee_schedules.id;


--
-- Name: employee_vacations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee_vacations (
    id integer NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    status public.vacationstatus,
    is_signed boolean,
    is_enjoyed boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    notes text,
    employee_id integer NOT NULL,
    approved_by_id integer
);


--
-- Name: employee_vacations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.employee_vacations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: employee_vacations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.employee_vacations_id_seq OWNED BY public.employee_vacations.id;


--
-- Name: employees; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employees (
    id integer NOT NULL,
    first_name character varying(64) NOT NULL,
    last_name character varying(64) NOT NULL,
    dni character varying(16) NOT NULL,
    "position" character varying(64),
    contract_type public.contracttype,
    bank_account character varying(64),
    start_date date,
    end_date date,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    is_active boolean,
    company_id integer NOT NULL,
    user_id integer,
    status character varying,
    status_start_date date,
    status_end_date date,
    status_notes text,
    is_on_shift boolean DEFAULT false,
    social_security_number character varying(20),
    email character varying(120),
    address character varying(200),
    phone character varying(20)
);


--
-- Name: employees_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.employees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: employees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.employees_id_seq OWNED BY public.employees.id;


--
-- Name: label_templates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.label_templates (
    id integer NOT NULL,
    name character varying(64) NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    is_default boolean,
    titulo_x integer,
    titulo_y integer,
    titulo_size integer,
    titulo_bold boolean,
    conservacion_x integer,
    conservacion_y integer,
    conservacion_size integer,
    conservacion_bold boolean,
    preparador_x integer,
    preparador_y integer,
    preparador_size integer,
    preparador_bold boolean,
    fecha_x integer,
    fecha_y integer,
    fecha_size integer,
    fecha_bold boolean,
    caducidad_x integer,
    caducidad_y integer,
    caducidad_size integer,
    caducidad_bold boolean,
    caducidad2_x integer,
    caducidad2_y integer,
    caducidad2_size integer,
    caducidad2_bold boolean,
    location_id integer NOT NULL
);


--
-- Name: label_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.label_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: label_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.label_templates_id_seq OWNED BY public.label_templates.id;


--
-- Name: local_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.local_users (
    id integer NOT NULL,
    name character varying(64) NOT NULL,
    username character varying(64) NOT NULL,
    password_hash character varying(256),
    pin character varying(256) NOT NULL,
    photo_path character varying(256),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    is_active boolean,
    location_id integer NOT NULL,
    last_name character varying(64) DEFAULT ''::character varying NOT NULL
);


--
-- Name: local_users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.local_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: local_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.local_users_id_seq OWNED BY public.local_users.id;


--
-- Name: locations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.locations (
    id integer NOT NULL,
    name character varying(128) NOT NULL,
    address character varying(256),
    city character varying(64),
    postal_code character varying(16),
    description text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    is_active boolean,
    company_id integer NOT NULL,
    portal_username character varying(64),
    portal_password_hash character varying(256)
);


--
-- Name: locations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: locations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.locations_id_seq OWNED BY public.locations.id;


--
-- Name: printer_configs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.printer_configs (
    id integer NOT NULL,
    printer_name character varying(128),
    is_default boolean,
    is_active boolean,
    last_check timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    location_id integer NOT NULL,
    local_user_id integer
);


--
-- Name: printer_configs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.printer_configs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: printer_configs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.printer_configs_id_seq OWNED BY public.printer_configs.id;


--
-- Name: product_conservations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_conservations (
    id integer NOT NULL,
    conservation_type public.conservationtype NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    product_id integer NOT NULL,
    hours_valid integer
);


--
-- Name: product_conservations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.product_conservations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: product_conservations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.product_conservations_id_seq OWNED BY public.product_conservations.id;


--
-- Name: product_labels; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_labels (
    id integer NOT NULL,
    created_at timestamp without time zone,
    expiry_date date NOT NULL,
    product_id integer NOT NULL,
    local_user_id integer NOT NULL,
    conservation_type public.conservationtype NOT NULL
);


--
-- Name: product_labels_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.product_labels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: product_labels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.product_labels_id_seq OWNED BY public.product_labels.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name character varying(128) NOT NULL,
    description text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    is_active boolean,
    location_id integer NOT NULL,
    shelf_life_days integer DEFAULT 0 NOT NULL
);


--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: task_completions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_completions (
    id integer NOT NULL,
    completion_date timestamp without time zone,
    notes text,
    task_id integer NOT NULL,
    local_user_id integer NOT NULL
);


--
-- Name: task_completions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.task_completions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: task_completions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.task_completions_id_seq OWNED BY public.task_completions.id;


--
-- Name: task_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_groups (
    id integer NOT NULL,
    name character varying(64) NOT NULL,
    description text,
    color character varying(7) DEFAULT '#17a2b8'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    location_id integer NOT NULL
);


--
-- Name: task_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.task_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: task_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.task_groups_id_seq OWNED BY public.task_groups.id;


--
-- Name: task_instances; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_instances (
    id integer NOT NULL,
    scheduled_date date NOT NULL,
    status public.taskstatus,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    task_id integer NOT NULL,
    completed_by_id integer
);


--
-- Name: task_instances_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.task_instances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: task_instances_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.task_instances_id_seq OWNED BY public.task_instances.id;


--
-- Name: task_schedules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_schedules (
    id integer NOT NULL,
    day_of_week public.weekday,
    day_of_month integer,
    start_time time without time zone,
    end_time time without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    task_id integer NOT NULL
);


--
-- Name: task_schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.task_schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: task_schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.task_schedules_id_seq OWNED BY public.task_schedules.id;


--
-- Name: task_weekdays; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_weekdays (
    id integer NOT NULL,
    day_of_week character varying(16) NOT NULL,
    task_id integer NOT NULL
);


--
-- Name: task_weekdays_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.task_weekdays_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: task_weekdays_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.task_weekdays_id_seq OWNED BY public.task_weekdays.id;


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    title character varying(128) NOT NULL,
    description text,
    priority public.taskpriority,
    frequency public.taskfrequency,
    status public.taskstatus,
    start_date date NOT NULL,
    end_date date,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    location_id integer NOT NULL,
    created_by_id integer,
    group_id integer
);


--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- Name: user_companies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_companies (
    user_id integer NOT NULL,
    company_id integer NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(256) NOT NULL,
    role public.userrole NOT NULL,
    first_name character varying(64),
    last_name character varying(64),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    is_active boolean,
    company_id integer
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: activity_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activity_logs ALTER COLUMN id SET DEFAULT nextval('public.activity_logs_id_seq'::regclass);


--
-- Name: api_tasks id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_tasks ALTER COLUMN id SET DEFAULT nextval('public.api_tasks_id_seq'::regclass);


--
-- Name: checkpoint_incidents id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_incidents ALTER COLUMN id SET DEFAULT nextval('public.checkpoint_incidents_id_seq'::regclass);


--
-- Name: checkpoint_original_records id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_original_records ALTER COLUMN id SET DEFAULT nextval('public.checkpoint_original_records_id_seq'::regclass);


--
-- Name: checkpoint_records id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_records ALTER COLUMN id SET DEFAULT nextval('public.checkpoint_records_id_seq'::regclass);


--
-- Name: checkpoints id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoints ALTER COLUMN id SET DEFAULT nextval('public.checkpoints_id_seq'::regclass);


--
-- Name: companies id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.companies ALTER COLUMN id SET DEFAULT nextval('public.companies_id_seq'::regclass);


--
-- Name: employee_check_ins id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_check_ins ALTER COLUMN id SET DEFAULT nextval('public.employee_check_ins_id_seq'::regclass);


--
-- Name: employee_contract_hours id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_contract_hours ALTER COLUMN id SET DEFAULT nextval('public.employee_contract_hours_id_seq'::regclass);


--
-- Name: employee_documents id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_documents ALTER COLUMN id SET DEFAULT nextval('public.employee_documents_id_seq'::regclass);


--
-- Name: employee_history id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_history ALTER COLUMN id SET DEFAULT nextval('public.employee_history_id_seq'::regclass);


--
-- Name: employee_notes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_notes ALTER COLUMN id SET DEFAULT nextval('public.employee_notes_id_seq'::regclass);


--
-- Name: employee_schedules id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_schedules ALTER COLUMN id SET DEFAULT nextval('public.employee_schedules_id_seq'::regclass);


--
-- Name: employee_vacations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_vacations ALTER COLUMN id SET DEFAULT nextval('public.employee_vacations_id_seq'::regclass);


--
-- Name: employees id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees ALTER COLUMN id SET DEFAULT nextval('public.employees_id_seq'::regclass);


--
-- Name: label_templates id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.label_templates ALTER COLUMN id SET DEFAULT nextval('public.label_templates_id_seq'::regclass);


--
-- Name: local_users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.local_users ALTER COLUMN id SET DEFAULT nextval('public.local_users_id_seq'::regclass);


--
-- Name: locations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations ALTER COLUMN id SET DEFAULT nextval('public.locations_id_seq'::regclass);


--
-- Name: printer_configs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.printer_configs ALTER COLUMN id SET DEFAULT nextval('public.printer_configs_id_seq'::regclass);


--
-- Name: product_conservations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_conservations ALTER COLUMN id SET DEFAULT nextval('public.product_conservations_id_seq'::regclass);


--
-- Name: product_labels id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_labels ALTER COLUMN id SET DEFAULT nextval('public.product_labels_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: task_completions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_completions ALTER COLUMN id SET DEFAULT nextval('public.task_completions_id_seq'::regclass);


--
-- Name: task_groups id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_groups ALTER COLUMN id SET DEFAULT nextval('public.task_groups_id_seq'::regclass);


--
-- Name: task_instances id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_instances ALTER COLUMN id SET DEFAULT nextval('public.task_instances_id_seq'::regclass);


--
-- Name: task_schedules id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_schedules ALTER COLUMN id SET DEFAULT nextval('public.task_schedules_id_seq'::regclass);


--
-- Name: task_weekdays id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_weekdays ALTER COLUMN id SET DEFAULT nextval('public.task_weekdays_id_seq'::regclass);


--
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: activity_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.activity_logs (id, action, ip_address, "timestamp", user_id) FROM stdin;
4953	Login exitoso: admin	172.31.128.105	2025-04-04 16:12:27.574959	8
4954	GET /profile	172.31.128.105	2025-04-04 16:12:33.604893	8
4955	GET /users/	172.31.128.105	2025-04-04 16:12:35.545446	8
4956	GET /users/	172.31.128.105	2025-04-04 16:12:36.287558	8
4957	Login exitoso: admin	127.0.0.1	2025-04-04 16:16:45.949738	8
4958	GET /companies/	127.0.0.1	2025-04-04 16:16:53.934813	8
4959	GET /register	127.0.0.1	2025-04-04 16:16:59.833557	8
4960	POST /register	127.0.0.1	2025-04-04 16:17:49.084044	8
4961	Usuario registrado: dnln	127.0.0.1	2025-04-04 16:17:49.809489	8
4962	GET /users/	127.0.0.1	2025-04-04 16:17:50.136556	8
4963	GET /companies/	127.0.0.1	2025-04-04 16:17:56.242016	8
4964	GET /companies/new	127.0.0.1	2025-04-04 16:17:57.887067	8
4965	POST /companies/new	127.0.0.1	2025-04-04 16:18:22.322241	8
4966	POST /companies/new	127.0.0.1	2025-04-04 16:18:28.688693	8
4967	Empresa creada: DNLN DISTRIBUCION SL	127.0.0.1	2025-04-04 16:18:28.941151	8
4968	GET /companies/	127.0.0.1	2025-04-04 16:18:29.299999	8
4969	GET /users/	127.0.0.1	2025-04-04 16:18:36.153468	8
4970	GET /users/9/edit	127.0.0.1	2025-04-04 16:18:39.13794	8
4971	POST /users/9/edit	127.0.0.1	2025-04-04 16:18:44.393303	8
4972	Usuario actualizado: dnln	127.0.0.1	2025-04-04 16:18:44.696371	8
4973	GET /users/	127.0.0.1	2025-04-04 16:18:45.058887	8
4974	GET /fichajes/	127.0.0.1	2025-04-04 16:18:59.925686	8
4975	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 16:19:00.334025	8
4976	GET /fichajes/checkpoints/new	127.0.0.1	2025-04-04 16:19:03.323644	8
4977	POST /fichajes/checkpoints/new	127.0.0.1	2025-04-04 16:19:36.480541	8
4978	GET /fichajes/checkpoints	127.0.0.1	2025-04-04 16:19:37.134017	8
4979	POST /employees/new	127.0.0.1	2025-04-04 16:20:17.782129	8
4980	Asignando empleado a 1 puntos de fichaje	127.0.0.1	2025-04-04 16:20:18.099141	8
4981	Empleado creado: Claudio Rad	127.0.0.1	2025-04-04 16:20:18.238338	8
4982	GET /fichajes/	127.0.0.1	2025-04-04 16:20:23.766807	8
4983	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 16:20:24.15831	8
4984	GET /fichajes/login	127.0.0.1	2025-04-04 16:20:27.51395	8
4985	POST /fichajes/login	127.0.0.1	2025-04-04 16:20:29.753549	8
4986	GET /fichajes/dashboard	127.0.0.1	2025-04-04 16:20:30.28855	8
4987	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-04 16:20:32.852971	8
4988	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-04 16:20:35.793726	8
4989	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-04 16:20:38.763638	8
4990	GET /fichajes/record/76	127.0.0.1	2025-04-04 16:20:39.459085	8
4991	GET /fichajes/employees/46/contract_hours	127.0.0.1	2025-04-04 16:20:47.574843	8
4992	POST /fichajes/employees/46/contract_hours	127.0.0.1	2025-04-04 16:21:04.392214	8
4993	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 16:21:04.941734	8
4994	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 16:22:30.821542	8
4995	POST /fichajes/record/76/checkout	127.0.0.1	2025-04-04 16:23:32.679532	8
4996	GET /fichajes/record/76/signature_pad	127.0.0.1	2025-04-04 16:23:33.465387	8
4997	POST /fichajes/record/76/signature_pad	127.0.0.1	2025-04-04 16:23:37.718044	8
4998	GET /fichajes/record/76	127.0.0.1	2025-04-04 16:23:38.308635	8
4999	GET /fichajes/records/76/adjust	127.0.0.1	2025-04-04 16:24:01.323427	8
5000	GET /fichajes/checkpoints/8/records	127.0.0.1	2025-04-04 16:24:19.885452	8
5001	GET /fichajes/records/76/adjust	127.0.0.1	2025-04-04 16:24:24.254138	8
5002	POST /fichajes/records/76/adjust	127.0.0.1	2025-04-04 16:24:32.96326	8
5003	GET /fichajes/checkpoints/8/records	127.0.0.1	2025-04-04 16:24:33.651096	8
5004	GET /fichajes/dashboard	127.0.0.1	2025-04-04 16:24:38.229831	8
5005	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-04 16:24:39.714561	8
5006	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-04 16:24:42.690004	8
5007	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-04 16:24:44.043952	8
5008	GET /fichajes/record/77	127.0.0.1	2025-04-04 16:24:44.685222	8
5009	GET /fichajes/records/76/adjust	127.0.0.1	2025-04-04 16:24:54.367144	8
5010	GET /fichajes/checkpoints/8/records	127.0.0.1	2025-04-04 16:24:56.498752	8
5011	GET /fichajes/records/77/adjust	127.0.0.1	2025-04-04 16:25:09.816648	8
5012	GET /fichajes/checkpoints/8/records	127.0.0.1	2025-04-04 16:25:37.046261	8
5013	GET /fichajes/records/77/adjust	127.0.0.1	2025-04-04 16:26:00.019004	8
5014	POST /fichajes/records/77/adjust	127.0.0.1	2025-04-04 16:26:07.364308	8
5015	GET /fichajes/checkpoints/8/records	127.0.0.1	2025-04-04 16:26:07.995979	8
5016	POST /fichajes/record/77/checkout	127.0.0.1	2025-04-04 16:26:15.285778	8
5017	GET /fichajes/record/77/signature_pad	127.0.0.1	2025-04-04 16:26:15.990476	8
5018	POST /fichajes/record/77/signature_pad	127.0.0.1	2025-04-04 16:26:18.59392	8
5019	GET /fichajes/record/77	127.0.0.1	2025-04-04 16:26:19.168621	8
5020	GET /fichajes/dashboard	127.0.0.1	2025-04-04 16:26:21.113835	8
5021	GET /fichajes/checkpoints/8/records	127.0.0.1	2025-04-04 16:26:26.676691	8
5022	GET /fichajes/	127.0.0.1	2025-04-04 16:26:29.615329	8
5023	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 16:26:30.023702	8
5024	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 16:26:35.27488	8
5025	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 16:26:50.003286	8
5026	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 16:26:53.162221	8
5027	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 16:26:54.544218	8
5028	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 16:26:56.924411	8
5029	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-04 16:27:01.449962	8
5030	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-04 16:27:04.662799	8
5031	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-04 16:27:06.02245	8
5032	GET /fichajes/record/78	127.0.0.1	2025-04-04 16:27:06.663055	8
5033	POST /fichajes/record/78/checkout	127.0.0.1	2025-04-04 16:27:08.818303	8
5034	GET /fichajes/record/78/signature_pad	127.0.0.1	2025-04-04 16:27:09.575881	8
5035	POST /fichajes/record/78/signature_pad	127.0.0.1	2025-04-04 16:27:11.65344	8
5036	GET /fichajes/record/78	127.0.0.1	2025-04-04 16:27:12.202418	8
5037	GET /fichajes/dashboard	127.0.0.1	2025-04-04 16:27:13.830959	8
5038	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 16:27:15.776474	8
5039	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-04 16:27:26.23252	8
5040	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-04 16:27:29.569657	8
5041	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-04 16:27:30.842246	8
5042	GET /fichajes/record/79	127.0.0.1	2025-04-04 16:27:31.491013	8
5043	GET /fichajes/dashboard	127.0.0.1	2025-04-04 16:27:33.714873	8
5044	GET /fichajes/	127.0.0.1	2025-04-04 16:27:37.76857	8
5045	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 16:27:38.163427	8
5046	GET /fichajes/records/export	127.0.0.1	2025-04-04 16:28:01.698404	8
5047	GET /fichajes/records/export	127.0.0.1	2025-04-04 16:28:17.7026	8
5048	GET /login	172.31.128.105	2025-04-04 16:36:09.768862	8
5049	GET /fichajes/	172.31.128.105	2025-04-04 16:36:15.098091	8
5050	GET /fichajes/company/dnln-distribucion-sl	172.31.128.105	2025-04-04 16:36:15.912639	8
5051	GET /fichajes/company/dnln-distribucion-sl	172.31.128.105	2025-04-04 16:36:51.114001	8
5052	GET /fichajes/records	172.31.128.105	2025-04-04 16:37:04.015739	8
5053	GET /fichajes/	172.31.128.105	2025-04-04 16:37:19.962397	8
5054	GET /fichajes/company/dnln-distribucion-sl	172.31.128.105	2025-04-04 16:37:20.772873	8
5055	GET /tasks/dashboard/labels	172.31.128.105	2025-04-04 16:37:56.48684	8
5056	GET /fichajes/	172.31.128.105	2025-04-04 16:38:00.947943	8
5057	GET /fichajes/company/dnln-distribucion-sl	172.31.128.105	2025-04-04 16:38:01.767265	8
5058	GET /fichajes/checkpoints/8/records	172.31.128.105	2025-04-04 16:38:12.814479	8
5059	GET /fichajes/records	172.31.128.105	2025-04-04 16:38:35.018451	8
5060	GET /fichajes/employees/46/contract_hours	172.31.128.105	2025-04-04 16:38:42.899451	8
5061	GET /tasks/dashboard/labels	172.31.128.105	2025-04-04 16:38:47.4939	8
5062	GET /tasks/dashboard/labels	172.31.128.105	2025-04-04 16:38:50.498162	8
5063	GET /fichajes/	172.31.128.105	2025-04-04 16:38:52.871715	8
5064	GET /fichajes/company/dnln-distribucion-sl	172.31.128.105	2025-04-04 16:38:53.712625	8
5065	GET /	172.31.128.91	2025-04-04 16:50:44.331573	8
5066	GET /	172.31.128.91	2025-04-04 16:50:58.296423	8
5067	GET /fichajes/	172.31.128.91	2025-04-04 16:52:12.062535	8
5068	GET /fichajes/company/dnln-distribucion-sl	172.31.128.91	2025-04-04 16:52:12.907138	8
5069	GET /fichajes/records	172.31.128.91	2025-04-04 16:53:52.310152	8
5070	GET /fichajes/records	172.31.128.91	2025-04-04 16:55:02.008788	8
5071	GET /fichajes/	172.31.128.91	2025-04-04 16:55:06.348226	8
5072	GET /fichajes/company/dnln-distribucion-sl	172.31.128.91	2025-04-04 16:55:07.154497	8
5073	GET /fichajes/employees/46/contract_hours	172.31.128.91	2025-04-04 16:55:16.927631	8
5074	GET /fichajes/	172.31.128.91	2025-04-04 16:55:29.060519	8
5075	GET /fichajes/company/dnln-distribucion-sl	172.31.128.91	2025-04-04 16:55:29.846105	8
5076	GET /fichajes/company/dnln-distribucion-sl	172.31.128.91	2025-04-04 16:58:23.719586	8
5077	GET /fichajes/company/dnln-distribucion-sl	172.31.128.91	2025-04-04 16:58:29.852457	8
5078	GET /fichajes/records	172.31.128.91	2025-04-04 16:58:56.315203	8
5079	GET /fichajes/records	172.31.128.91	2025-04-04 17:01:30.745332	8
5080	GET /fichajes/delete_records	172.31.128.91	2025-04-04 17:02:56.492014	8
5081	POST /fichajes/delete_records	172.31.128.91	2025-04-04 17:03:08.964556	8
5082	GET /fichajes/company/dnln-distribucion-sl	172.31.128.91	2025-04-04 17:03:10.624895	8
5083	GET /fichajes/records	172.31.128.91	2025-04-04 17:03:35.167393	8
5084	GET /fichajes/	172.31.128.91	2025-04-04 17:03:38.889741	8
5085	GET /fichajes/company/dnln-distribucion-sl	172.31.128.91	2025-04-04 17:03:39.677393	8
5086	GET /fichajes/	172.31.128.91	2025-04-04 17:04:51.380538	8
5087	GET /fichajes/company/dnln-distribucion-sl	172.31.128.91	2025-04-04 17:04:52.233992	8
5088	GET /fichajes/company/dnln-distribucion-sl/RRRRRR	172.31.128.91	2025-04-04 17:07:24.7497	8
5089	GET /fichajes/	172.31.128.91	2025-04-04 17:07:25.333629	8
5090	GET /fichajes/company/dnln-distribucion-sl	172.31.128.91	2025-04-04 17:07:26.539548	8
5091	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.91	2025-04-04 17:07:39.133822	8
5092	GET /fichajes/login	172.31.128.91	2025-04-04 17:07:46.05901	8
5093	POST /fichajes/login	172.31.128.91	2025-04-04 17:07:50.181401	8
5094	GET /fichajes/dashboard	172.31.128.91	2025-04-04 17:07:51.054485	8
5095	GET /fichajes/employee/46/pin	172.31.128.91	2025-04-04 17:07:54.6503	8
5096	POST /fichajes/api/validate-pin	172.31.128.91	2025-04-04 17:07:58.162678	8
5097	POST /fichajes/api/validate-pin	172.31.128.91	2025-04-04 17:08:01.070152	8
5098	POST /fichajes/employee/46/pin	172.31.128.91	2025-04-04 17:08:02.817124	8
5099	GET /fichajes/record/80	172.31.128.91	2025-04-04 17:08:04.240043	8
5100	GET /tasks/dashboard/labels	172.31.128.91	2025-04-04 17:08:05.046521	8
5101	GET /tasks/dashboard/labels	172.31.128.91	2025-04-04 17:08:05.772089	8
5102	GET /fichajes/	172.31.128.91	2025-04-04 17:08:06.48849	8
5103	GET /fichajes/company/dnln-distribucion-sl	172.31.128.91	2025-04-04 17:08:07.684516	8
5104	GET /	127.0.0.1	2025-04-04 17:14:06.991959	8
5105	POST /employees/new	127.0.0.1	2025-04-04 17:14:36.197722	8
5106	Asignando empleado a 1 puntos de fichaje	127.0.0.1	2025-04-04 17:14:36.487758	8
5107	Empleado creado: Lucia Mendez	127.0.0.1	2025-04-04 17:14:36.61664	8
5108	GET /fichajes/	127.0.0.1	2025-04-04 17:14:50.426415	8
5109	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 17:14:50.820021	8
5110	GET /fichajes/login	127.0.0.1	2025-04-04 17:15:04.477365	8
5111	GET /fichajes/dashboard	127.0.0.1	2025-04-04 17:15:04.828236	8
5112	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-04 17:15:06.626888	8
5113	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-04 17:15:08.824282	8
5114	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 17:15:11.831937	8
5115	GET /companies/	127.0.0.1	2025-04-04 17:15:17.646127	8
5116	GET /fichajes/	127.0.0.1	2025-04-04 17:15:34.694263	8
5117	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 17:15:35.085587	8
5118	GET /fichajes/login	127.0.0.1	2025-04-04 17:15:48.645644	8
5119	GET /fichajes/dashboard	127.0.0.1	2025-04-04 17:15:48.931674	8
5120	GET /fichajes/employee/47/pin	127.0.0.1	2025-04-04 17:15:58.15401	8
5121	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-04 17:16:00.68201	8
5122	POST /fichajes/employee/47/pin	127.0.0.1	2025-04-04 17:16:02.153727	8
5123	GET /fichajes/record/81	127.0.0.1	2025-04-04 17:16:02.866186	8
5124	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 17:16:03.194184	8
5125	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 17:16:03.988825	8
5126	GET /fichajes/employees/46/contract_hours	127.0.0.1	2025-04-04 17:16:08.861103	8
5127	GET /fichajes/employees/47/contract_hours	127.0.0.1	2025-04-04 17:16:12.784074	8
5128	POST /fichajes/employees/47/contract_hours	127.0.0.1	2025-04-04 17:16:16.806017	8
5129	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 17:16:17.366659	8
5130	GET /companies/	127.0.0.1	2025-04-04 17:16:19.656093	8
5131	GET /companies/dnln-distribucion-sl/edit	127.0.0.1	2025-04-04 17:16:21.530441	8
5132	GET /fichajes/	127.0.0.1	2025-04-04 17:16:27.202558	8
5133	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 17:16:27.591161	8
5134	GET /fichajes/checkpoints/8/edit	127.0.0.1	2025-04-04 17:16:30.966102	8
5135	GET /fichajes/	127.0.0.1	2025-04-04 17:17:13.253766	8
5136	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 17:17:13.642778	8
5137	GET /fichajes/dashboard	127.0.0.1	2025-04-04 17:17:16.386389	8
5138	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 17:17:37.826027	8
5139	GET /login	172.31.128.7	2025-04-04 17:31:37.944484	8
5140	GET /fichajes/	172.31.128.7	2025-04-04 17:31:44.046155	8
5141	GET /fichajes/company/dnln-distribucion-sl	172.31.128.7	2025-04-04 17:31:44.91662	8
5142	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.7	2025-04-04 17:31:52.114504	8
5143	GET /fichajes/	172.31.128.7	2025-04-04 17:32:59.584602	8
5144	GET /fichajes/company/dnln-distribucion-sl	172.31.128.7	2025-04-04 17:33:00.406216	8
5145	GET /fichajes/records/export	172.31.128.7	2025-04-04 17:33:09.24086	8
5146	POST /fichajes/records/export	172.31.128.7	2025-04-04 17:33:15.510064	8
5147	GET /fichajes/	172.31.128.7	2025-04-04 17:33:29.222678	8
5148	GET /fichajes/company/dnln-distribucion-sl	172.31.128.7	2025-04-04 17:33:30.040468	8
5149	GET /fichajes/company/dnln-distribucion-sl	172.31.128.7	2025-04-04 17:41:05.657743	8
5150	GET /fichajes/records	172.31.128.7	2025-04-04 17:41:36.540956	8
5151	GET /fichajes/	172.31.128.7	2025-04-04 17:43:15.563127	8
5152	GET /fichajes/company/dnln-distribucion-sl	172.31.128.7	2025-04-04 17:43:16.389425	8
5153	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-04 17:43:36.940275	8
5154	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-04 17:43:39.057957	8
5155	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-04 17:43:40.237154	8
5156	GET /fichajes/record/136	127.0.0.1	2025-04-04 17:43:40.903056	8
5157	POST /fichajes/record/136/checkout	127.0.0.1	2025-04-04 17:43:42.336962	8
5158	GET /fichajes/record/136/signature_pad	127.0.0.1	2025-04-04 17:43:43.053643	8
5159	POST /fichajes/record/136/signature_pad	127.0.0.1	2025-04-04 17:43:44.689814	8
5160	GET /fichajes/record/136	127.0.0.1	2025-04-04 17:43:45.24046	8
5161	GET /fichajes/dashboard	127.0.0.1	2025-04-04 17:43:46.833487	8
5162	GET /fichajes/employee/47/pin	127.0.0.1	2025-04-04 17:43:49.174766	8
5163	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-04 17:43:51.140545	8
5164	POST /fichajes/employee/47/pin	127.0.0.1	2025-04-04 17:43:52.367067	8
5165	GET /fichajes/record/137	127.0.0.1	2025-04-04 17:43:53.029499	8
5166	POST /fichajes/record/137/checkout	127.0.0.1	2025-04-04 17:43:54.88287	8
5167	GET /fichajes/record/137/signature_pad	127.0.0.1	2025-04-04 17:43:55.608394	8
5168	POST /fichajes/record/137/signature_pad	127.0.0.1	2025-04-04 17:43:58.027299	8
5169	GET /fichajes/record/137	127.0.0.1	2025-04-04 17:43:58.618721	8
5170	GET /fichajes/dashboard	127.0.0.1	2025-04-04 17:44:00.482553	8
5171	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-04 17:44:03.205143	8
5172	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-04 17:44:05.032729	8
5173	GET /	127.0.0.1	2025-04-04 17:45:35.733421	8
5174	GET /	127.0.0.1	2025-04-04 17:45:35.94606	8
5175	GET /fichajes/	127.0.0.1	2025-04-04 17:45:38.706082	8
5176	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 17:45:39.091786	8
5177	GET /fichajes/login	127.0.0.1	2025-04-04 17:45:42.530181	8
5178	GET /fichajes/dashboard	127.0.0.1	2025-04-04 17:45:42.820018	8
5179	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-04 17:45:44.105781	8
5180	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-04 17:45:46.846092	8
5181	GET /fichajes/record/138	127.0.0.1	2025-04-04 17:45:47.469047	8
5182	POST /fichajes/record/138/checkout	127.0.0.1	2025-04-04 17:45:52.626175	8
5183	GET /fichajes/record/138/signature_pad	127.0.0.1	2025-04-04 17:45:53.299923	8
5184	POST /fichajes/record/138/signature_pad	127.0.0.1	2025-04-04 17:45:55.623653	8
5185	GET /fichajes/record/138	127.0.0.1	2025-04-04 17:45:56.202926	8
5186	GET /fichajes/dashboard	127.0.0.1	2025-04-04 17:45:57.800432	8
5187	GET /fichajes/employee/47/pin	127.0.0.1	2025-04-04 17:45:58.929865	8
5188	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-04 17:46:01.220582	8
5189	POST /fichajes/employee/47/pin	127.0.0.1	2025-04-04 17:46:02.426091	8
5190	GET /fichajes/record/139	127.0.0.1	2025-04-04 17:46:03.055271	8
5191	POST /fichajes/record/139/checkout	127.0.0.1	2025-04-04 17:46:04.549801	8
5192	GET /fichajes/record/139/signature_pad	127.0.0.1	2025-04-04 17:46:05.213138	8
5193	POST /fichajes/record/139/signature_pad	127.0.0.1	2025-04-04 17:46:07.550155	8
5194	GET /fichajes/record/139	127.0.0.1	2025-04-04 17:46:08.095639	8
5195	GET /fichajes/dashboard	127.0.0.1	2025-04-04 17:46:09.563298	8
5196	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-04 17:46:10.731136	8
5197	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-04 17:46:13.247698	8
5198	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-04 17:46:14.489339	8
5199	GET /fichajes/record/140	127.0.0.1	2025-04-04 17:46:15.094733	8
5200	GET /fichajes/dashboard	127.0.0.1	2025-04-04 17:46:16.570348	8
5201	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-04 17:46:17.58096	8
5202	GET /fichajes/dashboard	127.0.0.1	2025-04-04 17:46:19.804135	8
5203	GET /fichajes/employee/47/pin	127.0.0.1	2025-04-04 17:46:20.721804	8
5204	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-04 17:46:22.255853	8
5205	POST /fichajes/employee/47/pin	127.0.0.1	2025-04-04 17:46:23.540795	8
5206	GET /fichajes/record/141	127.0.0.1	2025-04-04 17:46:24.155215	8
5207	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 17:46:26.679268	8
5208	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	127.0.0.1	2025-04-04 17:46:35.364817	8
5209	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 17:46:49.22203	8
5210	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 17:46:59.5064	8
5211	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	127.0.0.1	2025-04-04 17:47:01.960063	8
5212	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 17:47:11.061008	8
5213	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 17:47:16.013141	8
5214	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 17:47:18.574256	8
5215	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 17:47:27.115542	8
5216	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 17:47:27.693609	8
5217	POST /employees/46/edit	127.0.0.1	2025-04-04 17:47:37.212382	8
5218	GET /fichajes/	127.0.0.1	2025-04-04 17:47:39.501777	8
5219	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 17:47:39.898641	8
5220	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 17:47:44.00445	8
5221	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 17:47:44.497181	8
5222	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 17:47:48.792605	8
5223	GET /companies/	127.0.0.1	2025-04-04 17:47:52.936181	8
5224	POST /employees/46/edit	127.0.0.1	2025-04-04 17:48:06.595144	8
5225	POST /employees/47/edit	127.0.0.1	2025-04-04 17:48:22.156413	8
5226	GET /companies/	127.0.0.1	2025-04-04 17:48:24.200753	8
5227	GET /login	172.31.128.7	2025-04-04 17:57:55.696354	8
5228	POST /employees/46/toggle-active	172.31.128.7	2025-04-04 17:58:07.92097	8
5229	Empleado activado: Claudio Rad	172.31.128.7	2025-04-04 17:58:08.697588	8
5230	POST /employees/47/toggle-active	172.31.128.7	2025-04-04 18:02:48.557793	8
5231	Empleado desactivado: Lucia Mendez	172.31.128.7	2025-04-04 18:02:49.332559	8
5232	POST /employees/47/toggle-active	172.31.128.7	2025-04-04 18:02:55.041935	8
5233	Empleado activado: Lucia Mendez	172.31.128.7	2025-04-04 18:02:55.784454	8
5234	GET /fichajes/	172.31.128.7	2025-04-04 18:07:50.758584	8
5235	GET /fichajes/company/dnln-distribucion-sl	172.31.128.7	2025-04-04 18:07:51.631913	8
5236	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.7	2025-04-04 18:07:57.998416	8
5237	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.7	2025-04-04 18:08:03.264477	8
5238	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	172.31.128.7	2025-04-04 18:08:06.229754	8
5239	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	172.31.128.7	2025-04-04 18:08:13.692327	8
5240	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.7	2025-04-04 18:08:20.307679	8
5241	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	172.31.128.7	2025-04-04 18:08:23.50431	8
5242	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.7	2025-04-04 18:21:03.893548	8
5243	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.7	2025-04-04 18:21:07.470787	8
5244	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	172.31.128.7	2025-04-04 18:21:10.915138	8
5245	GET /tasks/dashboard/labels	172.31.128.7	2025-04-04 18:21:18.742378	8
5246	GET /tasks/dashboard/labels	172.31.128.7	2025-04-04 18:21:20.572504	8
5247	GET /fichajes/	172.31.128.7	2025-04-04 18:21:21.287719	8
5248	GET /fichajes/	172.31.128.7	2025-04-04 18:21:21.980289	8
5249	GET /fichajes/company/dnln-distribucion-sl	172.31.128.7	2025-04-04 18:21:22.788017	8
5250	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.7	2025-04-04 18:21:31.575234	8
5251	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	172.31.128.7	2025-04-04 18:21:34.484432	8
5252	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.7	2025-04-04 18:27:20.187754	8
5253	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.7	2025-04-04 18:27:41.220043	8
5254	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.7	2025-04-04 18:27:49.720187	8
5255	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	172.31.128.7	2025-04-04 18:27:52.732751	8
5256	Login exitoso: admin	127.0.0.1	2025-04-04 20:09:05.588117	8
5257	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 20:09:14.291144	8
5258	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 20:09:15.191772	8
5259	GET /fichajes/dashboard	127.0.0.1	2025-04-04 20:09:16.042248	8
5260	GET /fichajes/login	127.0.0.1	2025-04-04 20:09:16.326784	8
5261	POST /fichajes/login	127.0.0.1	2025-04-04 20:09:22.701416	8
5262	GET /fichajes/dashboard	127.0.0.1	2025-04-04 20:09:23.194089	8
5263	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-04 20:09:25.793805	8
5264	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-04 20:09:29.291156	8
5265	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 20:09:38.651531	8
5266	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 20:09:40.88805	8
5267	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 20:09:41.679632	8
5268	GET /fichajes/employees/46/contract_hours	127.0.0.1	2025-04-04 20:10:11.064334	8
5269	GET /fichajes/employees/47/contract_hours	127.0.0.1	2025-04-04 20:10:18.581451	8
5270	POST /fichajes/employees/47/contract_hours	127.0.0.1	2025-04-04 20:10:22.83394	8
5271	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 20:10:23.509148	8
5272	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-04 20:10:30.531493	8
5273	GET /fichajes/record/140/signature_pad	127.0.0.1	2025-04-04 20:10:31.256282	8
5274	POST /fichajes/record/140/signature_pad	127.0.0.1	2025-04-04 20:10:34.385813	8
5275	GET /fichajes/record/140	127.0.0.1	2025-04-04 20:10:34.94355	8
5276	GET /fichajes/dashboard	127.0.0.1	2025-04-04 20:10:37.088054	8
5277	GET /fichajes/employee/47/pin	127.0.0.1	2025-04-04 20:10:38.315566	8
5278	POST /fichajes/employee/47/pin	127.0.0.1	2025-04-04 20:10:40.674057	8
5279	GET /fichajes/record/141/signature_pad	127.0.0.1	2025-04-04 20:10:41.395967	8
5280	POST /fichajes/record/141/signature_pad	127.0.0.1	2025-04-04 20:10:44.381421	8
5281	GET /fichajes/record/141	127.0.0.1	2025-04-04 20:10:44.969842	8
5282	GET /fichajes/dashboard	127.0.0.1	2025-04-04 20:10:46.651259	8
5283	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-04 20:10:47.861216	8
5284	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-04 20:10:49.923807	8
5285	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-04 20:10:51.249495	8
5286	GET /fichajes/record/142	127.0.0.1	2025-04-04 20:10:51.977559	8
5287	GET /fichajes/dashboard	127.0.0.1	2025-04-04 20:10:54.009264	8
5288	GET /fichajes/employee/47/pin	127.0.0.1	2025-04-04 20:10:55.119631	8
5289	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-04 20:10:56.878761	8
5290	POST /fichajes/employee/47/pin	127.0.0.1	2025-04-04 20:10:57.854144	8
5291	GET /fichajes/record/143	127.0.0.1	2025-04-04 20:10:58.588394	8
5292	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 20:11:04.637805	8
5293	GET /fichajes/dashboard	127.0.0.1	2025-04-04 20:11:11.152339	8
5294	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 20:11:14.345188	8
5295	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 20:11:35.639536	8
5296	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 20:11:56.557263	8
5297	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 20:12:02.137891	8
5298	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 20:12:04.730286	8
5299	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 20:12:07.664575	8
5300	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-04 20:12:12.856528	8
5301	GET /fichajes/	127.0.0.1	2025-04-04 20:12:24.353091	8
5302	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 20:12:24.758233	8
5303	GET /fichajes/employee/47/pin	127.0.0.1	2025-04-04 20:13:22.58415	8
5304	Login exitoso: admin	127.0.0.1	2025-04-04 21:04:03.274332	8
5305	Login exitoso: admin	127.0.0.1	2025-04-04 21:12:00.984157	8
5306	GET /tasks/	127.0.0.1	2025-04-04 21:12:57.783907	8
5307	GET /tasks/locations/create	127.0.0.1	2025-04-04 21:12:59.899612	8
5308	GET /fichajes/checkpoints	127.0.0.1	2025-04-04 21:48:03.701958	8
5309	GET /fichajes/	127.0.0.1	2025-04-04 21:48:04.163141	8
5310	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-04 21:48:04.563417	8
5311	POST /tasks/locations/create	127.0.0.1	2025-04-04 22:03:07.494795	8
5312	Local creado: Chimeneas	127.0.0.1	2025-04-04 22:03:07.769728	8
5313	GET /tasks/locations	127.0.0.1	2025-04-04 22:03:08.263546	8
5314	POST /employees/47/toggle-active	127.0.0.1	2025-04-04 22:04:00.334859	8
5315	Empleado desactivado: Lucia Mendez	127.0.0.1	2025-04-04 22:04:00.606628	8
5316	GET /	127.0.0.1	2025-04-04 22:04:12.65564	8
5317	GET /	127.0.0.1	2025-04-04 22:04:12.947946	8
5318	Login exitoso: admin	172.31.128.42	2025-04-04 22:13:17.297785	8
5319	POST /employees/46/toggle-active	172.31.128.42	2025-04-04 22:16:29.976337	8
5320	Empleado desactivado: Claudio Rad	172.31.128.42	2025-04-04 22:16:30.732558	8
5321	Login exitoso: admin	127.0.0.1	2025-04-05 08:07:00.517359	8
5322	GET /fichajes/company/100rcs-sl	127.0.0.1	2025-04-05 08:07:00.999829	8
5323	GET /fichajes/	127.0.0.1	2025-04-05 08:07:01.413499	8
5324	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 08:07:01.907098	8
5325	GET /fichajes/checkpoints/8/edit	127.0.0.1	2025-04-05 08:07:44.944609	8
5326	GET /fichajes/checkpoints	127.0.0.1	2025-04-05 08:08:13.30449	8
5327	Login exitoso: admin	127.0.0.1	2025-04-05 08:09:27.233132	8
5328	GET /fichajes/	127.0.0.1	2025-04-05 08:09:44.419728	8
5329	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 08:09:44.826813	8
5330	GET /fichajes/login	127.0.0.1	2025-04-05 08:09:55.617234	8
5331	POST /fichajes/login	127.0.0.1	2025-04-05 08:09:58.002346	8
5332	GET /fichajes/dashboard	127.0.0.1	2025-04-05 08:09:58.507032	8
5333	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-05 08:10:01.359065	8
5334	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-05 08:10:05.059136	8
5335	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-05 08:10:06.559328	8
5336	GET /fichajes/record/142/signature_pad	127.0.0.1	2025-04-05 08:10:07.303454	8
5337	POST /fichajes/record/142/signature_pad	127.0.0.1	2025-04-05 08:10:15.059021	8
5338	GET /fichajes/record/142	127.0.0.1	2025-04-05 08:10:15.697668	8
5339	GET /fichajes/dashboard	127.0.0.1	2025-04-05 08:10:17.800604	8
5340	GET /fichajes/employee/47/pin	127.0.0.1	2025-04-05 08:10:19.490717	8
5341	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-05 08:10:23.439835	8
5342	POST /fichajes/employee/47/pin	127.0.0.1	2025-04-05 08:10:26.829989	8
5343	GET /fichajes/record/143/signature_pad	127.0.0.1	2025-04-05 08:10:27.539971	8
5344	POST /fichajes/record/143/signature_pad	127.0.0.1	2025-04-05 08:10:32.123396	8
5345	GET /fichajes/record/143	127.0.0.1	2025-04-05 08:10:32.724827	8
5346	GET /	127.0.0.1	2025-04-05 08:10:33.628295	8
5347	GET /	127.0.0.1	2025-04-05 08:10:33.931452	8
5348	GET /fichajes/dashboard	127.0.0.1	2025-04-05 08:10:36.891494	8
5349	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-05 08:10:38.20298	8
5350	GET /fichajes/	127.0.0.1	2025-04-05 08:10:42.187176	8
5351	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 08:10:42.605983	8
5352	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 08:11:45.500117	8
5353	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	127.0.0.1	2025-04-05 08:12:36.086592	8
5354	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 08:13:19.049819	8
5355	GET /fichajes/records/export	127.0.0.1	2025-04-05 08:13:39.768574	8
5356	POST /fichajes/records/export	127.0.0.1	2025-04-05 08:13:55.353743	8
5357	Login exitoso: admin	172.31.128.9	2025-04-05 08:22:45.063641	8
5358	GET /tasks/dashboard/labels	172.31.128.9	2025-04-05 08:22:56.910279	8
5359	GET /fichajes/	172.31.128.9	2025-04-05 08:22:59.835184	8
5360	GET /fichajes/company/dnln-distribucion-sl	172.31.128.9	2025-04-05 08:23:00.983354	8
5361	GET /fichajes/records/export	172.31.128.9	2025-04-05 08:23:08.76842	8
5362	POST /fichajes/records/export	172.31.128.9	2025-04-05 08:23:23.01092	8
5363	GET /fichajes/	172.31.128.9	2025-04-05 08:24:29.740777	8
5364	GET /fichajes/company/dnln-distribucion-sl	172.31.128.9	2025-04-05 08:24:30.583577	8
5365	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.9	2025-04-05 08:24:42.016696	8
5366	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	172.31.128.9	2025-04-05 08:24:45.31633	8
5367	GET /fichajes/company/dnln-distribucion-sl	172.31.128.9	2025-04-05 08:28:32.481789	8
5368	GET /fichajes/records/export	172.31.128.9	2025-04-05 08:28:44.736192	8
5369	GET /fichajes/records/export	172.31.128.9	2025-04-05 08:28:51.281446	8
5370	POST /fichajes/records/export	172.31.128.9	2025-04-05 08:29:02.657605	8
5371	GET /fichajes/records/export	172.31.128.9	2025-04-05 08:32:19.034923	8
5372	GET /fichajes/	172.31.128.9	2025-04-05 08:32:23.578333	8
5373	GET /fichajes/company/dnln-distribucion-sl	172.31.128.9	2025-04-05 08:32:24.395536	8
5374	GET /fichajes/records/export	172.31.128.9	2025-04-05 08:32:32.492051	8
5375	POST /fichajes/records/export	172.31.128.9	2025-04-05 08:32:51.137178	8
5376	GET /fichajes/records/export	172.31.128.9	2025-04-05 08:41:00.313788	8
5377	GET /tasks/	127.0.0.1	2025-04-05 15:12:51.861042	8
5378	GET /tasks/locations/6	127.0.0.1	2025-04-05 15:12:52.323477	8
5379	GET /fichajes/	127.0.0.1	2025-04-05 15:13:09.726093	8
5380	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 15:13:10.130168	8
5381	GET /fichajes/dashboard	127.0.0.1	2025-04-05 15:13:58.188962	8
5382	GET /fichajes/employee/47/pin	127.0.0.1	2025-04-05 15:14:14.50997	8
5383	POST /fichajes/employee/47/pin	127.0.0.1	2025-04-05 15:14:17.093877	8
5384	GET /fichajes/record/144	127.0.0.1	2025-04-05 15:14:17.741687	8
5385	GET /fichajes/dashboard	127.0.0.1	2025-04-05 15:14:22.062265	8
5386	GET /fichajes/	127.0.0.1	2025-04-05 15:15:14.312371	8
5387	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 15:15:14.756891	8
5388	GET /fichajes/checkpoints/8/edit	127.0.0.1	2025-04-05 15:15:21.145588	8
5389	POST /fichajes/checkpoints/8/edit	127.0.0.1	2025-04-05 15:15:47.331663	8
5390	GET /fichajes/checkpoints	127.0.0.1	2025-04-05 15:15:47.95048	8
5391	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 15:16:07.704343	8
5392	GET /fichajes/employee/47/pin	127.0.0.1	2025-04-05 15:25:55.093294	8
5393	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 15:25:59.958676	8
5394	GET /fichajes/checkpoints	127.0.0.1	2025-04-05 15:26:20.455559	8
5395	GET /fichajes/company/dnln-distribucion-sl/original	127.0.0.1	2025-04-05 15:26:23.159772	8
5396	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 15:26:39.119019	8
5397	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 15:26:49.930997	8
5398	GET /fichajes/	127.0.0.1	2025-04-05 15:26:59.898738	8
5399	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 15:27:00.299405	8
5400	GET /fichajes/	127.0.0.1	2025-04-05 15:36:15.59177	8
5401	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 15:36:16.02858	8
5402	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 15:36:21.824601	8
5403	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 15:36:26.242054	8
5404	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 15:36:48.987338	8
5405	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 15:37:45.917346	8
5406	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 15:37:49.184801	8
5407	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 15:37:52.682428	8
5408	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 15:38:01.058131	8
5409	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 15:38:14.101481	8
5410	GET /fichajes/	127.0.0.1	2025-04-05 15:39:42.921458	8
5411	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 15:39:43.338452	8
5412	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-05 15:39:48.571837	8
5413	POST /fichajes/employee/47/pin	127.0.0.1	2025-04-05 15:39:50.120013	8
5414	GET /fichajes/record/145	127.0.0.1	2025-04-05 15:39:50.807932	8
5415	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 15:39:56.587121	8
5416	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 15:40:06.007491	8
5417	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 15:40:18.325408	8
5418	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	127.0.0.1	2025-04-05 15:40:23.097783	8
5419	GET /fichajes/	127.0.0.1	2025-04-05 15:40:55.423619	8
5420	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 15:40:55.96191	8
5421	GET /fichajes/records	127.0.0.1	2025-04-05 15:42:37.879113	8
5422	GET /fichajes/delete_records	127.0.0.1	2025-04-05 15:42:41.700707	8
5423	POST /fichajes/delete_records	127.0.0.1	2025-04-05 15:42:55.812598	8
5424	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 15:42:56.470303	8
5425	GET /fichajes/	127.0.0.1	2025-04-05 15:43:40.926382	8
5426	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 15:43:41.332071	8
5427	GET /fichajes/	127.0.0.1	2025-04-05 15:51:52.232898	8
5428	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 15:51:52.72713	8
5429	GET /fichajes/records	127.0.0.1	2025-04-05 15:51:59.68922	8
5430	GET /fichajes/delete_records	127.0.0.1	2025-04-05 15:52:05.771949	8
5431	POST /fichajes/delete_records	127.0.0.1	2025-04-05 15:52:23.732807	8
5432	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 15:52:24.430165	8
5433	GET /fichajes/records	127.0.0.1	2025-04-05 15:52:37.975545	8
5434	GET /fichajes/delete_records	127.0.0.1	2025-04-05 15:53:07.399199	8
5435	POST /fichajes/delete_records	127.0.0.1	2025-04-05 15:53:17.776722	8
5436	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 15:53:18.480054	8
5437	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 16:00:11.550068	8
5438	GET /fichajes/records	127.0.0.1	2025-04-05 16:00:19.964218	8
5439	GET /fichajes/delete_records	127.0.0.1	2025-04-05 16:00:29.325714	8
5440	POST /fichajes/delete_records	127.0.0.1	2025-04-05 16:00:41.987766	8
5441	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 16:00:42.706185	8
5442	POST /fichajes/delete_records	127.0.0.1	2025-04-05 16:00:52.516222	8
5443	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 16:00:53.213819	8
5444	GET /fichajes/	127.0.0.1	2025-04-05 16:00:58.396843	8
5445	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 16:00:58.814923	8
5446	GET /fichajes/dashboard	127.0.0.1	2025-04-05 16:01:54.567159	8
5447	GET /fichajes/employee/47/pin	127.0.0.1	2025-04-05 16:01:56.254452	8
5448	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-05 16:02:00.478479	8
5449	GET /fichajes/dashboard	127.0.0.1	2025-04-05 16:02:02.245403	8
5450	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 16:02:38.743037	8
5451	GET /fichajes/employee/47/pin	127.0.0.1	2025-04-05 16:10:01.650285	8
5452	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-05 16:10:05.097563	8
5453	POST /fichajes/employee/47/pin	127.0.0.1	2025-04-05 16:15:44.256643	8
5454	GET /fichajes/record/146	127.0.0.1	2025-04-05 16:15:44.949302	8
5455	POST /fichajes/record/146/checkout	127.0.0.1	2025-04-05 16:16:13.403478	8
5456	GET /fichajes/record/146/signature_pad	127.0.0.1	2025-04-05 16:16:14.117557	8
5457	POST /fichajes/record/146/signature_pad	127.0.0.1	2025-04-05 16:16:18.441723	8
5458	GET /fichajes/record/146	127.0.0.1	2025-04-05 16:16:18.996218	8
5459	GET /fichajes/dashboard	127.0.0.1	2025-04-05 16:16:38.492514	8
5460	GET /fichajes/employee/47/pin	127.0.0.1	2025-04-05 16:16:41.798964	8
5461	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-05 16:16:48.307528	8
5462	POST /fichajes/employee/47/pin	127.0.0.1	2025-04-05 16:16:56.598569	8
5463	GET /fichajes/record/147	127.0.0.1	2025-04-05 16:16:57.207036	8
5464	GET /fichajes/	127.0.0.1	2025-04-05 16:17:04.016782	8
5465	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 16:17:04.400424	8
5466	GET /fichajes/checkpoints/8/edit	127.0.0.1	2025-04-05 16:17:11.08228	8
5467	POST /fichajes/checkpoints/8/edit	127.0.0.1	2025-04-05 16:17:24.582009	8
5468	GET /fichajes/checkpoints	127.0.0.1	2025-04-05 16:17:25.253884	8
5469	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-05 16:22:03.037413	8
5470	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	127.0.0.1	2025-04-05 16:22:08.194504	8
5471	GET /fichajes/checkpoints	127.0.0.1	2025-04-05 16:23:30.453486	8
5472	GET /fichajes/	127.0.0.1	2025-04-05 16:23:37.280436	8
5473	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-05 16:23:37.685975	8
5475	GET /login	172.31.128.37	2025-04-06 15:35:14.515756	8
5476	GET /fichajes/	172.31.128.37	2025-04-06 15:35:38.74108	8
5477	GET /fichajes/company/dnln-distribucion-sl	172.31.128.37	2025-04-06 15:35:41.561085	8
5478	GET /fichajes/records	172.31.128.37	2025-04-06 15:35:58.30578	8
5479	GET /fichajes/delete_records	172.31.128.37	2025-04-06 15:36:17.686374	8
5480	POST /fichajes/delete_records	172.31.128.37	2025-04-06 15:36:36.043869	8
5481	GET /fichajes/company/dnln-distribucion-sl	172.31.128.37	2025-04-06 15:36:41.365623	8
5482	GET /fichajes/	172.31.128.37	2025-04-06 15:37:05.264642	8
5483	GET /fichajes/company/dnln-distribucion-sl	172.31.128.37	2025-04-06 15:37:08.217592	8
5484	GET /fichajes/login	172.31.128.37	2025-04-06 15:37:28.347322	8
5485	GET /fichajes/dashboard	172.31.128.37	2025-04-06 15:37:31.100876	8
5486	GET /fichajes/employee/47/pin	172.31.128.37	2025-04-06 15:37:39.940003	8
5487	POST /fichajes/api/validate-pin	172.31.128.37	2025-04-06 15:37:50.232479	8
5488	POST /fichajes/employee/47/pin	172.31.128.37	2025-04-06 15:37:57.718321	8
5489	GET /fichajes/record/148	172.31.128.37	2025-04-06 15:38:03.039354	8
5490	POST /fichajes/record/148/checkout	172.31.128.37	2025-04-06 15:38:09.015376	8
5491	GET /fichajes/record/148/signature_pad	172.31.128.37	2025-04-06 15:38:15.060193	8
5492	POST /fichajes/record/148/signature_pad	172.31.128.37	2025-04-06 15:38:23.070963	8
5493	GET /fichajes/record/148	172.31.128.37	2025-04-06 15:38:27.921178	8
5494	GET /fichajes/dashboard	172.31.128.37	2025-04-06 15:38:33.107548	8
5495	GET /fichajes/employee/47/pin	172.31.128.37	2025-04-06 15:38:47.931557	8
5496	POST /fichajes/api/validate-pin	172.31.128.37	2025-04-06 15:38:54.858819	8
5497	POST /fichajes/employee/47/pin	172.31.128.37	2025-04-06 15:39:02.516542	8
5498	GET /fichajes/record/149	172.31.128.37	2025-04-06 15:39:07.802218	8
5499	GET /	172.31.128.37	2025-04-06 15:39:19.58178	8
5500	GET /fichajes/	172.31.128.37	2025-04-06 15:39:32.02846	8
5501	GET /fichajes/company/dnln-distribucion-sl	172.31.128.37	2025-04-06 15:39:34.76733	8
5502	GET /fichajes/checkpoints/8/edit	172.31.128.37	2025-04-06 15:40:10.448761	8
5503	POST /fichajes/checkpoints/8/edit	172.31.128.37	2025-04-06 15:40:32.415362	8
5504	GET /fichajes/checkpoints	172.31.128.37	2025-04-06 15:40:36.628301	8
5505	GET /fichajes/run_closer	172.31.128.37	2025-04-06 15:40:49.741085	8
5506	GET /fichajes/dashboard	172.31.128.37	2025-04-06 15:41:05.146907	8
5507	GET /fichajes/dashboard	172.31.128.37	2025-04-06 15:41:15.596452	8
5508	GET /fichajes/employee/47/pin	172.31.128.37	2025-04-06 15:41:35.749004	8
5509	POST /fichajes/employee/47/pin	172.31.128.37	2025-04-06 15:41:44.206778	8
5510	GET /fichajes/record/150	172.31.128.37	2025-04-06 15:41:49.610525	8
5511	GET /fichajes/record/150	172.31.128.5	2025-04-06 16:11:49.373531	8
5512	GET /fichajes/dashboard	172.31.128.5	2025-04-06 16:11:56.003986	8
5513	GET /fichajes/employee/47/pin	172.31.128.5	2025-04-06 16:12:01.179659	8
5514	POST /fichajes/api/validate-pin	172.31.128.5	2025-04-06 16:12:07.80053	8
5515	POST /fichajes/employee/47/pin	172.31.128.5	2025-04-06 16:12:13.01354	8
5516	GET /fichajes/record/151	172.31.128.5	2025-04-06 16:12:18.298749	8
5517	GET /	172.31.128.5	2025-04-06 16:12:26.364331	8
5518	GET /fichajes/	172.31.128.5	2025-04-06 16:12:42.031388	8
5519	GET /fichajes/company/dnln-distribucion-sl	172.31.128.5	2025-04-06 16:12:44.739119	8
5520	GET /fichajes/records	172.31.128.5	2025-04-06 16:13:02.797799	8
5521	GET /fichajes/	172.31.128.5	2025-04-06 16:13:30.269709	8
5522	GET /fichajes/company/dnln-distribucion-sl	172.31.128.5	2025-04-06 16:13:32.999821	8
5523	GET /fichajes/checkpoints/8/records	172.31.128.5	2025-04-06 16:13:55.836625	8
5524	GET /fichajes/checkpoints/	172.31.128.5	2025-04-06 16:14:09.656127	8
5525	GET /	172.31.128.5	2025-04-06 16:14:18.526327	8
5526	GET /fichajes/	172.31.128.5	2025-04-06 16:14:36.773496	8
5527	GET /fichajes/company/dnln-distribucion-sl	172.31.128.5	2025-04-06 16:14:39.499951	8
5528	GET /fichajes/	172.31.128.5	2025-04-06 16:14:46.960453	8
5529	GET /fichajes/company/dnln-distribucion-sl	172.31.128.5	2025-04-06 16:14:49.737129	8
5530	GET /fichajes/	172.31.128.5	2025-04-06 16:14:56.938832	8
5531	GET /fichajes/company/dnln-distribucion-sl	172.31.128.5	2025-04-06 16:14:59.664852	8
5532	GET /fichajes/incidents	172.31.128.5	2025-04-06 16:15:29.466534	8
5533	GET /fichajes/	172.31.128.5	2025-04-06 16:15:39.763235	8
5534	GET /fichajes/company/dnln-distribucion-sl	172.31.128.5	2025-04-06 16:15:43.665684	8
5535	GET /fichajes/	172.31.128.5	2025-04-06 16:16:33.560111	8
5536	GET /fichajes/company/dnln-distribucion-sl	172.31.128.5	2025-04-06 16:16:36.335135	8
5537	GET /fichajes/records	172.31.128.5	2025-04-06 16:16:56.741414	8
5538	GET /fichajes/records/151/adjust	172.31.128.5	2025-04-06 16:17:11.154925	8
5539	GET /	172.31.128.5	2025-04-06 16:17:23.27126	8
5540	GET /chcekpoints	172.31.128.5	2025-04-06 16:17:25.887092	8
5541	GET /chekpoints	172.31.128.5	2025-04-06 16:17:43.848205	8
5542	GET /fichajes/	172.31.128.5	2025-04-06 16:18:10.537722	8
5543	GET /fichajes/company/dnln-distribucion-sl	172.31.128.5	2025-04-06 16:18:13.170508	8
5544	GET /fichajes/	172.31.128.5	2025-04-06 16:18:20.327877	8
5545	GET /fichajes/company/dnln-distribucion-sl	172.31.128.5	2025-04-06 16:18:22.979182	8
5546	GET /fichajes/records	172.31.128.5	2025-04-06 16:19:28.782262	8
5547	GET /fichajes/	172.31.128.5	2025-04-06 16:19:44.481752	8
5548	GET /fichajes/company/dnln-distribucion-sl	172.31.128.5	2025-04-06 16:19:47.163214	8
5549	GET /fichajes/company/dnln-distribucion-sl	172.31.128.5	2025-04-06 16:22:18.125529	8
5550	GET /fichajes/login	172.31.128.5	2025-04-06 16:22:25.304214	8
5551	GET /fichajes/dashboard	172.31.128.5	2025-04-06 16:22:26.877854	8
5552	GET /fichajes/employee/47/pin	172.31.128.5	2025-04-06 16:22:31.234842	8
5553	POST /fichajes/api/validate-pin	172.31.128.5	2025-04-06 16:22:38.320874	8
5554	GET /	172.31.128.5	2025-04-06 16:22:49.373521	8
5555	GET /fichajes/	172.31.128.5	2025-04-06 16:23:03.883175	8
5556	GET /fichajes/company/dnln-distribucion-sl	172.31.128.5	2025-04-06 16:23:06.612913	8
5557	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.5	2025-04-06 16:23:23.635086	8
5558	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	172.31.128.5	2025-04-06 16:23:31.30979	8
5559	Login exitoso: admin	127.0.0.1	2025-04-06 18:32:41.891598	8
5560	GET /fichajes/	127.0.0.1	2025-04-06 18:32:51.688913	8
5561	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-06 18:32:52.130837	8
5562	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-06 18:32:59.07387	8
5563	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	127.0.0.1	2025-04-06 18:33:04.339453	8
5564	GET /login	172.31.128.19	2025-04-06 20:30:25.726053	8
5565	GET /fichajes/	172.31.128.19	2025-04-06 20:30:36.689403	8
5566	GET /fichajes/company/dnln-distribucion-sl	172.31.128.19	2025-04-06 20:30:39.375688	8
5567	GET /fichajes/	172.31.128.19	2025-04-06 20:30:46.492036	8
5568	GET /fichajes/company/dnln-distribucion-sl	172.31.128.19	2025-04-06 20:30:49.251376	8
5569	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.19	2025-04-06 20:31:07.900146	8
5570	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.19	2025-04-06 20:46:48.495999	8
5571	GET /fichajes/company/dnln-distribucion-sl	172.31.128.19	2025-04-06 20:47:03.331658	8
5572	GET /fichajes/company/dnln-distribucion-sl	172.31.128.19	2025-04-06 20:54:54.9295	8
5573	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.19	2025-04-06 20:55:13.906548	8
5574	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.19	2025-04-06 20:55:36.774212	8
5575	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	172.31.128.19	2025-04-06 20:55:47.748418	8
5576	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.19	2025-04-06 20:56:04.307946	8
5577	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.19	2025-04-06 20:56:13.788001	8
5578	GET /fichajes/	172.31.128.19	2025-04-06 21:12:19.97003	8
5579	GET /fichajes/company/dnln-distribucion-sl	172.31.128.19	2025-04-06 21:12:22.729372	8
5580	GET /fichajes/login	172.31.128.19	2025-04-06 21:13:28.581541	8
5581	GET /fichajes/dashboard	172.31.128.19	2025-04-06 21:13:30.138876	8
5582	GET /fichajes/company/dnln-distribucion-sl	172.31.128.19	2025-04-06 21:13:39.089088	8
5583	GET /fichajes/login	172.31.128.19	2025-04-06 21:13:52.533224	8
5584	GET /fichajes/dashboard	172.31.128.19	2025-04-06 21:13:54.46926	8
5585	GET /fichajes/employees/47/contract_hours	172.31.128.19	2025-04-06 21:13:58.891187	8
5586	POST /fichajes/employees/47/contract_hours	172.31.128.19	2025-04-06 21:14:13.892935	8
5587	GET /fichajes/company/dnln-distribucion-sl	172.31.128.19	2025-04-06 21:14:18.276335	8
5588	GET /fichajes/employee/47/pin	172.31.128.19	2025-04-06 21:14:25.469354	8
5589	POST /fichajes/employee/47/pin	172.31.128.19	2025-04-06 21:14:34.327142	8
5590	GET /fichajes/record/152	172.31.128.19	2025-04-06 21:14:39.763915	8
5591	POST /fichajes/record/152/checkout	172.31.128.19	2025-04-06 21:15:15.985453	8
5592	GET /fichajes/record/152/signature_pad	172.31.128.19	2025-04-06 21:15:21.995286	8
5593	GET /fichajes/company/dnln-distribucion-sl	172.31.128.19	2025-04-06 21:15:31.787316	8
5594	POST /fichajes/record/152/signature_pad	172.31.128.19	2025-04-06 21:15:59.304856	8
5595	GET /fichajes/record/152	172.31.128.19	2025-04-06 21:16:03.880617	8
5596	GET /fichajes/dashboard	172.31.128.19	2025-04-06 21:16:09.587105	8
5597	GET /fichajes/employee/47/pin	172.31.128.19	2025-04-06 21:16:23.397221	8
5598	POST /fichajes/api/validate-pin	172.31.128.19	2025-04-06 21:16:29.898877	8
5599	POST /fichajes/employee/47/pin	172.31.128.19	2025-04-06 21:16:34.09462	8
5600	GET /fichajes/record/153	172.31.128.19	2025-04-06 21:16:39.314126	8
5601	GET /fichajes/company/dnln-distribucion-sl	172.31.128.19	2025-04-06 21:16:48.540463	8
5602	GET /fichajes/records/153/adjust	172.31.128.19	2025-04-06 21:17:05.528593	8
5603	POST /fichajes/records/153/adjust	172.31.128.19	2025-04-06 21:17:21.025672	8
5604	GET /fichajes/checkpoints/8/records	172.31.128.19	2025-04-06 21:17:25.403475	8
5605	GET /fichajes/dashboard	172.31.128.19	2025-04-06 21:17:44.260729	8
5606	GET /fichajes/employee/47/pin	172.31.128.19	2025-04-06 21:18:08.484138	8
5607	POST /fichajes/api/validate-pin	172.31.128.19	2025-04-06 21:18:16.881383	8
5608	POST /fichajes/employee/47/pin	172.31.128.19	2025-04-06 21:18:37.161698	8
5609	GET /fichajes/record/153/signature_pad	172.31.128.19	2025-04-06 21:18:43.938457	8
5610	POST /fichajes/record/153/signature_pad	172.31.128.19	2025-04-06 21:18:50.718008	8
5611	GET /fichajes/record/153	172.31.128.19	2025-04-06 21:18:55.503383	8
5612	GET /fichajes/checkpoints/8/records	172.31.128.19	2025-04-06 21:19:07.608464	8
5613	GET /fichajes/	172.31.128.19	2025-04-06 21:19:28.727025	8
5614	GET /fichajes/company/dnln-distribucion-sl	172.31.128.19	2025-04-06 21:19:31.636492	8
5615	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	172.31.128.19	2025-04-06 21:19:49.13751	8
5616	GET /fichajes/company/dnln-distribucion-sl/rrrrrr/export	172.31.128.19	2025-04-06 21:20:08.355232	8
5617	GET /fichajes/	172.31.128.19	2025-04-06 21:24:08.45378	8
5618	GET /fichajes/company/dnln-distribucion-sl	172.31.128.19	2025-04-06 21:24:11.233099	8
5619	GET /fichajes/	172.31.128.19	2025-04-06 21:27:27.085121	8
5620	GET /fichajes/company/dnln-distribucion-sl	172.31.128.19	2025-04-06 21:27:29.787768	8
5621	Login exitoso: admin	127.0.0.1	2025-04-07 15:44:01.754426	8
5622	GET /checkins/employee/47	127.0.0.1	2025-04-07 15:44:27.416928	8
5623	GET /checkins/employee/47/new	127.0.0.1	2025-04-07 15:44:43.231196	8
5624	GET /schedules/employee/47	127.0.0.1	2025-04-07 15:46:09.322377	8
5625	GET /schedules/employee/47/weekly	127.0.0.1	2025-04-07 15:46:13.271476	8
5626	POST /schedules/employee/47/weekly	127.0.0.1	2025-04-07 15:46:25.125907	8
5627	Horarios semanales actualizados para Lucia Mendez	127.0.0.1	2025-04-07 15:46:25.711489	8
5628	GET /schedules/employee/47	127.0.0.1	2025-04-07 15:46:26.099074	8
5629	GET /checkins/employee/46	127.0.0.1	2025-04-07 15:47:05.22984	8
5630	GET /fichajes/company/dnln-distribucion-sl/rrrrrr	127.0.0.1	2025-04-07 17:15:03.713453	8
5631	GET /companies/	127.0.0.1	2025-04-07 17:15:17.986249	8
5632	GET /checkins/employee/47	127.0.0.1	2025-04-07 17:15:27.892884	8
5633	GET /checkins/employee/47/generate	127.0.0.1	2025-04-07 17:15:44.474364	8
5634	POST /checkins/employee/47/generate	127.0.0.1	2025-04-07 17:16:01.511797	8
5635	Fichajes generados para Lucia Mendez	127.0.0.1	2025-04-07 17:16:01.824102	8
5636	GET /checkins/employee/47	127.0.0.1	2025-04-07 17:16:02.112415	8
5637	GET /fichajes/	127.0.0.1	2025-04-07 17:16:53.966107	8
5638	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-07 17:16:54.49667	8
5639	POST /employees/47/toggle-active	127.0.0.1	2025-04-07 17:17:18.361729	8
5640	Empleado activado: Lucia Mendez	127.0.0.1	2025-04-07 17:17:18.682559	8
5641	POST /employees/47/toggle-active	127.0.0.1	2025-04-07 17:17:34.462111	8
5642	Empleado desactivado: Lucia Mendez	127.0.0.1	2025-04-07 17:17:34.787327	8
5643	GET /checkins/employee/46	127.0.0.1	2025-04-07 17:18:18.089357	8
5644	GET /checkins/employee/47	127.0.0.1	2025-04-07 17:18:34.373936	8
5645	GET /schedules/employee/47/weekly	127.0.0.1	2025-04-07 17:18:39.364257	8
5646	GET /schedules/employee/47	127.0.0.1	2025-04-07 17:18:48.73475	8
5647	GET /checkins/employee/47	127.0.0.1	2025-04-07 17:18:59.67135	8
5648	GET /checkins/employee/47/generate	127.0.0.1	2025-04-07 17:19:01.621719	8
5649	POST /checkins/employee/47/generate	127.0.0.1	2025-04-07 17:19:16.936618	8
5650	Fichajes generados para Lucia Mendez	127.0.0.1	2025-04-07 17:19:17.246266	8
5651	GET /checkins/employee/47	127.0.0.1	2025-04-07 17:19:17.541922	8
5652	POST /checkins/employee/47/export	127.0.0.1	2025-04-07 17:19:42.452341	8
5653	Exportados fichajes a PDF para Lucia Mendez	127.0.0.1	2025-04-07 17:19:42.620505	8
5654	GET /checkins/employee/46	127.0.0.1	2025-04-07 17:20:46.865656	8
5655	GET /schedules/employee/46/weekly	127.0.0.1	2025-04-07 17:20:55.783315	8
5656	POST /schedules/employee/46/weekly	127.0.0.1	2025-04-07 17:21:08.142411	8
5657	Horarios semanales actualizados para Claudio Rad	127.0.0.1	2025-04-07 17:21:08.84419	8
5658	GET /schedules/employee/46	127.0.0.1	2025-04-07 17:21:09.145589	8
5659	GET /checkins/employee/46	127.0.0.1	2025-04-07 17:21:14.018787	8
5660	GET /checkins/employee/46	127.0.0.1	2025-04-07 17:21:35.105658	8
5661	GET /checkins/employee/46	127.0.0.1	2025-04-07 17:22:23.013096	8
5662	GET /fichajes/	127.0.0.1	2025-04-07 17:37:05.080466	8
5663	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-07 17:37:05.569454	8
5664	GET /fichajes/records/export	127.0.0.1	2025-04-07 17:37:36.803767	8
5665	POST /fichajes/records/export	127.0.0.1	2025-04-07 17:37:47.523738	8
5666	GET /checkins/employee/47	127.0.0.1	2025-04-07 17:38:05.112408	8
5667	POST /employees/47/toggle-active	127.0.0.1	2025-04-07 17:43:32.131582	8
5668	Empleado activado: Lucia Mendez	127.0.0.1	2025-04-07 17:43:32.46421	8
5669	GET /fichajes/	127.0.0.1	2025-04-07 17:43:47.382727	8
5670	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-07 17:43:47.758483	8
5671	GET /fichajes/login	127.0.0.1	2025-04-07 17:43:52.286178	8
5672	POST /fichajes/login	127.0.0.1	2025-04-07 17:43:55.743793	8
5673	GET /fichajes/dashboard	127.0.0.1	2025-04-07 17:43:56.240434	8
5674	GET /fichajes/dashboard	127.0.0.1	2025-04-07 17:44:01.305439	8
5675	GET /fichajes/api/company-employees	127.0.0.1	2025-04-07 17:44:05.639897	8
5676	GET /fichajes/dashboard	127.0.0.1	2025-04-07 17:44:08.09794	8
5677	POST /employees/47/status	127.0.0.1	2025-04-07 17:44:50.365997	8
5678	Estado de empleado actualizado: Lucia Mendez	127.0.0.1	2025-04-07 17:44:50.636022	8
5679	GET /fichajes/api/company-employees	127.0.0.1	2025-04-07 17:44:59.872021	8
5680	GET /fichajes/dashboard	127.0.0.1	2025-04-07 17:45:02.98811	8
5681	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-07 17:45:09.415545	8
5682	GET /fichajes/	127.0.0.1	2025-04-07 17:45:15.481786	8
5683	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-07 17:45:15.857367	8
5684	GET /fichajes/login	127.0.0.1	2025-04-07 17:45:24.084322	8
5685	GET /fichajes/dashboard	127.0.0.1	2025-04-07 17:45:24.35638	8
5686	POST /employees/47/toggle-active	127.0.0.1	2025-04-07 17:46:22.944278	8
5687	Empleado desactivado: Lucia Mendez	127.0.0.1	2025-04-07 17:46:23.24564	8
5688	GET /fichajes/api/company-employees	127.0.0.1	2025-04-07 17:46:29.532828	8
5689	GET /fichajes/api/company-employees	127.0.0.1	2025-04-07 17:47:15.604771	8
5690	GET /fichajes/dashboard	127.0.0.1	2025-04-07 17:47:18.347886	8
5691	POST /employees/47/status	127.0.0.1	2025-04-07 17:47:52.624488	8
5692	Estado de empleado actualizado: Lucia Mendez	127.0.0.1	2025-04-07 17:47:52.936286	8
5693	GET /fichajes/api/company-employees	127.0.0.1	2025-04-07 17:48:00.70024	8
5694	GET /fichajes/dashboard	127.0.0.1	2025-04-07 17:48:03.184994	8
5695	GET /fichajes/dashboard	127.0.0.1	2025-04-07 17:48:06.570784	8
5696	GET /fichajes/dashboard	127.0.0.1	2025-04-07 17:59:27.219766	8
5697	GET /fichajes/api/company-employees	127.0.0.1	2025-04-07 17:59:31.565557	8
5698	GET /login	172.31.128.56	2025-04-07 17:59:41.46228	8
5699	GET /fichajes/	172.31.128.56	2025-04-07 18:00:36.001703	8
5700	GET /fichajes/	172.31.128.56	2025-04-07 18:00:38.678345	8
5701	GET /fichajes/company/dnln-distribucion-sl	172.31.128.56	2025-04-07 18:00:41.493523	8
5702	GET /fichajes/login	172.31.128.56	2025-04-07 18:01:02.98052	8
5703	GET /fichajes/dashboard	172.31.128.56	2025-04-07 18:01:04.57982	8
5704	POST /employees/46/toggle-active	172.31.128.56	2025-04-07 18:01:19.557366	8
5705	Empleado activado: Claudio Rad	172.31.128.56	2025-04-07 18:01:22.628332	8
5706	GET /fichajes/dashboard	172.31.128.56	2025-04-07 18:01:39.163262	8
5707	POST /employees/46/toggle-active	172.31.128.56	2025-04-07 18:01:58.111738	8
5708	Empleado desactivado: Claudio Rad	172.31.128.56	2025-04-07 18:02:01.173268	8
5709	GET /fichajes/dashboard	172.31.128.56	2025-04-07 18:02:14.671532	8
5710	POST /employees/46/edit	172.31.128.56	2025-04-07 18:03:54.695298	8
5711	POST /employees/46/toggle-active	172.31.128.56	2025-04-07 18:04:19.648952	8
5712	Empleado activado: Claudio Rad	172.31.128.56	2025-04-07 18:04:22.77059	8
5713	POST /employees/46/edit	172.31.128.56	2025-04-07 18:04:54.492366	8
5714	GET /fichajes/dashboard	172.31.128.56	2025-04-07 18:06:05.874933	8
5715	POST /employees/46/edit	172.31.128.56	2025-04-07 18:06:22.912784	8
5716	GET /fichajes/dashboard	172.31.128.56	2025-04-07 18:06:32.533476	8
5717	POST /employees/46/edit	172.31.128.56	2025-04-07 18:10:03.47354	8
5718	POST /employees/46/edit	172.31.128.56	2025-04-07 18:20:14.847172	8
5719	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:25:02.862874	8
5720	DEBUG post-form - Form end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:25:04.319239	8
5721	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:45:02.648011	8
5722	DEBUG post-form - Form end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:45:04.069201	8
5723	POST /employees/46/edit	172.31.128.56	2025-04-07 18:45:14.423152	8
5724	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:45:15.812065	8
5725	DEBUG post-form - Form end_date = 2025-04-06, tipo <class 'datetime.date'>	172.31.128.56	2025-04-07 18:45:17.211533	8
5726	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:45:36.052276	8
5801	GET /fichajes/record/156	127.0.0.1	2025-04-07 21:02:30.220262	8
5727	DEBUG post-form - Form end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:45:37.429053	8
5728	POST /employees/46/edit	172.31.128.56	2025-04-07 18:45:47.17408	8
5729	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:45:48.555398	8
5730	DEBUG post-form - Form end_date = 2025-04-08, tipo <class 'datetime.date'>	172.31.128.56	2025-04-07 18:45:49.939541	8
5731	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:45:57.774983	8
5732	DEBUG post-form - Form end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:45:59.209259	8
5733	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:47:56.433105	8
5734	DEBUG post-form - Form end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:47:57.826235	8
5735	POST /employees/46/edit	172.31.128.56	2025-04-07 18:48:13.85562	8
5736	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:48:15.286351	8
5737	DEBUG post-form - Form end_date = 2025-04-16, tipo <class 'datetime.date'>	172.31.128.56	2025-04-07 18:48:16.693562	8
5738	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:48:27.272761	8
5739	DEBUG post-form - Form end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:48:28.660788	8
5740	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:51:52.146309	8
5741	DEBUG post-form - Form end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:51:53.556374	8
5742	POST /employees/46/edit	172.31.128.56	2025-04-07 18:52:05.575281	8
5743	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:52:07.055591	8
5744	DEBUG post-form - Form end_date = 2025-04-08, tipo <class 'datetime.date'>	172.31.128.56	2025-04-07 18:52:08.460199	8
5745	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:52:39.033164	8
5746	DEBUG post-form - Form end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:52:40.439465	8
5747	POST /employees/46/edit	172.31.128.56	2025-04-07 18:53:01.483399	8
5748	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:53:02.887075	8
5749	DEBUG post-form - Form end_date = 2025-04-08, tipo <class 'datetime.date'>	172.31.128.56	2025-04-07 18:53:04.289696	8
5750	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:53:14.127888	8
5751	DEBUG post-form - Form end_date = None, tipo <class 'NoneType'>	172.31.128.56	2025-04-07 18:53:15.531418	8
5752	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.21	2025-04-07 20:13:04.538922	8
5753	DEBUG post-form - Form end_date = None, tipo <class 'NoneType'>	172.31.128.21	2025-04-07 20:13:05.957511	8
5754	POST /employees/46/edit	172.31.128.21	2025-04-07 20:13:29.98077	8
5755	DEBUG pre-form - Employee 46: end_date = None, tipo <class 'NoneType'>	172.31.128.21	2025-04-07 20:13:31.36521	8
5756	DEBUG post-form - Form end_date = 2025-04-30, tipo <class 'datetime.date'>	172.31.128.21	2025-04-07 20:13:32.76203	8
5757	DEBUG pre-form - Employee 46: end_date = 2025-04-30, tipo <class 'datetime.date'>	172.31.128.21	2025-04-07 20:39:41.483018	8
5758	DEBUG post-form - Form end_date = 2025-04-30, tipo <class 'datetime.date'>	172.31.128.21	2025-04-07 20:39:42.876846	8
5759	GET /fichajes/	172.31.128.21	2025-04-07 20:41:03.457351	8
5760	GET /fichajes/company/dnln-distribucion-sl	172.31.128.21	2025-04-07 20:41:06.201984	8
5761	GET /	127.0.0.1	2025-04-07 20:41:32.11415	8
5762	GET /fichajes/	172.31.128.21	2025-04-07 20:44:38.372455	8
5763	GET /fichajes/	127.0.0.1	2025-04-07 20:44:40.307411	8
5764	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-07 20:44:40.70225	8
5765	GET /fichajes/company/dnln-distribucion-sl	172.31.128.21	2025-04-07 20:44:41.010313	8
5766	GET /fichajes/login	127.0.0.1	2025-04-07 20:44:48.926988	8
5767	GET /fichajes/dashboard	127.0.0.1	2025-04-07 20:44:49.249131	8
5768	GET /fichajes/login	172.31.128.21	2025-04-07 20:46:41.772598	8
5769	GET /fichajes/dashboard	172.31.128.21	2025-04-07 20:46:43.352447	8
5770	GET /fichajes/dashboard	172.31.128.21	2025-04-07 20:51:41.144845	8
5771	GET /fichajes/api/company-employees	172.31.128.21	2025-04-07 20:51:49.966742	8
5772	GET /fichajes/dashboard	172.31.128.21	2025-04-07 20:51:58.952657	8
5773	GET /fichajes/employee/46/pin	172.31.128.21	2025-04-07 20:52:03.624848	8
5774	POST /fichajes/employee/46/pin	172.31.128.21	2025-04-07 20:52:09.160864	8
5775	GET /fichajes/record/154	172.31.128.21	2025-04-07 20:52:14.435962	8
5776	POST /fichajes/record/154/checkout	172.31.128.21	2025-04-07 20:52:21.771075	8
5777	GET /fichajes/record/154/signature_pad	172.31.128.21	2025-04-07 20:52:27.709978	8
5778	POST /fichajes/record/154/signature_pad	172.31.128.21	2025-04-07 20:52:33.719933	8
5779	GET /fichajes/record/154	172.31.128.21	2025-04-07 20:52:38.330322	8
5780	GET /fichajes/dashboard	172.31.128.21	2025-04-07 20:52:43.963679	8
5781	GET /fichajes/dashboard	172.31.128.21	2025-04-07 20:59:33.764728	8
5782	GET /fichajes/employee/46/pin	172.31.128.21	2025-04-07 20:59:49.791642	8
5783	POST /fichajes/employee/46/pin	172.31.128.21	2025-04-07 20:59:56.456893	8
5784	GET /fichajes/record/155	172.31.128.21	2025-04-07 21:00:01.823517	8
5785	POST /fichajes/record/155/checkout	172.31.128.21	2025-04-07 21:00:11.469689	8
5786	GET /fichajes/record/155/signature_pad	172.31.128.21	2025-04-07 21:00:17.571811	8
5787	POST /fichajes/record/155/signature_pad	172.31.128.21	2025-04-07 21:00:32.64586	8
5788	GET /fichajes/record/155	172.31.128.21	2025-04-07 21:00:37.253482	8
5789	GET /fichajes/dashboard	172.31.128.21	2025-04-07 21:00:42.845	8
5790	GET /fichajes/employee/46/pin	172.31.128.21	2025-04-07 21:00:49.151559	8
5791	POST /fichajes/employee/46/pin	172.31.128.21	2025-04-07 21:00:55.486542	8
5792	GET /fichajes/record/156	172.31.128.21	2025-04-07 21:01:03.972649	8
5793	GET /fichajes/dashboard	172.31.128.21	2025-04-07 21:01:16.565962	8
5794	GET /	172.31.128.21	2025-04-07 21:01:40.825657	8
5795	GET /	172.31.128.21	2025-04-07 21:01:47.668105	8
5796	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-07 21:02:20.444896	8
5797	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-07 21:02:24.226324	8
5798	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-07 21:02:26.011455	8
5799	GET /fichajes/record/156/signature_pad	127.0.0.1	2025-04-07 21:02:26.784424	8
5800	POST /fichajes/record/156/signature_pad	127.0.0.1	2025-04-07 21:02:29.581194	8
5802	GET /fichajes/dashboard	127.0.0.1	2025-04-07 21:02:32.341904	8
5803	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-07 21:02:33.923213	8
5804	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-07 21:02:37.331947	8
5805	GET /fichajes/	172.31.128.21	2025-04-07 21:03:15.591021	8
5806	GET /fichajes/company/dnln-distribucion-sl	172.31.128.21	2025-04-07 21:03:18.455128	8
5807	GET /fichajes/dashboard	127.0.0.1	2025-04-07 21:04:13.912053	8
5808	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-07 21:04:15.386987	8
5809	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-07 21:04:17.456302	8
5810	GET /fichajes/record/157	127.0.0.1	2025-04-07 21:04:18.211353	8
5811	POST /fichajes/record/157/checkout	127.0.0.1	2025-04-07 21:09:21.003573	8
5812	GET /fichajes/record/157/signature_pad	127.0.0.1	2025-04-07 21:09:21.936836	8
5813	POST /fichajes/record/157/signature_pad	127.0.0.1	2025-04-07 21:09:25.320831	8
5814	GET /fichajes/record/157	127.0.0.1	2025-04-07 21:09:25.923829	8
5815	GET /fichajes/dashboard	127.0.0.1	2025-04-07 21:09:28.105976	8
5816	GET /fichajes/login	172.31.128.21	2025-04-07 21:09:36.47245	8
5817	GET /fichajes/dashboard	172.31.128.21	2025-04-07 21:09:38.13626	8
5818	GET /fichajes/employee/46/pin	172.31.128.21	2025-04-07 21:09:45.021154	8
5819	POST /fichajes/api/validate-pin	172.31.128.21	2025-04-07 21:09:51.057278	8
5820	POST /fichajes/employee/46/pin	172.31.128.21	2025-04-07 21:09:58.97452	8
5821	GET /fichajes/record/158	172.31.128.21	2025-04-07 21:10:04.426071	8
5822	POST /fichajes/record/158/checkout	172.31.128.21	2025-04-07 21:10:42.264309	8
5823	GET /fichajes/record/158/signature_pad	172.31.128.21	2025-04-07 21:10:49.653715	8
5824	POST /fichajes/record/158/signature_pad	172.31.128.21	2025-04-07 21:10:56.74004	8
5825	GET /fichajes/record/158	172.31.128.21	2025-04-07 21:11:01.30246	8
5826	GET /fichajes/dashboard	172.31.128.21	2025-04-07 21:11:07.089561	8
5827	GET /fichajes/employee/46/pin	172.31.128.21	2025-04-07 21:11:13.227856	8
5828	POST /fichajes/api/validate-pin	172.31.128.21	2025-04-07 21:11:20.669726	8
5829	GET /fichajes/dashboard	172.31.128.21	2025-04-07 21:11:25.729453	8
5830	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-07 21:12:59.507817	8
5831	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:21:07.763591	8
5832	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:21:42.044282	8
5833	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:24:34.621914	8
5834	GET /fichajes/dashboard	172.31.128.25	2025-04-07 21:24:52.538496	8
5835	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:24:58.398726	8
5836	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:29:02.803587	8
5837	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 21:29:16.604342	8
5838	POST /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:29:26.722695	8
5839	GET /fichajes/record/159	172.31.128.25	2025-04-07 21:29:32.212494	8
5840	POST /fichajes/record/159/checkout	172.31.128.25	2025-04-07 21:29:49.162397	8
5841	GET /fichajes/record/159/signature_pad	172.31.128.25	2025-04-07 21:29:55.418156	8
5842	POST /fichajes/record/159/signature_pad	172.31.128.25	2025-04-07 21:30:03.921119	8
5843	GET /fichajes/record/159	172.31.128.25	2025-04-07 21:30:08.677739	8
5844	GET /fichajes/dashboard	172.31.128.25	2025-04-07 21:30:56.152236	8
5845	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:31:01.469101	8
5846	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:35:29.466118	8
5847	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:40:51.463416	8
5848	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 21:40:58.853768	8
5849	POST /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:41:04.37722	8
5850	GET /fichajes/record/160	172.31.128.25	2025-04-07 21:41:09.678712	8
5851	GET /fichajes/dashboard	172.31.128.25	2025-04-07 21:45:34.892238	8
5852	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:45:40.424385	8
5853	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 21:46:02.819005	8
5854	POST /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:46:08.760153	8
5855	GET /fichajes/record/160/signature_pad	172.31.128.25	2025-04-07 21:46:14.985967	8
5856	POST /fichajes/record/160/signature_pad	172.31.128.25	2025-04-07 21:46:22.552425	8
5857	GET /fichajes/record/160	172.31.128.25	2025-04-07 21:46:27.103508	8
5858	GET /fichajes/dashboard	172.31.128.25	2025-04-07 21:46:38.529326	8
5859	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:46:45.223401	8
5860	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 21:46:53.422316	8
5861	POST /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:46:58.093685	8
5862	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:47:03.366233	8
5863	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 21:48:44.161864	8
5864	POST /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:48:53.912218	8
5865	GET /fichajes/record/161/signature_pad	172.31.128.25	2025-04-07 21:49:00.01281	8
5866	POST /fichajes/record/161/signature_pad	172.31.128.25	2025-04-07 21:49:05.004405	8
5867	GET /fichajes/record/161	172.31.128.25	2025-04-07 21:49:09.524746	8
5868	GET /fichajes/dashboard	172.31.128.25	2025-04-07 21:53:44.933577	8
5869	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:53:50.306815	8
5870	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 21:53:57.453368	8
5871	POST /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:54:01.99755	8
5872	GET /fichajes/dashboard	172.31.128.25	2025-04-07 21:54:07.39053	8
5873	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:54:16.897696	8
5874	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 21:54:51.825466	8
5875	POST /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:55:08.229411	8
5876	GET /fichajes/record/162/signature_pad	172.31.128.25	2025-04-07 21:55:14.355862	8
5877	POST /fichajes/record/162/signature_pad	172.31.128.25	2025-04-07 21:55:27.973078	8
5878	GET /fichajes/record/162	172.31.128.25	2025-04-07 21:55:32.537506	8
5879	GET /fichajes/dashboard	172.31.128.25	2025-04-07 21:55:40.039431	8
5880	GET /fichajes/dashboard	172.31.128.25	2025-04-07 21:55:58.652384	8
5881	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:56:15.688507	8
5882	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 21:56:22.492552	8
5883	POST /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:56:27.134739	8
5884	GET /fichajes/dashboard	172.31.128.25	2025-04-07 21:56:32.286132	8
5885	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:56:56.018066	8
5886	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 21:57:01.320019	8
5887	POST /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:57:05.421757	8
5888	GET /fichajes/record/163/signature_pad	172.31.128.25	2025-04-07 21:57:11.447244	8
5889	POST /fichajes/record/163/signature_pad	172.31.128.25	2025-04-07 21:57:22.783948	8
5890	GET /fichajes/record/163	172.31.128.25	2025-04-07 21:57:27.22186	8
5891	GET /fichajes/dashboard	172.31.128.25	2025-04-07 21:57:48.532226	8
5892	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 21:57:56.358625	8
5893	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 21:58:02.348657	8
5894	GET /fichajes/dashboard	172.31.128.25	2025-04-07 21:58:07.925251	8
5895	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 22:01:25.684685	8
5896	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 22:01:41.001849	8
5897	POST /fichajes/employee/46/pin	172.31.128.25	2025-04-07 22:01:45.795254	8
5898	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:01:51.153131	8
5899	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 22:01:59.991633	8
5900	POST /fichajes/employee/46/pin	172.31.128.25	2025-04-07 22:02:04.858809	8
5901	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 22:02:10.943242	8
5902	GET /fichajes/record/164/signature_pad	172.31.128.25	2025-04-07 22:02:13.742704	8
5903	POST /fichajes/record/164/signature_pad	172.31.128.25	2025-04-07 22:02:31.551624	8
5904	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:02:36.159332	8
5905	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 22:03:05.59077	8
5906	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 22:03:14.850403	8
5907	POST /fichajes/employee/46/pin	172.31.128.25	2025-04-07 22:03:20.545499	8
5908	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:03:26.973178	8
5909	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 22:04:39.393235	8
5910	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 22:04:45.824726	8
5911	POST /fichajes/employee/46/pin	172.31.128.25	2025-04-07 22:04:50.303161	8
5912	GET /fichajes/record/165/signature_pad	172.31.128.25	2025-04-07 22:04:56.568622	8
5913	POST /fichajes/record/165/signature_pad	172.31.128.25	2025-04-07 22:05:04.93645	8
5914	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:05:09.557694	8
5915	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:05:17.045909	8
5916	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:08:40.686093	8
5917	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 22:08:47.020541	8
5918	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 22:08:53.507378	8
5919	POST /fichajes/employee/46/pin	172.31.128.25	2025-04-07 22:08:58.35381	8
5920	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:09:03.496303	8
5921	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:09:12.849216	8
5922	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:10:12.608745	8
5923	GET /	172.31.128.25	2025-04-07 22:12:40.420172	8
5924	GET /fichajes/	172.31.128.25	2025-04-07 22:12:54.943593	8
5925	GET /fichajes/company/dnln-distribucion-sl	172.31.128.25	2025-04-07 22:12:57.767128	8
5926	GET /fichajes/	172.31.128.25	2025-04-07 22:13:28.126167	8
5927	GET /fichajes/company/dnln-distribucion-sl	172.31.128.25	2025-04-07 22:13:30.928783	8
5928	GET /fichajes/login	172.31.128.25	2025-04-07 22:13:46.92701	8
5929	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:13:48.546646	8
5930	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:19:02.08805	8
5931	GET /fichajes/employee/46/pin	172.31.128.25	2025-04-07 22:19:11.16073	8
5932	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 22:19:16.727518	8
5933	POST /fichajes/employee/46/pin	172.31.128.25	2025-04-07 22:19:21.327702	8
5934	GET /fichajes/record/166/signature_pad	172.31.128.25	2025-04-07 22:19:27.639806	8
5935	POST /fichajes/record/166/signature_pad	172.31.128.25	2025-04-07 22:19:36.760979	8
5936	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:19:41.376472	8
5937	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:25:10.308393	8
5938	POST /employees/47/toggle-active	172.31.128.25	2025-04-07 22:25:37.51603	8
5939	Empleado activado: Lucia Mendez	172.31.128.25	2025-04-07 22:25:40.494525	8
5940	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:25:49.188999	8
5941	GET /fichajes/employee/47/pin	172.31.128.25	2025-04-07 22:25:59.161778	8
5942	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 22:26:23.202595	8
5943	POST /fichajes/employee/47/pin	172.31.128.25	2025-04-07 22:26:27.318997	8
5944	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:26:32.51662	8
5945	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:32:56.836824	8
5946	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:36:38.492507	8
5947	GET /fichajes/employee/47/pin	172.31.128.25	2025-04-07 22:36:58.655755	8
5948	POST /fichajes/employee/47/pin	172.31.128.25	2025-04-07 22:37:04.194159	8
5949	GET /fichajes/record/167/signature_pad	172.31.128.25	2025-04-07 22:37:10.424698	8
5950	POST /fichajes/record/167/signature_pad	172.31.128.25	2025-04-07 22:37:56.511756	8
5951	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:38:01.104819	8
5952	GET /fichajes/employee/47/pin	172.31.128.25	2025-04-07 22:41:56.032089	8
5953	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 22:42:01.728061	8
5954	POST /fichajes/employee/47/pin	172.31.128.25	2025-04-07 22:42:05.762247	8
5955	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:42:10.95282	8
5956	GET /fichajes/employee/47/pin	172.31.128.25	2025-04-07 22:42:31.897311	8
5957	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 22:42:37.284838	8
5958	POST /fichajes/employee/47/pin	172.31.128.25	2025-04-07 22:42:41.533832	8
5959	GET /fichajes/record/168/signature_pad	172.31.128.25	2025-04-07 22:42:47.537046	8
5960	POST /fichajes/record/168/signature_pad	172.31.128.25	2025-04-07 22:42:57.055021	8
5961	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:43:01.462396	8
5962	GET /fichajes/employee/47/pin	172.31.128.25	2025-04-07 22:45:12.8477	8
5963	POST /fichajes/api/validate-pin	172.31.128.25	2025-04-07 22:45:25.911706	8
5964	POST /fichajes/employee/47/pin	172.31.128.25	2025-04-07 22:45:39.79454	8
5965	GET /fichajes/dashboard	172.31.128.25	2025-04-07 22:45:45.168303	8
5966	GET /	127.0.0.1	2025-04-08 10:55:55.577624	8
5967	GET /fichajes/	127.0.0.1	2025-04-08 10:56:47.47006	8
5968	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-08 10:56:47.842767	8
5969	GET /fichajes/checkpoints/8/edit	127.0.0.1	2025-04-08 10:56:54.546959	8
5970	POST /fichajes/checkpoints/8/edit	127.0.0.1	2025-04-08 10:57:07.958072	8
5971	GET /fichajes/checkpoints	127.0.0.1	2025-04-08 10:57:08.597822	8
5972	Login exitoso: admin	127.0.0.1	2025-04-08 11:40:17.480161	8
5973	GET /fichajes/	127.0.0.1	2025-04-08 11:40:30.286821	8
5974	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-08 11:40:32.005275	8
5975	GET /fichajes/	127.0.0.1	2025-04-08 11:41:26.377217	8
5976	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-08 11:41:26.909263	8
5977	GET /fichajes/login	127.0.0.1	2025-04-08 11:41:32.865995	8
5978	POST /fichajes/login	127.0.0.1	2025-04-08 11:41:48.508558	8
5979	GET /fichajes/dashboard	127.0.0.1	2025-04-08 11:41:49.100389	8
5980	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-08 11:41:59.97898	8
5981	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-08 11:42:06.110314	8
5982	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-08 11:42:12.709257	8
5983	GET /fichajes/dashboard	127.0.0.1	2025-04-08 11:42:14.044492	8
5984	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-08 11:42:18.948513	8
5985	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-08 11:42:27.064067	8
5986	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-08 11:42:32.405595	8
5987	GET /fichajes/record/170/signature_pad	127.0.0.1	2025-04-08 11:42:33.278393	8
5988	POST /fichajes/record/170/signature_pad	127.0.0.1	2025-04-08 11:42:44.110395	8
5989	GET /fichajes/dashboard	127.0.0.1	2025-04-08 11:42:45.237855	8
5990	GET /	127.0.0.1	2025-04-08 12:34:24.023747	8
5991	GET /companies/	127.0.0.1	2025-04-08 12:34:34.264936	8
5992	GET /companies/dnln-distribucion-sl	127.0.0.1	2025-04-08 12:34:37.145695	8
5993	GET /tasks/	127.0.0.1	2025-04-08 12:34:54.28939	8
5994	GET /tasks/locations/6	127.0.0.1	2025-04-08 12:34:54.678936	8
5995	GET /tasks/dashboard/labels	127.0.0.1	2025-04-08 12:35:00.123159	8
5996	GET /fichajes/	127.0.0.1	2025-04-08 12:35:03.801393	8
5997	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-08 12:35:04.179083	8
5998	GET /fichajes/records/export	127.0.0.1	2025-04-08 12:35:12.800038	8
5999	POST /fichajes/records/export	127.0.0.1	2025-04-08 12:35:15.530347	8
6000	GET /fichajes/	127.0.0.1	2025-04-08 12:35:38.318841	8
6001	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-08 12:35:38.709534	8
6002	GET /fichajes/	127.0.0.1	2025-04-08 12:35:39.604721	8
6003	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-08 12:35:40.106889	8
6004	GET /fichajes/login	127.0.0.1	2025-04-08 12:35:46.870311	8
6005	GET /fichajes/dashboard	127.0.0.1	2025-04-08 12:35:47.176223	8
6006	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-08 12:36:14.692156	8
6007	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-08 12:36:17.003076	8
6008	GET /fichajes/dashboard	127.0.0.1	2025-04-08 12:36:17.629172	8
6009	GET /fichajes/employee/46/pin	127.0.0.1	2025-04-08 12:36:20.328468	8
6010	POST /fichajes/api/validate-pin	127.0.0.1	2025-04-08 12:36:23.969602	8
6011	POST /fichajes/employee/46/pin	127.0.0.1	2025-04-08 12:36:25.675626	8
6012	GET /fichajes/record/171/signature_pad	127.0.0.1	2025-04-08 12:36:26.353671	8
6013	POST /fichajes/record/171/signature_pad	127.0.0.1	2025-04-08 12:36:31.438307	8
6014	GET /fichajes/dashboard	127.0.0.1	2025-04-08 12:36:31.973619	8
6015	GET /fichajes/	127.0.0.1	2025-04-08 12:46:30.46526	8
6016	GET /fichajes/company/dnln-distribucion-sl	127.0.0.1	2025-04-08 12:46:30.923315	8
6017	GET /fichajes/checkpoints	127.0.0.1	2025-04-08 12:47:33.36489	8
6018	GET /fichajes/company/dnln-distribucion-sl/both	127.0.0.1	2025-04-08 12:47:44.088268	8
6019	GET /tasks/dashboard/labels	127.0.0.1	2025-04-08 12:48:32.350257	8
6020	GET /login	172.31.128.40	2025-04-08 12:53:33.743964	8
6021	GET /	172.31.128.40	2025-04-08 12:54:09.032831	8
6022	GET /fichajes/company/dnln-distribucion-sl	172.31.128.40	2025-04-08 12:54:11.279249	8
6023	GET /login	172.31.128.48	2025-04-08 14:46:15.396216	8
6024	GET /fichajes/	172.31.128.48	2025-04-08 14:46:41.349143	8
6025	GET /fichajes/company/dnln-distribucion-sl	172.31.128.48	2025-04-08 14:46:44.147184	8
6026	Login exitoso: admin	172.31.128.48	2025-04-08 14:47:09.786827	8
6027	GET /fichajes/company/dnln-distribucion-sl	172.31.128.48	2025-04-08 14:47:12.575322	8
6028	GET /companies/	172.31.128.7	2025-04-08 15:08:59.228718	8
6029	GET /companies/dnln-distribucion-sl	172.31.128.7	2025-04-08 15:11:27.423172	8
6030	POST /employees/new	172.31.128.7	2025-04-08 15:12:19.46546	8
6031	Asignando empleado a 1 puntos de fichaje	172.31.128.7	2025-04-08 15:12:22.46377	8
6032	Empleado creado: marcos menzdes	172.31.128.7	2025-04-08 15:12:23.815058	8
6033	GET /fichajes/	172.31.128.7	2025-04-08 15:17:54.667251	8
6034	GET /fichajes/company/dnln-distribucion-sl	172.31.128.7	2025-04-08 15:17:57.425862	8
6035	GET /companies/	172.31.128.7	2025-04-08 15:26:24.460154	8
6036	GET /companies/dnln-distribucion-sl	172.31.128.7	2025-04-08 15:26:32.201894	8
6037	GET /companies/	127.0.0.1	2025-04-08 15:55:57.864094	8
6038	GET /companies/dnln-distribucion-sl	127.0.0.1	2025-04-08 15:58:58.002647	8
6039	GET /checkins/employee/48	127.0.0.1	2025-04-08 15:59:10.641779	8
6040	GET /schedules/employee/48	127.0.0.1	2025-04-08 15:59:15.101416	8
6041	GET /schedules/employee/48/weekly	127.0.0.1	2025-04-08 15:59:23.849228	8
6042	POST /schedules/employee/48/weekly	127.0.0.1	2025-04-08 16:00:00.558878	8
6043	Horarios semanales actualizados para marcos menzdes	127.0.0.1	2025-04-08 16:00:01.215687	8
6044	GET /schedules/employee/48	127.0.0.1	2025-04-08 16:00:01.489117	8
6045	GET /checkins/employee/48	127.0.0.1	2025-04-08 16:00:23.081803	8
6046	GET /checkins/employee/48	127.0.0.1	2025-04-08 16:03:51.419756	8
6047	GET /login	172.31.128.65	2025-04-08 16:11:49.424943	8
6048	GET /backup/	172.31.128.65	2025-04-08 16:12:04.523322	8
6049	GET /backup/create	172.31.128.65	2025-04-08 16:12:16.211762	8
6050	POST /backup/create	172.31.128.65	2025-04-08 16:12:36.664906	8
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
6a9d8f1a6e1d
\.


--
-- Data for Name: api_tasks; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.api_tasks (id, title, description, priority, frequency, status, start_date, end_date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: checkpoint_incidents; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.checkpoint_incidents (id, incident_type, description, created_at, resolved, resolved_at, resolution_notes, record_id, resolved_by_id) FROM stdin;
37	MISSED_CHECKOUT	Salida automática durante ventana horaria de cierre (16:00:00 - 20:00:00)	2025-04-06 15:40:57.011391	f	\N	\N	149	\N
38	MISSED_CHECKOUT	Salida automática durante ventana horaria de cierre (16:00:00 - 20:00:00)	2025-04-06 15:42:58.165888	f	\N	\N	150	\N
39	MISSED_CHECKOUT	Salida automática durante ventana horaria de cierre (16:00:00 - 20:00:00)	2025-04-06 16:21:53.628712	f	\N	\N	151	\N
40	OVERTIME	Jornada con 0.07 horas extra sobre el límite diario de 1.0 horas	2025-04-06 21:18:40.541555	f	\N	\N	153	\N
41	MISSED_CHECKOUT	Salida automática durante ventana horaria de cierre (12:00:00 - 20:00:00)	2025-04-08 10:57:54.309307	f	\N	\N	169	\N
\.


--
-- Data for Name: checkpoint_original_records; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.checkpoint_original_records (id, record_id, original_check_in_time, original_check_out_time, original_signature_data, original_has_signature, original_notes, adjusted_at, adjusted_by_id, adjustment_reason, created_at) FROM stdin;
194	166	2025-04-07 22:08:59.935923	2025-04-07 22:19:22.953079	\N	f	\N	2025-04-07 22:09:00.618547	\N	Ajuste automático por límite de horas de contrato	2025-04-07 22:09:00.61855
175	148	2025-04-06 15:37:59.328016	2025-04-06 15:38:10.420426	\N	f	\N	2025-04-06 15:38:00.033728	\N	Ajuste automático por límite de horas de contrato	2025-04-06 15:38:00.033731
176	149	2025-04-06 15:39:04.144445	\N	\N	f	\N	2025-04-06 15:39:04.835623	\N	Registro original al iniciar fichaje	2025-04-06 15:39:04.835626
177	150	2025-04-06 15:41:45.877445	2025-04-06 18:00:00	\N	f	\N	2025-04-06 15:41:46.591303	\N	Registro original actualizado por cierre automático	2025-04-06 15:41:46.591307
178	151	2025-04-06 16:12:14.62796	2025-04-06 18:00:00	\N	f	\N	2025-04-06 16:12:15.349833	\N	Registro original actualizado por cierre automático	2025-04-06 16:12:15.349836
179	152	2025-04-06 21:14:35.945536	2025-04-06 21:15:17.364697	\N	f	\N	2025-04-06 21:14:36.667798	\N	Ajuste automático por límite de horas de contrato	2025-04-06 21:14:36.667801
181	153	2025-04-06 21:16:35.690882	\N	\N	f	\N	2025-04-06 21:17:22.865173	8	11	2025-04-06 21:17:22.865176
180	153	2025-04-06 21:16:35.690882	2025-04-06 21:18:38.849888	\N	f	\N	2025-04-06 21:16:36.376691	\N	Ajuste automático por límite de horas de contrato	2025-04-06 21:16:36.376697
195	167	2025-04-07 22:26:28.910185	2025-04-07 22:37:05.810116	\N	f	\N	2025-04-07 22:26:29.598966	\N	Ajuste automático por límite de horas de contrato	2025-04-07 22:26:29.59897
182	154	2025-04-07 20:52:10.776863	2025-04-07 20:52:23.144747	\N	f	\N	2025-04-07 20:52:11.475223	\N	Ajuste automático por límite de horas de contrato	2025-04-07 20:52:11.475226
183	155	2025-04-07 20:59:58.098141	2025-04-07 21:00:12.868821	\N	f	\N	2025-04-07 20:59:58.812866	\N	Ajuste automático por límite de horas de contrato	2025-04-07 20:59:58.812871
196	168	2025-04-07 22:42:07.311635	2025-04-07 22:42:43.083059	\N	f	\N	2025-04-07 22:42:08.005559	\N	Ajuste automático por límite de horas de contrato	2025-04-07 22:42:08.005562
184	156	2025-04-07 21:00:57.117685	2025-04-07 21:02:26.157158	\N	f	\N	2025-04-07 21:00:57.818597	\N	Ajuste automático por límite de horas de contrato	2025-04-07 21:00:57.8186
185	157	2025-04-07 21:04:17.626818	2025-04-07 21:09:21.285308	\N	f	\N	2025-04-07 21:04:17.701088	\N	Ajuste automático por límite de horas de contrato	2025-04-07 21:04:17.701093
197	169	2025-04-07 22:45:41.428458	2025-04-08 18:00:00	\N	f	\N	2025-04-07 22:45:42.151729	\N	Registro original actualizado por cierre automático	2025-04-07 22:45:42.151735
186	158	2025-04-07 21:10:00.645274	2025-04-07 21:10:43.703463	\N	f	\N	2025-04-07 21:10:01.3748	\N	Ajuste automático por límite de horas de contrato	2025-04-07 21:10:01.374803
187	159	2025-04-07 21:29:28.36903	2025-04-07 21:29:50.575854	\N	f	\N	2025-04-07 21:29:29.085247	\N	Ajuste automático por límite de horas de contrato	2025-04-07 21:29:29.08525
188	160	2025-04-07 21:41:05.995351	2025-04-07 21:46:10.366643	\N	f	\N	2025-04-07 21:41:06.697522	\N	Ajuste automático por límite de horas de contrato	2025-04-07 21:41:06.697525
198	170	2025-04-08 11:42:12.858877	2025-04-08 11:42:32.555583	\N	f	\N	2025-04-08 11:42:12.957615	\N	Ajuste automático por límite de horas de contrato	2025-04-08 11:42:12.957619
189	161	2025-04-07 21:46:59.710881	2025-04-07 21:48:55.495403	\N	f	\N	2025-04-07 21:47:00.409922	\N	Ajuste automático por límite de horas de contrato	2025-04-07 21:47:00.409925
190	162	2025-04-07 21:54:03.660059	2025-04-07 21:55:09.826375	\N	f	\N	2025-04-07 21:54:04.380395	\N	Ajuste automático por límite de horas de contrato	2025-04-07 21:54:04.380398
191	163	2025-04-07 21:56:28.705683	2025-04-07 21:57:06.989983	\N	f	\N	2025-04-07 21:56:29.412819	\N	Ajuste automático por límite de horas de contrato	2025-04-07 21:56:29.412822
199	171	2025-04-08 12:36:17.157542	2025-04-08 12:36:25.821526	\N	f	\N	2025-04-08 12:36:17.226228	\N	Ajuste automático por límite de horas de contrato	2025-04-08 12:36:17.226233
192	164	2025-04-07 22:01:47.435451	2025-04-07 22:02:06.489905	\N	f	\N	2025-04-07 22:01:48.146923	\N	Ajuste automático por límite de horas de contrato	2025-04-07 22:01:48.146926
193	165	2025-04-07 22:03:22.187425	2025-04-07 22:04:51.936422	\N	f	\N	2025-04-07 22:03:22.885408	\N	Ajuste automático por límite de horas de contrato	2025-04-07 22:03:22.885411
\.


--
-- Data for Name: checkpoint_records; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.checkpoint_records (id, check_in_time, check_out_time, original_check_in_time, original_check_out_time, adjusted, adjustment_reason, notes, created_at, updated_at, employee_id, checkpoint_id, signature_data, has_signature) FROM stdin;
162	2025-04-07 21:54:03.660059	2025-04-07 21:55:09.826375	\N	\N	t	\N	 [R] Hora entrada ajustada de 21:54 a 23:54	2025-04-07 21:54:03.896843	2025-04-07 21:55:29.384909	46	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAxwAAAGQCAYAAAAk6maCAAAAAXNSR0IArs4c6QAAIABJREFUeF7t3U0S5DZ2IGD6Bu2dd1OO8AHkE8jezS2kI4xPIPsE9g1aOsGsZ2XXCdR7L1qz886+QbsgVbZZLJIAmACJny8jFJKqmCDwvZeZfARI/sXiRYAAAQIECBAgQIAAgUoCf1GpXc0SIECAAAECBAgQIEBgUXBIAgIECBAgQIAAAQIEqgkoOKrRapgAAQIECBAgQIAAAQWHHCBAgAABAgQIECBAoJqAgqMarYYJECBAgAABAgQIEFBwyAECBAgQIECAAAECBKoJKDiq0WqYAAECBAgQIECAAAEFhxwgQIAAAQIECBAgQKCagIKjGq2GCRAgQIAAAQIECBBQcMgBAgQIECBAgAABAgSqCSg4qtFqmAABAgQIECBAgAABBYccIECAAAECBAgQIECgmoCCoxqthgkQIECAAAECBAgQUHDIAQIECBAgQIAAAQIEqgkoOKrRapgAAQIECBAgQIAAAQWHHCBAgAABAgQIECBAoJqAgqMarYYJECBAgAABAgQIEFBwyAECBAgQIECAAAECBKoJKDiq0WqYAAECBAgQIECAAAEFhxwgQIAAAQIECBAgQKCagIKjGq2GCRAgQIAAAQIECBBQcMgBAgQIECBAgAABAgSqCSg4qtFqmAABAgQIECBAgAABBYccIECAAAECBAgQIECgmoCCoxqthgkQIECAAAECBAgQUHDIAQIECBAgQIAAAQIEqgkoOKrRapgAAQIECBAgQIAAAQWHHCBAgAABAgQIECBAoJqAgqMarYYJECBAgAABAgQIEFBwyAECBAgQIECAAAECBKoJKDiq0WqYAAECBAgQIECAAAEFhxwgQIAAAQIECBAgQKCagIKjGq2GCRAgQIAAAQIECBBQcMgBAgQIECBAgAABAgSqCSg4qtFqmAABAgQIECBAgAABBYccIECAAAECBAgQIECgmoCCoxqthgkQIECAAAECBAgQUHDIAQIECBAgQIAAAQIEqgkoOKrRapgAAQIECBAgQIAAAQWHHCBAgAABAgQIECBAoJqAgqMarYYJECBAgAABAgQIEFBwyAECBAgQIECAAAECBKoJKDiq0WqYAAECBAgQIECAAAEFhxwgQIAAAQIECBAgQKCagIKjGq2GCRAgQIAAAQIECBBQcMgBAgQIECBAgAABAgSqCSg4qtFqmAABAgQIECBAgAABBYccIECAAAECBAgQIECgmoCCoxqthgkQIECAAAECBAgQUHDIAQIECBAgQIAAAQIEqgkoOKrRapgAAQIECBAgQIAAAQWHHCBAgAABAgQIECBAoJqAgqMarYYJECBAgAABAgQIEFBwyAECBAgQIECAAAECBKoJKDiq0WqYAAECBAgQIECAAAEFhxwgQIAAAQIECBAgQKCagIKjGq2GCRAgQIAAAQIECBBQcMgBAgQIECBAgAABAgSqCSg4qtFqmAABAgQIECBAgAABBYccIECAAAECBAgQIECgmoCCoxqthgkQIECAAAECBAgQUHDIAQIECBAgQIAAAQIEqgkoOKrRapgAAQIECBAgQIAAAQWHHCBAgAABAgQIECBAoJqAgqMarYYJECBAgAABAgQIEFBwyAECBAgQIECAAAECBKoJKDiq0WqYAAECBAgQIECAAAEFhxwgQIAAAQIECBAgQKCagIKjGq2GCRAgQIAAAQIECBBQcMgBAgQIECBAgAABAgSqCSg4qtFqmAABAgQIECBAgAABBYccIECAAAECBAgQIECgmoCCoxqthgkQIECAAAECBAgQUHDIAQIECBAgQIAAAQIEqgkoOKrRapgAAQIECBAgQIAAAQWHHCBAgAABAgQIECBAoJqAgqMarYYJECBAgAABAgQIEFBwyAECBAgQIECAAAECBKoJKDiq0WqYAAECBAgQIECAAAEFhxwgQIAAAQIECBAgQKCagIKjGq2GCRAgQIAAAQIECBBQcMgBAgQIECBAgAABAgSqCSg4qtFqmAABAgQIECBAgAABBYccIECAAAECBAgQIECgmoCCoxqthgkQIECAAAECBAgQUHDIAQIECBAgQIAAAQIEqgkoOKrRapgAAQIECBAgQIAAAQWHHCBAgAABAgQIECBAoJqAgqMarYYJECBAgAABAgQIEFBwyAECBAgQIECAAAECBKoJKDiq0WqYAAECBAgQIECAAAEFhxwgQIAAAQIECBAgQKCagIKjGq2GCRAgQIAAAQIECBBQcMgBAgQIECBAgAABAgSqCSg4qtFqmAABAgQIECBAgAABBYccIECAAAECBAgQIECgmoCCoxqthgkQIECAAAECBAgQUHDIAQIECBAgQIAAAQIEqgkoOKrRapgAAQIECBAgQIAAAQWHHCBAgAABAgQIECBAoJqAgqMarYYJECBAgAABAgQIEFBwyAECBAgQIECAAAECBKoJKDiq0WqYAAECBAgQIECAAAEFhxwgQIAAAQIECBAgQKCagIKjGq2GCRAgQIAAAQIECBBQcMgBAgQIECBAgAABAgSqCSg4qtFqmAABAgQIECBAgAABBYccIECAAAECBAgQIECgmoCCoxqthgkQIECAAAECBAgQUHDIAQIECBAgQIAAAQIEqgkoOKrRapgAAQIECBAgQIAAAQWHHCBAgAABAgQIECBAoJqAgqMarYYJECBAgAABAgQIEFBwyAECBAgQIECAAAECBKoJKDiq0WqYAAECBAgQIECAAAEFhxwgQIAAAQIECBAgQKCagIKjGq2GCRAgQIAAAQIECBBQcMgBAgQIECBAgAABAgSqCSg4qtFqmAABAgQIECBAgAABBYccIECAAAECBAgQIECgmoCCoxqthgkQIECAAAECBAgQUHDIAQIECBAgQIAAAQIEqgkoOKrRapgAAQIECBAgQIAAAQWHHCBAgAABAgQIECBAoJqAgqMarYYJECBAgAABAgQIEFBwyAECBAgQIECAAAECBKoJKDiq0WqYAAECBAgQIECAAAEFhxwgQIAAAQIECBAgQKCagIKjGq2GCRAgQIAAAQIECBBQcMgBAgQIECBAgAABAgSqCSg4qtFqmAABAgQIECBAgAABBYccIECAAAECBAgQIECgmoCCoxqthgkQIECAAAECBAgQUHDIAQIECBAgQIAAAQIEqgkoOKrRapgAAQIECBAgQIAAAQWHHCBAgAABAgQIECBAoJqAgqMarYYJECBAgAABAgQIEFBwyAECBAgQIECAAAECBKoJKDiq0WqYAAECBAgQIECAAAEFhxwgQIAAAQIECBAgQKCagIKjGq2GCRAgQIAAAQIECBBQcMgBAgQIECBAgAABAgSqCSg4qtFqmAABAgQIECBAgAABBYccIECgF4G/+9zR17//7fP/v/7dyzj0kwABAgQITCWg4Jgq3AZLoEuBUGD8sCzLq9A4GsSr8Pj4eYN/7HK0Ok2AAAECBAYTUHAMFlDDITCQQGqhcTTkf/r0F4qOgRLCUAgQIECgTwEFR59x02sCIwu8W2isbf7+08yIJVcjZ4uxESBAgEDzAgqO5kOkgwSmEQizEd8mLJ3K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	t
163	2025-04-07 21:56:28.705683	2025-04-07 21:57:06.989983	\N	\N	t	\N	 [R] Hora entrada ajustada de 21:56 a 23:56	2025-04-07 21:56:28.930114	2025-04-07 21:57:24.126563	46	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAxwAAAGQCAYAAAAk6maCAAAAAXNSR0IArs4c6QAAIABJREFUeF7t3Y3Z5LZ1BlC6A3cQpYLIFSgqIRVIriBxBRtXYHdgbQmpwFYFdgdWB3EHzkLeicYU/8kLXhBnnidRIg1B4AAzw/cDQP5i8CJAgAABAgQIECBAgECQwC+CylUsAQIECBAgQIAAAQIEBoHDICBAgAABAgQIECBAIExA4AijVTABAgQIECBAgAABAgKHMUCAAAECBAgQIECAQJiAwBFGq2ACBAgQIECAAAECBAQOY4AAAQIECBAgQIAAgTABgSOMVsEECBAgQIAAAQIECAgcxgABAgQIECBAgAABAmECAkcYrYIJECBAgAABAgQIEBA4jAECBAgQIECAAAECBMIEBI4wWgUTIECAAAECBAgQICBwGAMECBAgQIAAAQIECIQJCBxhtAomQIAAAQIECBAgQEDgMAYIECBAgAABAgQIEAgTEDjCaBVMgAABAgQIECBAgIDAYQwQIECAAAECBAgQIBAmIHCE0SqYAAECBAgQIECAAAGBwxggQIAAAQIECBAgQCBMQOAIo1UwAQIECBAgQIAAAQIChzFAgAABAgQIECBAgECYgMARRqtgAgQIECBAgAABAgQEDmOAAAECBAgQIECAAIEwAYEjjFbBBAgQIECAAAECBAgIHMYAAQIECBAgQIAAAQJhAgJHGK2CCRAgQIAAAQIECBAQOIwBAgQIECBAgAABAgTCBASOMFoFEyBAgAABAgQIECAgcBgDBAgQIECAAAECBAiECQgcYbQKJkCAAAECBAgQIEBA4DAGCBAgQIAAAQIECBAIExA4wmgVTIAAAQIECBAgQICAwGEMECBAgAABAgQIECAQJiBwhNEqmAABAgQIECBAgAABgcMYIECAAAECBAgQIEAgTEDgCKNVMAECBAgQIECAAAECAocxQIAAAQIECBAgQIBAmIDAEUarYAIECBAgQIAAAQIEBA5jgAABAgQIECBAgACBMAGBI4xWwQQIECBAgAABAgQICBzGAAECBAgQIECAAAECYQICRxitggkQIECAAAECBAgQEDiMAQIECBAgQIAAAQIEwgQEjjBaBRMgQIAAAQIECBAgIHAYAwQIECBAgAABAgQIhAkIHGG0CiZAgAABAgQIECBAQOAwBggQIECAAAEC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CBAgQCBOQOCIs1UyAQIECBAgQIAAge4FBI7uhwAAAgQIECBAgAABAnECAkecrZIJECBAgAABAgQIdC8gcHQ/BAAQIECAAAECBAgQiBMQOOJslUyAAAECBAgQIECgewGBo/shAIAAAQIECBAgQIBAnIDAEWerZAIECBAgQIAAAQLdCwgc3Q8BAAQIECBAgAABAgTiBASOOFslEyBAgAABAgQIEOheQODofggAIECAAAECBAgQIBAnIHDE2SqZAAECBAgQIECAQPcCAkf3QwAAAQIECBAgQIAAgTgBgSPOVskECBAgQIAAAQIEuhcQOLofAgAIECBAgAABAgQIxAkIHHG2SiZAgAABAgQIECDQvYDA0f0QAECAAAECBAgQIEAgTkDgiLNVMgECBAgQIECAAIHuBQSO7ocAAAIECBAgQIAAAQJxAgJHnK2SCRAgQIAAAQIECHQvIHB0PwQAECBAgAABAgQIEIgTEDjibJVMgAABAgQIECBAoHsBgaP7IQCAAAECBAgQIECAQJyAwBFnq2QCBAgQIECAAAEC3QsIHN0PAQAECBAgQIAAAQIE4gQEjjhbJRMgQIAAAQIECBDoXkDg6H4IACBAgAABAgQIECAQJyBwxNkqmQABAgQIECBAgED3AgJH90MAAAECBAgQIECAAIE4gf8Dejdi65w+TKkAAAAASUVORK5CYII=	t
148	2025-04-06 15:37:59.328016	2025-04-06 15:38:10.420426	\N	\N	t	\N	 [R] Hora entrada ajustada de 15:37 a 17:37	2025-04-06 15:37:59.560265	2025-04-06 15:38:24.474968	47	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkgAAAGQCAYAAADlQuzyAAAAAXNSR0IArs4c6QAAIABJREFUeF7t3dvV7TZ6Jmp2Bu4ILEew5QhkXe3L7gxUOwNXBOqKoJxBV4Xgy75SKYJSBpYj6Mpg7fVJP8pYFDl5mCCJwzPH0FiSFgkCDzD/A94J4L9NXgQIECBAgAABAgQIECBAgAABAgQIECBAgACBwQT+22Dt1VwCBAgQIECAAAECBAgQIECAAAECBAgQIECAwCQgMQgIECBAgAABAgQIECBAgAABAgQIECBAgACB4QQEJMN1uQYTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJjgAABAgQIECBAgAABAgQIECBAgAABAgQIEBhOQEAyXJdrMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQYIECBAgAABAgQIECBAgAABAgQIELhS4F+mafrLlQ9QNgECBM4ICEjOqLmHAAECBAgQIECAAAECBAgQIECAAIEtgQhG/tc0Td98XPitoGSLzN8TIHCngIDkTm3PIkCAAAECBAgQIECAAAECBAgQINC/QAQjf5ym6etZU//wEZj0L6CFBAg0ISAgaaKbVJIAAQIECBAgQIAAAQIECBAgQIBA9QIRjHz/eZVI/Dl/xRZbsYLEiwABAtUICEiq6QoVIUCAAAECBAgQIECAAAECBAgQINCkwKtgJBr00zRN/9xky1SaAIGuBQQkXXevxhEgQIAAAQIECBAgQIAAAQIECBC4TGArGIkH21brMn4FEyDwroCA5F1B9xMgQIAAAQIECBAgQIAAAQIECBAYSyAOXo+ttLZeDmXfEvL3BAg8KiAgeZTfwwkQIECAAAECBAgQIECAAAECBAg0IbBntUhqiFUjTXSpShIgICAxBggQIECAAAECBAgQIECAAAECBAgQWBN4FYz8PE3TV7MbhSPGEgECzQgISJrpKhUlQIAAAQIECBAgQIAAAQIECBAgcJvAq2AkDl2P19ez2thS67bu8SACBEoICEhKKCqDAAECBAgQIECAAAECBAgQIECAQPsCEYqkYGTemr98HLge//+H2V/G30U44kWAAIGmBAQkTXWXyhIgQIAAAQIECBAgQIAAAQIECBAoLvBqtUgKRuLPpcPZbalVvDsUSIDAXQICkrukPYcAAQIECBAgQIAAAQIECBAgQIBAPQJptcg3H6tG8prloUj6/7FqJO7JX8KRevpTTQgQOCEgIDmB5hYCBAgQIECAAAECBAgQIECAAAECjQqsrRbJt9CKf0+vpeuXApRGOVSbAIGRBQQkI/e+thMgQIAAAQIECBAgQIAAAQIECIwisBZ0RPtjJUgeiuThyPy8kXTt0vWjWGonAQKdCAhIOulIzSBAgAABAgQIECBAgAABAgQIECCwIHB2BYjzRgwnAgS6FxCQdN/FGkiAAAECBAgQIECAAAECBAgQIDCowPzckL1nhjhvZNABo9kERhMQkIzW49pLgAABAgQIECBAgAABAgQIECDQu8B89cfeYCRclsKRb1e24OrdUfsIEOhcQEDSeQdrHgECBAgQIECAAAECBAgQIECAwDAC8+20jhymfnYrrmFwNZQAgf4EBCT99akWESBAgAABAgQIECBAgAABAgQIjCXwTjASUnH//DD2CFdi5YgXAQIEuhUQkHTbtRpGgAABAgQIECBAgAABAgQIECAwgEC+JdaRFSOJZikcObIl1wDEmkiAQK8CApJee1a7CBAgQIAAAQIECBAgQIAAAQIEehaYnzNy5pwQ4UjPI0TbCBDYFBCQbBK5gAABAgQIECBAgAABAgQIECBAgEA1AvPttM6u9hCOVNOlKkKAwFMCApKn5D2XAAECBAgQIECAAAECBAgQIECAwH6Bd88ZyZ8kHNnv7koCBDoWEJB03LmaRoAAAQIECBAgQIAAAQIECBAg0IVAHmicOWdEONLFMNAIAgRKCwhISosqjwABAgQIECBAgAABAgQIECBAgEAZgXzVSAQjP34uNs4eOfuan1sS5ZzdoutsHdxHgACBagQEJNV0hYoQIECAAAECBAgQIECAAAECBAgQ+EVg6ZyRCEjin7Mv4chZOfcRINCtgICk267VMAIECBAgQIAAAQIECBAgQIAAgQYFIsj45iMkeXc7rdR84UiDA0GVCRC4XkBAcr2xJxAgQIAAAQIECBAgQIAAAQIECBDYEpgfnP7tmytGXoUjpcreapO/J0CAQNUCApKqu0flCBAgQIAAAQIECBAgQIAAAQIEOhcofc5I4ppv0xX/v9SKlM67RPMIEBhFQEAySk9rJwECBAgQIECAAAECBAgQIECAQG0C+dZXJQ9LXwpHSpZfm6P6ECBA4JSAgOQUm5sIECBAgAABAgQIECBAgAABAgQInBa44pyRVBnnjZzuFjcSIDCagIBktB7XXgIECBAgQIAAAQIECBAgQIAAgScFfvg4gD3qUPosEOHIkz3r2QQINCcgIGmuy1SYAAECBAgQIECAAAECBAgQIECgQYF81Ujp7a6cN9LggFBlAgSeFxCQPN8HakCAAAECBAgQIECAAAECBAgQINCvwFXnjCSxCEdiVUr+Kh3A9Ns7WkaAwNACApKhu1/jCRAgQIAAAQIECBAgQIAAAQIELhJIqzqi+Pj3K+bhbKl1UecplgCBMQSu+MI8hpxWEiBAgAABAgQIECBAgAABAgQIEFgWSCs6Ihi5ajVHfpZJ1OIvH8+KP70IECBAYIeAgGQHkksIECBAgAABAgQIECBAgAABAgQI7BCIFR3x+v7CYGRpS60IReLAdy8CBAgQOCAgIDmA5VICBAgQIECAAAECBAgQIECAAAECCwIRWsQ/31y4nVY81pZahh8BAgQKCghICmIqigABAgQIECBAgAABAgQIECBAYCiBu4KRpXDEllpDDTWNJUDgCgEByRWqyiRAgAABAgQIECBAgAABAgQIEOhZIIKReMVWWukA9vjzivM/lrbUuupck577TNsIECDwGwEBiUFBgAABAgQIECBAgAABAgQIECBA4JjAp4/LY27tqmAkHjEPR6waOdZPriZAgMBLAQGJAUKAAAECBAgQIECAAAECBAgQIEBgn8APH5f9+PFnOpR9393HropnpZUqcadw5JifqwkQILApICDZJHIBAQIECBAgQIAAAQIECBAgQIDA4AIRVqRQJCiuDEYiFElbdyV2W2oNPgA1nwCBawQEJNe4KpUAAQIECBAgQIAAAQIECBAgQKB9gbSCIwKSO0KKCF4iHEkvq0baH0NaQIBAxQICkoo7R9UIECBAgAABAgQIECBAgAABAgQeEbg7GIlGLm2p9e0jrfdQAgQIDCIgIBmkozWTAAECBAgQIECAAAECBAgQIEBgl0BaxZHCiVjFcfUrD0fiebGd15XbeF3dHuUTIECgCQEBSRPdpJIECBAgQIAAAQIECBAgQIAAAQIXC6RAIgKK2ObqjtUbS1tq3fHciykVT4AAgTYEBCRt9JNaEiBAgAABAgQIECBAgAABAgQIXCMQ22lFKJJWcdw1XzbfUuuOM06uEVQqAQIEGhW46wt+ozyqTYAAAQIECBAgQIAAAQIECBAg0LFAhCN3HcCeGGPVyDefQ5l0zomD2DseYJpGYPZeB1KZgICksg5RHQIECBAgQIAAAQIECBAgQIAAgcsFUkgR21nFv0dIcfdZI9HIeKYttS7vbg8gcItACj1ji754pf9eevjS15v//Ljw54+vS7dUevSHCEhGHwHaT4AAAQIECBAgQIAAAQIECBAYRyBtp5UHJHe0Pp4bk6b5qhEHsd8h7xkEygvkwcfX0zT9j40w5GwNYtu9u8Lbs3Vs/j4BSfNdqAEECBAgQIAAAQIECBAgQOBWgZgYSpND6VDrWyvgYQROCMSY/d00Td9N03T3WR9pG69UbatGTnSgWwjcJJCHH/HvsR1eer1aEXJl9eJrVrx8z71AWUByAaoiCRAgQIAAAQIECBAgQIBApwJ/+phgTs27e6K5U1bNulggP/Pjzx9BycWP/Hvx8ey03U78T++Zu+Q9h8C6QAo6aglAjvSVryFHtHZcKyDZgeQSAgQIECBAgAABAgQIECBA4JdtPvJP0gaJT8IbGDULzLe1irM+7jhnJJl8muGYh6t5tKhbjwJLQchdq0Dia01sozd/xffREnUQlBQasb4wF4JUDAECBAgQIECAAAECBAgQ6FhgKRyJ5pqg6bjTG29avnLj7nFq1Ujjg0f1mxN4MghJWPF9Mm2FtSeIzberjNDkq49/juDf/bXtSN2auVZA0kxXqSgBAgQIECBAgAABAgQIEHhEYC0cicrc/Yn8RwA8tCmBfNVImrDcM1lZqpE/ZJ8Od8ByKVXlEPgvgRSGpK3rSqzGyL9GpFUfW183tv7+bJ+lc0byrflelSUkOSv9cZ+A5E1AtxMgQIAAAQIECBAgQIAAgY4F5meO5E0VjnTc8Y02LT9r5O7t3+bbeQlHGh1Eql2NwHxVyLtByDwESf99VdBRAnK+Gm2tTCHJG9oCkjfw3EqAAAECBAgQIECAAAECBDoW+Os0TV+vtM9kTMcd32DTnj5rJJ/ETOcOpE+BN8ipygRuFygVhqSwY74KpOYQZA/2nqDE9+U9kgvXCEhOwrmNAAECBAgQIECAAAECBAh0KjCfbJ430yRMpx3faLOePGskyPKD2O9etdJol6k2gb8fUn52m6w8CIl/bz0A2Tsk8i38lu7x/XmvZHadgOQEmlsIECBAgAABAgQIECBAgEDHAq8mYEy+dNzxjTXt6bNG8u28gs6Wc40NINW9VSC9X+OhR7bKSsFHOvw87h8lDFnroK2Q5PfTNP3brb3b+MMEJI13oOoTIECAAAECBAgQIECAAIFCAjFp9ccX22rFY8wjFMJWzFsCT64aifdJPtn7xEHwb+G5mcANAkcDEUHI/k4J2whJXr0Etvs9/WBzwMqlBAgQIECAAAECBAgQIECgV4GtCReTwL32fFvtenrVSGilLbXShG5MRHoRGF0gBYff7FghMg9DRl8RcmbsbJ1JYru/A6o++XEAy6UECBAgQIAAAQIECBAgQKBDga1wJJpsa60OO76xJs0PQr87mIhPbMfBz+nMBJ/QbmwAqW5RgbRNVrwftrbMisn6eO+MdFZIUeyVwv5qxWcZZgFJGUelECBAgAABAgQIECBAgACBFgW2DmSPNpkIbrFn+6nz06tG0uRv2tImBTM+9d7PGNOSbQGByLbR3VdsfbjB9+6dPSIg2QnlMgIECBAgQIAAAQIECBAg0KHA1mGvVo502OkNNenpVSNBlW+pFZ+Cjzp5ERhBYO+2WVaIPDcaXn0Pt83Wzn4RkOyEchkBAgQIECBAgAABAgQIEOhMQDjSWYd21Jz8k9FPnX8z31LLHFpHA0xTFgXiffe7aZr+cWPbrPwMESupnh1MW2eRWEWyo398cd+B5BICBAgQIECAAAECBAgQINCZwFY44pOnnXV4I81Jn1hP53w8sYJpvqWWubNGBo9qnhLYs0rEoeqnaG+5aWubLd/Ld3SDL/I7kFxCgAABAgQIECBAgAABAgQ6EhCOdNSZHTVlvp1WhCN3fzo91cGWQR0NLE35QmDvWSJp5VbcfPf7UJcdE9j6nm7+f8MT0LEB52oCBAgQIECAAAECBAgQINCywNZ2HD5t2nLvtln3/BD2aMFTq0aiHjH+Y7LxiTq02Xtq3YLA/D22VGehYAs9uVzHrVUkttkSkLQ7utWcAAECBAgQIECAAAECBAgUFBCOFMRUVBGBGlaNREPSQewxkRgvn5gv0r0KeUhgzyoR54g81DkXPfbVKhIBiYDkomGnWAIECBAgQIAAAQIECBAg0I6AcKSdvhqhpvNPtD81gZcOYg/zb6ZpSgHJCH2gjX0JpPdUtCoFJPMWWiXSV5/nrXkVkFgRJyDpd+RrGQECBAgQIECAAAECBAgQ2CGwFY5EEU9NUO+ovks6E6hh1ch8Sxpb0Hc2yAZojsPVB+jkA0189X1eQCIgOTCUXEqAAAECBAgQIECAAAECBPoSEI701Z8tt6aWVSPz94RwsOVRNVbdnSUyVn8fae1/TNP01coNAhIByZGx5FoCBAgQIECAAAECBAgQINCNgHCkm65sviH59i+xzc9TW1nl74mYNIy6OG+k+eHVbQOcJdJt1xZvWDpHaalgAYmApPiAUyABAgQIECBAgAABAgQIEKhdYE84YtKk9l5sv375VlYRRKRQ4omW5SGNsf9ED3jmHoG9W2fFGI6XgG+Pav/XvApIrJITkPT/DtBCAgQIECBAgAABAgQIECCQCewJR0yYGDJXCsy3AnpytcZSXeI94kWgFoGtrbNSCPJkwFiLlXosCwhI3hgZDqF6A8+tBAgQIECAAAECBAgQIECgMoH54dNL1fPp+co6rbPq1HAIeyKtqS6ddbPmvCmwJxSxSuRN5IFuz1fIzZvte/7GQBCQDPRO0VQCBAgQIECAAAECBAgQ6FpAONJ191bfuNpWaszPPfHp++qHUNcV3HueiHHa9TC4rHGvApInz326rMElCxaQlNRUFgECBAgQIECAAAECBAgQeE7g1RYbUSufIn2ub3p/ck0rNWoLanrve+1bF9gKRWydZfSUEni1taaAZENZQFJqGCqHAAECBAgQIECAAAECBAg8J/DXaZq+fvF44chzfdPzk2sLI+arqJy10/Poq7Nte0IRW2fV2Xct1+rVClIBiYCk5bGt7gQIECBAgAABAgQIECBAYFNAOLJJ5IILBGrbwmr+CWrhyAWdrshFAaGIgfG0wNYWmxZJvOghOE8PX88nQIAAAQIECBAgQIAAgXcE0sRUKiNtWfJOmS3d+2rf8WiHlSMt9WYbdc0n4uL99uPnakc48eRrHtZEOOJF4EqBvaHIaN+TrjRX9muBV9tsCoxf2AlIvLUIECBAgAABAgQIECBAoAWBNBkVf37zUeF5OLLUjjSBG3/39CRuaedXe47Hs4QjpcXHLq+27bSiN+afmjbmxx6jV7deKHK1sPLfEXj1gQkBiYDknbHlXgIECBAgQIAAAQIECBC4USCfgEoToCUf38sEqnCk5KhQ1pZATYewp7rO3wO9vLe3+sLf3y8wDwfzGkQIH2PPSpH7+8UTvxR4FZD4+igg8X4hQIAAAQIECBAgQIAAgQoFYtLp6IqQEs1ofaJAOFJiFChjj0CNq0ai3s4b2dN7rnlHQCjyjp57nxB49bOBg9oFJE+MSc8kQIAAAQIECBAgQIAAgZlAHojs2R7rSsBWt5vYCkdMglw5asYpO71Xv/9ock2fkq/tcPhxRkX/Ld0TioSC1SL9j4UWW/jqoPa/TdP031ts1B11dgbJHcqeQYAAAQIECBAgQIAAgXEF0oRTCDwdisx7obWQ5NXkR5q0czj1uO+1Ui2vdXVGratZSrkr5xkBocgz7p5aXmDrZwQ5wIo5mPKDUYkECBAgQIAAAQIECBAg8GsYEp8+ry0UyfumpdUWWxMfLbXF+6NOgfl7tqYx5byROsdMq7War5Caf1/48WOViJUirfbwmPXe+jlBDiAgGfOdodUECBAgQIAAAQIECBC4WWBrC6grqhOTWF9N0xRbSMQ/+WsroKlpEviVzacXf1nT9kdX9K8yrxeo8RD21Oqa63Z9z3hCKYFXqxnja6hQpJS0cp4UePWzgoBEQPLk2PRsAgQIECBAgAABAgQIdC1wx2qR9EneNIkVoHs+3bv1icoop/attv7jIwBaG0S117/rwd9442rftko40vgAe7j6aaVI/PnNQl2Eyw93kMcXF3gVkPhZQUBSfMApkAABAgQIECBAgAABAqMLXBGMnA1CXvXFVkjyh883x0Rsja/wWJrYS3U14VFjr9Vfp6XttOJ9sCd0vKN1tQc3dxh4xnmBte9NVoqcN3VnGwI/vNja1M8LApI2RrFaEiBAgAABAgQIECBAoAGBUsFImoyNidl4XTk5+6/TNP1xxfb30zT9W4XuwpEKO6WDKtV6CHuinQeaNQeYHQyHbpqw57D1K7/HdAOpIU0LvApIWtlS9PYOsPfY7eQeSIAAAQIECBAgQIAAgWYFXh1su6dReSBy90TVq1UkNf5uLBzZM6Jcc0SghVUZtYc3R7xde72AUOR6Y09oS2DrHLgaf955XBjK412gAgQIECBAgAABAgQIEKhe4J1gJO3xHo28OxTJYdcCkho/USkcqf4t0VwF808V13ruwvyTz7aDaW6Y3VLh9P0oth6Mf5+/ah3ft+B4yPACW1uK+rq6MEQEJMO/bwAQIECAAAECBAgQIEDgpcCr7RrWbqx1n/elw0trC0j+NE3Tdy96xOSGN+wRgfmniWvcrmrpPJQY514EcgGrRYwHAvsEXh3UXtvPPPtadPFVApKLgRVPgAABAgQIECBAgACBRgW2JuqXmlX7J3eXJg1qmjDe2hpDONLom+mBatd+CHsicd7IA4OjoUfuCUWiOU+uTmyIU1UHEdj6YIufJWYDQUAyyDtDMwkQIECAAAECBAgQILBTYOsX63kxtYciqb5r4UMtAcnWthi11HPnMHLZgwL5WK/5/dnC6pYHu3HYR78KRVIYEl8PhSLDDhEN3xDY+nkibheSZIgCEu8pAgQIECBAgAABAgQIENiakFoSqnnidV7fVyszavi9eGvliHDEe3SPQEurMRzGvqdHx7lm63tQS99vxuk1La1Z4D+mafpqo4I1/PxThSGIKrpBJQgQIECAAAECBAgQIPCIwNak1LxSrU5Sre3HXUPwsPVJzxrq+Mjg9NDdAq1sp5Ua5DD23V3b9YXpgPXvHbbedT9r3DMCewKSqJmVJNM0CUieGaSeSoAAAQIECBAgQIAAgScFRglGwrjm1SPCkSffBX08u6WVGA5j72PMvdOKPaFIlG8LrXeU3UtgmrZ+vsiNhg9JBCTeMgQIECBAgAABAgQIEBhH4Egw0upqkbw3Xx00X8PKjFef8KyhfuO8M9pr6fy9XPt4cd5Ie2OsZI23vvf08P2mpJeyCJQQ2Nq+U0jyISAgKTHclEGAAAECBAgQIECAAIG6BY78ktzLRNWrT0/WMJn812mavl4ZNjXUr+4RPW7tWttOK3pKODLmeBWKjNnvWl2XwN6VJPGzX6wkGfIlIBmy2zWaAAECBAgQIECAAIEBBLYmp+YEvQQjqV1roVAN4cPamShR9xrqN8Dbo8kmthg0tLQFWJODorJKb33f6e37TGX8qkNgUWDrfZluGnarLQGJdw4BAgQIECBAgAABAgT6Etj7i3BqdY8TVmufmPx5mqZ/eri7hSMPd0CDj2/17I78MPYev840OJQuqfLW95zo+xT+pn+/pCIKJUBgVWDPSpJhV5EISLxzCBAgQIAAAQIECBAg0IfA1iTVvJU9r1RYWz3y9KcjhSN9vNfubEWLIcPS16Kn33t39tkIz9r6fiMUGWEUaGNrAntCkiGzgiEb3droVV8CBAgQIECAAAECBAi8ENiaqMpvHeFT3LVurZVPdI8UVnnznhNocTutaOl8Am7YTySf6/aq70rfa1I/L1V2hO8xVXeSyhHYENgKSYYMswUk3jcECBAgQIAAAQIECBBoU0AwstxvSwHJ05O0a6FNtKDnlTxtvrOerXWLh7AnsVZDnWd7vO6nC0Xq7h+1I3BU4NXPI1GWgOSoqOsJECBAgAABAgQIECBA4HYBwcg6eY1bawlHbn+LNPvAfKy09kl84Uizw+43FY/vMfH6/mNF0FLLWhuf/fSOlhB4T2BrBcmPL9737z254rutIKm4c1SNAAECBAgQIECAAAECmcDWp/5yrFEnr5bO+HhyhYZwxFt4j8B8wurJMbunvvNrhCNn1Oq650goEjV32Hpd/ac2BLYEjny4prXvQVtt3/x7AckmkQsIECBAgAABAgQIECDwqIBgZB//ktOTv+QLR/b128hXtbydVvSbw9jbH71bk6YOW2+/j7VgbIH4WeSbE6tChsoMhmrs2O8HrSdAgAABAgQIECBAoDEBwcj+Dluzeup33ldbWDwZ2uwXdeXVAq2vulg6jD3GtpUFV4+c98vfCkXiCaOuQnxfVwmtCqRVVPP6z/9/hA1HXmvlHinj52ma/vbxT2yBNX/Nv+7GM8+EInm5T/38dMSl2LVDNbaYmoIIECBAgAABAgQIECBwncDRYCQO1Bz5VeO5I0tbfUUfCUdGHqm/tn1p1Uhr7+HWw50RR6FQZMReH7fNeSiR//s83CgRXvSqPFRmMFRjex2x2kWAAAECBAgQIECAQBcCeyawUkNNtP8qsRaOPOkjHOni7XhJI1o+hD2BCEcuGRqXFHrkXBErfy7pAoUWEBB2FEA8WMSTP0MdrGqZywUkZRyVQoAAAQIECBAgQIAAgbMCe4ORmMCKrRVigtLr10/i/7AA8eQv9muBzZ+nafqdThtWYP4ef3KMvtMJ8X7LJytbbcc7Bi3cu/U9JW2fFW0RjLTQo23Xcb5K49WKjmipVR3P9nd8TWhtVePbYgKStwkVQIAAAQIECBAgQIAAgVMCW5NYqVB7wS/zLq3UeHLCtsbVLKcGppuKCuShQsvv5Xk4IvQrOkzeLmzr+4nD1t8mHqaAFFDEmJmv3kjjKP3/2LLqP6dp+sdMJ/5uft0weI02NH0AJ/4cMjQVkDQ6clWbAAECBAgQIECAAIGmBeaTjWuNiU/xDfnL6kbvLvkJR5p+S3RX+V62olo6jN1KtjqGawpFojZrn7pvOZSrQ7nOWpw5UDzet87gqLM/n6iVrw2ZuoDkiSHomQQIECBAgAABAgQIjCqw9wD2Jyf7a+8b4UjtPTR2/Za202r1U7lL4Uh8bRLaPjvG96wW0U/P9NGe1RPzcGMeWuQ1t93UM/3Y61OFIis9KyDpdchrFwECBAgQIECAAAECNQlsTWilugpGXvfaf0zT9NXskif3y7atVk3vsufr0sMh7ElxPrZNrD07vra+hwy/Rc4b3bMUQiyFGKOtwMhm0Yf0AAAgAElEQVS32EqhaBjEK0Kd9O/xPfnn7P/Hv6agSMDzxsAsdKvt9XZACkh2ILmEAAECBAgQIECAAAECJwW2JrUEI/thl8II4ch+P1deJzB/nz85Lku0spftwUpYPFlGmlz+3hZav+mGPVtMLa3M6HHCfmlFVwovcrj8XJD5PXetCnt1YPu8k1+trFl6X+Znp6SQJv4827Ylw/lzj5Z99Pr8efPzYF59bcqf884zn/z6d+uzBSS3cnsYAQIECBAgQIAAAQIDCezZTsunsvcNiCXL+MTqP+27vfhV862H0gOsACpOXX2BPa0aCWzhyPNDbitY7+X7xtpkeZoYn6/YaC3c2DsxPZ+IX7tvb3nPj2A1INCYgICksQ5TXQIECBAgQIAAAQIEqhfYmtyKBvQywXVHZ9S2ciTa/Gmh4a2vGrijL3t6xjwk6yEcm5/v00ObWhlzW983attC61VYkf6upQPB18KHpfAiP2ckjS/hRSvvNPUksCAgIDEsCBAgQIAAAQIECBAgUE5ga9WIYOSYdSvhSLTK79fH+rblq/MgoYf39NKKKOHIPSN0TzByx4Hrr7Y+SkFHLSs49mwplc7PWLpWmHHP2PYUAs0I+AGuma5SUQIECBAgQIAAAQIEKhbYmuSKqptwPNaBtYUjr/rY79bH+rbVq+dBwrdv7G9fi8G8TT0EPrXYrtVj6/vF2T5YO6MgX8nxVMixFWosnYkxP1Oi9n5VPwIEGhXwQ1yjHafaBAgQIECAAAECBAhUI7Bn1UhMpHrtF1g74+PJCen59kOpNU/Wab+oK98R6O0Q9mQx/9p1dmL+HdtR7t174Pq/T9P0b9mh7F9//u9/mKZp6VyOq8KOrTAj9ZmDoEcZvdpJoHMBAUnnHax5BAgQIECAAAECBAhcJnDVp4Avq3AjBQtHGumoQao5DxF6CcSWwhFBbplBnQcXv5um6f+ZpimCjrXXTy/+/udpmr5auXFpG6l0ZkYeqAg0yvSrUggQ6FRAQNJpx2oWAQIECBAgQIAAAQKXCmytGrGd1nn+pZUaT05KWzlyvi9bvrPXVSPRJ/MxHRPtwpHl0bp326q0muLMqo58JUYKOJbCj1fnarT8XlN3AgQIPCogIHmU38MJECBAgAABAgQIEGhMYM+qERON5zv108KtT4ZNa0HYk3U6r+vOvQJ5v/e07dTS169RxvKrQ8hjXOTndMR/nwk6YiVIrPaILbGWXvH3f/7YQmvvWHQdAQIECFwsICC5GFjxBAgQIECAAAECBAh0I/Bq1UhPk6hPdVhtK0eEI0+NhOeeOw8QegoPlsZzS+1bCizS/5uHG2kEnQk55udvpBUdUebSmRvxjPgn6rD2PN8fnntPezIBAgQ2BQQkm0QuIECAAAECBAgQIEBgcIGtVSMtTTLW2pVL4ciTrsKRWkfKdfXqddVIiNUUjqQQYR4mlFjBkUbHnkPG59cs3fNqtG19X4h7n/wadt07RckECBDoTEBA0lmHag4BAgQIECBAgAABAkUFrBopyrlYmJUj1xt7wrpAz6tGSocjR7epiuefWcWR91YKLvKVHPH37wYcZ94Te0IRq0XOyLqHAAECDwoISB7E92gCBAgQIECAAAECBKoVeDURZgKsXLdZOVLOUknHBXpeNbIWjvx+mqY4C2MeXiyt4EiHgh+X/fKOVys6lratevd5Je9PAc/3G2GP7wsl1ZVFgACBGwUEJDdiexQBAgQIECBAgAABAk0IvFo1YsuUcl3YSjgSE5/flmu2kioQaGnVyKuzN4Iygo1YXZEHHHHPzx8HhpfgzkOM+UqOKP+J1Rwl2vWqjD2rRVLb4/vC0S26rq6/8gkQIEBgp4CAZCeUywgQIECAAAECBAgQ6F7AqpF7unjNOUKIpyYZX4Vifm++Z1zc9ZS7V43sCTjmbX93W6oly3hvpSAl/kyrQ3oMN86Opb2hiGDkrLD7CBAgUKGAH/Qq7BRVIkCAAAECBAgQIEDgdgGrRu4hbykcsXLknjFx11POrhrZOncj6j9fvVGiTWcPGq/tTJ8SFleWcSQUiXpYRXhlbyibAAECDwgISB5A90gCBAgQIECAAAECBKoR2Fo1Ymulcl0V1jF5O3/VunLkyXqVU1dSCOQBaGw9FSso4s/5uRtxbYnVG2srobZWbsSzz66iWnp/CfmWx//RUCStvolx5EWAAAECnQkISDrrUM0hQIAAAQIECBAgQGC3wNokmcN2dxPuvnBthc6Tv5OmOi2d1eBT4ru79pYLt1ZxlF7BMQ8paj93Yy0ccTbGfw3Po6FI3Ol7wS1vbw8hQIDAswJP/jD6bMs9nQABAgQIECBAgACBkQXWJuxNjJcfFUvWT3+y3ZZq5ft5b4lLYcd8Jce7qzhifH2VHVL+t48VI/+eVTKFIGdXbOxt79XX1Rg+Xt3mveWfCUUEI3t1XUeAAIFOBAQknXSkZhAgQIAAAQIECBAgsEtgbZunpyfsd1W+wYuEIw122o4q5wFG/u9XBB15ddJKjrVQIx08/n22VVbPoedfp2n6etZfI38tS2Mx7/8dw/mXS6wW2SvlOgIECHQmICDprEM1hwABAgQIECBAgACBVYGlw4vjYmdNXDNolryfnqy2cuTLvk4TyvnZF+n/ldy2Kg805ttVzcOOd1Z05P3b84T3q+0BRzs3KVnEyD6z8qjncXLNV3alEiBAoDMBAUlnHao5BAgQIECAAAECBAj8RsBk4r2DYs1bOFK+H9KEcFo5MZ8kjm2m8sPIz04g589JrVhazfFOuPGOznzMPT3W3mnL1r1rIV/08z9t3dzJ35/dOis1XyjSyUDQDAIECJQQEJCUUFQGAQIECBAgQIAAAQK1CvxpmqbvZpUzOXZdb60dFh2T6TGx+9Sr9pUj8y2r8sAjzNJqjqVAZK9pKjPCg1TePOTIV5I8FXbsbU+6bvRVI+HQ+7ZaMS7jnxi3Z0K+ZBR/Orj+6DvM9QQIEOhcQEDSeQdrHgECBAgQIECAAIFBBWpdxdBzd6yFEE9vYZaHNj/NzmwoMbG8dOh4ChdKbleVhyap/Pl2VflE8NL1PY2/NGke5030HhKsvbdKjN9ax8S7W2eldgnEa+1h9SJAgEAlAgKSSjpCNQgQIECAAAECBAgQKCawNJk40vYzxSAPFFTjYexR/bxea+HIUsCRmj4/dDwnOfNJ9jw4WTqX49Xh4we6o/tL89Cr5wnwV1tJpZUQraz02RqUJVaJCEW2lP09AQIECPxGQEBiUBAgQIAAAQIECBAg0IvA2mTi0ysYevFda8dSOHLnGRBrAUfakifq/bdpmv6hYEesHTr+arK6l4nsgoynivoh22bpznF2qrJv3PRq1cjTW9a90awvbi21SiQK7TkoK+WtHAIECBBYEBCQGBYECBAgQIAAAQIECPQgsLaCwX7z1/ZuPlmdnnRm0np+Bse81vlKjjMrN+blxWqSCE3iNd+mKg8y8n/Pz+e4VlXpSwLz8216DT63Vo08eZZPiZH57gHreR2EIiV6RBkECBAYXEBAMvgA0HwCBAgQIECAAAECjQs4a+S5DlwKR34/TVOED/MQY37IeIlaL63IiLAjgo8/fjzg/0zT9P/OHtbrxHoJ01rLGGXVyDwEyvuj1XGbvhbEWTHvhpvpPS/4rvWdql4ECBBoUEBA0mCnqTIBAgQIECBAgAABAr8I1HruRQvdc/Rg8dSmdyc4Uzlr4ca7W1TlE8x/nqbpu1lnnFnd0kJ/9lrHPADtfbXAUuAY/driWSOlzxPJHXod69pFgAABAg8JCEgegvdYAgQIECBAgAABAgROC4y+amQppEj/L1ZqxCqK+eHipYKNpU6LFRv/Pk3Tz9lfLgUdV5/BkYcjSwbCkdNvuUduzAPQGDuxgqLHVy9bal1xnkj099VfN3ocU9pEgAABAgcEBCQHsFxKgAABAgQIECBAgMDjAktb0NT+yfK1cCL//0vBRulQYz7ROD97Y20yMt339GHsrwZfPsls5cjjb9O3KjDKWSOB9CocaWFLrStCEYHIW28fNxMgQIDAUQEByVEx1xMgQIAAAQIECBAg8JRAqQPBt+q/tkIjJu7WztbIyywZbOTPzCcOXx0sntel1GTjUjgSQcTvtjBv+vs0NmKVSJx1kL+sHLmpEwo8ZpSzRhLV0te02lfLlDpk3XkiBd4wiiBAgACB9wUEJO8bKoEAAQIECBAgQIAAgWsFtlaN7FmhETWcbzsV/69kmDEPJqLstbM20rVPbEV1tLdqXjkSbcnDkejjvE9rn2w+2he9Xj8/ayQCwBh3Pb9qf1/l9iVDkQgs41UqvO15jGgbAQIECNwgICC5AdkjCBAgQIAAAQIECBDYDCLmZ2gEWUx2fz1N0z9c7JdWaWyFGWlSbx58vLr/4qpfWvzapGhNW//86eMg9jTpmq8eEY5cOjyKFR5BQQq2at8ur1ijP690+jQrrLaVTqW2zxqpT0uOD2URIECAwE0CApKboD2GAAECBAgQIECAQEMCr1ZV3L3F1Jztp4/QJIUV6e/TllPpLI+t0MKnl18PyKVwpLbAIa0c+f1HiDbfWsvvu3V/0ZmPsZqCt6vlllaPPD1eoz/inxLBtFDk6hGkfAIECBAoJvD0N+BiDVEQAQIECBAgQIAAgUEFtraIShNeWzxb5Wzdv/T3aysy0lZXKdSYX/fHLARJ5canq+M6wcaZnjh2z9LkbW3hSKrj0sqRaK3fdY/1+d1Xp/772zRNEXqm9/fd9XjqeUtnj9w9ZvNA5N2v/84TeWokeS4BAgQIvC1w9zfgtyusAAIECBAgQIAAAQINCsy3ZFo7BHzetLvOzFgLHe4+CHzrrJEGu765KrdwLsJWOFLbVkXNDYILKzziWSNzzqfeY3kgEnV6NxSJMqwUufDNomgCBAgQuEdAQHKPs6cQIECAAAECBAi0JZAmjtI2TXnt80mlfCXEPMwoMfk0V9sbZOT3pXtqX3mxNmlo1ch9752nJm6PtDAPR2JsxCfx85dw5Ijmfdemyfm0DdqoE+tL77HohSvmZtL3oDAv9f3ISpH73jOeRIAAAQI3CVzxTfimqnsMAQIECBAgQIAAgV8mfdKETT4BtPT/18KMV2HIWeKtMGK+MiOes3TPVjln61fTfS0cBF6T11V1Wdryp7awIdUxbcckHLlqNJQtd74ybKSzRnLJ+Hq+tCowvh9EcLL2fWBvb5Q6VH3+PKHI3h5wHQECBAg0KSAgabLbVJoAAQIECBAg0JzAUmCRr85Y+nTrq0BjaWXHGZS8nDyMmB/4ncqeBxbzcGaEQOOM89o9Vo2U1DxXVisBVR6OxLiZBzq1hTnneqOvu+Zja+RzhNZWjrzq8fh+snZOU9yXny9VaoVIHtKk8318X+vrfak1BAgQIDATEJAYEgQIECBAgAABAmmiJU2MzCda1iZe8k/Crq3kKKmbhxHzMCPqkq/KSMFHft3a/SXrqKx9Aq1Myu9rTbtXtXAYe+jOw5F5vYUj9Y3BvI/SRH9aJVFfba+v0afrH3H6CfkKkTwgOV2gGwkQIECAQEsCApKWektdCRAgQIAAgREF9n4q9NUKjOSWX1NqBca8T16FGHFtHmSsXbsUbozY9722eW1SPn26vNd219auFs4bEY7UNmq26zPfTmvUs0bmUktb2G1rXnNFCqyc73SNr1IJECBAoDEBAUljHaa6BAgQIECAQFUCe8OLqHS6dmn/8aUAo3RD54HIfMuMpdUXqQ7zVRj5mR2l66m8fgXWVo349P/9fd7CeSN7wpH42hTnWXg9L7D0/vbe/q9+Wfv6d3XPWR1ytbDyCRAgQKB5AQFJ812oAQQIECBAgMCGwFKIsRVsPBFirO3xvXSYd9Qv7Q2ehy9r52MYJASeFrBq5Oke+PX580/3p1rVeGj21rZawpE6xlTUYv7+1jf7+ib9LJL/TBLf37d+RnlVer46JK5zfsi+vnAVAQIECAwsICAZuPM1nQABAgQIPCCw9Uv/nm2i8mpvlXdFE5cmG5ZCjPzZS+dgXFE3ZRKoTcCqkXp6pKWQKtU1rUBYCnZqDHXq6e17arL0/tYv5ezDd2v1afz8kX7GEIaUs1cSAQIECAwkICAZqLM1lQABAgSGFjhygParA7njF/G11RVHnlG6M7YO334VYLyaUDDZULqnlDeSQEsT8j33S2sh1Z5wxNZNz4/Y+TZtzhp5vk/UgAABAgQIEDghICA5geYWAgQIECCwIJCHA+mv96xuyM9yeLV64lUwEc9Lz9/zzLs6cCtcWAot9hzOvVXuXe3zHAIElgXSp56/n/21Se37R0yr4Ui+RdN8It4KhfvHUf7EpeBTnzzbJ55OgAABAgQIvCEgIHkDz60ECBAgUFxgKWTIH3J28n/Pfa/OnDgSeBRHOVngVtCQApetlRWv+mTrGSer7jYCBBoWiMnT+R76Pln+TIcuTWRHTWqdzE5ByKtwRMj2zFiKp64dwh795YMLz/WLJxMgQIAAAQJvCghI3gR0OwECBCoRWNraKN9yKKqZJrPngcP8urVrY8JrPpmehwpbWy+lclsMG+bdfGQiIDdbMkxlb20RdfS6SoamahAgMJDA0oS8Ce37B8DaqpGaD85eCkfm48lYun8spSdaNfKcvScTIECAAAECFwsISC4GVjwBAkMIrJ27sBZazA9bzIOF/5ym6R8ztSfPdCjReUuhzDwoOfqcrcOw50HC0fKPhB9Hy3Y9AQIEehRobRunHvvg1UR2/F3N4cL8zJGor3CkjlG6tmok+seLAAECBAgQINCFgICki2483Yj4pFa88gnYfKJ2/u9xbfq0eJqgfPVp6FSx+QRpPvmY771/tCEmMY+K9X/90jZKaxP0aezPVZbGeH7N1nkR7yr/NE3T19lWBa+2NzrzHl16Py69D9eee9X7+V039xMgQIDAMwIOYn/Gff7UV6tGIhyp9edm4Ugd42epFvOzX+KaWrdnq1dRzQgQIECAAIHqBQQk1XfRpRX8NNty59VE8qUVeajwPb8oLm0ZtPfT69Gs3HTv9jlLHPNy5pP0S2XPVx6sPf/VdakurybVt7pvz9kPayHFUtlnytuq456/X9quKt23FFSs9f+r/7+nHq4hQIAAAQK1CCxNoNa8UqEWt9L1WDtrpPa+WNpWK2zid5T8Z9CYlPe6T8BWefdZexIBAgQIECBQgYCApIJOaKgKa1v9bE2eL30SPZ/kXjr/YC/LnkOVX5X11GT73va5bl1gT8CV370UbC2V8SoI0R8ECBAgQIDAr6uP00rkfCK75pUKPfZbq6tGoi+EI/WNyLXxZNVIfX2lRgQIECBAgEBBAQFJQUxFdScwD0/2Bjnz8OdICJNvWZZv9bT070+A51urxfO3VtOUOH/iaBDyhItnEiBAgACBUQSsGqmjp1tdNRJ6S9tqxf/PV47Ef5uYv2esvQrarN65pw88hQABAgQIEHhQQEDyIL5HEyBAgAABAgQIEGhEwKfL6+iolleNhODaypF54CMcuWe8OUPoHmdPIUCAAAECBCoWEJBU3DmqRoAAAQIECBAgQKACgbVJVJ8uv7dzWl41Ihy5d6xsPW0taKv93Jqtdvl7AgQIECBAgMBhAQHJYTI3ECBAgAABAgQIEBhGwJZaz3d166tGQnBtWy0rR+4fX0vv6djS1hlC9/eFJxIgQIAAAQIVCAhIKugEVSBAgAABAgQIECBQmYCD2OvokNZXjYTi3m21rF64dswtvafjidyvdVc6AQIECBAgULmAgKTyDlI9AgQIECBAgAABAjcLLE3Km0S9txN6WDUSYntXjhhf142vXsbSdUJKJkCAAAECBIYWEJAM3f0aT4AAAQIECBAgQODvAg5ir2MwLG2BFDVr7eDytZUj0Za8jT9N0/TPddB3V4u1sSSQ6q6rNYgAAQIECBA4KyAgOSvnPgIECBAgQIAAAQL9CKxtqeUg9vv6+NXB2XFGRPzTyitNzC9NxOeT9tEmY6x8r65tp+WskfLWSiRAgAABAgQaFxCQNN6Bqk+AAAECBAgQIEDgTQFbar0JWOD2pT5odTJ778oR4UiBgTMr4tV2Wj9+vjbGmRcBAgQIECBAgEAmICAxHAgQIECAAAECBAiMK7C0BU9rWzm13Hs9rRqJfni1ciQPgYQj5UftUsgWT7GdVnlrJRIgQIAAAQIdCQhIOupMTSFAgAABAgQIECCwU2BpYt6k9U68QpcthVOtrhrJx9PSOJpP3pu0LzSIPm+9ZjutcpZKIkCAAAECBAYUEJAM2OmaTIAAAQIECBAgMLSALbWe7f61T/q3HFDtXTkS8sKRMuNvbfUR4zK+SiFAgAABAgQGERCQDNLRmkmAAAECBAgQIEDgs8B8cr7VFQstdubahHY6G6KlQ9hz/08f/7EUfFg5cs1IfRWyRT+0Opau0VIqAQIECBAgQOCFgIDE8CBAgAABAgQIECAwhsB8S6eWVyy01GMRjKRwZF7vlldT5IHPUjvmWz+13NZaxtvadlpRP7619JJ6ECBAgAABAk0JCEia6i6VJUCAAAECBAgQIHBYYGlS1WTqYcZTN/S4nVZAbIUjcU0eyAnjTg2fv9/0ajstq8Des3U3AQIECBAgMLiAgGTwAaD5BAgQIECAAAECXQssTdB/awuey/v81YR2D/6vttWahyPx3z20+fJBs/KA+cqv/DKuT/WK5xIgQIAAAQLdCAhIuulKDSFAgAABAgQIECDwhcDSllrOJ7h2kPS6nVZSy1cjra1Cmodyfuc8N+bWVh9FaVaAnTN1FwECBAgQIEDgNwJ+WDUoCBAgQIAAAQIECPQnMA9HTKhe38e9H5x9JhyxwuH4uLOd1nEzdxAgQIAAAQIETgsISE7TuZEAAQIECBAgQIBAdQLOG7m/S3rfTitEz4QjQrljY/HVOIqShE3HPF1NgAABAgQIENglICDZxeQiAgQIECBAgAABAtULOG/k3i7a+qR/TGj38MrH1d5ttYQjx3r+1XZaDrg/ZulqAgQIECBAgMAhAQHJIS4XEyBAgAABAgQIEKhSYD7BalL12m7qfTutpLcnHJmvWhKO7B97WyGbM4P2W7qSAAECBAgQIHBKQEByis1NBAgQIECAAAECBKoREI7c1xWvJrR7Cwb2hCMhn593I5jbNxa3ttPqbSztU3EVAQIECBAgQOABAQHJA+geSYAAAQIECBAgQKCQgMPYC0FuFDNSMBIUe8OReTjnnIzXA2krGBEw3fN+9hQCBAgQIECAwN8FBCQGAwECBAgQIECAAIH2BJYOYzc5fU0/jrKdVtLL2/tqTAlHjo23rXNGbKd1zNPVBAgQIECAAIEiAgKSIowKIUCAAAECBAgQIHCbwNKWWiZXy/O/CkZ+/Py4+PveXmfDEVtCrY+ErVUj7Hp7F2kPAQIECBAg0JSAgKSp7lJZAgQIECBAgACBwQXmk/YmV8sPiNG200qCwpGyY2krGInttASbZc2VRoAAAQIECBA4LCAgOUzmBgIECBAgQIAAAQKPCAhHrmV/NaHd+2T23nBkvrWbgO63Y1Iwcu37VOkECBAgQIAAgaICApKinAojQIAAAQIECBAgcImAw9gvYf2l0JGDkWh/Pra2fj/8NOuGreuv67U6S351zkjUWKBUZ7+pFQECBAgQIDCwgB9oB+58TSdAgAABAgQIEKhewGHs13XR6MFIHo7ECpk4kP3Vax7S+V3yv7QEI9e9T5VMgAABAgQIELhUwA+1l/IqnAABAgQIECBAgMBpgXk4smcS+/TDBrpxawukCArCuvdXCjz2jCvbuy2Phq2x1PvWbL2/R7SPAAECBAgQGEBAQDJAJ2siAQIECBAgQIBAcwImpMt32dZk9ijBSMgKR94bX1tjSTDynq+7CRAgQIAAAQK3CQhIbqP2IAIECBAgQIAAAQK7BObhyEgT97uADl60NZk90rkQ+aqkPe0W1H052LbGUly9x/XgEHY5AQIECBAgQIDAVQICkqtklUuAAAECBAgQIEDguIBw5LjZ2h2vzoUY8RP+R8ORcM0PZd+zFVe53quvpK1zRkYcU/X1khoRIECAAAECBA4KCEgOgrmcAAECBAgQIECAwAUC80+mjz4ZfZZ46xP+o05inwlH5oeyj7qSyZg6+250HwECBAgQIECgAQEBSQOdpIoECBAgQIAAAQLdC+ST0bboOd7dJrHXzfKVD3vHlq21pmlrTIX4Xs/jI9odBAgQIECAAAECtwgISG5h9hACBAgQIECAAAECiwImot8bGFuT2KOuGEmqwpHj42trTAlGjpu6gwABAgQIECBQrYCApNquUTECBAgQIECAAIHOBZw3cr6DtyaxRw9GQrZEODLaVm/OGTn/nnQnAQIECBAgQKBJAQFJk92m0gQIECBAgAABAo0LCEeOd+BWKBIl2vLoV9d8fB05OyQ/lD3KOXLv8R6t5w7BSD19oSYECBAgQIAAgVsFBCS3cnsYAQIECBAgQIAAgS8mr0f7hP6Z7t8KRqwW+VI1P8/mSMAxP5R9hLBpa2yNFBKdeW+6hwABAgQIECDQvICApPku1AACBAgQIECAAIGGBPJJaOHI647bmrwWjPzWL62EODq2RjsLZ2tshewIAVFDXzpVlQABAgQIECBwjYCA5BpXpRIgQIAAAQIECBDIBWJCNsKR9DL5uj4+wup/T9P01colgpFlmBS+vRuOHL2/pXf6nmDE+GqpR9WVAAECBAgQIPCmgIDkTUC3EyBAgAABAgQIENgQEI7sGyJzp/wuk9avDVM4cjR4m5v3HI44Z2Tf+9BVBAgQIECAAIGhBAQkQ3W3xhIgQIAAAQIECNwskE/K9jz5/A7rq4lrwchr2TzgODO+RjiU/VXwlnSPnNXyzlh3LwECBAgQIECAQGUCApLKOkR1CBAgQIAAAQIEuhEQjqx35dZWR4KR7bdBbnh05UiU/tdpmr7OHnOmjO1aPk65FIcAACAASURBVHfF1hiLmvXW5ue0PZkAAQIECBAg0KiAgKTRjlNtAgQIECBAgACBqgWEI8vdszVpLRjZN6zzVRFnJvn/NE3Td52GI1tjLJptnO0bZ64iQIAAAQIECHQvICDpvos1kAABAgQIECBA4GaBdB5EPPbM5PXN1b3lcVuT1ias93dDHr6d2RpqvqXZz9M0/dP+x1d9pXNGqu4elSNAgAABAgQI1CcgIKmvT9SIAAECBAgQIECgTYH5WQdnJq/bbPl6rQUjZXs0DwDOhG9LAUIP41QwUnacKY0AAQIECBAgMIyAgGSYrtZQAgQIECBAgACBCwWEI1/iCkbKD7bSK0eihmdClvItO1/i1jjroY3nddxJgAABAgQIECCwKSAg2SRyAQECBAgQIECAAIGXAv86TdMfP66IraLiE/kjvvZMVttK69zISNu2nfWbB3itBwd7x9qo78Vzo8xdBAgQIECAAIEBBQQkA3a6JhMgQIAAAQIECBQTeHfLo2IVebCgvZPVsVohJvi9jgmkMfZO+PZp9shWV47EWEvjbU3xbIh0rFdcTYAAAQIECBAg0IWAgKSLbtQIAgQIECBAgACBBwRGD0cEI9cPunzlyNnVEKmMVNtWwxHnjFw/3jyBAAECBAgQIDCcgIBkuC7XYAIECBAgQIAAgTcF5sFAqxPOZxj2hCJRrk/xn9H98p4S4cg8VHhnFcr7LTpXwp4x18NB8+d03EWAAAECBAgQIPCWgIDkLT43EyBAgAABAgQIDCaQT9aOEgLsmaBOw2AUkyuHfX5eyDvh29KKi5aChD3j7h2fK/tQ2QQIECBAgAABAo0ICEga6SjVJECAAAECBAgQeFwgn7hu8ZP4RwDzcx7i31+9wuLHzxfEhLzXewKlwpGWD2XfE4wI4t4bZ+4mQIAAAQIECBD4EBCQGAoECBAgQIAAAQIEtgXyT+P3Go6kIOT7j4Owt1RMUm8JHfv7UuFIPLXVc0ecM3JszLiaAAECBAgQIEDgTQEByZuAbidAgAABAgQIEOheoOfD2I+GItHZgpHyQ77kGJuHDC1sQ7W04iVXNubKjzklEiBAgAABAgQITNMkIDEMCBAgQIAAAQIECKwLlJy4rsU5JqPjn292rhRJ9TZJfU0PlhxjSyswav6db892Wi0EPNeMDKUSIECAAAECBAhcLlDzD8uXN94DCBAgQIAAAQIECKwIpBAhtpuKV+uTtEfOFMlJhCLXvkXyQKPEAeqfZtWtddzuCUaMvWvHntIJECBAgAABAgSsIDEGCBAgQIAAAQIECPxGYL7dT4mJ6yeY90xCL9XLxPQ9vVU6HGllay3njNwzvjyFAAECBAgQIEBgh4AVJDuQXEKAAAECBAgQIDCMQB6OtHgY+7uhSHR0tNvrWoGrw5GofW3BnnNGrh1TSidAgAABAgQIEDghICA5geYWAgQIECBAgACBLgXySetWwpGzW2elICS2YBKI3Duc0zgrNcaWgoeattbaCu3C4cfPXRAuXgQIECBAgAABAgRuFRCQ3MrtYQQIECBAgAABApUKlDwo++omCkWuFr6u/NLhSNT0h88hV4yJ/FXD73lbwUjUt1RIdF2PKZkAAQIECBAgQKBrgRp+cO4aWOMIECBAgAABAgSqF8gnmGv65H0Ot2eyeQk6rQ6xUuTZYZj3X8lQYOk8jxrG8FJok/eAc26eHY+eToAAAQIECBAg8CEgIDEUCBAgQIAAAQIERhaoORx5JxSJSfJ42T7r+dF9ZzgSrX3ydzwHsD8/3tSAAAECBAgQIEDggMCTPzwfqKZLCRAgQIAAAQIECBQVmJ/bUMOB1mki/atpmuKfI6/0iXyhyBG166/Nw5HSKzs+LVS/9DP2Cm0FI1FODe+xve1xHQECBAgQIECAwCACApJBOlozCRAgQIAAAQIE/i6QhyNPbfUTdYh/vvmo1fwMiT3d9VTd99TNNb/2b6xQilfp4OJP0zR9N0Mu/Yw9fbh0QPz8PuN0j6RrCBAgQIAAAQIEHhEQkDzC7qEECBAgQIAAAQIPCeSfdC95FsSr5qTw4/uPi86EIXGr80QeGjQnHpsHB6VXTqyt1rjzd7s9278JRk4MHLcQIECAAAECBAjcK3DnD9H3tszTCBAgQIAAAQIECHwpcNd5I/nqkLNhSKp5TDL/+BGOOE+kjRGdBxilw5EQWDoA/a7VI3uCkajjFe1uo/fVkgABAgQIECBAoCkBAUlT3aWyBAgQIECAAAECJwWuCkdKrQ7JA5H493+fpuknh6yf7O3nbnsiHInWXv173d5gJIKaCPKEec+NQU8mQIAAAQIECBA4IHD1D9IHquJSAgQIECBAgAABAsUF5hO7736y/apAJE0sFwdQ4G0CeThyxe9ZS1trXb2N1d5g5Op63NaJHkSAAAECBAgQIDCWwBU/uI8lqLUECBAgQIAAAQK1Crx7GHvpMCSc8nNE8v+u1VC99gnEWPnf0zR9ddFqjrXD0N8N/NZatzcYifvv2t5rX0+4igABAgQIECBAgMABAQHJASyXEiBAgAABAgQINCNwJBxJQUj8+c1HC989OyRBOUOkmSHzVkU/fdx91e9Xa6tHIiAp+ToSjMTYLv38km1RFgECBAgQIECAAIFNgat+gN98sAsIECBAgAABAgQIXCSQTyanSdw8BInHlg5CUlMEIhd1asXFpnDkqtUcS+FIcJT8Xe5oMGJLuIoHpKoRIECAAAECBAjsFyj5Q/X+p7qSAAECBAgQIEDgLoF8JURPByfPV3ik//7uY5uju3wFIndJ1/mcFF5ctc3U2tZaJZ53JBQJfeeM1DkG1YoAAQIECBAgQOANAQHJG3huJUCAAAECBAhUILC0PVRU650topaClFRe/N07Zedka4HNf36EHOmT+fk9pZ59puucH3JGrd978vDiqt+rllaPvBOORJ3TVnJH3kvvPLPfEaBlBAgQIECAAAECzQtc9YN88zAaQIAAAQIECBC4SOBfp2n6n1nZEQL8uPGstB1ULUHBRTTVFZuvDonK9bQCpzrsxir0VDgSTEe28kohyPcng03njDQ2MFWXAAECBAgQIEDgmICA5JiXqwkQIECAAAEC7wosrYp4t0z3vyeQgo8IquLfBSHveY5w9w8fgcOVKyuWvlbseV7aOiv64cgqkbzfbKc1wijWRgIECBAgQIAAgaIH++EkQIAAAQIECBB4LRCTjkurQbhdK5AHIPGk9N+CkGvdey09bXt15eqKtbNHlj7gViIQSX0lGOl11GoXAQIECBAgQIDAooAVJAYGAQIECBAgQOA+gf87TdM/3Pe47p6UBxpfZYex/zxN0/83a63wo7vur6JBd4Qj0dC1gCS210qvs9tmLUEKRqoYXipBgAABAgQIECBwt4CA5G5xzyNAgAABAgRGFojzR/44MsCLts+3ucovnYcd+cHVe7YcQk6ghMDd425pi62/FQxZ8zN2BIolRogyCBAgQIAAAQIEmhMQkDTXZSpMgAABAgQINC4w+jZbS0HIkcnZuyepGx9uql9Q4I5zR/LqpucVbMIv28s5a6ekqLIIECBAgAABAgSaFhCQNN19Kk+AAAECBAg0KhArSeL100r9tw5Wzs8x2br2CaJ3Q5C1OucTxlaOPNGz4z7z7nAkpJdWkBztgfRejPfLkSDy6HNcT4AAAQIECBAgQKBJAQFJk92m0gQIECBAgACBRYEIS/LA5LuP7XjijI6vC5rlE63p0+ip+CsmYdMh1KltcQ7DFc8pSKSojgTyc0fuDBrOBiTpPJHoAu+TjgaiphAgQIAAAQIECJQXEJCUN1UiAQIECBAgQKBVgflqlBomV4UjrY6mPuqdb+l2ZzC3dkj7kqpVIn2MNa0gQIAAAQIECBB4QEBA8gC6RxIgQIAAAQIECOwSyCen4wY/u+5ic1FBgbSK44kt3V6dQZJWidQQYhbkVhQBAgQIECBAgACBewX8knmvt6cRIECAAAECBAjsE8jDkZgEjk/vexG4U+DJcCS1M9/ey+Hqd/a+ZxEgQIAAAQIECAwhICAZops1kgABAgQIECDQlIBwpKnu6rKyeTAhnOuyizWKAAECBAgQIECAgG0KjAECBAgQIECAAIG6BPJw5IltjerSUJsnBPIx6ANlT/SAZxIgQIAAAQIECBC4ScAP/DdBewwBAgQIECBAgMCmgHBkk8gFFwsYgxcDK54AAQIECBAgQIBATQICkpp6Q10IECBAgAABAuMKmJget+9rabkxWEtPqAcBAgQIECBAgACBmwQEJDdBewwBAgQIECBAgMCqwA/TNP3Lx9/aVstAeUogjUNj8Kke8FwCBAgQIECAAAECNwsISG4G9zgCBAgQIECAAIG/C0Qo8n0WjsRh2H/hQ+ABgTyk8zvSAx3gkQQIECBAgAABAgSeEPDD/xPqnkmAAAECBAgQICAcMQZqEci31hLS1dIr6kGAAAECBAgQIEDgBgEByQ3IHkGAAAECBAgQIPCFgHDEgKhFwLkjtfSEehAgQIAAAQIECBB4QEBA8gC6RxIgQIAAAQIEBhaIcCS2M0ovn9gfeDA83HThyMMd4PEECBAgQIAAAQIEnhYQkDzdA55PgAABAgQIEBhHIA9H4qyRCEe8CDwhIBx5Qt0zCRAgQIAAAQIECFQmICCprENUhwABAgQIECDQqYBwpNOObbRZn7J6W8XUaCeqNgECBAgQIECAAIF3BQQk7wq6nwABAgQIECBAYEtAOLIl5O/vFBCO3KntWQQIECBAgAABAgQqFhCQVNw5qkaAAAECBAgQ6EAgD0f+8Lk9sbWRF4GnBGyt9ZS85xIgQIAAAQIECBCoUEBAUmGnqBIBAgQIECBAoBMBk9GddGQnzTAeO+lIzSBAgAABAgQIECBQSkBAUkpSOQQIECBAgAABArmAyWjjoSYB47Gm3lAXAgQIECBAgAABApUICEgq6QjVIECAAAECBAh0JJBPRv9lmqY4BNuLwFMCxuNT8p5LgAABAgQIECBAoHIBAUnlHaR6BAgQIECAAIHGBHxSv7EO67y6wpHOO1jzCBAgQIAAAQIECLwjICB5R8+9BAgQIECAAAECuYBwxHioSSAfj1GvWMkUK5q8CBAgQIAAAQIECBAg8IuAgMRAIECAAAECBAgQKCEgHCmhqIxSAv8yTdMPWWHCkVKyyiFAgAABAgQIECDQkYCApKPO1BQCBAgQIECAwEMCwpGH4D12UWAejvzh81UxRr0IECBAgAABAgQIECDwhYCAxIAgQIAAAQIECBB4R0A48o6ee68QiJUjEZLESzhyhbAyCRAgQIAAAQIECHQiICDppCM1gwABAgQIECDwgED+SX0T0Q90gEd+IWDliAFBgAABAgQIECBAgMAhAQHJIS4XEyBAgAABAgQIfAhYOWIo1CaQrxyJw9jj3BEvAgQIECBAgAABAgQIrAoISAwOAgQIECBAgACBowLCkaNirr9aQDhytbDyCRAgQIAAAQIECHQoICDpsFM1iQABAgQIECBwoYBw5EJcRZ8SEI6cYnMTAQIECBAgQIAAAQICEmOAAAECBAgQIEBgr4AzR/ZKue4ugTwciWf6/eYuec8hQIAAAQIECBAg0IGAXyA66ERNIECAAAECBAjcIGDlyA3IHnFIIB+TcWOcORJnj3gRIECAAAECBAgQIEBgl4CAZBeTiwgQIECAAAECQwtYOTJ091fZ+PnKkT98rmUEJl4ECBAgQIAAAQIECBDYLSAg2U3lQgIECBAgQIDAkALCkSG7vepGz8MRK0eq7i6VI0CAAAECBAgQIFCvgICk3r5RMwIECBAgQIDA0wK21Xq6Bzx/LmDliDFBgAABAgQIECBAgEAxAQFJMUoFESBAgAABAgS6ErBypKvubL4x+XhMjbFypPlu1QACBAgQIECAAAECzwoISJ7193QCBAgQIECAQI0CwpEae2XcOsV4/P7zAezxZ3o5c2Tc8aDlBAgQIECAAAECBIoJCEiKUSqIAAECBAgQINCFQL6t1l+maYpP6XsReErAypGn5D2XAAECBAgQIECAwAACApIBOlkTCRAgQIAAAQI7Bawc2QnlslsElsIRK0duofcQAgQIECBAgAABAmMICEjG6GetJECAAAECBAhsCQhHtoT8/Z0C+Uqm9FxnjtzZA55FgAABAgQIECBAYAABAckAnayJBAgQIECAAIENgTwcsa2W4fK0gHDk6R7wfAIECBAgQIAAAQKDCAhIBulozSRAgAABAgQIrAjkB2ALRwyTpwXm4UiMydhWK/70IkCAAAECBAgQIECAQFEBAUlRToURIECAAAECBJoT+OHz5HOEJM52aK7ruqtwGoupYcKR7rpYgwgQIECAAAECBAjUJSAgqas/1IYAAQIECBAgcKeAcORObc9aE8hXMeXhSJw54kWAAAECBAgQIECAAIHLBAQkl9EqmAABAgQIECBQtYBwpOruGaZy+fk3wpFhul1DCRAgQIAAAQIECNQhICCpox/UggABAgQIECBwp8Cnj4c5c+ROdc+aCywdxm6rN+OEAAECBAgQIECAAIHbBAQkt1F7EAECBAgQIECgCoG0ckQ4UkV3DFuJ+XkjASEcGXY4aDgBAgQIECBAgACBZwQEJM+4eyoBAgQIECBA4AmB9Il94cgT+p4ZAkvnjcT/j/NGYlx6ESBAgAABAgQIECBA4DYBAclt1B5EgAABAgQIEHhUQDjyKL+HfxZY2lJLWGdoECBAgAABAgQIECDwmICA5DF6DyZAgAABAgQI3CYgHLmN2oNWBJa21BKOGC4ECBAgQIAAAQIECDwqICB5lN/DCRAgQIAAAQKXCwhHLif2gBcCsaVWhCPzl/NGDBsCBAgQIECAAAECBB4XEJA83gUqQIAAAQIECBC4TEA4chmtgncIrG2pFeGI80Z2ALqEAAECBAgQIECAAIFrBQQk1/oqnQABAgQIECDwlIBw5Cl5z107iD1CEeGI8UGAAAECBAgQIECAQDUCApJqukJFCBAgQIAAAQLFBP40TdN3H5/S/7ZYqQoisC2wtGok7rKl1radKwgQIECAAAECBAgQuFlAQHIzuMcRIECAAAECBC4WSBPUP03T9HtbGV2srfgkYNWIsUCAAAECBAgQIECAQHMCApLmukyFCRAgQIAAAQKLAjFBHVsYpYlqWxkZKHcJWDVyl7TnECBAgAABAgQIECBQVEBAUpRTYQQIECBAgACBxwQ+fTzZz3ePdcFwD15bNRIQsbWbg9iHGxIaTIAAAQIECBAgQKAtAb9At9VfakuAAAECBAgQmAvEJHW80p/xaX4vAlcLrK0acRD71fLKJ0CAAAECBAgQIECgmICApBilgggQIECAAAECtwtEKPKDA7Bvdx/5gWnMLRlYNTLyyNB2AgQIECBAgAABAg0KCEga7DRVJkCAAAECBIYXiE/vf/MRjKSzR2xnNPywuBwgwri0Uil/mFUjl9N7AAECBAgQIECAAAECVwgISK5QVSYBAgQIECBA4FoBK0eu9VX6lwJr22nFVVaNGC0ECBAgQIAAAQIECDQrICBptutUnAABAgQIEBhQIE1Ux6R0vKwaGXAQ3NjkV4ew/+FzPZx3c2NneBQBAgQIECBAgAABAuUFBCTlTZVIgAABAgQIECgtEBPVaWuj2ForBSSln6M8AknAIezGAgECBAgQIECAAAEC3QsISLrvYg0kQIAAAQIEOhBIZz/YzqiDzqy8Ca8OYbdqpPLOUz0CBAgQIECAAAECBI4JCEiOebmaAAECBAgQIHCnQPoUf0xMx3ZattS6U3+sZ73aTssh7GONBa0lQIAAAQIECBAgMIyAgGSYrtZQAgQIECBAoCGBfEut76dp8jNbQ53XYFUdwt5gp6kyAQIECBAgQIAAAQLvC/hl+31DJRAgQIAAAQIESgvkh7FbNVJaV3lJwCHsxgIBAgQIECBAgAABAkMLCEiG7n6NJ0CAAAECBCoTyLfUiqrFf3sRKC1gO63SosojQIAAAQIECBAgQKBJAQFJk92m0gQIECBAgECHAnEQ+4/TNMWWWg7D7rCDK2nSq+20jLtKOkk1CBAgQIAAAQIECBC4R0BAco+zpxAgQIAAAQIE1gTi0/zxioAkttP6FhWBCwS2Vo0YdxegK5IAAQIECBAgQIAAgboFBCR194/aESBAgAABAv0LfPpoYnx6PwISZ4703+d3tzDCtxTE5c+OsZbG3d118jwCBAgQIECAAAECBAg8LiAgebwLVIAAAQIECBAYVCBtdZQCEZ/gH3QgXNhs22ldiKtoAgQIECBAgAABAgTaFxCQtN+HWkCAAAECBAi0J5B/ot+5D+31X+013tpOy6qR2ntQ/QgQIECAAAECBAgQuEVAQHILs4cQIECAAAECBH4RmE9c+1nMwCgt8GrVSKxSsoVbaXHlESBAgAABAgQIECDQrIBfypvtOhUnQIAAAQIEGhOIcCQFJM5+aKzzGqjuq1UjVik10IGqSIAAAQIECBAgQIDA/QICkvvNPZEAAQIECBAYTyAmr2NbrXiZrB6v/69u8dqqEUHc1fLKJ0CAAAECBAgQIECgaQEBSdPdp/IECBAgQIBAAwL55LVwpIEOa6iKVo001FmqSoAAAQIECBAgQIBAfQICkvr6RI0IECBAgACBfgSEI/30ZW0tsWqkth5RHwIECBAgQIAAAQIEmhMQkDTXZSpMgAABAgQINCLw6aOesc1RHI7tRaCEgFUjJRSVQYAAAQIECBAgQIAAgc97YAtIDAMCBAgQIECAQFmB/LwR4UhZ29FLi3NsYnzNX84aGX1kaD8BAgQIECBAgAABAqcEBCSn2NxEgAABAgQIEFgUcBi7gXGFQD6u5uU71+YKcWUSIECAAAECBAgQIDCEgIBkiG7WSAIECBAgQOAGAeeN3IA84COcNTJgp2syAQIECBAgQIAAAQL3CAhI7nH2FAIECBAgQKBvAeFI3/37ROtenTUSZ9rEtlpeBAgQIECAAAECBAgQIPCGgIDkDTy3EiBAgAABAgSmacrPhTBxbUiUELBqpISiMggQIECAAAECBAgQILAhICAxRAgQIECAAAEC5wXyiWzhyHlHd/4q8GrViLNGjBICBAgQIECAAAECBAgUFhCQFAZVHAECBAgQIDCMgJUjw3T1LQ1dO4g9ttKKcMSWWrd0g4cQIECAAAECBAgQIDCSgIBkpN7WVgIECBAgQKCUQApHYtI6Vo54EXhHYG1LLatG3lF1LwECBAgQIECAAAECBDYEBCSGCAECBAgQIEDgmICVI8e8XL0usLZqJO6wZZuRQ4AAAQIECBAgQIAAgYsFBCQXAyueAAECBAgQ6ErAypGuuvPRxrw6iN2qpEe7xsMJECBAgAABAgQIEBhFQEAySk9rJwECBAgQIPCugAPZ3xV0fwg4iN04IECAAAECBAgQIECAQCUCApJKOkI1CBAgQIAAgaoFhCNVd08zlVsLR5xl00wXqigBAgQIECBAgAABAj0JCEh66k1tIUCAAAECBK4QEI5coTpemQ5iH6/PtZgAAQIECBAgQIAAgcoFBCSVd5DqESBAgAABAo8LfPqowR8+/xmT3F4Ejgi8WjXyozF1hNK1BAgQIECAAAECBAgQKCsgICnrqTQCBAgQIECgL4H0qX/hSF/9eldrXoUjMaZiay0vAgQIECBAgAABAgQIEHhIQEDyELzHEiBAgAABAtULxOT2Dx+19DNT9d1VXQVtqVVdl6gQAQIECBAgQIAAAQIEvhTwy74RQYAAAQIECBBYFrB6xMg4IxDBWlo5kt8fq0WsGjkj6h4CBAgQIECAAAECBAhcJCAguQhWsQQIECBAgEDzAs4eab4Lb2+ALbVuJ/dAAgQIECBAgAABAgQInBcQkJy3cycBAgQIECDQt0AKSPy81Hc/l2qdLbVKSSqHAAECBAgQIECAAAECNwn4hf8maI8hQIAAAQIEmhJw/khT3fV4ZYUjj3eBChAgQIAAAQIECBAgQOC4gIDkuJk7CBAgQIAAgf4FBCT993GpFv7wceZIXp7zRkrpKocAAQIECBAgQIAAAQIXCghILsRVNAECBAgQINCsQFoREBPd3zbbChW/UiAP0ebhiDFzpbyyCRAgQIAAAQIECBAgUEhAQFIIUjEECBAgQIBAVwICkq66s3hj1sKRP3x+UowdLwIECBAgQIAAAQIECBBoQEBA0kAnqSIBAgQIECBwu0AKSEx4305f/QOXttSKSseqkVhx5EWAAAECBAgQIECAAAECjQgISBrpKNUkQIAAAQIEbhX49PE0Acmt7NU/bO28EVtqVd91KkiAAAECBAgQIECAAIHfCghIjAoCBAgQIECAwJcCDmg3InKBGA/x+n7hMHYBmrFCgAABAgQIECBAgACBhgUEJA13nqoTIECAAAEClwg4f+QS1qYKjVAk/vlmIRRJDRGONNWlKkuAAAECBAgQIECAAIHfCghIjAoCBAgQIECAwJcCttcab0REGBIrROKVVoysKcQ5IxGOOG9kvHGixQQIECBAgAABAgQIdCYgIOmsQzWHAAECBAgQeEsgrR6JQvyc9BZl1Tfn22btCUXimghFYkWJcKTqrlU5AgQIECBAgAABAgQI7Bfwi/9+K1cSIECAAAEC/QtYPdJnHx8NRGJ1SNwTYUi84r+tGOlzbGgVAQIECBAgQIAAAQIDCwhIBu58TSdAgAABAgS+ELB6pK8BsecckXmLIwT5USDS10DQGgIECBAgQIAAAQIECKwJCEiMDQIECBAgQIDArwJWj7Q/EtJZIlvniKSWphUiEY55ESBAgAABAgQIECBAgMBgAgKSwTpccwkQIECAAIFFAatH2hwY+SqRaMGeYMQh6232tVoTIECAAAECBAgQIECguICApDipAgkQIECAAIHGBPJwJFYUWE1QdwceXSWSApFolXNE6u5btSNAgAABAgQIECBA12SawwAABP5JREFUgMCtAgKSW7k9jAABAgQIEKhQIG2tFZPn31ZYv9GrdPQsEeeIjD5itJ8AAQIECBAgQIAAAQI7BQQkO6FcRoAAAQIECHQpkK8eiXDECoM6uvnIKpHUZ7H6R//V0X9qQYAAAQIECBAgQIAAgSYEBCRNdJNKEiBAgAABAhcI2FrrAtSTRaazQ753jshJQbcRIECAAAECBAgQIECAwGEBAclhMjcQIECAAAECnQikrbWcO/JMhx7ZOsu2Wc/0kacSIECAAAECBAgQIECgawEBSdfdq3EECBAgQIDAisAP2UoFW2vdN0zS1lnxxLRqZOnp+bZZ8fe2zrqvjzyJAAECBAgQIECAAAECwwgISIbpag0lQIAAAQIEPgRsrXXvUNh7noizRO7tF08jQIAAAQIECBAgQIDA8AICkuGHAAACBAgQIDCUQEzWx+qReP15mqbfDdX6+xp7JBSJLc7iZZXIff3jSQQIECBAgAABAgQIECAwTZOAxDAgQIAAAQIERhLIt9ZK7Xa+xfsjYO8h61aJvG+tBAIECBAgQIAAAQIECBAoJCAgKQSpGAIECBAgQKAJgdhe65uN8y/mwUn8d0zsW+HwZRcfOU/kR4ZNvD9UkgABAgQIECBAgAABAkMJCEiG6m6NJUCAAAECBGYCMckf/+wNTebbQY0WmhwJRWyd5e1GgAABAgQIECBAgAABAlULCEiq7h6VI0CAAAECBB4QSKFJPHpPcJK26Irre1xpcjQUGS00emCIeiQBAgQIECBAgAABAgQIlBAQkJRQVAYBAgQIECDQu8DZ0KTVwGTPIevOE+l91GsfAQIECBAgQIAAAQIEOhcQkHTewZpHgAABAgQIXCZwNDTJt5yqcZXF3lDE1lmXDSkFEyBAgAABAgQIECBAgMCdAgKSO7U9iwABAgQIEOhd4MiZJk9vzRV1jdf3G4fWRz2FIr2PXO0jQIAAAQIECBAgQIDAgAICkgE7XZMJECBAgACB2wSOrjLJQ5P/dUEtnSdyAaoiCRAgQIAAAQIECBAgQKBNAQFJm/2m1gQIECBAgEC7AnloEqs3tl5nV5qkFSLx59Zh884T2eoFf0+AAAECBAgQIECAAAEC3QkISLrrUg0iQIAAAQIEGhQ4sjVX3rz5WSYpFNlDYOusPUquIUCAAAECBAgQIECAAIFuBQQk3XathhEgQIAAAQINCxzdmmtPU9NKlPizxkPi97TBNQQIECBAgAABAgQIECBAoJiAgKQYpYIIECBAgAABApcLzIOTVw/8MQtCBCKXd40HECBAgAABAgQIECBAgEBrAgKS1npMfQkQIECAAAECBAgQIECAAAECBAgQIECAAIG3BQQkbxMqgAABAgQIECBAgAABAgQIECBAgAABAgQIEGhNQEDSWo+pLwECBAgQIECAAAECBAgQIECAAAECBAgQIPC2gIDkbUIFECBAgAABAgQIECBAgAABAgQIECBAgAABAq0JCEha6zH1JUCAAAECBAgQIECAAAECBAgQIECAAAECBN4WEJC8TagAAgQIECBAgAABAgQIECBAgAABAgQIECBAoDUBAUlrPaa+BAgQIECAAAECBAgQIECAAAECBAgQIECAwNsCApK3CRVAgAABAgQIECBAgAABAgQIECBAgAABAgQItCYgIGmtx9SXAAECBAgQIECAAAECBAgQIECAAAECBAgQeFvg/wdhIuFjxIhGDgAAAABJRU5ErkJggg==	t
149	2025-04-06 15:39:04.144445	2025-04-06 18:00:00	\N	\N	t	\N	 [Cerrado automáticamente durante ventana de cierre 16:00:00 - 20:00:00]	2025-04-06 15:39:04.374212	2025-04-06 15:40:56.081938	47	8	\N	f
150	2025-04-06 15:41:45.877445	2025-04-06 18:00:00	\N	\N	t	\N	 [Cerrado automáticamente durante ventana de cierre 16:00:00 - 20:00:00]	2025-04-06 15:41:46.115533	2025-04-06 15:42:56.999148	47	8	\N	f
151	2025-04-06 16:12:14.62796	2025-04-06 18:00:00	\N	\N	t	\N	 [Cerrado automáticamente durante ventana de cierre 16:00:00 - 20:00:00]	2025-04-06 16:12:14.859122	2025-04-06 16:21:52.438645	47	8	\N	f
152	2025-04-06 21:14:35.945536	2025-04-06 21:15:17.364697	\N	\N	t	\N	 [R] Hora entrada ajustada de 21:14 a 23:14	2025-04-06 21:14:36.177517	2025-04-06 21:16:00.673546	47	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkgAAAGQCAYAAADlQuzyAAAAAXNSR0IArs4c6QAAIABJREFUeF7t3duVHbeVBmA4A2VgOwM7ArojmDWP8yQ5AzkCihHIIUgRTAhNZuDJQH6bt3EGnN7yKalUPJeqOnUBsL9ai6tpdl2Ab6Pl7vobwO+KgwABAgQIECBAgAABAgQIECBAgAABAgQIECCQTOB3yfqruwQIECBAgAABAgQIECBAgAABAgQIECBAgACBIiAxCAgQIECAAAECBAgQIECAAAECBAgQIECAAIF0AgKSdCXXYQIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgwQIECAAAECBAgQIECAAAECBAgQIECAAAEC6QQEJOlKrsMECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQYIECAAAECBAgQIECAAAECBAgQIECAAAECBNIJCEjSlVyHCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJMUCAAAECBAgQIECAAAECBAgQIECAAAECBAikExCQpCu5DhMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmOAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIElXch0mQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCTGAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBOQECSruQ6TIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIjAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgnYCAJF3JdZgAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkBgDBAgQIECAAAECBAgQIECAAAECBAgQIECAQDoBAUm6kuswAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxBggQIECAAAECBAgQIECAAAECBAgQIECAAIF0AgKSdCXXYQIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgwQIECAAAECBAgQIECAAAECBAgQIECAAAEC6QQEJOlKrsMECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQYIECAAAECBAgQIECAAAECBAgQIECAAAECBNIJCEjSlVyHCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJMUCAAAECBAgQIECAAAECBAgQIECAAAECBAikExCQpCu5DhMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmOAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIElXch0mQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCTGAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBOQECSruQ6TIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIjAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgnYCAJF3JdZgAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkBgDBAgQIECAAAECBAgQIECAAAECBAgQIECAQDoBAUm6kuswAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxBggQIECAAAECBAgQIECAAAECBAgQIECAAIF0AgKSdCXXYQIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgwQIECAAAECBAgQIECAAAECBAgQIECAAAEC6QQEJOlKrsMECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQYIECAAAECBAgQIECAAAECBAgQIECAAAECBNIJCEjSlVyHCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJMUCAAAECBAgQIECAAAECBAgQIECAAAECBAikExCQpCu5DhMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmOAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIElXch0mQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCTGAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBOQECSruQ6TIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIjAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgnYCAJF3JdZgAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkBgDBAgQIECAAAECBAgQIECAAAECBAgQIECAQDoBAUm6kuswAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxBggQIECAAAECBAgQIECAAAECBAgQIECAAIF0AgKSdCXXYQIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgwQIECAAAECBAgQIECAAAECBAgQIECAAAEC6QQEJOlKrsMECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQYIECAAAECBAgQIECAAAECBAgQIECAAAECBNIJCEjSlVyHCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJMUCAAAECBAgQIECAAAECBAgQIECAAAECBAikExCQpCu5DhMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmOAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIElXch0mQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCTGAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBOQECSruQ6TIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIjAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgnYCAJF3JdZgAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkBgDBAgQIECAAAECBAgQIECAAAECBAgQIECAQDoBAUm6kuswAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxBggQIECAAAECBAgQIECAAAECBAgQIECAAIF0AgKSdCXXYQIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgwQIECAAAECBAgQIECAAAECBAgQIECAAAEC6QQEJOlKrsMECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQYIECAAAECBAgQIECAAAECBAgQIECAAAECBNIJCEjSlVyHCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJMUCAAAECBAgQIECAAAECBAgQIECAAAECBAikExCQpCu5DhMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmOAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIElXch0mQIAAAQIECBAg0JTAX0op7y8tjr/H8bGU8unyMf7uIECAAAECBAgQIECAwGIBAcliMhcQIECAAAECBAgQILCjQIQg8efd5eOcR314O+m7OSc6hwABAgQIECBAgAABAoOAgMRYIECAAAECBAgQIEDgbIFhlsgwQ2RNe14uM0rWXOsaAgQIECBAgAABAgQSCghIEhZdlwkQIECAAAECBAhUIrBFMDJ0xSySSoqqGQQIECBAgAABAgRaERCQtFIp7SRAgAABAgQIECDQj8CwjNawt8gWPROQbKHoHgQIECBAgAABAgQSCQhIEhVbVwkQIECAAAECBAhUIBB7hWwZjAxd8rNNBcXVBAIECBAgQIAAAQItCfghoqVqaSsBAgQIECBAgACBdgW2XE5rrPBTKeWP7bJoOQECBAgQIECAAAECZwkISM6S91wCBAgQIECAAAECOQT2CkY+llJiWa346CBAgAABAgQIECBAgMBiAQHJYjIXECBAgAABAgQIECAwU2Cv5bTsNzKzAE4jQIAAAQIECBAgQOC2gIDE6CBAgAABAgQIECBAYGuBmDXyuvVNL/cTjuwE67YECBAgQIAAAQIEsgkISLJVXH8JECBAgAABAgQI7Cew13Ja0WJLau1XN3cmQIAAAQIECBAgkFJAQJKy7DpNgAABAgQIECBAYHOBvZbTEoxsXio3JECAAAECBAgQIEAgBAQkxgEBAgQIECBAgAABAs8I7Lmc1otN2J8pjWsJECBAgAABAgQIELgnICAxPggQIECAAAECBAgQWCOw53Ja9hlZUxHXECBAgAABAgQIECCwSEBAsojLyQQIECBAgAABAgQIvAnstZyWYMTwIkCAAAECBAgQIEDgMAEByWHUHkSAAAECBAgQIECgeYG9Zo3YZ6T5oaEDBAgQIECAAAECBNoTEJC0VzMtJkCAAAECBAgQIHCGwF6zRuwzckY1PZMAAQIECBAgQIAAAZu0GwMECBAgQIAAAQIECNwV2GvWiOW0DDwCBAgQIECAAAECBE4VMIPkVH4PJ0CAAAECBAgQIFC1QIQjrxu30HJaG4O6HQECBAgQIECAAAEC6wQEJOvcXEWAAAECBAgQIECgd4E9ltQya6T3UaN/BAgQIECAAAECBBoSEJA0VCxNJUCAAAECBAgQIHCAwB5Lapk1ckDhPIIAAQIECBAgQIAAgWUCApJlXs4mQIAAAQIECBAg0LPA1ktqCUZ6Hi36RoAAAQIECBAgQKBxAQFJ4wXUfAIECBAgQIAAAQIbCWy9pJbltDYqjNsQIECAAAECBAgQILCPgIBkH1d3JUCAAAECBAgQINCSwJbhiFkjLVVeWwkQIECAAAECBAgkFhCQJC6+rhMgQIAAAQIECBAopbyWUmJprS0Os0a2UHQPAgQIECBAgAABAgQOERCQHMLsIQQIECBAgAABAgSqE9hyM/aYNfJSXQ81iAABAgQIECBAgAABAncEBCSGBwECBAgQIECAAIF8Alttxm45rXxjR48JECBAgAABAgQIdCMgIOmmlDpCgAABAgQIECBAYJbAVuGI5bRmcTuJAAECBAgQIECAAIFaBQQktVZGuwgQIECAAAECBAhsL7DFZuxmjWxfF3ckQIAAAQIECBAgQOAEAQHJCegeSYAAAQIECBAgQOAEgWfDEcHICUXzSAIECBAgQIAAAQIE9hMQkOxn684ECBAgQIAAAQIEahF4Nhz5sZTyTS2d0Q4CBAgQIECAAAECBAhsISAg2ULRPQgQIECAAAECBAjUK/BMOGLWSL111TICBAgQIECAAAECBJ4UEJA8CehyAgQIECBAgAABAhULvJZSYlP2NcfL27URkDgIECBAgAABAgQIECDQpYCApMuy6hQBAgQIECBAgACBsjYciVAkwhEHAQIECBAgQIAAAQIEuhYQkHRdXp0jQIAAAQIECBBIKBAzRiIcWXpYTmupmPMJECBAgAABAgQIEGhaQEDSdPk0ngABAgQIECBAgMBvBNaGIx/e7hJ7lTgIECBAgAABAgQIECCQRkBAkqbUOkqAAAECBAgQINC5wJpwxKyRzgeF7hEgQIAAAQIECBAgcFtAQGJ0ECBAgAABAgQIEGhfIGZ/vF/YDbNGFoI5nQABAgQIECBAgACBvgQEJH3VU28IECBAgAABAgTyCSwNR8wayTdG9JgAAQIECBAgQIAAgSsCAhLDggABAgQIECBAgEC7AkvDkZdSSgQkDgIECBAgQIAAAQIECKQXEJCkHwIACBAgQIAAAQIEGhVYEo5YTqvRIms2AQIECBAgQIAAAQL7CQhI9rN1ZwIECBAgQIAAAQJ7CfxQSvl6xs0tpzUDySkECBAgQIAAAQIECOQUEJDkrLteEyBAgAABAgQItCvwUynl9zOab9bIDCSnECBAgAABAgQIECCQV0BAkrf2ek6AAAECBAgQINCWwLellO9nNNmskRlITiFAgAABAgQIECBAgICAxBggQIAAAQIECBAgULfAXy7ByJ9mNNOskRlITiFAgAABAgQIECBAgEAICEiMAwIECBAgQIAAAQL1CthrpN7aaBkBAgQIECBAgAABAo0LCEgaL6DmEyBAgAABAgQIdCkQs0bel1Li473Dclpdll+nCBAgQIAAAQIECBA4QkBAcoSyZxAgQIAAAQIECBCYJzA3GIm7WU5rnqmzCBAgQIAAAQIECBAgcFVAQGJgECBAgAABAgQIEKhD4LvLrJFHrTFr5JGQzxMgQIAAAQIECBAgQGCGgIBkBpJTCBAgQIAAAQIECOwoMDcYiSaYNbJjIdyaAAECBAgQIECAAIFcAgKSXPXWWwIECBAgQIAAgXoEliyn9Y9Syo+llL/X03wtIUCAAAECBAgQIECAQNsCApK266f1BAgQIECAAAEC7QksCUaid7Gk1kt73dRiAgQIECBAgAABAgQI1C0gIKm7PlpHgAABAgQIECDQj8DSYEQ40k/t9YQAAQIECBAgQIAAgQoFBCQVFkWTCBAgQIAAAQIEdhWIoCL+xN4fRx1L9hkZ2mS/kaOq4zkECBAgQIAAAQIECKQUEJCkLLtOEyBAgAABAgTSCnye9HzvEGJNMBJN3LtdaQeAjhMgQIAAAQIECBAgQGAQEJAYCwQIECBAgAABAlkEboUVEUbEPh/xZ6tjzXJaw7Njv5Et27JVn9yHAAECBAgQIECAAAECXQkISLoqp84QIECAAAECBAjcEXg0m2OLWRvPBCP/KKX8TThiDBMgQIAAAQIECBAgQOAYAQHJMc6eQoAAAQIECBAgUIfAdImta61aG5Q8CmDuCUQ48uc6iLSCAAECBAgQIECAAAECOQQEJDnqrJcECBAgQIAAAQK/CswNMuYGJc/MGolWzX2OGhIgQIAAAQIECBAgQIDAhgICkg0x3YoAAQIECBAgQKApgSVBSXQszp8ec+9xDeZfpZT/tKRWU2NGYwkQIECAAAECBAgQ6EhAQNJRMXWFAAECBAgQIEBglUCEHO/egoqYCXLviJkeccT5z84a+amU8sdVrXURAQIECBAgQIAAAQIECGwiICDZhNFNCBAgQIAAAQIEOhAYZoi837kvP5ZSvtn5GW5PgAABAgQIECBAgAABAg8EBCSGCAECBAgQIECAAIHfCsTskGGGyNY2L5bU2prU/QgQIECAAAECBAgQILBOQECyzs1VBAgQIECAAAECOQTmLr81R0M4MkfJOQQIECBAgAABAgQIEDhIQEByELTHECBAgAABAgQINCkQM0m+L6X86YnWfyylxP4l8dFBgAABAgQIECBAgAABApUICEgqKYRmECBAgAABAgQIVCfwQynl6ydb9b+llP8Sjjyp6HICBAgQIECAAAECBAjsICAg2QHVLQkQIECAAAECBJoWGPYfiY9bHTGDZNgEfqt7ug8BAgQIECBAgAABAgQIPCEgIHkCz6UECBAgQIAAAQLdCUSI8X7HXkVQEoewZEdktyZAgAABAgQIECBAgMAcAQHJHCXnECBAgAABAgQIZBB4fVsKa4tZI59KKe9mgJlVMgPJKQQIECBAgAABAgQIENhLQECyl6z7EiBAgAABAgQItCIQoUiEI1sc49BjmCXyaEaKWSVbyLsHAQIECBAgQIAAAQIEFgoISBaCOZ0AAQIECBAgQKArgS2X1Lo3I2RJWPLRpu5djTGdIUCAAAECBAgQIECgUgEBSaWF0SwCBAgQIECAAIFdBbbeiP1lQagxN5SJwEVYsuswcHMCBAgQIECAAAECBDILCEgyV1/fCRAgQIAAAQI5BeYGFHN1loQj43tGSDMENY+eZRmuR0I+T4AAAQIECBAgQIAAgYUCApKFYE4nQIAAAQIECBBoVuCZWSPXNl6P2R3DLI9nUZaEJfHcaI/ZJc+qu54AAQIECBAgQIAAgdQCApLU5dd5AgQIECBAgEAagTWzRoYg4t1lpscYa8twZFqEISy59txrBRtml8Tnhr1O0hRWRwkQIECAAAECBAgQILBWQECyVs51BAgQIECAAAECLQismTUyDj9eb4QjsazWUcfcDd6H9phhclRlPIcAAQIECBAgQIAAgaYFBCRNl0/jCRAgQIAAAQIEbgg8G4zEbWsIR651b2lgMswwsSSXLxcCBAgQIECAAAECBAiMBAQkhgMBAgQIECBAgEBvAkuX05oul3UrXImgocYlrJYGJlFvm773Nur1hwABAgQIECBAgACBxQICksVkLiBAgAABAgQIEKhU4NlgJLrVWjhyrRTPBCZmmVQ6uDWLAAECBAgQIECAAIHtBQQk25u6IwECBAgQIECAwLECEWrEclhzj1sbrPcQjtwKTP5QSvl6LtBbUDTsYxKX1DhrZkFXnEqAAAECBAgQIECAAIHrAgISI4MAAQIECBAgQKBVgTX7jMTm6vHyf3r0Go5cq230Nf7E8X5B8YUmC7CcSoAAAQIECBAgQIBA/QICkvprpIUECBAgQIAAAQK/FVgTjNzbP+TWDJRa9xzZYzysDU1sAL9HNdyTAAECBAgQIECAAIFDBAQkhzB7CAECBAgQIECAwAYC315mPHy14F4x6yFmjdw6hCO3bYaltd6NZpzMoR9CkzjX8lxzxJxDgAABAgQIECBAgMApAgKSU9g9lAABAgQIECBAYIXA5wXX3NpnZHyLW+HIrWW4Fjy+21PXhibj5blsBN/t8NAxAgQIECBAgAABAm0JCEjaqpfWEiBAgAABAgSyCsRL9ZjJ8OiYE4zEPYQjjyTnfX68NNfSmSbxBMHJPGdnESBAgAABAgQIECCwg4CAZAdUtyRAgAABAgQIENhcIJbX+v7OXecGI7fCkSXXb965zm74bGgyBCfx8dPFxqyTzgaJ7hAgQIAAAQIECBCoQUBAUkMVtIEAAQIECBAgQGCOwP+VUqb7jywNNq7NHFl6jzltdc6XAlsEJ0N4MgQnw/+OGjoIECBAgAABAgQIECCwSEBAsojLyQQIECBAgAABAicLDEtt/auUEpuB/31Be+IF/fvJhuPCkQWAO50adYkjPg7LqA3/tuaRQ1hi9skaPdcQIECAAAECBAgQSCQgIElUbF0lQIAAAQIECCQXuLbJuw3Z6x4U41knQ0vX7HUyXCs8qbveWkeAAAECBAgQIEDgUAEByaHcHkaAAAECBAgQIHCSwLVwxPfCJxVjw8dOA5RnwhMhyoaFcSsCBAgQIECAAAECLQj4obCFKmkjAQIECBAgQIDAMwLTcCRmEcTMEUf/AnsEKLG02zRMsQdK/2NJDwkQIECAAAECBDoUEJB0WFRdIkCAAAECBAgQ+EXg9cqeI8IRAyQEppvGD//2jI4lvJ7Rcy0BAgQIECBAgACBgwUEJAeDexwBAgQIECBAgMBhAtfCkfjtf7/tf1gJmn7Qd6PWb7F5/HC7GH/DBvLxb8N4NC6bHi4aT4AAAQIECBAg0KKAgKTFqmkzAQIECBAgQIDAI4F4uf1+cpLvfR+p+fwcgZh5EsfwcevwJO4rRJlTCecQIECAAAECBAgQeFLAD4lPArqcAAECBAgQIECgOgHLalVXklQNuhagDP+2NcR0Sa+4/3gmilkpW4u7HwECBAgQIECAQFcCApKuyqkzBAgQIECAAIH0AtOZI/GC2LJa6YdFNQDjoGT895iFsleIMnT+WpgiUKlmaGgIAQIECBAgQIDAGQICkjPUPZMAAQIECBAgQGAPgWvLasWG7H6Lfg9t99xL4F6IEs88MkgZlg8b9kwZ75cyLAW2l4P7EiBAgAABAgQIENhdQECyO7EHECBAgAABAgQIHCBwbeZIhCMOAr0K3ApSor9b7osy128IT6bByXhD+mv3uhZgCjXnqjuPAAECBAgQIEDgKQEByVN8LiZAgAABAgQIEKhAwMyRCoqgCdULPJqZEh3Ye3bKWqRpYDINXYQsa2VdR4AAAQIECBBILiAgST4AdJ8AAQIECBAg0LjAtXDE97iNF1XzqxGIwGQITSKEGP4eM1S+KqX8Tynl9xUHK9cgH4UtwzW3ZrHUNLtlTqA155zo81Dfe/2rqe/VfJFoCAECBAgQINC2gB8e266f1hMgQIAAAQIEMgvEi7/XCYA9RzKPCH2vQWB4IX/rxfwZy38d5fIoQBhmvoTBdBbMH0opP42WRxu3eW7IcVQ/5wRPcc7c5dUeuZ3ZL88mQIAAAQIEOhcQkHReYN0jQIAAAQIECHQqIBzptLC6lU5g+vJ//L+HMCVQWggJ0hVv4w6Pg5JxuDL8uyBlY3C3I0CAAAECBEoRkBgFBAgQIECAAAECrQkIR1qrmPYS2Fbg1iwVgcq2zjXfLcKSIUSJvwtPaq6WthEgQIAAgYoFBCQVF0fTCBAgQIAAAQIEvhC4Fo58eDsr9iJxECBAYCpwb4bKcO44WIl/M1ul3XEUy5T98xKY+P+Fduuo5QQIECBA4DABAclh1B5EgAABAgQIECCwgUDsOTJ+eWnPkQ1Q3YIAgVkCj4KTR58f7z0yDWViD5L449hOQHi+naU7ESBAgACBbgUEJN2WVscIECBAgAABAt0JCEe6K6kOESBwQ+DRMmKPwhiw/xYQkhgJBAgQIECAwF0BAYkBQoAAAQIECBAg0IJALJXyftRQL71aqJo2EiBwhMC1MGWYoSJIsffqEWPQMwgQIECAQLMCApJmS6fhBAgQIECAAIE0AsKRNKXWUQIEdhS4F6TEY3sNU7z32HFQuTUBAgQIEGhdwDcKrVdQ+wkQIECAAAECfQsIR/qur94RIFCvwJwN7v/jsnfKV/V2o3jvUXFxNI0AAQIECJwt4BuFsyvg+QQIECBAgAABArcE4uVc7DsyHJbVMlYIECBQh0D89zmWPVw66+TjZV+Q+HhrRkuELbFh/Rahi//fqGO8aAUBAgQIEKhWQEBSbWk0jAABAgQIECCQWkA4krr8Ok+AQKUCS4ORCELiiKBi+PvcrsUMwjhiP5VPpZSYrfKnuRfboH2BlFMJECBAgEBiAQFJ4uLrOgECBAgQIECgUgHhSKWF0SwCBFILTJc8vIXxTCiyFHiYhfLNZdbJT5cb/LAikFn6bOcTIECAAAECHQgISDoooi4QIECAAAECBDoTiGW1hpdelkfprLi6Q4BAcwLfXmZvPFpOa7x8VnOd1GACBAgQIEAgp4CAJGfd9ZoAAQIECBAgUKvAOByJl20vtTZUuwgQINC5wNzltATZnQ8E3SNAgAABAj0LCEh6rq6+ESBAgAABAgTaEhCOtFUvrSVAoE8BwUifddUrAgQIECBA4IqAgMTDhJnCAAAgAElEQVSwIECAAAECBAgQqEFgvLa9mSM1VEQbCBDIJjA3GLGUVraRob8ECBAgQKBjAQFJx8XVNQIECBAgQIBAIwLCkUYKpZkECHQpEP8Nfjfa++lWJ2MD9B/fPhnnOwgQIECAAAECXQgISLooo04QIECAAAECBJoVEI40WzoNJ0CgYYGYLTLMGHnUDTNGHgn5PAECBAgQINCsgICk2dJpOAECBAgQIECgeYFpOBIb/caLOAcBAgQI7Ccw/m/vvacIRvargTsTIECAAAEClQgISCophGYQIECAAAECBJIJTF/QvQhHko0A3SVA4EiBJfuLfHprmGW0jqyOZxEgQIAAAQKnCQhITqP3YAIECBAgQIBAWoF4Ufc66r1wJO1Q0HECBHYWWBKMmMW3czHcngABAgQIEKhPQEBSX020iAABAgQIECDQs8D0ZZ1wpOdq6xsBAmcJzAlGhiUNBSNnVclzCRAgQIAAgdMFBCSnl0ADCBAgQIAAAQJpBOKFXSzb8u7SY+FImtLrKAECBwjMCUWiGfYWOaAYHkGAAAECBAi0ISAgaaNOWkmAAAECBAgQ6EFg2Hfkp1LKX+050kNJ9YEAgQoE5gYjw0yRYeZIBU3XBAIECBAgQIDAuQICknP9PZ0AAQIECBAgkEVgvCl7vKSzAXCWyusnAQJ7CcwJRswW2UvffQkQIECAAIEuBAQkXZRRJwgQIECAAAECVQsIR6ouj8YRINCYwPi/qbeaLhhprKiaS4AAAQIECJwjICA5x91TCRAgQIAAAQJZBIQjWSqtnwQI7CkwZ7ZIPN8MvT2r4N4ECBAgQIBAdwICku5KqkMECBAgQIAAgWoEhCPVlEJDCBBoVGBOMGK2SKPF1WwCBAgQIEDgfAEByfk10AICBAgQIECAQI8CwpEeq6pPBAgcJTAnGPmplPLXUopN14+qiucQIECAAAEC3QkISLorqQ4RIECAAAECBE4XEI6cXgINIECgUYE5wYgZI40WV7MJECBAgACB+gQEJPXVRIsIECBAgAABAi0LxMu910sH4iXeS8ud0XYCBAgcIDAnFIlmCEYOKIZHECBAgAABArkEBCS56q23BAgQIECAAIE9BcbhSDzH95p7ars3AQKtC8wNRmy83nqltZ8AAQIECBCoVsAPrdWWRsMIECBAgAABAk0JCEeaKpfGEiBwksAQisTj4++3DrNFTiqQxxIgQIAAAQK5BAQkueqttwQIECBAgACBPQSm4Yjfdt5D2T0JEGhZYO5sEcFIy1XWdgIECBAgQKA5AQFJcyXTYAIECBAgQIBAdQKx58jwm9DCkerKo0EECJwkMDcUieYJRk4qkscSIECAAAECuQUEJLnrr/cECBAgQIAAgWcFhCPPCrqeAIGeBCIUiT/vHiyhNYQiny7hSAQkDgIECBAgQIAAgYMFBCQHg3scAQIECBAgQKAjge9KKe8v/TFzpKPC6goBAosFls4WiWAk/hvqIECAAAECBAgQOFFAQHIivkcTIECAAAECBBoWEI40XDxNJ0BgE4EloUg80DJam7C7CQECBAgQIEBgOwEByXaW7kSAAAECBAgQyCIgHMlSaf0kQGAqIBQxJggQIECAAAECHQkISDoqpq4QIECAAAECBA4QEI4cgOwRBAhUJxD7LcURAcmcw2yROUrOIUCAAAECBAicLCAgObkAHk+AAAECBAgQaEhgHI7Ey7+XhtquqQQIEFgqYLbIUjHnEyBAgAABAgQaExCQNFYwzSVAgAABAgQInCQgHDkJ3mMJEDhUQChyKLeHESBAgAABAgTOFRCQnOvv6QQIECBAgACBFgTiheGwvEy0N2aOxAwSBwECBHoRWBKMDMtnRd/9t7CXEaAfBAgQIECAQEoBAUnKsus0AQIECBAgQGCRwOfR2b5/XETnZAK7CcQL/WE/jJjh5VgusCQUGcKQD0KR5dCuIECAAAECBAjUKuAH3Foro10ECBAgQIAAgfMFzBw5vwZaQGAqEF+X/11K+Wr0iXhpLySZN1aEIvOcnEWAAAECBAgQSCEgIElRZp0kQIAAAQIECKwSiGW1ht9Q9wJ2FaGLCGwqMA0txzf3s9196iXBSCyb9ekyU8QSWpsOYTcjQIAAAQIECNQl4JvouuqhNQQIECBAgACBWgTGm7ILR2qpinZkFhh/TV5z8LPdlypLQpG4ethbRCiS+StN3wkQIECAAIFUAr6JTlVunSVAgAABAgQIzBIwc2QWk5MIHCIw5yW/EPPXUszxGhfup1LKX+0rcshY9hACBAgQIECAQHUCApLqSqJBBAgQIECAAIFTBcwcOZXfwwn8IjD3RX+84P9jcre5VmMms0WSDxrdJ0CAAAECBAiEgIDEOCBAgAABAgQIEBgExuFIvDx8QUOAwCkCj5bTGjcq6890a0KRcBOMnDKkPZQAAQIECBAgUKdA1m+m66yGVhEgQIAAAQIEzhMwc+Q8e08mMBZYEo7EdRFkZtgzIwKR+PPu8nHpqBGMLBVzPgECBAgQIEAggYCAJEGRdZEAAQIECBAg8EDAzBFDhEAdAuP9f+a2qNfZXhGGxPF+ZSAy+AlG5o4k5xEgQIAAAQIEEgoISBIWXZcJECBAgAABAiOBeAkZL2Xj6PVFq4ITaEHgVjgSX5f/LKV8faMTPWzQPoQhz8wQmfKES9hlmF3TwvjWRgIECBAgQIBAlQICkirLolEECBAgQIAAgUMEpmv4Z1mq5xBcDyGwQOBWODKEH5/v3Ku1gGSPMGTgiTDk09v/iFlxDgIECBAgQIAAAQIPBQQkD4mcQIAAAQIECBDoVmD8UlY40m2ZdaxygVvhxxB8/HBn9kh0reav3fG+IdHWIRzZuiSW0dpa1P0IECBAgAABAkkEBCRJCq2bBAgQIECAAIGJwDgcae030BWTQA8C0xlc4z4Nocd4Cbx7fT77a3g6K2TPMGTsIBjp4StBHwgQIECAAAECJwoISE7E92gCBAgQIECAwEkC403Zz36xehKBxxI4VWD8NThtyHhGyL3zrnXgqK/n8cyQvWaF3CqQUOTUoevhBAgQIECAAIG+BAQkfdVTbwgQIECAAAECjwSEI4+EfJ7AvgK3Qo9rL/7nziCZtnjLoGQIQN5fHnJ0IBKPFYrsOybdnQABAgQIECCQVkBAkrb0Ok6AAAECBAgkFBCOJCy6LlcjcG9JrX+UUv58o6X3Nmh/1Llh0/JH572bnPDPUkr82x8eXbjT56PdcUTQM/x9p0e5LQECBAgQIECAQGYBAUnm6us7AQIECBAgkElgHI7EC8dYxsdBgMAxAvfCkR9LKd/cacbaWSTH9Gybp4wDkbijUGQbV3chQIAAAQIECBB4ICAgMUQIECBAgAABAv0LTF+w+h6w/5rrYT0CS5bUutfqpfuR1CPwZUuGmS3xURhSc6W0jQABAgQIECDQuYAfjjsvsO4RIECAAAECBN6Wynl9ewk57Bsw3gAaDgEC+wncmzXyzB4hLQUlQ/jxaRSECET2G3PuTIAAAQIECBAgsFBAQLIQzOkECBAgQIAAgcYExuHIMy9lG+u25hI4VeBeiLFVSFlbUDINQwQhpw5BDydAgAABAgQIEJgjICCZo+QcAgQIECBAgECbAjZlb7NuWt22wK3gYq+A8qygxDJZbY9TrSdAgAABAgQIECilCEgMAwIECBAgQIBAnwLCkT7rqlf1CtxaUmsIEuJrcs9jz6DEJup7Vs69CRAgQIAAAQIEThMQkJxG78EECBAgQIAAgd0Exi9K48VmLOnjIEBgP4F7s0aO3og8gpr4826099C459eWvoo9QqbnfFNK+cEm6vsNGncmQIAAAQIECBA4X0BAcn4NtIAAAQIECBAgsKVAvBiNfUfiEI5sKeteBL4UuLcR+1Z7jXAnQIAAAQIECBAgQGAnAQHJTrBuS4AAAQIECBA4SeDz6Lle0J5UBI9NIXBr1ohgMkX5dZIAAQIECBAgQKAHAQFJD1XUBwIECBAgQIDAvwXsO2IkENhfwKyR/Y09gQABAgQIECBAgMAhAgKSQ5g9hAABAgQIECCwu4BwZHdiDyDwmxByzGHWiMFBgAABAgQIECBAoEEBAUmDRdNkAgQIECBAgMBEQDhiSBDYV+DWrJEIRj7YyHxffHcnQIAAAQIECBAgsJeAgGQvWfclQIAAAQIECBwjYFP2Y5w9Ja/Arb1GIhiJzzkIECBAgAABAgQIEGhUQEDSaOE0mwABAgQIECBwERhvyu57O8OCwLYCr2+zQyKEHB9mjWxr7G4ECBAgQIAAAQIEThPwQ/Rp9B5MgAABAgQIEHhaYPzy1m+zP83pBgR+ETBrxGAgQIAAAQIECBAgkEBAQJKgyLpIgAABAgQIdClg35Euy6pTJwvYa+TkAng8AQIECBAgQIAAgSMFBCRHansWAQIECBAgQGAbgfG+I2aObGPqLgTGX1djDV9jxgYBAgQIECBAgACBTgUEJJ0WVrcIECBAgACBrgWGfUdiL4SXrnuqcwSOEbDXyDHOnkKAAAECBAgQIECgKgEBSVXl0BgCBAgQIECAwEOB8dJaEY5ESOIgQGCdgFkj69xcRYAAAQIECBAgQKALAQFJF2XUCQIECBAgQCCJgH1HkhRaNw8RMGvkEGYPIUCAAAECBAgQIFCvgICk3tpoGQECBAgQIEBgLCAcMR4IbCNg1sg2ju5CgAABAgQIECBAoHkBAUnzJdQBAgQIECBAIIGATdkTFFkXDxEwa+QQZg8hQIAAAQIECBAg0IaAgKSNOmklAQIECBAgkFtg/FLX92+5x4LerxO4Nmsk9u/59Ha7mJ3lIECAAAECBAgQIEAgoYAfsBMWXZcJECBAgACBpgQsrdVUuTS2QoFbs0ZeKmyrJhEgQIAAAQIECBAgcKCAgORAbI8iQIAAAQIECCwUEI4sBHM6gZHArb1GIhiJ2SMOAgQIECBAgAABAgSSCwhIkg8A3SdAgAABAgSqFbDvSLWl0bAGBK7NGvnw1m7LaTVQPE0kQIAAAQIECBAgcJSAgOQoac8hQIAAAQIECCwT+Dw63fdsy+ycnVfg1l4jEY6YNZJ3XOg5AQIECBAgQIAAgasCftg2MAgQIECAAAEC9QlYWqu+mmhR3QIRjLx/C0Hi4/iwnFbdddM6AgQIECBAgAABAqcKCEhO5fdwAgQIECBAgMAXAsIRg4LAMoHx18xwZcwWsQn7MkdnEyBAgAABAgQIEEgnICBJV3IdJkCAAAECBCoWsO9IxcXRtOoErs0aiWDEclrVlUqDCBAgQIAAAQIECNQpICCpsy5aRYAAAQIECOQUGDaW9tvvOeuv1/MEbi2nZRP2eX7OIkCAAAECBAgQIEDgIiAgMRQIECBAgAABAnUIjJcJsm9CHTXRivoELKdVX020iAABAgQIECBAgECzAgKSZkun4QQIECBAgEBHAvYd6aiYurKLgOW0dmF1UwIECBAgQIAAAQK5BQQkueuv9wQIECBAgMD5AvYdOb8GWlCvgGCk3tpoGQECBAgQIECAAIHmBQQkzZdQBwgQIECAAIHGBYZ9R6IbvjdrvJiav5lABCNDODK+qX1GNiN2IwIECBAgQIAAAQIE/BBuDBAgQIAAAQIEzhOw78h59p5cr8CtfUYiHPlYb7O1jAABAgQIECBAgACB1gQEJK1VTHsJECBAgACBXgTsO9JLJfVjKwHLaW0l6T4ECBAgQIAAAQIECMwSEJDMYnISAQIECBAgQGBTAfuObMrpZo0LCEYaL6DmEyBAgAABAgQIEGhVQEDSauW0mwABAgQIEGhZYNh3JJYLemm5I9pO4EmBa8tp2WfkSVSXEyBAgAABAgQIECAwT0BAMs/JWQQIECBAgACBrQTsO7KVpPu0LHBrnxGBYctV1XYCBAgQIECAAAECjQkISBormOYSIECAAAECTQvYd6Tp8mn8BgKW09oA0S0IECBAgAABAgQIENhGQECyjaO7ECBAgAABAgTmCHy+nGQJoTlazulNYFhabuhXLDEXXwvx0UGAAAECBAgQIECAAIHDBQQkh5N7IAECBAgQIJBUYPxy2PdgSQdB0m7/UEr5etL3WEpLMJJ0QOg2AQIECBAgQIAAgVoE/HBeSyW0gwABAgQIEOhZYLy0lu+/eq60vo0FYjmtCAbHh9lTxggBAgQIECBAgAABAtUI+AG9mlJoCAECBAgQINCpwPgl8d9KKX/vtJ+6RWAQuLbPyKe3T0ZQaNaIcUKAAAECBAgQIECAQDUCApJqSqEhBAgQIECAQIcC43DEb853WGBd+o2ADdgNCAIECBAgQIAAAQIEmhIQkDRVLo0lQIAAAQIEGhOwtFZjBdPc1QLjsT7cRCi4mtOFBAgQIECAAAECBAgcISAgOULZMwgQIECAAIGMAuMXxjakzjgCcvT51j4jsZSW5bRyjAG9JECAAAECBAgQINCsgICk2dJpOAECBAgQIFCxwDgc8Vv0FRdK01YL3FpOK8JABwECBAgQIECAAAECBJoQEJA0USaNJECAAAECBBoT+Hxpb/wGvRfGjRVPc+8K2GfEACFAgAABAgQIECBAoBsBAUk3pdQRAgQIECBAoBIB+45UUgjN2Fzg9W3ZrAhIxofl4zZndkMCBAgQIECAAAECBI4SEJAcJe05BAgQIECAQAYBS2tlqHK+Pl7bZ8TsqHzjQI8JECBAgAABAgQIdCcgIOmupDpEgAABAgQInCQwfols35GTiuCxmwpYTmtTTjcjQIAAAQIECBAgQKA2AQFJbRXRHgIECBAgQKBVgWH5Ib9Z32oFtXsQEIwYCwQIECBAgAABAgQIpBAQkKQos04SIECAAAECOwuMl9ayJ8PO2G6/m8CtYOTT2xNjjDsIECBAgAABAgQIECDQlYCApKty6gwBAgQIECBwgoB9R05A98jNBcbjeLi5peI2Z3ZDAgQIECBAgAABAgRqEhCQ1FQNbSFAgAABAgRaE7DvSGsV096pwK1gJJaKiz8OAgQIECBAgAABAgQIdCsgIOm2tDpGgAABAgQIHCAw7DsSj/J91QHgHrGZgH1GNqN0IwIECBAgQIAAAQIEWhXwg3yrldNuAgQIECBA4GwBS2udXQHPXyMgGFmj5hoCBAgQIECAAAECBLoUEJB0WVadIkCAAAECBHYWEI7sDOz2mwsIRjYndUMCBAgQIECAAAECBFoXEJC0XkHtJ0CAAAECBM4Q+Hx5aOzR8HJGAzyTwEyBa8FIXBrj1h4jMxGdRoAAAQIECBAgQIBAnwICkj7rqlcECBAgQIDAfgLj2SNeMu/n7M7PCdwKRj683TbGsIMAAQIECBAgQIAAAQLpBQQk6YcAAAIECBAgQGCBgKW1FmA59RQBwcgp7B5KgAABAgQIECBAgECLAgKSFqumzQQIECBAgMAZAvHi+fXyYL+Ff0YFPPORwDjAG861DNwjNZ8nQIAAAQIECBAgQCCtgIAkbel1nAABAgQIEFgoEOFIhCRx+B5qIZ7TdxW4FYxEkGefkV3p3ZwAAQIECBAgQIAAgZYF/HDfcvW0nQABAgQIEDhKwNJaR0l7zlyBCOuG5bTG10QgIhiZq+g8AgQIECBAgAABAgRSCwhIUpdf5wkQIECAAIEZAsKRGUhOOUxAMHIYtQcRIECAAAECBAgQINC7gICk9wrrHwECBAgQIPCsgKW1nhV0/RYCtzZfN2NkC133IECAAAECBAgQIEAgpYCAJGXZdZoAAQIECBCYKWD2yEwop+0mIBjZjdaNCRAgQIAAAQIECBDILiAgyT4C9J8AAQIECBC4J/D58sn4Lf0XVAQOFBCMHIjtUQQIECBAgAABAgQI5BQQkOSsu14TIECAAAECjwXMHnls5IztBQQj25u6IwECBAgQIECAAAECBK4KCEgMDAIECBAgQIDAlwLCEaPiaAHByNHinkeAAAECBAgQIECAQHoBAUn6IQCAAAECBAgQuCIwLK0Vn/L9kiGyp4BgZE9d9yZAgAABAgQIECBAgMAdAT/wGx4ECBAgQIAAgd8KmD1iRBwhcCsY+fD28BiDDgIECBAgQIAAAQIECBDYWUBAsjOw2xMgQIAAAQJNCcRL69dRi32v1FT5mmisYKSJMmkkAQIECBAgQIAAAQIZBPzQn6HK+kiAAAECBAjMFTB7ZK6U85YK3ApGXkopH5fezPkECBAgQIAAAQIECBAg8LyAgOR5Q3cgQIAAAQIE+hAQjvRRx9p6cS0YiUAkltISjNRWLe0hQIAAAQIECBAgQCCVgIAkVbl1lgABAgQIELgjMN6Y3W/1GyrPCghGnhV0PQECBAgQIECAAAECBHYWEJDsDOz2BAgQIECAQBMCZo80UaYmGikYaaJMGkmAAAECBAgQIECAAIFSBCRGAQECBAgQIECglPHsEd8fGRFrBAQja9RcQ4AAAQIECBAgQIAAgRMFvAA4Ed+jCRAgQIAAgSoEzB6pogzNNkIw0mzpNJwAAQIECBAgQIAAgewCApLsI0D/CRAgQIBAboF4uf06IvC9Ue7xsKT3Eay9e9toPcbQcNh8fYmgcwkQIECAAAECBAgQIHCygJcAJxfA4wkQIECAAIFTBcweOZW/yYdPQ7XoxIe3oCTCkfjjIECAAAECBAgQIECAAIFGBAQkjRRKMwkQIECAAIHNBcbhSNzc90WbE3d1w+l4ic6ZMdJViXWGAAECBAgQIECAAIFsAl4EZKu4/hIgQIAAAQKDQCytNSyPFDMA4gW4g8BUYDxOhs8JRowTAgQIECBAgAABAgQIdCAgIOmgiLpAgAABAgQILBYwe2QxWaoLrm28HgCCkVTDQGcJECBAgAABAgQIEOhdQEDSe4X1jwABAgQIELgm8Hn0j2aPGCODgGDEWCBAgAABAgQIECBAgEAiAQFJomLrKgECBAgQIPCzwA+llK8vFjEj4IVLegHBSPohAIAAAQIECBAgQIAAgYwCApKMVddnAgQIECCQW8Dskdz1H/deMGIsECBAgAABAgQIECBAILGAgCRx8XWdAAECBAgkFBiHI/8opfw5oYEulyIYMQoIECBAgAABAgQIECBAoAhIDAICBAgQIEAgi8B0Y/ZYWiuW2HLkERCM5Km1nhIgQIAAAQIECBAgQOChgIDkIZETCBAgQIAAgU4ELK3VSSFXdGMajg23iIDsg6BshahLCBAgQIAAAQIECBAg0IGAgKSDIuoCAQIECBAg8FDg9e0leMweiMPG7A+5ujgh6j3MGJl2SDDSRYl1ggABAgQIECBAgAABAs8JCEie83M1AQIECBAgUL/AdPZAzBiIf3P0KXBrGa3orWCkz5rrFQECBAgQIECAAAECBFYJCEhWsbmIAAECBAgQaEjA0loNFeuJpgpGnsBzKQECBAgQIECAAAECBDIKCEgyVl2fCRAgQIBAHoHp7BHf+/RXe8FIfzXVIwIECBAgQIAAAQIECBwi4CXBIcweQoAAAQIECJwgYGmtE9APfKRg5EBsjyJAgAABAgQIECBAgECPAgKSHquqTwQIECBAgEAI2Ji9z3EwDb7GvbTHSJ811ysCBAgQIECAAAECBAjsIiAg2YXVTQkQIECAAIGTBaYv0V8uG3Sf3CyPXylwb7ZI3FIwshLWZQQIECBAgAABAgQIEMgsICDJXH19J0CAAAEC/QrYmL2P2gpG+qijXhAgQIAAAQIECBAgQKBKAQFJlWXRKAIECBAgQOAJARuzP4FXyaWCkUoKoRkECBAgQIAAAQIECBDoWUBA0nN19Y0AAQIECOQUMHukzbpHKDIEI7d68OHtExGAOQgQIECAAAECBAgQIECAwNMCApKnCd2AAAECBAgQqEjA7JGKijGzKXNmi3wSjMzUdBoBAgQIECBAgAABAgQIzBYQkMymciIBAgQIECDQgIDZIw0U6dLEOcFIzBiJDdgdBAgQIECAAAECBAgQIEBgcwEByeakbkiAAAECBAicJGD2yEnwCx77KBSJW0UgIhhZgOpUAgQIECBAgAABAgQIEFgnICBZ5+YqAgQIECBAoD6B18seFtEye1XUVR/BSF310BoCBAgQIECAAAECBAgQeHt5ICAxDAgQIECAAIEeBOIFfAQkwyEgOb+qw6br70bB1bVWmTFyfq20gAABAgQIECBAgAABAikFBCQpy67TBAgQIECgOwHLa9VTUrNF6qmFlhAgQIAAAQIECBAgQIDAHQEBieFBgAABAgQI9CBgc/Zzq2i2yLn+nk6AAAECBAgQIECAAAECKwQEJCvQXEKAAAECBAhUJTCdPfJy2ei7qkZ22pg5s0Wi65bR6nQA6BYBAgQIECBAgAABAgRaFhCQtFw9bSdAgAABAgRCwPJax44Docix3p5GgAABAgQIECBAgAABAjsJCEh2gnVbAgQIECBA4DABy2sdQy0YOcbZUwgQIECAAAECBAgQIEDgIAEByUHQHkOAAAECBAjsImB5rV1Yf7mpUGRfX3cnQIAAAQIECBAgQIAAgRMFBCQn4ns0AQIECBAg8LTAePZI3Mz3Nk+T/nwDwcg2ju5CgAABAgQIECBAgAABAhULeIlQcXE0jQABAgQIELgrMJ098uHt7Pg3xzoBocg6N1cRIECAAAECBAgQIECAQKMCApJGC6fZBAgQIECAwBebs7+8zXz4yGWRQIQi8efd5eO9i8M2QijGi4idTIAAAQIECBAgQIAAAQK1CghIaq2MdhEgQIAAAQKPBCyv9Ujo9ufNFllv50oCBAgQIECAAAECBAgQ6ERAQNJJIXWDAAECBAgkE7C81vKCzw1F4s5miyz3dQUBAgQIECBAgAABAgQINCYgIGmsYJpLgAABAgQI/CzwOlkSyvJatwfG3GBEKOKLiwABAgQIECBAgAABAgRSCQhIUpVbZwkQIECAQBcC35ZSvh/1JF7sR0Di+FVgSSjy6TJjxN4iRhABAgQIECBAgAABAgQIpBIQkKQqt84SIECAAGwIl7YAAAd9SURBVIEuBKbLa/1YSvmmi54934klwYgN15/3dgcCBAgQIECAAAECBAgQaFhAQNJw8TSdAAECBAgkFbC81m8LLxRJ+oWg2wQIECBAgAABAgQIECDwnICA5Dk/VxMgQIAAAQLHCtic/d/eQygy/P1eFewtcuwY9TQCBAgQIECAAAECBAgQaERAQNJIoTSTAAECBAgQ+Fkg++wRs0V8IRAgQIAAAQIECBAgQIAAgY0EBCQbQboNAQIECBAgsLvAdPZIPDDD9zJLQhEbru8+DD2AAAECBAgQIECAAAECBHoRyPBSoZda6QcBAgQIEMgukG15rSXBiA3Xs3916D8BAgQIECBAgAABAgQILBYQkCwmcwEBAgQIECBwksDnyXMjFIjQpLdjTjBiX5Heqq4/BAgQIECAAAECBAgQIHC4gIDkcHIPJECAAAECBFYITGePREDwsuI+tV4SoUgcscfKvUMwUmsFtYsAAQIECBAgQIAAAQIEmhMQkDRXMg0mQIAAAQIpBXqdPWK2SMrhrNMECBAgQIAAAQIECBAgUIOAgKSGKmgDAQIECBAg8EhgGpDE7JGYTdHqIRhptXLaTYAAAQIECBAgQIAAAQLdCAhIuimljhAgQIAAgW4Fellea04oEkW0jFa3Q1nHCBAgQIAAAQIECBAgQKAmAQFJTdXQFgIECBAgQOCaQOzLMezREZ9vbXN2wYhxTYAAAQIECBAgQIAAAQIEKhQQkFRYFE0iQIAAAQIEfiPQ6vJaghEDmQABAgQIECBAgAABAgQIVCwgIKm4OJpGgAABAgQI/DxzJGaQjI+av3+ZG4pEfyylZYATIECAAAECBAgQIECAAIETBWp+wXAii0cTIECAAAEClQhMA5IIFWKD9pqOJaGIYKSmymkLAQIECBAgQIAAAQIECKQWEJCkLr/OEyBAgACB6gWuzSCpISRZGooIRqofahpIgAABAgQIECBAgAABAtkEBCTZKq6/BAgQIECgPYHpHiRD2HDkTJIIROLPu8mG8XM0LaU1R8k5BAgQIECAAAECBAgQIEDgYAEBycHgHkeAAAECBAgsFrg2iyRuEgFJhA9rj7jv+Bj+d4QgwzE9Z8mznm3fkmc5lwABAgQIECBAgAABAgQIEFgoICBZCOZ0AgQIECBA4BSB70op7ydPvrXU1jjUGGZ9bBF4zOm42SJzlJxDgAABAgQIECBAgAABAgQqEBCQVFAETSBAgAABAgRmCVxbautvpZSvLktfxU2emfExqxFXThpmsXx4ckbL2ue7jgABAgQIECBAgAABAgQIEFghICBZgeYSAgQIECBA4BSB15MCkGudFYqcMgQ8lAABAgQIECBAgAABAgQIbCcgINnO0p0IECBAgACBfQVu7UWy71N/vfuwfFb8yzN7nxzVXs8hQIAAAQIECBAgQIAAAQIE7ggISAwPAgQIECBAoBWBb0sp3+/Y2HHo8enynPg3YciO6G5NgAABAgQIECBAgAABAgTOEhCQnCXvuQQIECBAgMAagWv7kNy7zxBujAOP8fnCjzVVcA0BAgQIECBAgAABAgQIEOhAQEDSQRF1gQABAgQIJBL4rpTyftLfcQgy/F3wkWhQ6CoBAgQIECBAgAABAgQIEFgjICBZo+YaAgQIECBA4GyB2I8kDkHI2ZXwfAIECBAgQIAAAQIECBAg0KiAgKTRwmk2AQIECBAgQIAAAQIECBAgQIAAAQIECBAgsF5AQLLezpUECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAowICkkYLp9kECBAgQIAAAQIECBAgQIAAAQIECBAgQIDAegEByXo7VxIgQIAAAQIECBAgQIAAAQIECBAgQIAAAQKNCghIGi2cZhMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLrBQQk6+1cSYAAAQIECBAgQIAAAQIECBAgQIAAAQIECDQqICBptHCaTYAAAQIECBAgQIAAAQIECBAgQIAAAQIECKwXEJCst3MlAQIECBAgQIAAAQIECBAgQIAAAQIECBAg0KiAgKTRwmk2AQIECBAgQIAAAQIECBAgQIAAAQIECBAgsF5AQLLezpUECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAowICkkYLp9kECBAgQIAAAQIECBAgQIAAAQIECBAgQIDAegEByXo7VxIgQIAAAQIECBAgQIAAAQIECBAgQIAAAQKNCghIGi2cZhMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLrBQQk6+1cSYAAAQIECBAgQIAAAQIECBAgQIAAAQIECDQqICBptHCaTYAAAQIECBAgQIAAAQIECBAgQIAAAQIECKwXEJCst3MlAQIECBAgQIAAAQIECBAgQIAAAQIECBAg0KiAgKTRwmk2AQIECBAgQIAAAQIECBAgQIAAAQIECBAgsF5AQLLezpUECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAowICkkYLp9kECBAgQIAAAQIECBAgQIAAAQIECBAgQIDAegEByXo7VxIgQIAAAQIECBAgQIAAAQIECBAgQIAAAQKNCvw/9XqT3EgJF+AAAAAASUVORK5CYII=	t
164	2025-04-07 22:01:47.435451	2025-04-07 22:02:06.489905	\N	\N	t	\N	 [R] Hora entrada ajustada de 22:01 a 00:01	2025-04-07 22:01:47.668975	2025-04-07 22:02:32.950455	46	8	data:image/png;base64,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	t
153	2025-04-06 16:00:00	2025-04-06 17:04:00	2025-04-06 21:16:35.690882	\N	t	11	 [R] Hora entrada ajustada de 16:00 a 18:00 [R] Hora salida ajustada de 23:18:38 a 19:04:00	2025-04-06 21:16:35.918809	2025-04-06 21:18:52.160669	47	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkgAAAGQCAYAAADlQuzyAAAAAXNSR0IArs4c6QAAIABJREFUeF7t3c2x5cZ5BuBWBJaXXpmKwFQEFFde0hlwlIEUwVgRKARzMrB23o0mAjED0jsvlQE9LV+4DiE0fruBBr7nVE3x5+IA/T1fn6q5563u/kXyIkCAAAECBAgQIECAAAECBAgQIECAAAECBAgEE/hFsHqVS4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIAhKTgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBAIJyAgCddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQCCcgIAnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEAgnICAJ13IFEyBAgAABAgQIECBAgACBbgV+8zayP3c7QgMjQIAAAQIEHiMgIHlMKxVCgAABAgQIECBAgAABAgRuLfAxpTQEJLmQrz//t6Dk1i01eAIECBAg0LeAgKTv/hgdAQIECBAgQIAAAQIECBB4skAORN6PgpGh3hyO5JDEiwABAgQIECDQREBA0oTVTQkQIECAAAECBAgQIECAAIEZgblgREBi6hAgQIAAAQKnCAhITmH2EAIECBAgQIAAAQIECBAgQOBtpUhpxcgY6A+f/8e/UyNAgAABAgQItBIQkLSSdV8CBAgQIECAAAECBAgQIEBgEFizYuRV60NK6R0+AgQIECBAgEBLAQFJS133JkCAAAECBAgQIECAAAECsQXyCpC8YmTLy8qRLVquJUCAAAECBHYLCEh203kjAQIECBAgQIAAAQIECBAgMCGwdbXI6y2EI6YUAQIECBAgcJqAgOQ0ag8iQIAAAQIECBAgQIAAAQKPFtgSjPyYUvpipCEcefT0UBwBAgQIEOhPQEDSX0+MiAABAgQIECBAgAABAgQI3ElgSzDy55TSn1JKf5wo0HcUd+q6sRIgQIAAgQcI+MvHA5qoBAIECBAgQIAAAQIECBAgcIHA1mAkrxDJr48TY7V65IIGeiQBAgQIEIguICCJPgPUT4AAAQIECBAgQIAAAQIEtgusPXw9rxjJ4Uf+Zw5UhCPbrb2DAAECBAgQaCQgIGkE67YECBAgQIAAAQIECBAgQOCBAqWQY1zqEIrkYCS/SoGKlSMPnCRKIkCAAAECdxEQkNylU8ZJgAABAgQIECBAgAABAgSuE1i7ndZU4CEcua5vnkyAAAECBAjMCAhITA8CBAgQIECAAAECBAgQIEBgTmDNdlqllSCl9379tu0WeQIECBAgQIDAZQICksvoPZgAAQIECBAgQIAAAQIECHQtsGbVyOsZI+NipsKRueu7xjA4AgQIECBA4HkCApLn9VRFBAgQIECAAAECBAgQIEDgqMCaVSNzq0CEI0c74P0ECBAgQIBAcwEBSXNiDyBAgAABAgQIECBAgAABArcRWLtqJIcjpdfHz9tn5fu8vvLKkbn33AbIQAkQIECAAIHnCAhIntNLlRAgQIAAAQIECBAgQIAAgSMCS6tG1myPNXWP0vkkR8bqvQQIECBAgACBwwICksOEbkCAAAECBAgQIECAAAECBG4tsGbVyFLI4TD2W08BgydAgAABAjEFBCQx+65qAgQIECBAgAABAgQIECCQBWqsGpkKWPJqk09v9ydNgAABAgQIEOhSQEDSZVsMigABAgQIECBAgAABAgQINBWosWpkLmDxfUPT9rk5AQIECBAgUEPAX1hqKLoHAQIECBAgQIAAAQIECBC4j8DSqpFcST5QPa8CmXuVVo7k7biW3nsfLSMlQIAAAQIEHisgIHlsaxVGgAABAgQIECBAgAABAgR+JrBm1UgONnI4svT6S0rpy9FFS+eULN3TzwkQIECAAAECpwoISE7l9jACBAgQIECAAAECBAgQIHCJwNKqkRyMrF358V1K6dtRFWtWnFxSuIcSIECAAAECBEoCAhJzgwABAgQIECBAgAABAgQIPFeg5qqRrDQVtFg58tz5ozICBAgQIPBoAQHJo9urOAIECBAgQIAAAQIECBAILJDDkY8L9W9Z+TEVjnxIKb0LbKx0AgQIECBA4MYCApIbN8/QCRAgQIAAAQIECBAgQIDAhMCaVSNbV31YOWKqESBAgAABAo8TEJA8rqUKIkCAAAECBAgQIECAAIHAAktnjWSaLatG8vXCkcATSukECBAgQODJAgKSJ3dXbQQIECBAgAABAgQIECAQRaDFqhHhSJTZo04CBAgQIBBUQEAStPHKJkCAAAECBAgQIECAAIHHCLRYNSIcecz0UAgBAgQIECBQEhCQmBsECBAgQIAAAQIECBAgQOCeAq1WjZTCka1bc91T1agJECBAgACBMAICkjCtVigBAgQIECBAgAABAgQIPEjgY0opByRzr72BxtSKlL33ehC5UggQIECAAIGnCQhIntZR9RAgQIAAAQIECBAgQIDAkwVyKJLDkRbBSL6ncOTJs0dtBAgQIECAwM8EBCQmBAECBAgQIECAAAECBAgQuIfA0lkjf04p/eHzypL8zz0v4cgeNe8hQIAAAQIEbisgILlt6wycAAECBAgQIECAAAECBAIJLIUjORjJ1+x9CUf2ynkfAQIECBAgcFsBAclt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21LrlDZ4CAECBAgQIECAAIG/FxCQmBUECBAgQIAAAQIECPQisDUUGcbdY8iwppYex93LXDAOAgQIECBAgAABAs0FBCTNiT2AAAECBAgQIECAAIEFgTVhQukWeXuqrzsTXlo1koebx5zH7kWAAAECBAgQIECAwEUCApKL4D2WAAECBAgQIECAQHCBI6HIK11PqzDW1OS8keATX/kECBAgQIAAAQL9CAhI+umFkRAgQIAAAQIECBB4ukAOEPLr/efVE8O/L9U8rLL475TSt6OLewpH1qwa6XG1y5K/nxMgQIAAAQIECBB4rICA5LGtVRgBAgQIECBAgACBbgTWrKwYD/Z1pUUpfOjh95m1tfUU5nQzMQyEAAECBAgQIECAwJUCPfxCcWX9nk2AAAECBAgQIECAQBuBITjId1+7WiRfO5wnMqwcKYUjH1JK79oMffVd164ayeGI80ZWs7qQAAECBAgQIECAwDkCApJznD2FAAECBAgQIECAQASBHITkP19tDEVK53KUAoirV2OsXTViS60Is16NBAgQIECAAAECtxUQkNy2dQZOgAABAgQIECBA4HKBPWeKDIMeQpH831OrK/K9P05UeGU4sjYYycO+cpyXTwwDIECAAAECBAgQIHAHAQHJHbpkjAQIECBAgAABAgT6Edi7ddY4GFnacuqnzsKRNdtpDWGPLbX6ma9GQoAAAQIECBAgQKAoICAxOQgQIECAAAECBAgQmBM4GojsCQ3yypGpc0uu+P2ltJJlysyWWj5LBAgQIECAAAECBG4kcMUvGDfiMVQCBAgQIECAAAEC4QSObJv1ilU6V2QJtLRSIx/evrTqZOneW36+ZTutfN+zx7elFtcSIECAAAECBAgQIDAhICAxLQgQIECAAAECBAgQqLFKZFD8kFL6bmeY0cOh7FuDEatGfH4IECBAgAABAgQI3FRAQHLTxhk2AQIECBAgQIAAgQMCtVaJvA6hxgqKK88d2RqM5Npr1Hygjd5KgAABAgQIECBAgMARAQHJET3vJUCAAAECBAgQIHAfgZqrRIaq926jNaU2tXrkrNUZaw9gH8adD2HP7/EiQIAAAQIECBAgQODGAgKSGzfP0AkQIECAAAECBAjMCLRYJdIiGMn3LAUUrX9f2bpqpGYgZPISIECAAAECBAgQIHCxQOtfOC4uz+MJECBAgAABAgQIhBJosUrkFbBVQDAVkLRcpbE1GMkGLccTapIqlgABAgQIECBAgEAvAgKSXjphHAQIECBAgAABAgS2C7QORIYRtQpGhvtPnT3S4neVPcFI69q3d907CBAgQIAAAQIECBCoItDil44qA3MTAgQIECBAgAABAgT+TuCsQGR4cF41kQOC/KfV66zVI1vPGRGMtOq4+xIgQIAAAQIECBDoREBA0kkjDIMAAQIECBAgQIDAhMDZgUgeQg4GPn3+l7MOIZ8KLmr+nrI1GMkGttPycSRAgAABAgQIECAQQKDmLx4BuJRIgAABAgQIECBAoJnA66Hq+SHDfzd74OjGV62YaLW91p7ttAQjZ802zyFAgAABAgQIECDQgYCApIMmGAIBAgQIECBAgEBYgfwl/ruU0jcppV9epHBVMJLLbbG91p5g5EqDi9rusQQIECBAgAABAgQICEjMAQIECBAgQIAAAQLnC+z5Er/mKIdAIN+z5fkiS2OuHZBs3U5LMLLUIT8nQIAAAQIECBAg8GABAcmDm6s0AgQIECBAgACBrgSuDkWGMGQ4eL0HnFrba20NRnLtttPqYQYYAwECBAgQIECAAIELBQQkF+J7NAECBAgQIECAwOMFrg5FhtUhPYUiQ9OnQo083q83zIo9voKRDcAuJUCAAAECBAgQIPBkAQHJk7urNgIECBAgQIAAgSsE9nxpX3OcOWT49LZ11pXbZy3VNLV6ZG14scfYdlpLHfFzAgQIECBAgAABAsEEBCTBGq5cAgQIECBAgACBqgL5i/r8ev/2z+G/qz5k4WY9rxIpDT2P+auJH675/WTrdlqCkTNno2cRIECAAAECBAgQuJHAml9AblSOoRIgQIAAAQIECBBoIvC7lNK/pZT+IaX018+rM64IQobCXgOR/P96XiVSasbU6pEfU0q/nagnW+c/OVD5MqX0yw0dztt13dFnQ4kuJUCAAAECBAgQIEBgr4CAZK+c9xEgQIAAAQIECEQRKK12OKv+JwQiY6upgGS4ZjgvJa/K2RtErd2q66weeg4BAgQIECBAgAABAh0KCEg6bIohESBAgAABAgQIdCNwRTjyfUrpTzc4Q+RIkz4eCD/mnms7rSNd8V4CBAgQIECAAAECwQQEJMEarlwCBAgQIECAAIFNAjUDkmElSD5APb+G/466BdTWs0QEI5umrosJECBAgAABAgQIEFgSEJAsCfk5AQIECBAgQIBAZIF89sgfNwK8BiHRQ5Aluhohie20lpT9nAABAgQIECBAgACBSQEBiYlBgAABAgQIECBAYF6gtIpEEFJv5mzZcuuvKaW8DVl+5UPYvQgQIECAAAECBAgQILBLQECyi82bCBAgQIAAAQIEggkMYch/vn05H3VbrJZtL60meeIh9S0d3ZsAAQIECBAgQIAAgZUCApKVUC4jQIAAAQIECBAgQKC5wG/eDm+3NVlzag8gQIAAAQIECBAgQEBAYg4QIECAAAECBAgQIECAAAECBAgQIECAAAEC4QQEJOFarmACBAgQIECAAAECBAgQIHFkvNwAAAVtSURBVECAAAECBAgQIEBAQGIOECBAgAABAgQIECBAgAABAgQIECBAgAABAuEEBCThWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiDhAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLhBAQk4VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYg4QIECAAAECBAgQIECAAAECBAgQIECAAAEC4QQEJOFarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIOECBAgAABAgQIECBAgAABAgQIECBAgAABAuEEBCThWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiDhAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLhBAQk4VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYg4QIECAAAECBAgQIECAAAECBAgQIECAAAEC4QQEJOFarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIOECBAgAABAgQIECBAgAABAgQIECBAgAABAuEEBCThWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiDhAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLhBAQk4VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYg4QIECAAAECBAgQIECAAAECBAgQIECAAAEC4QQEJOFarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIOECBAgAABAgQIECBAgAABAgQIECBAgAABAuEEBCThWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiDhAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLhBAQk4VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYg4QIECAAAECBAgQIECAAAECBAgQIECAAAEC4QQEJOFarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIOECBAgAABAgQIECBAgAABAgQIECBAgAABAuEEBCThWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiDhAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLhBAQk4VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYg4QIECAAAECBAgQIECAAAECBAgQIECAAAEC4QQEJOFarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIOECBAgAABAgQIECBAgAABAgQIECBAgAABAuEEBCThWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiDhAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLhBAQk4VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYg4QIECAAAECBAgQIECAAAECBAgQIECAAAEC4QQEJOFarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIOECBAgAABAgQIECBAgAABAgQIECBAgAABAuEEBCThWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiDhAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLhBAQk4VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYg4QIECAAAECBAgQIECAAAECBAgQIECAAAEC4QQEJOFarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIOECBAgAABAgQIECBAgAABAgQIECBAgAABAuEEBCThWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiDhAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLhBP4X9VX13ELiBr8AAAAASUVORK5CYII=	t
165	2025-04-07 22:03:22.187425	2025-04-07 22:04:51.936422	\N	\N	t	\N	 [R] Hora entrada ajustada de 22:03 a 00:03	2025-04-07 22:03:22.41987	2025-04-07 22:05:06.335809	46	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAxwAAAGQCAYAAAAk6maCAAAAAXNSR0IArs4c6QAAIABJREFUeF7t3c8V5LadIGBMBt4M5AhWc9qjrNOeJwLJEew6Aq0jGGcwUgTz9jinsSKQM7AyWGUwK7S6rBKbJEASIPHnq/f6ta1mgcD3QxXxKwDkPwUvAgQIECBAgAABAgQIVBL4p0rlKpYAAQIECBAgQIAAAQJBwqETECBAgAABAgQIECBQTUDCUY1WwQQIECBAgAABAgQISDj0AQIECBAgQIAAAQIEqglIOKrRKpgAAQIECBAgQIAAAQmHPkCAAAECBAgQIECAQDUBCUc1WgUTIECAAAECBAgQICDh0AcIECBAgAABAgQIEKgmIOGoRqtgAgQIECBAgAABAgQkHPoAAQIECBAgQIAAAQLVBCQc1WgVTIAAAQIECBAgQICAhEMfIECAAAECBAgQIECgmoCEoxqtggkQIECAAAECBAgQkHDoAwQIECBAgAABAgQIVBOQcFSjVTABAgQIECBAgAABAhIOfYAAAQIECBAgQIAAgWoCEo5qtAomQIAAAQIECBAgQEDCoQ8QIECAAAECBAgQIFBNQMJRjVbBBAgQIECAAAECBAhIOPQBAgQIECBAgAABAgSqCUg4qtEqmAABAgQIECBAgAABCYc+QIAAAQIECBAgQIBANQEJRzVaBRMgQIAAAQIECBAgIOHQBwgQIECAAAECBAgQqCYg4ahGq2ACBAgQIECAAAECBCQc+gABAgQIECBAgAABAtUEJBzVaBVMgAABAgQIECBAgICEQx8gQIAAAQIECBAgQKCagISjGq2CCRAgQIAAAQIECBCQcOgDBAgQIECAAAECBAhUE5BwVKNVMAECBAgQIECAAAECEg59gAABAgQIECBAgACBagISjmq0CiZAgAABAgQIECBAQMKhDxAgQIAAAQIECBAgUE1AwlGNVsEECBAgQIAAAQIECEg49AECBAgQIECAAAECBKoJSDiq0SqYAAECBAgQIECAAAEJhz5AgAABAgQIECBAgEA1AQlHNVoFEyBAgAABAgQIECAg4dAHCBAgQIAAAQIECBCoJiDhqEarYAIECBAgQIAAAQIEJBz6AAECBAgQIECAAAEC1QQkHNVoFUyAAAECBAgQIECAgIRDHyBAgAABAgQIECBAoJqAhKMarYIJECBA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	t
154	2025-04-07 20:52:10.776863	2025-04-07 20:52:23.144747	\N	\N	t	\N	 [R] Hora entrada ajustada de 20:52 a 22:52	2025-04-07 20:52:11.006535	2025-04-07 20:52:35.093106	46	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkgAAAGQCAYAAADlQuzyAAAAAXNSR0IArs4c6QAAIABJREFUeF7t3cuVJsd5JuCQB/JAkAegBS2s5syKZywAZcGQFrRoASkLBHow2s0ObAuEsYCgBcPl7DD1EZVA4u+8RN7j8uQ5fXjpzLg8EdVVle8fEf+QXAQIECBAgAABAgQIECBAgAABAgQIECBAgACBzgT+obP+6i4BAgQIECBAgAABAgQIECBAgAABAgQIECBAIAlITAICBAgQIECAAAECBAgQIECAAAECBAgQIECgOwEBSXdDrsMECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQcIECAAAECBAgQIECAAAECBAgQIECAAAECBLoTEJB0N+Q6TIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAECBAgQIECAAAECBAgQIECAAAECBAgQIECgOwEBSXdDrsMECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQcIECAAAECBAgQIECAAAECBAgQIECAAAECBLoTEJB0N+Q6TIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAECBAgQIECAAAECBAgQIECAAAECBAgQIECgOwEBSXdDrsMECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQcIECAAAECBAgQIECAAAECBAgQIECAAAECBLoTEJB0N+Q6TIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAECBAgQIECAAAECBAgQIECAAAECBAgQIECgOwEBSXdDrsMECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQcIECAAAECBAgQIECAAAECBAgQIECAAAECBLoTEJB0N+Q6TIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAECBAgQIECAAAECBAgQIECAAAECBAgQIECgOwEBSXdDrsMECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQcIECAAAECBAgQIECAAAECBAgQIECAAAECBLoTEJB0N+Q6TIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAECBAgQIECAAAECBAgQIECAAAECBAgQIECgOwEBSXdDrsMECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQcIECAAAECBAgQIECAAAECBAgQIECAAAECBLoTEJB0N+Q6TIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAECBAgQIECAAAECBAgQIECAAAECBAgQIECgOwEBSXdDrsMECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQcIECAAAECBAgQIECAAAECBAgQIECAAAECBLoTEJB0N+Q6TIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAECBAgQIECAAAECBAgQIECAAAECBAgQIECgOwEBSXdDrsMECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQcIECAAAECBAgQIECAAAECBAgQIECAAAECBLoTEJB0N+Q6TIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAECBAgQIECAAAECBAgQIECAAAECBAgQIECgOwEBSXdDrsMECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQcIECAAAEC9wj8S0rpY0rpU0rpz+9/7qlZLQQIECBAgAABAgQIECBAgAABAp8JCEhMCgIECBAgcI/AD6Nqfv/23//tnmrVQoAAAQIECBAgQIAAAQIECBAgMCUgIDEvCBAgQIDAPQLfvq0aiVUkcQlI7jFXCwECBAgQIECAAAECBAgQIEBgVkBAYnIQIECAAIF7BMYBSWyx9dU91aqFAAECBAgQIECAAAECBAgQIEBgSkBAYl4QIECAAIF7BGJLrTiDJC4ByT3maiFAgAABAgQIECBAgAABAgQIzAoISEwOAgQIECBwj0BsrxWrSAQk93irhQABAgQIECBAgAABAgQIECCwKCAgMUEIECBAgMA9AuOAJGr0Pfged7UQIECAAAECBAgQIECAAAECBCYFvJwxMQgQIECAwD0CrwFJnEESW225CBAgQIAAAQIECBAgQIAAAQIEHhAQkDyArkoCBAgQ6Fbgh1HPBSTdTgMdJ0CAAAECBAgQIECAAAECBEoQEJCUMAraQIAAAQK9CMQZJLGSJC4BSS+jrp8ECBAgQIAAAQIECBAgQIBAkQICkiKHRaMIECBAoFGBcUAS22tFSOIiQIAAAQIECBAgQIAAAQIECBB4QEBA8gC6KgkQIECgWwEBSbdDr+MECBAgQIAAAQIECBAgQIBAaQICktJGRHsIECBAoGWBf0spfXzvoBUkLY+0vhEgQIAAAQIECBAgQIAAAQLFCwhIih8iDSRAgACBhgTi/JFYRTJcvg83NLi6QoAAAQIECBAgQIAAAQIECNQl4MVMXeOltQQIECBQt4CApO7x03oCBAgQIECAAAECBAgQIECgIQEBSUODqSsECBAgUIXAD6NWxiHtsdWWiwABAgQIECBAgAABAgQIECBA4GYBAcnN4KojQIAAge4FHNTe/RQAQIAAAQIECBAgQIAAAQIECJQgICApYRS0gQABAgR6EhCQ9DTa+kqAAAECBAgQIECAAAECBAgUKyAgKXZoNIwAAQIEGhVwDkmjA6tbBAgQIECAAAECBAgQIECAQF0CApK6xktrCRAgQKB+gdeAxDkk9Y+pHhAgQIAAAQIECBAgQIAAAQIVCghIKhw0TSZAgACB6gXG22wJSKofTh0gQIAAAQIECBAgQIAAAQIEahQQkNQ4atpMgAABArULOIek9hHUfgIECBAgQIAAAQIECBAgQKB6AQFJ9UOoAwQIECBQoYBzSCocNE0mQIAAAQIECBAgQIAAAQIE2hIQkLQ1nnpDgAABAvUI/DBqqm226hk3LSVAgAABAgQIECBAgAABAgQaERCQNDKQukGAAAEC1Qn8W0rp43ur/5xSipDERYAAAQIECBAgQIAAAQIECBAgcJOAgOQmaNUQIECAAIEXgddttqwiMUUIECBAgAABAgQIECBAgAABAjcKCEhuxFYVAQIECBB4EXBYuylBgAABAgQIECBAgAABAgQIEHhIQEDyELxqCRAgQIBASskqEtOAAAECBAgQIECAAAECBAgQIPCQgIDkIXjVEiBAgACBdwGrSEwFAgQIECBAgAABAgQIECBAgMADAgKSB9BVSYAAAQIERgKvq0h+//Z3cYC7iwABAgQIECBAgAABAgQIECBA4EIBAcmFuIomQIAAAQKZAhGIfBzd68D2TDi3ESBAgAABAgQIECBAgAABAgT2CghI9sp5jgABAgQInCtgq61zPZVGgAABAgQIECBAgAABAgQIEFgUEJCYIAQIECBAoAwBW22VMQ5aQYAAAQIECBAgQIAAAQIECHQiICDpZKB1kwABAgSqELDVVhXDpJEECBAgQIAAAQIECBAgQIBACwICkhZGUR8IECBAoCUBW221NJr6QoAAAQIECBAgQIAAAQIECBQrICApdmg0jAABAgQ6FbDVVqcDr9sECBAgQIAAAQIECBAgQIDAvQICknu91UaAAAECBHIEbLWVo+QeAgQIECBAgAABAgQIECBAgMABAQHJATyPEiBAgACBCwXGW21FNb5nX4itaAIECBAgQIAAAQIECBAgQKA/AS9b+htzPSZAgACBegR+GDX192//PVaWuAgQIECAAAECBAgQIECAAAECBE4QEJCcgKgIAgQIECBwkcDreSRfpZT+fFFdiiVAgAABAgQIECBAgAABAgQIdCUgIOlquHWWAAECBCoUGJ9HEuFIrCQRklQ4kJpMgAABAgQIECBAgAABAgQIlCUgIClrPLSGAAECBAhMCYy32opwJFaSuAgQIECAAAECBAgQIECAAAECBA4ICEgO4HmUAAECBAjcJPC61ZbzSG6CVw0BAgQIECBAgAABAgQIECDQroCApN2x1TMCBAgQaEtgvNVW9Mz38LbGV28IECBAgAABAgQIECBAgACBmwW8XLkZXHUECBAgQOCAwLdv54/EapK4vksp/epAWR4lQIAAAQIECBAgQIAAAQIECHQtICDpevh1ngABAgQqFBifR2KrrQoHUJMJECBAgAABAgQIECBAgACBMgQEJGWMg1YQIECAAIFcgdettoQkuXLuI0CAAAECBAgQIECAAAECBAiMBAQkpgMBAgQIEKhPQEhS35hpMQECBAgQIECAAAECBAgQIFCYgICksAHRHAIECBAgkCkgJMmEchsBAgQIECBAgAABAgQIECBAYEpAQGJeECBAgACBegVeQ5Kv3g5x/3O93dFyAgQIECBAgAABAgQIECBAgMB9AgKS+6zVRIAAAQIErhAQklyhqkwCBAgQIECAAAECBAgQIECgeQEBSfNDrIMECBAg0IGAkKSDQdZFAgQIECBAgAABAgQIECBA4FwBAcm5nkojQIAAAQJPCbyGJL7HPzUS6iVAgAABAgQIECBAgAABAgSqEPDypIph0kgCBAgQIJAl8O3bGST/8n5nnEUSZ5K4CBAgQIAAAQIECBAgQIAAAQIEJgQEJKYFAQIECBBoS0BI0tZ46g0BAgQItC8QH26IDza4CBAgQIAAAQIEbhYQkNwMrjoCBAgQIHCDwDgk+f1bfbH9losAAQIECBB4RmBY3Rm1x3//MGrG+O/GrdsSmMyV8drbKPPT+//pZ4Nn5oJaCRAgQIAAgcIEBCSFDYjmECBAgACBEwTiRUmEJMNlu60TUBVBgAABAgQWBIaQIjcA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	t
155	2025-04-07 20:59:58.098141	2025-04-07 21:00:12.868821	\N	\N	t	\N	 [R] Hora entrada ajustada de 20:59 a 22:59	2025-04-07 20:59:58.33455	2025-04-07 21:00:34.041476	46	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkgAAAGQCAYAAADlQuzyAAAAAXNSR0IArs4c6QAAIABJREFUeF7t3cu1Hcl1JuCQB/KApAWiB4U76qEmPS/0XAPKAggWUD3oedW8DejZRVnAlgclD+QBdHfVTVZWIs/JZ2TG48u1QBC4+Yj4dnDhnPwZEf+QHAQIECBAgAABAgQIECBAgAABAgQIECBAgACBzgT+obP+6i4BAgQIECBAgAABAgQIECBAgAABAgQIECBAIAlIDAICBAgQIECAAAECBAgQIECAAAECBAgQIECgOwEBSXcl12ECBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIMECBAgAABAgQIECBAgAABAgQIECBAgAABAt0JCEi6K7kOEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISY4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBDoTkBA0l3JdZgAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkBgDBAgQIECAAAECBAgQIECAAAECBAgQIECAQHcCApLuSq7DBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEGCBAgAABAgQIECBAgAABAgQIECBAgAABAgS6ExCQdFdyHSZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJMYAAQIECBAgQIAAAQIECBAgQIAAAQIECBAg0J2AgKS7kuswAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxBggQIECAAAECBAgQIECAAAECBAgQIECAAIHuBAQk3ZVchwkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiTFAgAABAgQIECBAgAABAgQIECBAgAABAgQIdCcgIOmu5DpMgAABAgQIECBAgAABAgQIECBAgAABAgQICEiMAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKA7AQFJdyXXYQIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgwQIECAAAECBAgQIECAAAECBAgQIECAAAEC3QkISLoruQ4TIECAAAECBAgQIECAAAECBAgQIECAAAECAhJjgAABAgQIECBAgAABAgQIECBAgAABAgQIEOhOQEDSXcl1mAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQGAMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAdwICku5KrsMECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQYIECAAAECBAgQIECAAAECBAgQIECAAAECBLoTEJB0V3IdJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkxgABAgQIECBAgAABAgQIECBAgAABAgQIECDQnYCApLuS6zABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAge4EBCTdlVyHCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJMUCAAAECBAgQIECAAAECBAgQIECAAAECBAh0JyAg6a7kOkyAAAECBAgQIECAAAECBAgQIECAAAECBAgISIwBAgQIECBAgAABAgQIECBAgAABAgQIECBAoDsBAUl3JddhAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLdCQhIuiu5DhMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmOAAAECBAgQIECAAAECBAgQIECAAAECBAgQ6E5AQNJdyXWYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJAYAwQIECBAgAABAgQIECBAgAABAgQIECBAgEB3AgKS7kquwwQIECBAgAABAgQIECBAgAABAgQIECBAgICAxBggQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEuhMQkHRXch0mQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCTGAAECBAgQIECAAAECBAgQIECAAAECBAgQINCdgICku5LrMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQYIECBAgAABAgQIECBAgAABAgQIECBAgACB7gQEJN2VXIcJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkxQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECHQnICDpruQ6TIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIjAECBAgQIECAAAECBAgQIECAAAECBAgQIECgOwEBSXcl12ECBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIMECBAgAABAgQIECBAgAABAgQIECBAgAABAt0JCEi6K7kOEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISY4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBDoTkBA0l3JdZgAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkBgDBAgQIECAAAECBAgQIECAAAECBAgQIECAQHcCApLuSq7DBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEGCBAgAABAgQIECBAgAABAgQIECBAgAABAgS6ExCQdFdyHSZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJMYAAQIECBAgQIAAAQIECBAgQIAAAQIECBAg0J2AgKS7kuswAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxBggQIECAAAECBAgQIECAAAECBAgQIECAAIHuBAQk3ZVchwkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiTFAgAABAgQIECBAgAABAgQIECBAgAABAgQIdCcgIOmu5DpMgAABAgQIECBAgAABAgQIECBAgAABAgQICEiMAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKA7AQFJdyXXYQIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgwQIECAAAECBAgQIECAAAECBAgQIECAAAEC3QkISLoruQ4TIECAAAECBAgQIECAAAECBAgQIECAAAECAhJjgAABAgQIECBAoDWBD+8d+vT++/DnoZ9fUko/vf/h31rrvP4QIECAAAECBAgQIECAwDoBAck6J2cRIECAAAECBAiULRAhyKNAZKnln4UlS0R+ToAAAQIECBAgQIAAgfYEBCTt1VSPCBAgQIAAAQK9CIxnikxniew1GGaXmFmyV9B1BAgQIECAAAECBAgQqERAQFJJoTSTAAECBAgQIEDgF4EIQuLXd++/52SJmSURmMQvBwECBAgQIECAAAECBAg0JiAgaaygukOAAAECBAgQaFAgApGY0fH1glDkEd+PKaWPDdrqEgECBAgQIECAAAECBLoVEJB0W3odJ0CAAAECBAgULzDsK3LW8llHO2yvkqOCridAgAABAgQIECBAgEBBAgKSgoqhKQQIECBAgAABAr8InBmMjJfHOitoEZQYqAQIECBAgAABAgQIEGhAQEDSQBF1gQABAgQIECDQiMAZwcgQiAz7h8zRnLWPSTzDZu6NDD7dIECAAAECBAgQIECgPwEBSX8112MCBAgQIECAQGkCR4KRcSAS/dqzoXqEHHs3fReSlDaatIcAAQIECBAgQIAAAQIrBQQkK6GcRoAAAQIECBAgkEUgwolPG+4cAchPoyBkTyDy7HFb2xP3etkZzGzotlMJECBAgAABAgQIECBA4GwBAcnZou5HgAABAgQIECCwRmBLEBEhyLMls9Y8b+s50b6Y2RIzS5aOaF+EJA4CBAgQIECAAAECBAgQqEhAQFJRsTSVAAECBAgQINCAQIQOryv7cUcwMm3asF/J0iwXs0hWFtVpBAgQIECAAAECBAgQKEVAQFJKJbSDAAECBAgQINC2wJZ9RoZltErbAP3ZrBezSNoev3pHgAABAgQIECBAgECDAgKSBouqSwQIECBAgACBggS2BCPR7NI3PY/ZL9GnucNn64IGnqYQIECAAAECBAgQIEBgScCXuCUhPydAgAABAgQIENgjsDUYqWUGxrMlwiyztWekuIYAAQIECBAgQIAAAQI3CQhIboL3WAIECBAgQIBAwwKlb8B+hP5ZQFJLyHOk/64lQIAAAQIECBAgQIBAMwICkmZKqSMECBAgQIAAgdsFtswaKWED9r1gltnaK+c6AgQIECBAgAABAgQIFCQgICmoGJpCgAABAgQIEKhUoJdgZCjPX1JKf31QK5+vKx3Emk2AAAECBAgQIECAQH8CvsD1V3M9JkCAAAECBAicKbBlOa1W9uh4tsyWz9dnji73IkCAAAECBAgQIECAQEYBX+Ay4ro1AQIECBAgQKBhgWchwbTbn9/+IoKUVg4BSSuV1A8CBAgQIECAAAECBLoWEJB0XX6dJ0CAAAECBAhsFuhtOa05IAHJ5mHjAgIECBAgQIAAAQIECJQnICApryZaRIAAAQIECBAoVWDtclo1b8C+1v7rgxN9vl4r6DwCBAgQIECAAAECBAjcLOAL3M0F8HgCBAgQIECAQCUCrymlmDmxdLSyz8hSPwUkS0J+ToAAAQIECBAgQIAAgcIFBCSFF0jzCBAgQIAAAQI3C6zda6S1fUaW2AUkS0J+ToAAAQIECBAgQIAAgcIFBCSFF0jzCBAgQIAAAQI3CqxZUquH5bTmSiAguXFgejQBAgQIECBAgAABAgTOEBCQnKHoHgQIECBAgACB9gTWLKnV26yRocqPgqMIi2KJMQcBAgQIECBAgAABAgQIVCAgIKmgSJpIgAABAgQIELhQYM2SWr3OGlkKSHoNjC4cnh5FgAABAgQIECBAgACB8wQEJOdZuhMBAgQIECBAoHaBNeGIECAly2vVPtK1nwABAgQIECBAgAABAiklAYlhQIAAAQIECBAgEAJL+430PmtkGCWPnARH/ndEgAABAgQIECBAgACBygQEJJUVTHMJECBAgAABAhkElsIRL/9/RX82w4ZRhoHplgQIECBAgAABAgQIEMgpICDJqeveBAgQIECAAIHyBZbCkdh0PGaPOB7PshGOGB0ECBAgQIAAAQIECBCoUEBAUmHRNJkAAQIECBAgcJLAs3DEklrfIj/ae0SIdNKAdBsCBAgQIECAAAECBAhcKSAguVLbswgQIECAAAEC5QgshSPx0t/xm8APKaXvZ0DMHjFKCBAgQIAAAQIECBAgUKmAgKTSwmk2AQIECBAgQOCAwLNwxAv/edhHs0d8nj4wEF1KgAABAgQIECBAgACBOwV8obtT37MJECBAgAABAtcLCEe2mz8y+zGl9HH77VxBgAABAgQIECBAgAABAiUICEhKqII2ECBAgAABAgSuERCO7HO298g+N1cRIECAAAECBAgQIECgaAEBSdHl0TgCBAgQIECAwGkCwpF9lI/cLEW2z9NVBAgQIECAAAECBAgQKEZAQFJMKTSEAAECBAgQIJBN4Fk4Epuxf8n25Ppv/Prm82GmG9zqr60eECBAgAABAgQIECDQuYCApPMBoPsECBAgQIBA8wLCkf0lNntkv50rCRAgQIAAAQIECBAgULyAgKT4EmkgAQIECBAgQGC3gHBkN90vFz7ae8Rn6GOuriZAgAABAgQIECBAgEARAr7cFVEGjSBAgAABAgQInC4Qy0LF8lBzh+WhlrnNHlk2cgYBAgQIECBAgAABAgSqFhCQVF0+jSdAgAABAgQIzAoIR44NjGczb3x+PmbragIECBAgQIAAAQIECBQj4AteMaXQEAIECBAgQIDAaQJzS0PFRuwxc8TxXMCyZEYIAQIECBAgQIAAAQIEOhEQkHRSaN0kQIAAAQIEuhF4tG+GZbWWh8CzcOTz2+XxcwcBAgQIECBAgAABAgQINCIgIGmkkLpBgAABAgQIEHjfcySW1xofZo6sGxrCkXVOziJAgAABAgQIECBAgEAzAgKSZkqpIwQIECBAgEDnAnMv+IUj6waFcGSdk7MIECBAgAABAgQIECDQlICApKly6gwBAgQIECDQqcCj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/MjMkf2OriRAgAABAgQIECBAgAABAosCApJFIicQIECAAAECGwXMHtkI9n76OByJv/I5bZ+jqwgQIECAAAECBAgQIECAwCoBX7xXMTmJAAECBAgQWClg9shKqMlpwpF9bq4iQIAAAQIECBAgQIAAAQK7BQQku+lcSIAAAQIECMwImD2yfViMQ6W42uez7YauIECAAAECBAgQIECAAAECmwV8Ad9M5gICBAgQIEDggYDZI9uHxjQcse/IdkNXECBAgAABAgQIECBAgACBXQICkl1sLiJAgAABAgQmAuMX/V7yrxsewpF1Ts4iQIAAAQIECBAgQIAAAQJZBAQkWVjdlAABAgQIdCcwvOz/klJ66a732zssHNlu5goCBAgQIECAAAECBAgQIHCqgIDkVE43I0CAAAECXQqYPbKt7MKRbV7OJkCAAAECBAgQIECAAAECWQQEJFlY3ZQAAQIECHQlMLzwt7TWctmFI8tGziBAgAABAgQIECBAgAABApcICEguYfYQAgQIECDQrIDZI+tLKxxZb+VMAgQIECBAgAABAgQIECCQXUBAkp3YAwgQIECAQNMCZo+sK++HlNLr6FR7taxzcxYBAgQIECBAgAABAgQIEMgmICDJRuvGBAgQIECgeQGzR9aVeDpzRDiyzs1ZBAgQIECAAAECBAgQIEAgq4CAJCuvmxMgQIAAgaYFzB5ZLu905khc8ZJSipDEQYAAAQIECBAgQIAAAQIECNwoICC5Ed+jCRAgQIBAxQJmjywXz7Jay0bOIECAAAECBAgQIECAAAECtwkISG6j92ACBAgQIFC1wDgg8Xni21KaOVL18NZ4AgQIECBAgAABAgQIEOhBwAuNHqqsjwQIECBA4FwBs0eee86FI5/fLgk3BwECBAgQIECAAAECBAgQIFCIgICkkEJoBgECBAgQqEjA7JHHxRKOVDSQNZUAAQIECBAgQIAAAQIE+hYQkPRdf70nQIAAAQJ7BL6+X2RWxLd6g83wE0Z7RphrCBAgQIAAAQIECBAgQIDABQICkguQPYIAAQIECDQkYPbIfDHNHGlokOsKAQIECBAgQIAAAQIECPQhICDpo856SYAAAQIEzhIwe2Re8jWlFCHJcJg5ctaIcx8CBAgQIECAAAECBAgQIJBJQECSCdZtCRAgQIBAgwJmjwhHGhzWukSAAAECBAgQIECAAAEC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ngABAgQIECBAgAABAgQIECBAgAABAgQIEKhOQEBSXck0mAABAgQIECBAgAABAgQIECBAgAABAgQIEDgqICA5Kuh6AgQIECBAgAABAgQIECBAgAABAgQIECBAoDoBAUl1JdNgAgQIECBAgAABAgQIECBAgAABAgQIECBA4KiAgOSooOsJECBAgAABAgQIECBAgAABAgQIECBAgACB6gQEJNWVTIMJECBAgAABAgQIECBAgAABAgQIECBAgACBowICkqOCridAgAABAgQIECBAgAABAgQIECBAgAABAgSqExCQVFcyDSZAgAABAgQIECBAgAABAgQIECBAgAABAgSOCghIjgq6ngABAgQIECBAgAABAgQIECBAgAABAgQIEKhOQEBSXck0mAABAgQIECBAgAABAgQIECBAgAABAgQIEDgqICA5Kuh6AgQIECBAgAABAgQIECBAgAABAgQIECBAoDoBAUl1JdNgAgQIECBAgAABAgQIECBAgAABAgQIECBA4KiAgOSooOsJECBAgAABAgQIECBAgAABAgQIECBAgACB6gQEJNWVTIMJECBAgAABAgQIECBAgAABAgQIECBAgACBowICkqOCridAgAABAgQIECBAgAABAgQIECBAgAABAgSqExCQVFcyDSZAgAABAgQIECBAgAABAgQIECBAgAABAgSOCghIjgq6ngABAgQIECBAgAABAgQIECBAgAABAgQIEKhOQEBSXck0mAABAgQIECBAgAABAgQIECBAgAABAgQIEDgqICA5Kuh6AgQIECBAgAABAgQIECBAgAABAgQIECBAoDoBAUl1JdNgAgQIECBAgAABAgQIECBAgAABAgQIECBA4KiAgOSooOsJECBAgAABAgQIECBAgAABAgQIECBAgACB6gQEJNWVTIMJECBAgAABAgQIECBAgAABAgQIECBAgACBowICkqOCridAgAABAgQIECBAgAABAgQIECBAgAABAgSqExCQVFcyDSZAgAABAgQIECBAgAABAgQIECBAgAABAgSOCghIjgq6ngABAgQIECBAgAABAgQIECBAgAABAgQIEKhOQEBSXck0mAABAgQIECBAgAABAgQIECBAgAABAgQIEDgqICA5Kuh6AgQIECBAgAABAgQIECBAgAABAgQIECBAoDoBAUl1JdNgAgQIECBAgAABAgQIECBAgAABAgQIECBA4KiAgOSooOsJECBAgAABAgQIECBAgAABAgQIECBAgACB6gT+G9FlMNyFpXsXAAAAAElFTkSuQmCC	t
166	2025-04-07 22:08:59.935923	2025-04-07 22:19:22.953079	\N	\N	t	\N	 [R] Hora entrada ajustada de 22:08 a 00:08	2025-04-07 22:09:00.160303	2025-04-07 22:19:38.178553	46	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAsQAAAGQCAYAAACponb/AAAAAXNSR0IArs4c6QAAIABJREFUeF7t3d3V7bZ9J2Cmg6QCOxXYrkD21aypQnIFE1egmQrsDiKVkMu5clRB1EHkCuK5m7uZA+ulxUPxAyQB4uvZa3lJ1uEmgeeP/e7fiwOC/zB5ESBAgAABAgQIEBhY4B8G7ruuEyBQp8Bvp2n6etG07z7+/d9X/6yz9VpFgAABAs0JCMTNlUyDCXQrMAfh8M+Y1//6dND/jDnQMQQIECBA4EhAIDY+CBCoQeDP0zTFBuFle3/36X3zzHEN/dAGAgQIEGhQQCBusGiaTKAjgRCCQxi++wphOIRiLwIECBAgcFtAIL5N540ECDwQuLo8Yu9S307T9NWDdngrAQIECBCYBGKDgACBtwX+c5qmXya6aLjh7s5Si0SXdxoCBAgQ6EFAIO6hivpAoB2B/3ehqWE5RAi8XxyEXmuIL4A6lAABAgS2BQRiI4MAgbcErtw4t14bvLfWWCB+q3quQ4AAgY4FBOKOi6trBCoSuBKG97ZT2zqHrdcqKrKmECBAoFUBgbjVymk3gXYEwl7BywdtHLX8aMZ36zwCcTvjQEsJECBQrYBAXG1pNIxAFwKxYThm+zSBuIshoRMECBCoT0Agrq8mWkSgF4HYMBy7ddrWDXnWEPcyWvSDAAECBQUE4oL4Lk2gY4HYB27ELnnYC9d+hnU8iHSNAAECbwn4MnlL2nUIjCUQs71abBgOcpZLjDV+9JYAAQKvCgjEr3K7GIEhBGJ2lIhZM7zE2grYfn4NMZx0kgABAvkFfKHkN3YFAiMJxITh4HHlZ4/Z4ZFGkL4SIECggMCVL6UCzXNJAgQaEoi9ie7qz52t2eEryy0aItRUAgQIECghcPWLqUQbXZMAgfoFYsPw1SC7dXPe1XPUr6eFBAgQIFBUQCAuyu/iBLoQyBWGA87WuWO3aesCVycIECBAIL+AQJzf2BUI9CyQenu1tdVWIPZzq+cRpW8ECBAoIOCLpQC6SxLoRCB3GA5M6/XDV3en6IRaNwgQIEAgp4BAnFPXuQn0LRCz1/DTALu+hvXDfY8pvSNAgEARAYG4CLuLEmheIGZ7tadh2HZrzQ8THSBAgEAbAgJxG3XSSgI1CcTeRPe7aZpCKL77sn74rpz3ESBAgMAlAYH4EpeDCQwv8FYYDtDrWeinM87DFw8AAQIECGwLCMRGBgECsQKxYTjVOl/rh2Mr4zgCBAgQeCQgED/i82YCwwi8HYa3drB4ugRjmGLpKAECBAhcExCIr3k5msCIAm9sr7Z2tX54xJGmzwQIECgkIBAXgndZAg0JxGyvlmqZxMyyDsSpz98Qv6YSIECAQG4BgTi3sPMTaFvgje3VtoSsH2573Gg9AQIEmhIQiJsql8YSeFUgZt1wrp0f1oHYz6pXS+9iBAgQGEvAl8xY9dZbArECMWE4nCvHjW6WS8RWyXEECBAgkERAIE7C6CQEuhIoGYYD5HqZhvXDXQ0vnSFAgEB9AgJxfTXRIgIlBUrsKLHur+USJUeAaxMgQGBAAYF4wKLrMoEDgZib6HLO2FouYXgSIECAwOsCAvHr5C5IoFqBmKUSOcNwgBGIqx0eGkaAAIF+BQTifmurZwSuCNQQhkN7LZe4UjXHEiBAgEASAYE4CaOTEGhaICYM59pebQlndrjpYaTxBAgQaFdAIG63dlpOIJVAzJPo3vhZIRCnqqjzECBAgMAlgTe+5C41yMEECLwqEHMTXY69hrc6abnEq6V3MQIECBCYBQRiY4HAuAIxSyVy30Q365sdHncc6jkBAgSKCwjExUugAQSKCNQUhgOAQFxkGLgoAQIECAQBgdg4IDCmwNm64bdmhmd9yyXGHId6TYAAgSoEBOIqyqARBF4VOJsdfmNHiWWH1+15+/qv4rsYAQIECNQnIBDXVxMtIpBT4CwMl/ibo2+mafpy0em3Z6dzejs3AQIECDQgIBA3UCRNJJBQ4GypxFs7Siy7tN7pws+lhAV3KgIECBA4F/DFc27kCAK9CJzNDpeYmf3tNE0hEM8vyyV6GW36QYAAgYYEBOKGiqWpBB4I1BiGQ3fsLvGgqN5KgAABAmkEBOI0js5CoHaBo6USJWdlLZeofeRoHwECBAYQEIgHKLIuDi9wNjtc8ufAMqiXWLIx/OAAQIAAAQL2ITYGCPQucBaGS4ZQyyV6H336R4AAgUYESs4MNUKkmQSaFjhaKlEyDAdUyyWaHloaT4AAgX4EBOJ+aqknBNYCR7PDpcNwaKvlEsYsAQIECFQhIBBXUQaNIJBcYL2d2foCpT/7lkskL7kTEiBAgMBdgdJfinfb7X0ECBwLrJcjLI8u8fCNdWstlzCCCRAgQKAaAYG4mlJoCIFkArUvlQgdtVwiWbmdiAABAgSeCgjETwW9n0B9Ans30tWwbjhoWS5R35jRIgIECAwtIBAPXX6d71DgaHa4ls+75RIdDjxdIkCAQMsCtXxBtmyo7QRqETgKwzWsG56dLJeoZcRoBwECBAj8TUAgNhAI9COwdyNdLUslgrTlEv2MNz0hQIBANwICcTel1JHBBfZmh2sKw1uB2M+gwQeu7hMgQKAGAV9GNVRBGwg8F9i7ka62z7jlEs9r7QwECBAgkFigti/LxN1zOgJDCLQ6O1zTuuYhBopOEiBAgMC2gEBsZBBoW2DviXS1LZUIynaXaHusaT0BAgS6FRCIuy2tjg0isDU7/O/TNIXZ19pelkvUVhHtIUCAAIG/CQjEBgKBdgX2lkrU+Llet7XGNrY7ErScAAECBB4J+FJ6xOfNBIoKbN1IV+NSiYC0bGutM9hFi+niBAgQIFBOQCAuZ+/KBJ4IbM0O1xqG1+uca23nk3p4LwECBAg0LCAQN1w8TR9aYGt2uNbPs+USQw9VnSdAgED9ArV+gdYvp4UEygm0NDu8Xi5hdrjcuHFlAgQIENgREIgNDQLtCaxnh2sOmR7V3N740mICBAgMJyAQD1dyHW5coLWAablE4wNO8wkQIDCCgEA8QpX1sReBraUStX+G7T3cy+jTDwIECHQsUPuXacf0ukbgskBLSyVC58wOXy6xNxAgQIBACQGBuIS6axK4LtDaUonQw+Wjmmte53y9Gt5BgAABAl0JCMRdlVNnOhZo8cEWlkt0PCB1jQABAj0JCMQ9VVNfehX4ZpqmLxed+900TeFpbzW/LJeouTraRoAAAQKfCQjEBgSBugXWwfIP0zT9qe4m/611ZocbKJImEiBAgMCPAgKxkUCgboEWl0qsQ3wLM9p1jwKtI0CAAIGsAgJxVl4nJ/BIoNVlB8t2h6UdIRB7ESBAgACBagUE4mpLo2GDC7S4q8RcMsslBh+8uk+AAIHWBATi1iqmvaMItBoqW53VHmVc6ScBAgQIbAgIxIYFgfoEWl6D22qQr28UaBEBAgQIvCYgEL9G7UIEogRaXirRctujiuMgAgQIEOhTQCDus6561a5Ai7tKzNqplkv89tM+y+F/X3ycOPz7+hVu1vvu4z+G63oRIECAAIHbAgLxbTpvJJBcIFWgTN6wyBMeLZdYhtqtgBv+2y+mafpl5LWWh4XHQoeXYHwDz1sIECBAwD7ExgCBWgRaX26wbv/8JL2t8JvTXDjOqevcBAgQ6FTADHGnhdWt5gRavxlt2f5a8EM4NmtcSzW0gwABAhULCMQVF0fThhFodalEmP39+mO9b63F8mCQWiujXQQIEKhIQCCuqBiaMqRAi0slWgjCy8Hk0dFDfrR0mgABAvECAnG8lSMJ5BBoaalEa0F4rte30zR9laN4zkmAAAECfQgIxH3UUS/aFGhlqcQ30zT9apqmXxdgnm/OC1ushX+fb9ILSzViX3+YpulPsQc7jgABAgTGExCIx6u5Htch0MJSiT+/vD74h2ma/jpNUwiw4TWH4b2KrQ33jrNkoo4xrxUECBCoVkAgrrY0Gta5QK1LJVIui1jO7u4F3LPQGzMMQpv/9WAPY4E4RtExBAgQGFhAIB64+LpeTKDGpRIpgvAcbsN2ZymC7pUChfaHGe2tl+3Xrkg6lgABAgMKCMQDFl2XiwrUtlQiRRAOoKVvXDsKxLZeKzrkXZwAAQL1CwjE9ddIC/sSqGWpxJMgHALmX6Zp+nJRmhp+luyteRaI+/oM6Q0BAgSSC9TwJZa8U05IoFKBGpZKhDZ8ceNmue8/ZoHn3RpqCfbLUu89Lc+SiUo/EJpFgACBWgQE4loqoR29C5ReKnFnRjjMrM7bnS3XBJfuy9ZYOdpxQiDu/dOlfwQIEHgoIBA/BPR2ApECpWZU7wbhoxvjapjpXrPvzQ6H4/ycixykDiNAgMCoAr4oRq28fr8pUCpAxu7TO1uEWeCYHSJKhfu9mpkdfnM0uxYBAgQ6FBCIOyyqLlUlUGJ5wdGOC1s4sUE4vLdUuL8Ths0OV/VR0BgCBAjUKyAQ11sbLetDYDmb+sZuB1dmha8E4bkaZof7GJd6QYAAAQILAYHYcCCQT2AdTnM/MS32Uct3gvDW7HDpm9W+WW39tqzkG7985Bs5zkyAAAECrwoIxK9yu9hAAm8ulYhdInE3CM9lq225xNGNdKXD+kBDXVcJECDQvoBA3H4N9aBOgbeWFsQukXgaENeh++n5nlbNjXRPBb2fAAECBP4uIBAbDATSC7w1kxoThp/OCu/NDude/nFWFdusnQn5cwIECBCIFhCIo6kcSCBK4K2lEjHrhVPO4r59c+AR9tEvAt9O0/RVVKUcRIAAAQIEPgQEYkOBQFqBN5ZKnIXhVLPCe7PDKYP2Vf2j9dIl23W1H44nQIAAgYoEBOKKiqEpzQvkXioR89S5HKFwvTyh5M+NvV8G7CrR/MdHBwgQIFBOoOQXW7leuzKB9AK5l0rEhOEc63pz9+tKJY5mxv0suyLpWAIECBD4TMCXiAFBII1AzqUSZzfPpV4isRSpIRCfbSuXY1Y8zahwFgIECBBoQkAgbqJMGlm5QM6lEmdhOHcYLL1conT/Kx96mkeAAAECKQQE4hSKzjGyQM4Z1KMnsQXz3GE4Z9/OxkzMEpHc/T9roz8nQIAAgU4EBOJOCqkbxQSW61pT3th1NDOac4nEErLU7PDZrPAbvwwUG1AuTIAAAQLvCwjE75u7Yj8C6+CW6qa2GsJwidnhmFnht34Z6GeU6gkBAgQInAoIxKdEDiCwK5DjRrqjnRTeXCLwdiA2K+yDRoAAAQLFBATiYvQu3LhA6hvpznZSePMJbFttyfmz4uxBIz9M0/T7aZrC7LAXAQIECBBILpDzSy55Y52QQCUCqWdPz8JwqqUYsXyp+7d33bN+h/d9P03Tb2Ib7jgCBAgQIHBHQCC+o+Y9owukXCpxFgrfDsOhtm/cTBezRKJE30cf2/pPgACBIQUE4iHLrtMPBFIulTi7eS4EwrdfuWeHY2+cK9H3t61djwABAgQqERCIKymEZjQhkDIs1hiGt2aHU87SxswKv3njYBODTiMJECBAIL+AQJzf2BX6EUi1VKLWMLxuV6p9lWNnhUMYduNcP58XPSFAgEAzAgJxM6XS0MICqZZK1LKt2hZnyhnw+fxmhQsPXJcnQIAAgXMBgfjcyBEE1je+3f1r/ZrDcI6t1s62U/OQDZ8tAgQIEKhCQCCuogwaUbnA08czny0ZuBuwU7KlnB0+2zkjtLuGPqf0cy4CBAgQaFhAIG64eJr+isDTxzOfhcOUN609AUm11drZrHBoYy19fuLlvQQIECDQkYBA3FExdSWLwJMb6VoJwylmh8/6GoqT6ia9LIV2UgIECBAYV0AgHrf2en4u8ORGulp3ktjq9Xp2+OpyhphZ4avnPK+OIwgQIECAQCIBgTgRpNN0J/DkRrqWwvBWW2N/LsTOCttOrbuPhw4RIECgL4HYL76+eq03BM4FlkHxyuxmS2E4KNyZHT67SXDWveJ2XhFHECBAgACBTAICcSZYp21a4O5SiaMwXGM4vDM7HLOvsO3Umh7+Gk+AAIHxBATi8Wqux+cCd26kay0MB4UrN9PFzgrbQeJ8fDmCAAECBCoTEIgrK4jmFBe4MzvcYhiOfRBHbBC2g0TxoasBBAgQIHBXQCC+K+d9vQpcnR1uMQzHzg5bHtHrKNcvAgQIEPhMQCA2IAj8JHD1RrpWw3Do8dHNdDFBOJyjxnXRxjMBAgQIELgsIBBfJvOGTgWuPpHuKDTWvo5272a6K8sjbKXW6QdBtwgQIDCigEA8YtX1eUtg+XCJs5nPlsPw1uzwt9M0/eLTk+RCID562T3CZ4cAAQIEuhQQiLssq05dFLhyI13rYTh2OcSa8OyXhIvkDidAgAABAvUICMT11EJLygnE3kjXehjemh0+U7d7xJmQPydAgACB5gUE4uZLqAMPBZYh9yj89RCGr8wOWx7xcGB5OwECBAi0IyAQt1MrLU0vsN6Ld29ZwNaevXNrar+Bbm7nUR+WsoJw+nHmjAQIECBQuYBAXHmBNC+rQMw2a62H4didIwK0dcJZh5uTEyBAgECtAgJxrZXRrtwCsTfSLXefWLap9vB4JQibFc492pyfAAECBKoWEIirLo/GZRSImR1uMQwLwhkHjVMTIECAQJ8CAnGfddWrY4GY2eG9G9BqnRm+EoT/7zRN//3TvsNhZtiLAAECBAgMLyAQDz8EhgQ422attTC8N5O9V9xaQ/2Qg1GnCRAgQKC8gEBcvgZa8K7A2VKJlsLwlW3Ulso+9++OOVcjQIAAgcoFfDFWXiDNSy6wnB1ej/+9HSVqm1G9G4QDZm19SV5gJyRAgAABAlcFBOKrYo5vWeBsdnhr6UFNAfJKEA7rg/8yTdOXq4L5zLc8grWdAAECBLII+HLMwuqklQoczQ5vhc1aHlt8JQgvZ4GX/TU7XOmg1CwCBAgQKC8gEJevgRa8I3A0O7wXOEs/he5uEA6iW+/1eX9nrLkKAQIECDQm4AuysYJp7i2Bo23WagzDV4Pw1oM1zA7fGireRIAAAQIjCgjEI1Z9vD4v1wYv1wTv3URXamb46vZpe0+YMzs83hjXYwIECBB4ICAQP8Dz1iYEri6VePsmuisP1FiCH7VzHazf7lMTA0MjCRAgQIDALCAQGwu9C+zdSLc1i/pmcMwRhEMtv9nYWaLUjHfvY0v/CBAgQKATAYG4k0LqxqbA3uxwyTAcrv3Fp8cmh0B85RUb1q0dvqLqWAIECBAg8GmTfoHYMOhZYGt2eGvdcO7t1cI1/zhN069vYMcG4XDqraD/7TRNX924rrcQIECAAIFhBATiYUo9XEf3ZofX62tzhuG7yyJCm777CLixhdu7QdBnPFbQcQQIECAwrIAvy2FL333H59nhZeDdmkFNvb72bggOBdnbNSKmWCWXgcS0zzEECBAgQKBaAYG42tJo2AOBrdnhnGF4DsGhyVfXBj8NwuH9e/sW+3w/GETeSoAAAQLjCPjCHKfWo/R0uXRgXn+7tZzgytrcLbs5+H59MwSnCMJzu9Y30oX//rR/o4wX/SRAgAABAm6qMwa6E1jOls6/8KXceeHJkogZO+UyjRqftNfdoNIhAgQIEOhbwAxx3/UdrXdbSyX+Y7W7w52b6FKE4HlGOIThVK+9MHynj6na5DwECBAgQKA5AYG4uZJp8IHAcgeJMLbXgfH7aZp+Eyn4dF3w8jJPbpY7au7eo54tl4gsssMIECBAgEAQEIiNg14E1rPDoV9hfe/yFTPeU80Gz9fNFU73Zod9rnsZ0fpBgAABAq8JxASE1xrjQgQeCCy3WQshNMyexobh1CE4XDfXrPDcp60b6cKf5QrgD0rjrQQIECBAoG4Bgbju+mhdnMBytjQ8me3L1dv2QmKOIPxGKDU7HDcuHEWAAAECBKIEBOIoJgdVLjDPlobg+8VqG7R1GA4hOPxvfVyKLr4xO7v3RLo3gngKI+cgQIAAAQLVCQjE1ZVEgy4KLGdLwzKF5YMxlgE1/Pd/nabplxfPH3N47uURyzbs3UgnEMdUyjEECBAgQGBDQCA2LFoXmGeHv/uY9V32J4zvXMsiwnXeDMLhekdLJcKf+zy3Ppq1nwABAgSKCPgCLcLuookEjgJiWEv8iwdPkTtq4ttBeG7L3o10ZocTDSinIUCAAIExBQTiMeveQ6+P1tLm6l+pIGx2OFdFnZcAAQIECPgrVmOgYYF5dviv0zT9Y8Z+hBAcXimfMHenuWaH76h5DwECBAgQiBAwQxyB5JDqBM7W0qZocMnZ4HX7z/r7xu4WKUydgwABAgQIVCkgEFdZFo06EMi5W0S4bAiXIQzPM8OlixGzNMTnuHSVXJ8AAQIEmhbwRdp0+YZp/LyVWngU83JbtVQANc0Gmx1OVVXnIUCAAAECkQICcSSUw14XmLdLCxfOEYLD2uMfpmn6Q0WzwVfDcDjeZ/j1oemCBAgQINCbgC/T3irabn9yPkFuXv4QlkOEVy3LIc6qZe3wmZA/J0CAAAECCQQE4gSITnFb4F+maQrLIFLvEjEvgWgp/N6ZHXYz3e2h540ECBAgQOAnAYHYaCgpcLSV2JV29RCA7wRin98ro8SxBAgQIEBgR8AXqqFRSiDMDv/xwcVrvhHuQbf+9tazpRLhGLPDT5W9nwABAgQIfAgIxIZCKYEngTg8JKOVdcB3fP8ccSOhz+4dWe8hQIAAAQIbAr5UDYuSAv91sH44BN6/TNP05aqBvc+Mmh0uOSJdmwABAgSGFBCIhyx7VZ0OwfeLaZrCNmj/Nk3TN4vZ3/VMae9hOBRGIK5qeGoMAQIECIwgIBCPUOU2+7gOhmHP4H9usyvRrY4Jw+FkPrfRpA4kQIAAAQLnAr5Yz40c8b7AVjAcYazGBOIRZsmvjLj5oS3hn8HPiwABAgQIXBYYIWRcRvGGogJbofDbT0+V+6poq/JfPCYMmx3+vA5bZr3fcJl/JLoCAQIEBhQQiAcsesVdDrN8Yd3w8jXCUonQ35hAbHb487GxtY91WJMeQrEXAQIECBCIFhCIo6kc+ILA1nZjI8z4bf0isMUtEP+kcmQ2wph54ePoEgQIEBhHQCAep9a193RrhnSUAGh2+ProPDLzc+26p3cQIEBgaAFfHEOXv5rO74WbEQKx2eF7w3BvzFgycc/TuwgQIDC0gEA8dPmr6PzIYTgUIGZ2OBzns/r5cN17mt8Iv0RV8cHVCAIECPQk4Eu2p2q21xfrQKdp68awdSWFvJ+PbYG4vc+7FhMgQKBaAYG42tIM0bDRQ43Z4fvDfO8XCb883Df1TgIECAwrIBAPW/riHV+Hwe8+HuE80vIAs8P3h+GenR0m7pt6JwECBIYVEIiHLX3Rjh/NjI4yw2d2+P4QPFpq42fafVfvJECAwLACvjyGLX2xjm+FGbPD2+UY5ZeDq4PRDhNXxRxPgAABAocCArEB8rbA+q+6Q+j7+qMRowRAs8PPRt3oa8+f6Xk3AQIECPxMQCA2KN4UWAfBEIDDaw7Eo4xHa4efjTo31D3z824CBAgQWAmMEkAUvrzAOgyHByiEQBxm+8LL7PDnNfLZ3B6znlBX/rOsBQQIEOhOwJdudyWtskNb64bDbgDhv5sd/nnJRvnl4M5gHf1BLnfMvIcAAQIETgQEYkPkDYH1ms/1UolRAqC1w89Hm+USzw2dgQABAgRWAgKxIZFbYGvdcPhvc0gOSyfCbPEIL2uHn1XZdmvP/LybAAECBHYEBGJDI6fAXhhe/nezw59XwGdyf0SGX56+2PjjkX6pyvl5dW4CBAgMK+DLd9jSZ+/41mzePN7mmdJRwnDANjv8fMi1sFwi/LIXXiGkh/95ESBAgEADAgJxA0VqtIlb64ZDWDA7vF9Qn8d9mxZ2l1gHdo+RbvSHl2YTIDCegC/g8Wr+Ro/3lkosZ0pHmR0+Wve6rMUoHnfG31EY/mGapn++c9LE79l6WIilHImRnY4AAQK5BATiXLLjnndrv+H5prnln40y9uws8fyzcGRYwy8Snpz3vMbOQIAAgaICo4SSosiDXXz918bLMTba2mGzw88H/9kvFKV/hu2FYbPDz2vvDAQIEHhNoPSXyWsddaFXBI6WSow4O7y3K8K6GD6H+8Oz1kB89MuOMPzKjxsXIUCAQDoBX8TpLEc/01EYDjajzQ6HPv/HNE2/PhkYNfyVf61j92yGvZTdUUgXhmsdTdpFgACBAwGB2PBIIbAOLutQMOLs8PKXgCNjn8H7s8MlAnHt65lTfJ6dgwABAsMJ+DIeruRZOrxeR7nebmrE2eGzv+oPhfju01614ZcJr22Bs72b3/75dTRjXSKcGzcECBAgkEjg7S+URM12mooEzpZKjDo7vHez1bJ0Pn/3Z4ffXpqwF4ZDO0IY9hCOin4oaQoBAgSuCvhCvirm+KXAOiRszZKNODscjM5mN80oHn+WavPbas/bodxPHwIECBDIJCAQZ4Id5LTrWdD1eBp1djhmuYTP3v6H5OxmuvDON3+h8NCNQX6g6SYBAuMK+FIet/ZPe362VGI5S/pmeHnarxTvPwvEo3lcNT3zC+d762fXVlvMDF+tqOMJECBQucBbXyqVM2jeRYGYpRKjzg4vfxHYY/W5Ox5wZ8sl3grEe8Fc/S7+wHA4AQIEahfwg732CtXZvrOlEmaH9+tmdvh4TMfMDr9huNeO9Q4qdX5CtYoAAQIELgkIxJe4HPxJIGapxMizw2e7SwhU9QdiYdiPOgIECAwmIBAPVvCH3Y1ZKjHy7PDZzWBvzGw+LHHxt5deLhFq+PXG/tBqV3xoaAABAgTyCQjE+Wx7PPNy9nPvxqKRZ4fP/rrf7PDz2eFwhpw/t7ZqKAz3+NNMnwgQILAQyPnFArovgXVQ2At3o+47vJwZ36q8UHX+eTj7hSKcIaejMHxeI0cQIECgSwGBuMuyZunU8q+y90LJyLPDlks8H3YxyyVyzbKHv/H4YqMLfkY+r6szECBAoHoBP+yrL1EVDVwulTiaoRt5dvhodjPnrGYVAyRBI2Jmh8NlcvzMstdwggLnvcFkAAAZ4ElEQVQ6BQECBFoWyPHl0rKHtv9cYB0W9sbMyLPDQe1odlMgPv9kne3OEc6Qw3FvZj/Htc4VHEGAAAECRQQE4iLszVw0dleJZSAcMUiYHX42pM+Wm8xnz/HzausXmW+nafrqWZe8mwABAgRaEsjxBdNS/7X1WGAZ9I6C7uizwwLxs09SzHKJHL9obc1K57jOMx3vJkCAAIHsAgJxduJmLxC7VGL02eFl/9fFFq7ihn/MzXSpLe0oEVcbRxEgQGAIAYF4iDJf7uSVpRJmh398kMPWK3WIu1zIRt4QE4hT/qwShhsZGJpJgACBtwRSfsm81WbXyS8Qu6uE2eH9m+n2HlySv3ptXSFm/XDKNb3CcFvjQ2sJECDwioBA/ApzUxdZBoazUGd22Ozw08Eds3441c8pYfhptbyfAAECnQqk+qLplGfIbsU8gGOGGXnf4WBwFOZ8tuI+Pm8FYmE4rh6OIkCAwJACvrSHLPtup2N3lViHwVHXyu6tfR3V486n6Wz/4RSWwvCdyngPAQIEBhIQiAcq9klXryyVCKeag0yKwNJiFcwOp6naWSB++qjmrTXKo47ZNBVzFgIECHQoIBB3WNSbXbqyVOLKTPLN5lT/NrPDaUp0tsPEk59RwnCaGjkLAQIEuhd48mXTPc5AHbwacEe/me5oZwSzj/EfnLMdJp5YCsPxdXAkAQIEhhcQiIcfAj+7MSxmTLiZbnt3ibNdOYy2zwXOAvHd5RLCsJFGgAABApcEYsLPpRM6uDmB5V9Zx4yH0WeHQ4Etl0gzzI/WYd/95SKE4fCglPDP+fVkpjlNT52FAAECBKoWiAlAVXdA4x4JXF0qsQyDo4YMN9M9GnKfvfnI8u74Wt+kd/c86XrpTAQIECBQvYBAXH2JsjXwThg2O7y/97DgdX2oHu0wcedn03rmXk2u18Q7CBAgMKTAnS+dIaE67PQyjMSu1Rx97fByhnw9JISv6x+Sox0mrv5sMjN83d87CBAgQOBD4OqXDrg+BL6ZpunLj67EBjmzw55Ml3L0p9ypQxhOWRnnIkCAwIACAvGARV/cFPb9NE2/iSQwO/zTw0jMDkcOmoPDUq3FFoaf18IZCBAgMLyAQDzeELi6q0QQurPeuEfZvb/i9zm6Xu29QHxldwlh+Lq7dxAgQIDAhoAv8rGGxd1ga7mE5RKpPylPt65bB+rYpT+p++F8BAgQINCBgEDcQREju7Bcs3k1PFguYXeJyGEWfdheII65wVMYjmZ2IAECBAjECAjEMUp9HLMMETGhY+612eEfJSyXSPc5eLJ+WBhOVwdnIkCAAIEPAYF4jKFwd6nEMghenVXuSTasa/1io0NXbkrsyeNpX/YC8dkYW+6OEtpwZb3x0zZ7PwECBAh0LCAQd1zcRdfm2c2rAcLs8I+Ie4H422mavhpjCCXt5d4DOY4C8TpEXx3LSTvgZAQIECDQl4BA3Fc9t3pjdvh5jf9lmqY/bpzG5+ee7dX1w+swbGb+nrt3ESBAgMCOgC/0vofGkzD85L09qq5nib/7NHMcblT0ui5wZT22meHrvt5BgAABAhcFBOKLYI0dfmfP4bmLcxDxV9OfFz3MFv+psXFQU3P3nlC3Nc6E4Zoqpy0ECBDoWEAg7re4T2Z4n2zR1q+onqUQiL2hThhOoe0cBAgQIBAlIBBHMTV30JMwHDrrZrrmSt5Mg2MC8XoW2d9SNFNeDSVAgECbAgJxm3U7a/WTpRLh3B7EcSbsz+8KnK0fFobvynofAQIECNwWEIhv01X7RrPD1ZZGw04ecLIVhsNWbGGG2IsAAQIECGQTEIiz0RY58dMwbHa4SNmGuejRDXUh+Ib9iZevK09UHAZRRwkQIEAgvYBAnN605BmfLpVIEahL9t+16xbYe8DJ/56m6b8tmm7NcN111DoCBAh0JyAQ91PSFGHWVmv9jIcae7IXiJdtFYZrrJw2ESBAoHMBgbiPAqcIw7Za62Ms1NyLvSf+LdtsmUTNFdQ2AgQIdCogEPdR2LD2cn5q2t2azqH6r9M0/VMfLHpRocB/fXqwyT9utMvMcIXF0iQCBAiMInA3PI3i00I/U8wOh37aaq2FavfRxu+nafrVqitmhvuorV4QIECgSQGBuMmy/b3Ry2UOT2bYPIij7XHQUuvDmP168TcaT8Ztrn6HNv56mqb/MU3TLz8usrf12/w3M8s//8vHe77ZmQnP1W7nJUCAAIGbAgLxTbhK3rZcKvFkhs3scCUFHaAZyzEbuvtk3KbimkNtCOrhNf//VOc/Os8cpL9bHDT/t2XIDm2yH/MbFXENAgSGFBCI2y17qqUSZofbHQOttXy5LWDpmeH1THVrljHtPQrQYR33/4kM2V98+sVlGdhjrr0+Jsy0//DxH0O7Uv3SEX5+eREgQOCxgED8mLDICVItlQiNNztcpIRDXbSWxzGHdsxBeKgCdN7ZGv6WoXNi3SPQv4BA3GaNl3/tHJ7wdXeWJNUsc5uKWv2GQOnHMc8h+MvFeuA3+u0a7wmU/tuG93rqSgQIZBMQiLPRZjtxyhA7zw77QslWrqFPXOIGuuV64FR/LT90ERvpvO+yRgqlmQRqFfBDpNbKbLdrPdv2pH4pg3Vbilr7hsCbYXi5DEIIfqO6dV3jyd+S1dUTrSFAoJjAk0BVrNEDXzjVUolA6Ga6gQdS5q7nXjMcnngXbgoLN3vlDsDhQTVbDxLJTOj0kQL+disSymEECBwLCMTtjJDUM7pupmun9i21dDlOQ7tTBJZ5HXCuALzc+my5M8OVbc5yrFUOYTz8L+zOsBf85zbGbMu23iki7Pww75W8tZ9yqN/6v8dc583xeqVGb7bLtQgQaExAIG6nYMstq57WzexwO3VvqaUpwvAy/C4DWWqHEKRCQAz/zBGqtgLs0Wz23SCe2sX5CBAgMKTA02A1JFqBTpsdLoDukpcEri6TmMNh+GeY+c0ZfueOhEdGh+UPv88Ugi+BOZgAAQIE6hEQiOupxV5LUodhs8P117y1Fq5nhr9d/FX83JevPv7lFy+s+52vOc+6hpuuwivHTHBrtdJeAgQIENgQEIjrHxYpl0qE3lo7XH/Nj1oYbij7U0QXztacbp1i/Z5fT9MUZlWX/32ezZ3fn/umtoiu/v2QZQAWfq/IOZYAAQKDCwjEdQ+AnLPDnu5Ud+3XrQsBbxlGQ1D9t8XM57z0ICwJCEF2hFe44Sw4hBlgAXiEiusjAQIEMgkIxJlgE5w2dRg2O5ygKIVOsQ7DhZpRxWWDhSUQVZRCIwgQINCPgEBcby1TL5XIEbDr1eurZSMHYssg+hrLekOAAIEqBQTiKsvy2UMzUj2Fyc10ddY6plUjBeLc26HFeDuGAAECBAYTEIjrK3iOmdwc56xPrt8WhRvp/thZ97YehmEdcGdF1h0CBAi0IiAQ11ep5eOZU934Zna4vjrfaVEIjL9q9FHC9gC+U3HvIUCAAIFXBATiV5ijL5JrJtdWa9ElaObA+YluocFfV9pqN8BVWhjNIkCAAIHPBQTiekbE+klfqWpjdrieGudsSahzyXC8XgJh+UPOajs3AQIECCQVSBW6kjZq0JMtg2uqpRKB0uzwWAMq/GIVxtL6ARpPFX6Ypins+zvvfRzON4de4feprvcTIECAQFEBgbgo/98vnmupRK6QXYeaVpwJLJ8iF/NEuWWwDcsw5vek2unkrL3+nAABAgQIFBEQiIuw/+yiqfccni9gdriO+rbWiuWNncJwa9XTXgIECBC4LCAQXyZL/oY3ZoeFmuRl6/KEYUbYzHCXpdUpAgQIEDgSEIjLjo9cYTj0ys10ZWvb2tWF4dYqpr0ECBAgkExAIE5GeetEuZZKhMZYLnGrJMO+6Ztpmr786L2/URh2GOg4AQIExhQQiMvV3exwOXtX/lxgORa/nabpK0AECBAgQGAkAYG4XLXNDpezd+WfBJZhOPxXPxOMDgIECBAYTsCXX5mSvzU7nHI/4zJSrppbIMejwnO32fkJECBAgEBSAYE4KWfUyXKG4dAAa4ejyuCgTwK5xyJkAgQIECDQhIBA/H6Zci6VEHDer2erV1yOlfBAjvC3CV4ECBAgQGBIAYH43bLnDqy2Wnu3ni1fbfmLmV0lWq6kthMgQIDAYwGB+DHhpRPMISTXjJzlEpfKMezBnkQ3bOl1nAABAgS2BATi98bFcvY2x81uZoffq2XLV7KrRMvV03YCBAgQyCIgEGdh/dlJcy+VCBc0O/xOLVu+yjoM5/jFrGUfbSdAgACBQQUE4ncKn/NGutCDNwL3O1KuklPAUomcus5NgAABAs0KCMT5S/dGWLVcIn8dW7/CMgznWsPeupH2EyBAgMCgAgJx/sLnvpEu9MByifx1bPkKlkq0XD1tJ0CAAIHsAgJxXuLcN9KF1r9xjbxKzp5TYB2GbbGWU9u5CRAgQKBJAYE4X9l+O01T+Gvq8MoZQt6Ygc6n5Mw5BZZjMPc4zNkP5yZAgAABAlkFBOJ8vG+s631jfXI+IWfOLbBcNxyu5fOeW9z5CRAgQKBJAV+Qecr2VlB9I3TnEXLW3AKWSuQWdn4CBAgQ6EZAIM5TytzbrM2tdjNdnvq1flZhuPUKaj8BAgQIvCogEKfnLjE7nHONcnohZ8wpIAzn1HVuAgQIEOhSQCBOX9a3Zm2X60PVMX0dWzzj+iY6+w23WEVtJkCAAIHXBQSptORvzQ6HVr8VvNMKOVsugXUYDtfxNwe5tJ2XAAECBLoSEIjTlfOtbdZCi+09nK5uvZxpvaOEMNxLZfWDAAECBLILCMTpiN/c8cHew+nq1sOZhOEeqqgPBAgQIFBMQCBOQ//mUok3r5VGx1lyCriJLqeucxMgQIDAEAICcZoyv7XNWmjtmzPRaXScJZfAOgyH6/hM59J2XgIECBDoVsCX5/PSvj1j62a65zXr4QzCcA9V1AcCBAgQqEJAIH5ehjcD6tvh+7mOM+QQ2ArDv5umKWyz5kWAAAECBAhcFBCIL4KtDn87oFou8axePbx7KwzbUaKHyuoDAQIECBQTEIif0b85Oxxa+vb1nul4d2oBYTi1qPMRIECAAAE34DwaA2/P1r49G/0Ix5uTCwjDyUmdkAABAgQI/ChghvjeSCgRTt/cyeKeinflEhCGc8k6LwECBAgQEIhvjwGzw7fpvPGiwPqhG+Ht1gxfRHQ4AQIECBA4EjBDfH18lJgd9qjm63Vq/R3hUeBff9o5Ivxz+RKGW6+s9hMgQIBAdQIC8fWSlHhssuUS1+vU8jtCCA4zw+uXMNxyVbWdAAECBKoVEIivlab07LBAdK1eLR69tV449EPtW6ymNhMgQIBAEwIC8bUyldj27O31ytdEHJ1SQBhOqelcBAgQIEAgUkAgjoT6dFipdbwllmjEqzgyhcDeeuFwbk+gSyHsHAQIECBA4EBAII4fHqVnh/2VeXytWjpyb1Y4PIY51NzjmFuqprYSIECAQJMCAnFc2UotW1huuaVWcbVq5aijWeEQgsPMsBcBAgQIECDwgoCQdY68vOP/zVnaUtc9F3HEU4G9WeFw3jfH2NN+eD8BAgQIEOhCQCA+L+McXr6fpuk354cnO+KbaZq+/DibkJSMteiJjmaFQ8OsFy5aHhcnQIAAgVEFBOLjys8PRQgPSPju06EhHL/1mtcs/3Wapn9666Kuk01g64lz88UskcjG7sQECBAgQOBcQCDeN5pnhkuEFcslzsduK0fsPWRjbr9Z4VYqqZ0ECBAg0K2AQLxd2hBi5r/efnu5QomHf3Q7wAt27Gx5hF0kChbHpQkQIECAwFJAIP75eCg5Mxxas/yr9bfDuE9HGoGjm+bCFdQ1jbOzECBAgACBJAIC8eeM85rhEEpLhBazw0mGdbGTnC2PKLH8phiGCxMgQIAAgVYEBOKfKrWcGS7xQIRlGBacWvkE/dhOyyPaqpfWEiBAgACBzwQE4p8CTfi3MDMcXiVcPISjzQ+n5RFt1k2rCRAgQIDA3wVKBL8a+ectzkrd8W+pRI2j4rhNZoXbq5kWEyBAgACBTYHRA/FyzXCpmeHlulNLJer/oJ4F4dCDUr9Y1a+nhQQIECBAoEKB0QNx6R0lwpCYZ6cFqQo/IKsmWR5Rf420kAABAgQIXBYYORDXsL2ZpRKXh2yRN5zNCttTuEhZXJQAAQIECKQRGDUQL5cplDKwVCLNGM59FrPCuYWdnwABAgQIFBYoFQZLdnu5TOK7Tw0J/7/Ey1KJEurx1zQrHG/lSAIECBAg0LTAaIF4GXJKPHhjHiyWStT9sTErXHd9tI4AAQIECCQVGC0Qz7OytYThUMzRapB0AGc42XJt+fr01gpnAHdKAgQIECBQWmCUMLb+6++S/a7hZr7S467G658tkSj5S1SNXtpEgAABAgS6ESgZDN9ErGF7tdBfSyXerHr8tY6WSJgVjnd0JAECBAgQaFJghEC8DMNhli8EnFKv5Y10I9iXcr5y3aMlEmaFr0g6lgABAgQINCrQeyiraUa2prY0OlyTNnu57d36xGaFk1I7GQECBAgQqFug50C8DDw1zPSZHa7ns3C0RKKGsVKPlJYQIECAAIEBBHoOxHMADbN9vytcS7PDhQuwuPzREokwTkouqalHSUsIECBAgMBAAr0G4prCcBhOZofLf6gskShfAy0gQIAAAQJVCvQYiJczgDX0z+xw+aFviUT5GmgBAQIECBCoVqCGwJgSp8bwaXY4ZYWvn0sYvm7mHQQIECBAYCiBngJxbTfRhYFUY0AfaYDvrRe2i8RIo0BfCRAgQIDAiUAvgXgZhmu4iW5mNztc5iN49NS5msZHGR1XJUCAAAECBD4T6CUQ17Zu2OxwuQ/a0c1ztlQrVxdXJkCAAAEC1Qr0EIhrXZZQa7uqHYwJGma9cAJEpyBAgAABAqMJtB6Ia1w3PI+hGmetex3fIQiHsfDFRgetF+616vpFgAABAgQSCbQeiGteo1vbXsiJhkw1p5nXCYcGhX/felkvXE25NIQAAQIECNQr0HIgXv71eG1PGKt55rre0XjesuC6DMJH77Be+NzTEQQIECBAgMA0Ta0G4toDp/XDaT9eR7tGrK8UZoW/+/QfQw28CBAgQIAAAQKnAq0G4mXgrLEPtQf204FRyQFhHXZ47S2JmJsZQnB4hVnh+d8r6YJmECBAgAABArUL1Bgmz8xamH0ViM+quP/nV2eDheD71t5JgAABAgQINLpkovbZ4XlGc57dtJb1/KM2rw0Ou0TEzAaHJRFhJths8LmtIwgQIECAAIETgRZniOfdG2oOmrU+Oa+2D4TZ4Noqoj0ECBAgQGBAgdYCcQuzw/Mwsu3a9gfq6mywJRED/mDSZQIECBAg8KaAQJxPu+Y9kvP1ev/MsbPBHqRRojquSYAAAQIEBhZoLRC39PS3ZVtr2yf5rSEfG4JDewTht6riOgQIECBAgMBnAq0F4paWTIwciGODsBDsBxIBAgQIECBQXKC1QLy8Wa32Wdean6SXY+BdCcHh+tYG56iCcxIgQIAAAQKXBVoLxKGDrdys1sJ+yZcHzMYbrgRhITiFuHMQIECAAAECSQVaDMTzUoTw1+1hlrjWV88P5xCCax112kWAAAECBAhcFmg5EIfO1tz+HgOxIHz5I+YNBAgQIECAQO0CNQfKPbtW1uYu21n7bPbROBWCa/8Uax8BAgQIECDwSEAgfsR3+ObW1xDHBOEQ9D1GOd8YcmYCBAgQIEDgBQGBOB9yi4E4JgQHMdul5Rs3zkyAAAECBAi8LNBiIG7l4RwtBeKYICwEv/zhdDkCBAgQIEDgHYEWA3GL267VuGdyTAg2G/zO59BVCBAgQIAAgYICrQXilnZuqPFJdcEvvL7+tOxh/vet4Wc2uOCH0qUJECBAgACBdwVaC8QtLUOYZ7JDRUs7x8wGu0Hu3c+eqxEgQIAAAQKVCJQOalcZagqZZ20vvbRjDsGhnWaDz6rlzwkQIECAAIFhBVoKxC3NDpfcgzh2NthjlIf92Os4AQIECBAgsBQQiPOMh7fDe2wILr1ncGhn+F9YnhH+50WAAAECBAgQKC7QUiBuabnE8oa6MBMbAnLqV0wIDtes5Qa55S8JoV25XFI7Ox8BAgQIECDQuUArgfjtGdenZc8R3mN3iKgpBM+O6zA8//cat6N7WnvvJ0CAAAECBBoTaCUQ5wiYuUq13BpuvkaYDQ2vqzPFsTfG1RiCl757gdgsca5R6LwECBAgQIBAtEALgfibaZq+/OjRvAb2i2mawr+H1/Lft/7/HsbVNaxXjl8G+PX155vZluebZ3/DP0N/jnaFWJ6vluUQZwNOID4T8ucECBAgQIBAMYEWAvFRuCwGt3HhdWD+5ccx8z9TtHW+Rms7ROzV0JKJFKPCOQgQIECAAIFHAi0E4uUNao862+CblwE4NP/KLHVN3d0LxC2Mv5octYUAAQIECBDIINBKIFlu13XGMG/rNR83Lz9Yh8nYZQnhPGEZw9b5rpzjrN3hz3+Ypun3Hwe2Gn7X/dxbLhH6F2aIvQgQIECAAAECRQVaCcRFkS5c/EpAXt4wt75ELzebbd1gOPe1lz5eGB4OJUCAAAECBGoUEIjLV2VvBjW0rNXQeBSEZ3Fjr/zY0wICBAgQIEDgU+ASSuoZBkc7MbT0ZLejgG92uJ7xpiUECBAgQIDAh4BAXN9QaHmLspgwbO1wfWNOiwgQIECAwNACAnG95W8hGM83O4abDsP2cmdbzAnD9Y43LSNAgAABAsMKCMR1l750KF7eJDg/NCSIXbl5MBzfygNE6h4NWkeAAAECBAhkERCIs7AmP+lRMA4Xu/pI6LmBe4H3Tujd67SHbyQfDk5IgAABAgQIpBT4/02Akxi7PjsjAAAAAElFTkSuQmCC	t
156	2025-04-07 21:00:57.117685	2025-04-07 21:02:26.157158	\N	\N	t	\N	 [R] Hora entrada ajustada de 21:00 a 23:00	2025-04-07 21:00:57.349832	2025-04-07 21:02:29.765182	46	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkgAAAGQCAYAAADlQuzyAAAAAXNSR0IArs4c6QAAIABJREFUeF7t3dGx3MaVBuDW2z4qBDmClSKgGIFDIBXByhHQetpHOwOTEXg3ApoRrEJgJvI99oV3ajwDoDEAprvPhyqWZF3MoM93jlwi/2r0N8VFgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgm8E2yepVLgAABAgQIECBAgAABAgQIECBAgAABAgQIECgCEkNAgAABAgQIECBAgAABAgQIECBAgAABAgQIpBMQkKRruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBNIJCEjStVzBBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLpBAQk6VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBdAICknQtVzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEDBAgQIECAAAECBAgQIECAAAECBAgQIECAQDoBAUm6liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCdgIAkXcsVTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAABAgQIECBAgAABAgQIECBAgAABAgQIECCQTkBAkq7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECKQTEJCka7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTSCQhI0rVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAEC6QQEJOlarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgXQCApJ0LVcwAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxAwQIECBAgAABAgQIECBAgAABAgQIECBAgEA6AQFJupYrmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgnYCAJF3LFUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgkE5AQJKu5QomQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCRmgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISM0CAAAECBAgQIECAAAECBAgQIECAAAECBAikExCQpGu5ggkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiRkgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIE0gkISNK1XMEECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQMECBAgAABAgQIECBAgAABAgQIECBAgAABAukEBCTpWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiBggQIECAAAECBAgQIECAAAECBAgQIECAAIF0AgKSdC1XMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAOgEBSbqWK5gAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgBAgQIECBAgAABAgQIECBAgAABAgQIECBAIJ2AgCRdyxVMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBOQECSruUKJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkZoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEjNAgAABAgQIECBAgAABAgQIECBAgAABAgQIpBMQkKRruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBNIJCEjStVzBBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLpBAQk6VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBdAICknQtVzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEDBAgQIECAAAECBAgQIECAAAECBAgQIECAQDoBAUm6liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCdgIAkXcsVTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAABAgQIECBAgAABAgQIECBAgAABAgQIECCQTkBAkq7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECKQTEJCka7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTSCQhI0rVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAEC6QQEJOlarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgXQCApJ0LVcwAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxAwQIECBAgAABAgQIECBAgAABAgQIECBAgEA6AQFJupYrmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgnYCAJF3LFUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgkE5AQJKu5QomQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCRmgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISM0CAAAECBAgQIECAAAECBAgQIECAAAECBAikExCQpGu5ggkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiRkgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIE0gkISNK1XMEECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQMECBAgAABAgQIECBAgAABAgQIECBAgAABAukEBCTpWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiBggQIECAAAECBAgQIECAAAECBAgQIECAAIF0AgKSdC1XMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAOgEBSbqWK5gAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgBAgQIECBAgAABAgQIECBAgAABAgQIECBAIJ2AgCRdyxVMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBOQECSruUKJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkZoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEjNAgAABAgQIECBAgAABAgQIECBAgAABAgQIpBMQkKRruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBNIJCEjStVzBBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLpBAQk6VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBdAICknQtVzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEDBAgQIECAAAECBAgQIECAAAECBAgQIECAQDoBAUm6liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCdgIAkXcsVTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAABAgQIECBAgAABAgQIECBAgAABAgQIECCQTkBAkq7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECKQTEJCka7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTSCQhI0rVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAEC6QQEJOlarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgXQCApJ0LVcwAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxAwQIECBAgAABAgQIECBAgAABAgQIECBAgEA6AQFJupYrmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgnYCAJF3LFUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgkE5AQJKu5QomQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCRmgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISM0CAAAECBAgQIECAAAECBAgQIECAAAECBAikExCQpGu5ggkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiRkgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIE0gkISNK1XMEECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQMECBAgAABAgQIECBAgAABAgQIECBAgAABAukEBCTpWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiBggQIECAAAECBAgQIECAAAECBAgQIECAAIF0AgKSdC1XMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAOgEBSbqWK5gAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgBAgQIECBAgAABAgQIECBAgAABAgQIECBAIJ2AgCRdyxVMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBOQECSruUKJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkZoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEjNAgAABAgQIECBAgAABAgQIECBAgAABAgQIpBMQkKRruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBNIJCEjStVzBBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLpBAQk6VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBdAICknQtVzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEDBAgQIECAAAECBAgQIECAAAECBAgQIECAQDoBAUm6liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCdgIAkXcsVTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAABAgQIECBAgAABAgQIECBAgAABAgQIECCQTkBAkq7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECKQTEJCka7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTSCQhI0rVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAEC6QQEJOlarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgXQCApJ0LVcwAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxAwQIECBAgAABAgQIECBAgAABAgQIECBAgEA6AQFJupYrmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgnYCAJF3LFUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgkE5AQJKu5QomQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCRmgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISM0CAAAECBAgQIECAAAECBAgQIECAAAECBAikExCQpGu5ggkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiRkgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIE0gkISNK1XMEECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQMECBAgAABAgQIECBAgAABAgQIECBAgAABAukEBCTpWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiBggQIECAAAECBAgQIECAAAECBAgQIECAAIF0AgKSdC1XMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAOgEBSbqWK5gAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgBAgQIECBAgAABAgQIECBAgAABAgQIECBAIJ2AgCRdyxVMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBOQECSruUKJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkZoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEjNAgAABAgQIECBAgAABAgQIECBAgAABAgQIpBMQkKRruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBNIJCEjStVzBBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLpBAQk6VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBdAICknQtVzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEDBAgQIECAAAECBAgQIECAAAECBAgQIECAQDoBAUm6liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCdgIAkXcsVTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAABAgQIECBAgAABAgQIECBAgAABAgQIECCQTkBAkq7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECKQTEJCka7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTSCQhI0rVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAEC6QQEJOlarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQODZAj+WUv727EV4PgECBAgQIECAQC4BAUmufquWAAECBAgQIECAAAECLQhEIPLhdSHx99MVIcmX1/8Rfy80aaFb1kCAAAECBAgQGFRAQDJoY5VFgAABAgQIECBAgACBBgWmYOQyFJlb5i8vP/xjg3VYEgECBAgQIECAwAACApIBmqgEAgQIECBAgAABAgQINCYwBSDx1zeva1sbilyXErtI3jZWn+UQIECAAAECBAgMICAgGaCJSiBAgAABAgQIECBAgMCTBSL8mMKQrUHIXAl+7/rkBns8AQIECBAgQGBEAf+ROWJX1USAAAECBAgQIECAAIHjBKYA5NYZIkc91e9dj5L1vQQIECBAgACBxAL+IzNx85VOgAABAgQIECBAgACBFQJTIBJngUyvy1rxsd1ucQ7JbpS+iAABAgQIECBA4FJAQGIeCBAgQIAAAQIECBAgQOBaYDpMPf75Ea/Mmp4X54tEAHK9K+Xy584fMZ8ECBAgQIAAAQKHCAhIDmH1pQQIECBAgAABAgQIVAj8XEr5r1LK15fDuL+8fC52KrjOFTgrEFkTfEz9j/AkfrkIECBAgAABAgQIHCIgIDmE1ZcSIECAAAECBAgQIHAlMO0QmP46varp1u4Er1Q6fnyO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AQIECBAgQIAAAQIEKgUEJJVgbidAgAABAgTSCcztHFkTjsRukfellHeVcoKRSjC3EyBAgAABAgQIECBAgACBGgEBSY2WewkQIECAAIFsAo+EI9NrtOKvNZdgpEbLvQQIECBAgAABAgQIECBAYKOAgGQjnI8RIECAAAECwwvMhSNfSym/uyMgGBl+NBRIgAABAgQIECBAgAABAiMICEhG6KIaCBAgQIAAgb0F5sKRX0spP9x4oGBk7y74PgIECBAgQIAAAQIECBAgcKCAgORAXF9NgAABAgQIdCkwF4788lJR/PzyEox02WaLJkCAAAECBAgQIECAAIHsAgKS7BOgfgIECBAgQOBSYO2ZI1tDkXjWrZBFFwgQIECAAAECBAgQIECAAIGTBQQkJ4N7HAECBAgQINC0wG8zq4vD0+OqPXR9+sr4/Numq7c4AgQIECBAgAABAgQIECCQSEBAkqjZSiVAgAABAgRmBeZ2jzxCF8FI7BqZApZHvstnCRAgQIAAAQIECBAgQIAAgZ0EBCQ7QfoaAgQIECBAoHuBCDDe7FiFYGRHTF9FgAABAgQIECBAgAABAgT2FhCQ7C3q+wgQIECAAIEeBfbcPSIY6XECrJkAAQIECBAgQIAAAQIE0gkISNK1XMEECBAgQIDADYE9AhLBiNEiQIAAAQIECBAgQIAAAQIdCQhIOmqWpRIgQIAAAQKHCXzeePj6dK6IM0YOa40vJkCAAAECBAgQIECAAAECxwgISI5x9a0ECBAgQIBAXwI/vpw/EiHJ0nUZiMS9Dl5fEvNzAgQIECBAgAABAgQIECDQqICApNHGWBYBAgQIECBwusCt12xNr80ShpzeDg8kQIAAAQIECBAgQIAAAQLHCghIjvX17QQIECBAgEB/ArGbRCDSX9+smAABAgQIECBAgAABAgQIVAkISKq43EyAAAECBAgQIECAAAECBAgQIECAAAECBAiMICAgGaGLaiBAgAABAgQIECBAgAABAgQIECBAgAABAgSqBAQkVVxuJkCAAAECBAgQIECAAAECBAgQIECAAAECBEYQEJCM0EU1ECBAgAABAgQIECBAgAABAgQIECBAgAABAlUCApIqLjcTIECAAAECBAgQIECAAAECBAgQIECAAAECIwgISEboohoIECBAgAABAgQIECBAgAABAgQIECBAgACBKgEBSRWXmwkQIECAAAECBAgQIECAAAECBAgQIECAAIERBAQkI3RRDQQIECBAgAABAgQIECBAgAABAgQIECBAgECVgICkisvNBAgQIECAAAECBAgQIECAAAECBAgQIECAwAgCApIRuqgGAgQIECBAgAABAgQIECBAgAABAgQIECBAoEpAQFLF5WYCBAgQIECAAAECBAgQIECAAAECBAgQIEBgBAEByQhdVAMBAgQIECBAgAABAgQIECBAgAABAgQIECBQJSAgqeJyMwECBAgQIECAAAECBAgQIECAAAECBAgQIDCCgIBkhC6qgQABAgQIECBAgAABAgQIECBAgAABAgQIEKgSEJBUcbmZAAECBAgQIECAAAECBAgQIECAAAECBAgQGEFAQDJCF9VAgAABAgQIECBAgAABAgQIECBAgAABAgQIVAkISKq43EyAAAECBAgQIECAAAECBAgQIECAAAECBAiMICAgGaGLaiBAgAABAgQIECBAgAABAgQIECBAgAABAgSqBAQkVVxuJkCAAAECBAgQIECAAAECBAgQIECAAAECBEYQEJCM0EU1ECBAgAABAgQIECBAgAABAgQIECBAgAABAlUCApIqLjcTIECAAAECBAgQIECAAAECBAgQIECAAAECIwgISEboohoIECBAgAABAgQIECBAgAABAgQIECBAgACBKgEBSRWXmwkQIECAAAECBAgQIECAAAECBAgQIECAAIERBAQkI3RRDQQIECBAgAABAgQIECBAgAABAgQIECBAgECVgICkisvNBAgQIECAAAECBAgQIECAAAECBAgQIECAwAgCApIRuqgGAgQIECBAgAABAgQIECBAgAABAgQIECBAoEpAQFLF5WYCBAgQIECAAAECBAgQIECAAAECBAgQIEBgBAEByQhdVAMBAgQIECBAgAABAgQIECBAgAABAgQIECBQJSAgqeJyMwECBAgQIECAAAECBAgQIECAAAECBAgQIDCCgIBkhC6qgQABAgQIECBAgAABAgQIECBAgAABAgQIEKgSEJBUcbmZAAECBAgQIECAAAECBAgQIECAAAECBAgQGEFAQDJCF9VAgAABAgQIECBAgAABAgQIECBAgAABAgQIVAkISKq43EyAAAECBAgQIECAAAECBAgQIECAAAECBAiMICAgGaGLaiBAgAABAgQIECBAgAABAgQIECBAgAABAgSqBAQkVVxuJkCAAAECBAgQIECAAAECBAgQIECAAAECBEYQEJCM0EU1ECBAgAABAgQIECBAgAABAgQIECBAgAABAlUCApIqLjcTIECAAAECBAgQIECAAAECBAgQIECAAAECIwgISEboohoIECBAgAABAgQIECBAgAABAgQIECBAgACBKgEBSRWXmwkQIECAAAECBAgQIECAAAECBAgQIECAAIERBAQkI3RRDQQIECBAgAABAgQIECBAgAABAgQIECBAgECVgICkisvNBAgQIECAAAECBAgQIECAAAECBAgQIECAwAgCApIRuqgGAgQIECBAgAABAgQIECBAgAABAgQIECBAoEpAQFLF5WYCBAgQIECAAAECBAgQIECAAAECBAgQIEBgBAEByQhdVAMBAgQIECBAgAABAgQIECBAgAABAgQIECBQJSAgqeJyMwECBAgQIECAAAECBAgQIECAAAECBAgQIDCCgIBkhC6qgQABAgQIECBAgAABAgQIECBAgAABAgQIEKgSEJBUcbmZAAECBAgQIECAAAECBAgQIECAAAECBAgQGEFAQDJCF9VAgAABAgQIECBAgAABAgQIECBAgAABAgQIVAkISKq43EyAAAECBAgQIECAAAECBAgQIECAAAECBAiMICAgGaGLaiBAgAABAgQIECBAgAABAgQIECBAgAABAgSqBAQkVVxuJkCAAAECBAgQIECAAAECBAgQIECAAAECBEYQEJCM0EU1ECBAgAABAgQIECBAgAABAgQIECBAgAABAlUCApIqLjcTIECAAAECBAgQIECAAAECBAgQIECAAAECIwgISEboohoIECBAgAABAgQIECBAgAABAgQIECBAgACBKgEBSRWXmwkQIECAAAECBAgQIECAAAECBAgQIECAAIERBAQkI3RRDQQIECBAgAABAgQIECBAgAABAgQIECBAgECVgICkisvNBAgQIECAAAECBAgQIECAAAECBAgQIECAwAgCApIRuqgGAgQIECBAgAABAgQIECBAgAABAgQIECBAoEpAQFLF5WYCBAgQIECAAAECBAgQIECAAAECBAgQIEBgBAEByQhdVAMBAgQIECBAgAABAgQIECBAgAABAgQIECBQJSAgqeJyMwECBAgQIECAAAECBAgQIECAAAECBAgQIDCCgIBkhC6qgQABAgQIECBAgAABAgQIECBAgAABAgQIEKgS+Duf8KCvDP+u3gAAAABJRU5ErkJggg==	t
157	2025-04-07 21:04:17.626818	2025-04-07 21:09:21.285308	\N	\N	t	\N	 [R] Hora entrada ajustada de 21:04 a 23:04	2025-04-07 21:04:17.648071	2025-04-07 21:09:25.454033	46	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkgAAAGQCAYAAADlQuzyAAAAAXNSR0IArs4c6QAAIABJREFUeF7t3Y1xJTd2BtC7GcgRWJuBHAFnItE4gl1FwJkIdjOwFMJGIDICK4NVBqsMxg9rPonDeT/9g+4GcM+rYo0tdqNxz4WrSH5G40/hQ4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJvCnZPUqlwABAgQIECBAgAABAgQIECBAgAABAgQIECAQAhKLgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISa4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmuAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJrgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISa4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmuAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJrgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISa4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmuAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJrgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISa4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmuAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJrgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISa4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmuAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJrgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISa4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmuAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJrgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISa4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmuAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJrgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISa4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmuAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJrgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISa4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmuAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJrgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISa4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmuAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJrgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISa4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmuAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJrgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISa4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmuAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCcgIEnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJrgAABAgQIECBAgAABAgQIECBAgAABAgQIEEgnICBJ13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISa4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBBIJyAgSddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmuAAAECBAgQIPC1wLs3/+kJEgECBAgQIECAAAECBAgQIDCWgIBkrH6qhgABAgQIELgs8DbweHtVCUDKNY8v/14apVzz/PKNc2AiOLHiCBAgQIAAAQIECBAgQIBApwICkk4bZ9oECBAgQGAggdfhxev/+eFGjefrfo2I8nUvANmSq4Qkn05zEJZsqWxsAgQIECBAgAABAgQIECBQWUBAUhnUcAQIECBAgMDvAiW0+C4ifnkVYLwOPY4MNbZoUwlJ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xKIgQIAAAQIECLQv4DVb7ffIDAkQIECAAAECBAgQIECgMwEBSWcNM10CBAgQIEAgrcC1XSR+nku7JBROgAABAgQIECBAgAABAmsE/EK9Rs+9BAgQIECAAIH9BLxmaz9rTyJAgAABAgQIECBAgACBBAICkgRNViIBAgQIECAwhIDXbA3RRkUQIECAAAECBAgQIECAQCsCApJWOmEeBAgQIECAAIH7AnaR3DdyBQECBAgQIECAAAECBAgQmCQgIJnE5CICBAgQIECAQBMCdpE00QaTIECAAAECBAgQIECAAIERBAQkI3RRDQQIECBAgEAmgc9XivVzXaZVoFYCBAgQIECAAAECBAgQWC3gF+nVhAYgQIAAAQIECOwq4DVbu3J7GAECBAgQIECAAAECBAiMKiAgGbWz6iJAgAABAgRGFfCarVE7qy4CBAgQIECAAAECBAgQ2FVAQLIrt4cRIECAAAECBKoI2EVShdEgBAgQIECAAAECBAgQIJBZQECSuftqJ0CAAAECBHoVsIuk186ZNwECBAgQIECAAAECBAg0IyAgaaYVJkKAAAECBAgQmCVgF8ksLhcTIECAAAECBAgQIECAAIEvBQQkVgQBAgQIECBAoE+Ba7tI3kfEU58lmTUBAgQIECBAgAABAgQIENhPQECyn7UnESBAgAABAgRqC3y+MqCf8WpLG48AAQIECBAgQIAAAQIEhhPwy/NwLVUQAQIECBAgkEjALpJEzVYqAQIECBAgQIAAAQIECNQVEJDU9TQaAQIECBAgQGBvgUu7SMortsqrtnwIECBAgAABAgQIECBAgACBKwICEkuDAAECBAgQINC3wMeIeLxQgrNI+u6r2RMgQIAAAQIECBAgQIDAxgICko2BDU+AAAECBAgQ2EHALpIdkD2CAAECBAgQIECAAAECBMYSEJCM1U/VECBAgAABAjkF7CLJ2XdVEyBAgAABAgQIECBAgMAKAQHJCjy3EiBAgAABAgQaEbh2WPun0/xKeOJDgAABAgQIECBAgAABAgQIvBEQkFgSBAgQIECAAIExBH6OiBKUvP78FhH/MUZ5qiBAgAABAgQIECBAgAABAnUFBCR1PY1GgAABAgQIEDhK4NouEoe1H9URzyVAgAABAgQIECBAgACBpgUEJE23x+QIECBAgAABArME/hkR37654ykiSkjiQ4AAAQIECBAgQIAAAQIECLwSEJBYDgQIECBAgACBcQTsIhmnlyohQIAAAQIECBAgQIAAgY0FBCQbAxueAAECBAgQILCzwKWzSOwi2bkJHkeAAAECBAgQIECAAAEC7QsISNrvkRkSIECAAAECBOYI2EUyR8u1BAgQIECAAAECBAgQIJBWQECStvUKJ0CAAAECBAYWsItk4OYqjQABAgQIECBAgAABAgTqCAhI6jgahQABAgQIECDQkoBdJC11w1wIECBAgAABAgQIECBAoEkBAUmTbTEpAgQIECBAgMBqAbtIVhMagAABAgQIECBAgAABAgRGFhCQjNxdtREgQIAAAQKZBT5GxOMFgPcRUQ5t9yFAgAABAgQIECBAgAABAqkFBCSp2694AgQIECBAYHCBzxfq+3T6byU88SFAgAABAgQIECBAgAABAqkFBCSp2694AgQIECBAYHCBa7tI/Aw4eOOVR4AAAQIECBAgQIAAAQL3BfxyfN/IFQQIECBAgACBngUu7SIpr9gqr9ryIUCAAAECBAgQIECAAAECaQUEJGlbr3ACBAgQIEAgiYCzSJI0WpkECBAgQIAAAQIECBAgME9AQDLPy9UECBAgQIAAgR4F7CLpsWvmTIAAAQIECBAgQIAAAQKbCghINuU1OAECBAgQIECgCQG7SJpog0kQIECAAAECBAgQIECAQEsCApKWumEuBAgQIECAAIFtBN5FxM8XhnYWyTbeRiVAgAABAgQIECBAgACBDgQEJB00yRQJECBAgAABAhUE7CKpgGgIAgQIECBAgAABAgQIEBhHQEAyTi9VQoAAAQIECBC4J+AskntCvk+AAAECBAgQIECAAAECaQQEJGlarVACBAgQIECAQNhFYhEQIECAAAECBAgQIECAAIEXAQGJpUCAAAECBAgQyCVQziIpZ5K8/jiLJNcaUC0BAgQIECBAgAABAgQIRISAxDIgQIAAAQIECOQSuHZg+6cTQ9lh4kOAAAECBAgQIECAAAECBFIICEhStFmRBAgQIECAAIEvBC7tIikXvD/tLim7SXwIECBAgAABAgQIECBAgMDwAgKS4VusQAIECBAgQIDAVwLXdpF41ZbFQoAAAQIECBAgQIAAAQJpBAQkaVqtUAIECBAgQIDAFwIObLcgCBAgQIAAAQIECBAgQCC1gIAkdfsVT4AAAQIECCQXcGB78gWgfAIECBAg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gG4nQIAAAQIECBAgQCCvgIAkb+9VToAAAQIECBAg0IZA2Vmy9lB3QUkbvTQLAgQIECBAgAABAgQ6EhCQdNQsUyVAgAABAgQIEBhaoMYruAQlQy8RxREgQIAAAQIECBAgUFNAQFJT01gECBAgQIAAAQIE6gisPdj9+TSNMsZTnekYhQABAgQIECBAgAABAuMJCEjG66mKCBAgQIAAAQIExhFYu6uk7Cgpn/M448iohAABAgQIECBAgAABAisFBCQrAd1OgAABAgQIECBAYCeBtWeVeP3WTo3yGAIECBAgQIAAAQIE+hAQkPTRJ7MkQIAAAQIECBAgcBaosavEjhLriQABAgQIECBAgACB9AICkvRLAAABAgQIECBAgEDHAmvOKik7SsoZJc4p6XgBmDoBAgQIECBAgAABAssFBCTL7dxJgAABAgQIECBAoBWBdxHxISK+XzAh55QsQHMLAQIECBAgQIAAAQL9CwhI+u+hCggQIECAAAECBAi8Fli6q6TsJHk+DeT1W9YTAQIECBAgQIAAAQIpBAQkKdqsSAIECBAgQIAAgYQCa84qcaB7wgWjZAIECBAgQIAAAQLZBAQk2TquXgIECBAgQIAAgWwC5fVb5etxQeGCkgVobiFAgAABAgQIECBAoA8BAUkffTJLAgQIECBAgAABAjUEyq4SQUkNSWMQIECAAAECBAgQINC9gICk+xYqgAABAgQIECBAgMBsgSVBiTNKZjO7gQABAgQIECBAgACBlgUEJC13x9wIECBAgAABAgQIbCuw5ED38tqt8nGY+7a9MToBAgQIECBAgAABAhsLCEg2BjY8AQIECBAgQIAAgQ4Elhzo7nySDhprigQIECBAgAABAgQIXBcQkFgdBAgQIECAAAECBAicBZYc6P5TRHxASIAAAQIECBAgQIAAgd4EBCS9dcx8CRAgQIAAAQIECOwjMPecEjtK9umLpxAgQIAAAQIECBAgUElAQFIJ0jAECBAgQIAAAQIEBhUQlAzaWGURIECAAAECBAgQyC4gIMm+AtRPgAABAgQIECBAYJqAoGSak6sIECBAgAABAgQIEOhEQEDSSaNMkwABAgQIECBAgEAjAoKSRhphGgQIECBAgAABAgQIrBMQkKzzczcBAgQIECBAgACBrAI/RsT3M4p3RskMLJcSIECAAAECBAgQILC9gIBke2NPIECAAAECBAgQIDCygB0lI3dXbQQIECBAgAABAgQGFhCQDNxcpREgQIAAAQIECBDYUUBQsiO2RxEgQIAAAQIECBAgsF5AQLLe0AgECBAgQIAAAQIECPwhICixGggQIECAAAECBAgQ6EJAQNJFm0ySAAECBAgQIECAQHcCgpLuWmbCBAgQIECAAAECBHIJCEhy9Vu1BAgQIECAAAECBPYWEJTsLe55BAgQIECAAAECBAhMEhCQTGJyEQECBAgQIECAAAECKwXmBCWfXp5V7vEhQIAAAQIECBAgQIDAJgICkk1YDUqAAAECBAgQIECAwBWBuUGJkMRSIkCAAAECBAgQIEBgEwEBySasBiVAgAABAgQIECBA4I6AoMQSIUCAAAECBAgQIEDgUAEByaH8Hk6AAAECBAgQIEAgvYCgJP0SAECAAAECBAgQIEDgGAEByTHunkqAAAECBAgQIECAwJcCghIrggABAgQIECBAgACBXQUEJLtyexgBAgQIECBAgAABAncEpgYlDnK3lAgQIECAAAECBAgQWCUgIFnF52YCBAgQIECAAAECBDYSmBOUOMh9oyYYlgABAgQIECBAgMDIAgKSkburNgIECBAgQIAAAQJ9C7yLiPL1OKGMnyLiw4TrXEKAAAECBAgQIECAAIF/CwhILAQCBAgQIECAAAECBFoXOO8QmRKUlFdv2VHSekfNjwABAgQIECBAgEADAgKSBppgCgQIECBAgAABAgQITBIowcfDy66SezcISu4J+T4BAgQIECBAgACB5AICkuQLQPkECBAgQIAAAQIEOhSYcz5JKc+Okg6bbMoECBAgQIAAAQIEthYQkGwtbHwCBAgQIECAAAECBLYSmBOUCEm26oJxCRAgQIAAAQIECHQqICDptHGmTYAAAQIECBAgQIDA7wKCEouBAAECBAgQIECAAIHZAgKS2WRuIECAAAECBAgQIECgUQFBSaONMS0CBAgQIECAAAECLQoISFrsijkRIECAAAECBAgQILBGQFCyRs+9BAgQIECAAAECBJIICEiSNFqZBAgQIECAAAECBJIJnM8ceZxQ96fTNc4omQDlEgIECBAgQIAAAQIjCQhIRuqmWggQIECAAAECBAgQeCtQgo+HiHh3h+YpIp4FJRYQAQIECBAgQIAAgTwCApI8vVYpAQIECBAgQIAAgcwCc167VZzsKMm8WtROgAABAgQIECCQQkBAkqLNiiRAgAABAgQIECBA4EVgTlAiJLFsCBAgQIAAAQIECAwsICAZuLlKI0CAAAECBAgQIEDgqoCgxOIgQIAAAQIECBAgkFxAQJJ8ASifAAECBAgQIECAQHIBQUnyBaB8AgQIECBAgACBvAICkry9VzkBAgQIECBAgAABAn8ITAlKHORuxRAgQIAAAQIECBAYSEBAMlAzlUKAAAECBAgQIECAwCqB85kjj3dG+RQRJSwpXz4ECBAgQIAAAQIECHQqICDptHGmTYAAAQIECBAgQIDAZgJTdpOUh5egxEHum7XBwAQIECBAgAABAgS2FRCQbOtrdAIECBAgQIAAAQIE+hUQlPTbOzMnQIAAAQIECBAgcFdAQHKXyAUECBAgQIAAAQIECCQXEJQkXwDKJ0CAAAECBAgQGFNAQDJmX1VFgAABAgQIECBAgEB9gSlByU8R8aPzSerjG5EAAQIECBAgQIBAbQEBSW1R4xEgQIAAAQIECBAgMLrAlKDE+SSjrwL1ESBAgAABAgQIdC8gIOm+hQogQIAAAQIECBAgQOAAgXenXSLl6/HOswUlBzTHIwkQIECAAAECBAhMERCQTFFyDQECBAgQIECAAAECBC4LTNlNUu4UlFhBBAgQIECAAAECBBoTEJA01hDTIUCAAAECBAgQIECgS4ESlPwlIr65MfuniHg+fb9c60OAAAECBAgQIECAwMECApKDG+DxBAgQIECAAAECBAgMJTBlR4ndJEO1XDEECBAgQIAAAQK9CghIeu2ceRMgQIAAAQIECBAg0LKAoKTl7pgbAQIECBAgQIAAgdN7cAUklgEBAgQIECBAgAABAgS2ESghycPLYe63nmBHyTb+RiVAgAABAgQIECBwU0BAYoEQIECAAAECBAgQIEBgW4Epu0nKDAQl2/bB6AQIECBAgAABAgS+EBCQWBAECBAgQIAAAQIECBDYR0BQso+zpxAgQIAAAQIECBCYJCAgmcTkIgIECBAgQIAAAQIECFQTEJRUozQQAQIECBAgQIAAgeUCApLldu4kQIAAAQIECBAgQIDAGoEpQUl57Vb5lGt9CBAgQIAAAQIECBCoKCAgqYhpKAIECBAgQIAAAQIECMwUmHOQ+9PpwPfy5UOAAAECBAgQIECAQAUBAUkFREMQIECAAAECBAgQIEBgpcCU3STlEQ5yXwntdgIECBAgQIAAAQJnAQGJtUCAAAECBAgQIECAAIF2BAQl7fTCTAgQIECAAAECBAYXEJAM3mDlESBAgAABAgQIECDQpYCgpMu2mTQBAgQIECBAgEBPAgKSnrplrgQIECBAgAABAgQIZBOYEpS8dzZJtmWhXgIECBAgQIAAgRoCApIaisYgQIAAAQIECBAgQIDAdgLvTgFI+Xq88ohycHsJSXwIECBAgAABAgQIEJghICCZgeVSAgQIECBAgAABAgQIHChwbTeJg9sPbIpHEyBAgAABAgQI9CsgIOm3d2ZOgAABAgQIECBAgEBOgddBid0jOdeAqgkQIECAAAECBCoICEgqIBqCAAECBAgQIECAAAECBAgQIECAAAECBAgQ6EtAQNJXv8yWAAECBAgQIECAAAECBAgQIECAAAECBAgQqCAgIKmAaAgCBAgQIECAAAECBAgQIECAAAECBAgQIECgLwEBSV/9MlsCBAgQIECAAAECBAgQIECAAAECBAgQIECggoCApAKiIQgQIECAAAECBAgQIECAAAECBAgQIECAAIG+BAQkffXLbAkQIECAAAECBAgQIECAAAECBAgQIECAAIEKAgKSCoiGIECAAAECBAgQIECAAAECBAgQIECAAAECBPoSEJD01S+zJUCAAAECBAgQIECAAAECBAgQIECAAAECBCoICEgqIBqCAAECBAgQIECAAAECBAgQIECAAAECBAgQ6EtAQNJXv8yWAAECBAgQIECAAAECBAgQIECAAAECBAgQqCAgIKmAaAgCBAgQIECAAAECBAgQIECAAAECBAgQIECgLwEBSV/9MlsCBAgQIECAAAECBAgQIECAAAECBAgQIECggoCApAKiIQgQIECAAAECBAgQIECAAAECBAgQIECAAIG+BAQkffXLbAkQIECAAAECBAgQIECAAAECBAgQIECAAIEKAgKSCoiGIECAAAECBAgQIECAAAECBAgQIECAAAECBPoSEJD01S+zJUCAAAECBAgQIECAAAECBAgQIECAAAECBCoICEgqIBqCAAECBAgQIECAAAECBAgQIECAAAECBAgQ6EtAQNJXv8yWAAECBAgQIECAAAECBAgQIECAAAECBAgQqCAgIKmAaAgCBAgQIECAAAECBAgQIECAAAECBAgQIECgLwEBSV/9MlsCBAgQIECAAAECBAgQIECAAAECBAgQIECggoCApAKiIQgQIECAAAECBAgQIECAAAECBAgQIECAAIG+BAQkffXLbAkQIECAAAECBAgQIECAAAECBAgQIECAAIEKAgKSCoiGIECAAAECBAgQIECAAAECBAgQIECAAAECBPoSEJD01S+zJUCAAAECBAgQIECAAAECBAgQIECAAAECBCoICEgqIBqCAAECBAgQIECAAAECBAgQIECAAAECBAgQ6EtAQNJXv8yWAAECBAgQIECAAAECBAgQIECAAAECBAgQqCAgIKmAaAgCBAgQIECAAAECBAgQIECAAAECBAgQIECgLwEBSV/9MlsCBAgQIECAAAECBAgQIECAAAECBAgQIECggoCApAKiIQgQIECAAAECBAgQIECAAAECBAgQIECAAIG+BAQkffXLbAkQIECAAAECBAgQIECAAAECBAgQIECAAIEKAgKSCoiGIECAAAECBAgQIECAAAECBAgQIECAAAECBPoSEJD01S+zJUCAAAECBAgQIECAAAECBAgQIECAAAECBCoICEgqIBqCAAECBAgQIECAAAECBAgQIECAAAECBAgQ6EtAQNJXv8yWAAECBAgQIECAAAECBAgQIECAAAECBAgQqCAgIKmAaAgCBAgQIECAAAECBAgQIECAAAECBAgQIECgLwEBSV/9MlsCBAgQIECAAAECBAgQIECAAAECBAgQIECggoCApAKiIQgQIECAAAECBAgQIECAAAECBAgQIECAAIG+BAQkffXLbAkQIECAAAECBAgQIECAAAECBAgQIECAAIEKAgKSCoiGIECAAAECBAgQIECAAAECBAgQIECAAAECBPoSEJD01S+zJUCAAAECBAgQIECAAAECBAgQIECAAAECBCoICEgqIBqCAAECBAgQIECAAAECBAgQIECAAAECBAgQ6EtAQNJXv8yWAAECBAgQIECAAAECBAgQIECAAAECBAgQqCDwf4XY4a9MRFL6AAAAAElFTkSuQmCC	t
167	2025-04-07 22:26:28.910185	2025-04-07 22:37:05.810116	\N	\N	t	\N	 [R] Hora entrada ajustada de 22:26 a 00:26	2025-04-07 22:26:29.138138	2025-04-07 22:37:57.91118	47	8	data:image/png;base64,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Y05GESBAgAABAgQIJBUQiJM2VlkECBAgQIAAAQIxAYE45mQUAQIECBAgQIBAUgGBOGljlUWAAAECBAgQIBATEIhjTkYRIECAAAECBAgkFRCIkzZWWQQIECBAgAABAjEBgTjmZBQBAgQIECBAgEBSAYE4aWOVRYAAAQIECBAgEBMQiGNORhEgQIAAAQIECCQVEIhihqM+AAAFWUlEQVSTNlZZBAgQIECAAAECMQGBOOZkFAECBAgQIECAQFIBgThpY5VFgAABAgQIECAQExCIY05GESBAgAABAgQIJBUQiJM2VlkECBAgQIAAAQIxAYE45mQUAQIECBAgQIBAUgGBOGljlUWAAAECBAgQIBATEIhjTkYRIECAAAECBAgkFRCIkzZWWQQIECBAgAABAjEBgTjmZBQBAgQIECBAgEBSAYE4aWOVRYAAAQIECBAgEBMQiGNORhEgQIAAAQIECCQVEIiTNlZZBAgQIECAAAECMQGBOOZkFAECBAgQIECAQFIBgThpY5VFgAABAgQIECAQExCIY05GESBAgAABAgQIJBUQiJM2VlkECBAgQIAAAQIxAYE45mQUAQIECBAgQIBAUgGBOGljlUWAAAECBAgQIBATEIhjTkYRIECAAAECBAgkFRCIkzZWWQQIECBAgAABAjEBgTjmZBQBAgQIECBAgEBSAYE4aWOVRYAAAQIECBAgEBMQiGNORhEgQIAAAQIECCQVEIiTNlZZBAgQIECAAAECMQGBOOZkFAECBAgQIECAQFIBgThpY5VFgAABAgQIECAQExCIY05GESBAgAABAgQIJBUQiJM2VlkECBAgQIAAAQIxAYE45mQUAQIECBAgQIBAUgGBOGljlUWAAAECBAgQIBATEIhjTkYRIECAAAECBAgkFRCIkzZWWQQIECBAgAABAjEBgTjmZBQBAgQIECBAgEBSAYE4aWOVRYAAAQIECBAgEBMQiGNORhEgQIAAAQIECCQVEIiTNlZZBAgQIECAAAECMQGBOOZkFAECBAgQIECAQFIBgThpY5VFgAABAgQIECAQExCIY05GESBAgAABAgQIJBUQiJM2VlkECBAgQIAAAQIxAYE45mQUAQIECBAgQIBAUgGBOGljlUWAAAECBAgQIBATEIhjTkYRIECAAAECBAgkFRCIkzZWWQQIECBAgAABAjEBgTjmZBQBAgQIECBAgEBSAYE4aWOVRYAAAQIECBAgEBMQiGNORhEgQIAAAQIECCQVEIiTNlZZBAgQIECAAAECMQGBOOZkFAECBAgQIECAQFIBgThpY5VFgAABAgQIECAQExCIY05GESBAgAABAgQIJBUQiJM2VlkECBAgQIAAAQIxAYE45mQUAQIECBAgQIBAUgGBOGljlUWAAAECBAgQIBATEIhjTkYRIECAAAECBAgkFRCIkzZWWQQIECBAgAABAjEBgTjmZBQBAgQIECBAgEBSAYE4aWOVRYAAAQIECBAgEBMQiGNORhEgQIAAAQIECCQVEIiTNlZZBAgQIECAAAECMQGBOOZkFAECBAgQIECAQFIBgThpY5VFgAABAgQIECAQExCIY05GESBAgAABAgQIJBUQiJM2VlkECBAgQIAAAQIxAYE45mQUAQIECBAgQIBAUgGBOGljlUWAAAECBAgQIBATEIhjTkYRIECAAAECBAgkFRCIkzZWWQQIECBAgAABAjEBgTjmZBQBAgQIECBAgEBSAYE4aWOVRYAAAQIECBAgEBMQiGNORhEgQIAAAQIECCQVEIiTNlZZBAgQIECAAAECMQGBOOZkFAECBAgQIECAQFIBgThpY5VFgAABAgQIECAQExCIY05GESBAgAABAgQIJBUQiJM2VlkECBAgQIAAAQIxAYE45mQUAQIECBAgQIBAUgGBOGljlUWAAAECBAgQIBATEIhjTkYRIECAAAECBAgkFRCIkzZWWQQIECBAgAABAjEBgTjmZBQBAgQIECBAgEBSAYE4aWOVRYAAAQIECBAgEBMQiGNORhEgQIAAAQIECCQV+B+kSu2vQz4qywAAAABJRU5ErkJggg==	t
158	2025-04-07 21:10:00.645274	2025-04-07 21:10:43.703463	\N	\N	t	\N	 [R] Hora entrada ajustada de 21:10 a 23:10	2025-04-07 21:10:00.89094	2025-04-07 21:10:58.12701	46	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkgAAAGQCAYAAADlQuzyAAAAAXNSR0IArs4c6QAAIABJREFUeF7t3Y3R5MQRBmARgckAQiCDsyMwGdghOIMPIiAFp+AI7MvAIUAEJgTfUDtVQuyPpFVLLfVzVVf3w+5o+uk+7mrfb6SvBt8IECBAgAABAgQIECBAgAABAgQIECBAgAABAsUEvipWr3IJECBAgAABAgQIECBAgAABAgQIECBAgAABAoOAxBAQIECAAAECBAgQIECAAAECBAgQIECAAAEC5QQEJOVarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgXICApJyLVcwAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxAwQIECBAgAABAgQIECBAgAABAgQIECBAgEA5AQFJuZYrmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAECBAgQIECAAAECBAgQIECAAAECBAgQIECgnICApFzLFUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUE5AQFKu5QomQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCRmgAABAgQIECBAgAABAgQIECBAgAABAgQIECgnICAp13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISM0CAAAECBAgQIECAAAECBAgQIECAAAECBAiUExCQlGu5ggkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiRkgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEygkISMq1XMEECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQMECBAgAABAgQIECBAgAABAgQIECBAgAABAuUEBCTlWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiBggQIECAAAECBAgQIECAAAECBAgQIECAAIFyAgKSci1XMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAOQEBSbmWK5gAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgBAgQIECBAgAABAgQIECBAgAABAgQIECBAoJyAgKRcyxVMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAAECBAgQIECAAAECBAgQIECAAAECBAgQIFBOQEBSruUKJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkZoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJyAgKddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEjNAgAABAgQIECBAgAABAgQIECBAgAABAgQIlBMQkJRruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBMoJCEjKtVzBBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLlBAQk5VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBcgICknItVzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEDBAgQIECAAAECBAgQIECAAAECBAgQIECAQDkBAUm5liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCcgICkXMsVTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAABAgQIECBAgAABAgQIECBAgAABAgQIECBQTkBAUq7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQKCcgICnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECJQTEJCUa7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTKCQhIyrVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAEC5QQEJOVarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgXICApJyLVcwAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxAwQIECBAgAABAgQIECBAgAABAgQIECBAgEA5AQFJuZYrmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAECBAgQIECAAAECBAgQIECAAAECBAgQIECgnICApFzLFUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUE5AQFKu5QomQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCRmgAABAgQIECBAgAABAgQIECBAgAABAgQIECgnICAp13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISM0CAAAECBAgQIECAAAECBAgQIECAAAECBAiUExCQlGu5ggkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiRkgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEygkISMq1XMEECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQMECBAgAABAgQIECBAgAABAgQIECBAgAABAuUEBCTlWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiBggQIECAAAECBAgQIECAAAECBAgQIECAAIFyAgKSci1XMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAOQEBSbmWK5gAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgBAgQIECBAgAABAgQIECBAgAABAgQIECBAoJyAgKRcyxVMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAAECBAgQIECAAAECBAgQIECAAAECBAgQIFBOQEBSruUKJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkZoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJyAgKddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEjNAgAABAgQIECBAgAABAgQIECBAgAABAgQIlBMQkJRruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBMoJCEjKtVzBBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLlBAQk5VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBcgICknItVzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEDBAgQIECAAAECBAgQIECAAAECBAgQIECAQDkBAUm5liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCcgICkXMsVTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAABAgQIECBAgAABAgQIECBAgAABAgQIECBQTkBAUq7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQKCcgICnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECJQTEJCUa7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTKCQhIyrVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAEC5QQEJOVarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgXICApJyLVcwAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxAwQIECBAgAABAgQIECBAgAABAgQIECBAgEA5AQFJuZYrmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAECBAgQIECAAAECBAgQIECAAAECBAgQIECgnICApFzLFUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUE5AQFKu5QomQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCRmgAABAgQIECBAgAABAgQIECBAgAABAgQIECgnICAp13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISM0CAAAECBAgQIECAAAECBAgQIECAAAECBAiUExCQlGu5ggkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiRkgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEygkISMq1XMEECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQMECBAgAABAgQIECBAgAABAgQIECBAgAABAuUEBCTlWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiBggQIECAAAECBAgQIECAAAECBAgQIECAAIFyAgKSci1XMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAOQEBSbmWK5gAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgBAgQIECBAgAABAgQIECBAgAABAgQIECBAoJyAgKRcyxVMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAAECBAgQIECAAAECBAgQIECAAAECBAgQIFBOQEBSruUKJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkZoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJyAgKddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEjNAgAABAgQIECBAgAABAgQIECBAgAABAgQIlBMQkJRruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBMoJCEjKtVzBBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLlBAQk5VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBcgICknItVzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEDBAgQIECAAAECBAgQIECAAAECBAgQIECAQDkBAUm5liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCcgICkXMsVTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAABAgQIECBAgAABAgQIECBAgAABAgQIECBQTkBAUq7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQKCcgICnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECJQTEJCUa7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTKCQhIyrVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAEC5QQEJOVarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgXICApJyLVcwAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxAwQIECBAgAABAgQIECBAgAABAgQIECBAgEA5AQFJuZYrmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAECBAgQIECAAAECBAgQIECAAAECBAgQIECgnICApFzLFUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUE5AQFKu5QomQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCRmgAABAgQIECBAgAABAgQIECBAgAABAgQIECgnICAp13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISM0CAAAECBAgQIECAAAECBAgQIECAAAECBAiUExCQlGu5ggkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiRkgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEygkISMq1XMEECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQMECBAgAABAgQIECBAgAABAgQIECBAgAABAuUEBCTlWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiBggQIECAAAECBAgQIECAAAECBAgQIECAAIFyAgKSci1XMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAOQEBSbmWK5gAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgBAgQIECBAgAABAgQIECBAgAABAgQIECBAoJyAgKRcyxVMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAAECBAgQIECAAAECBAgQIECAAAECBAgQIFBOQEBSruUKJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkZoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJyAgKddyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEjNAgAABAgQIECBAgAABAgQIECBAgAABAgQIlBMQkJRruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBMoJCEjKtVzBBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLlBAQk5VquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBcgICknItVzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEDBAgQIECAAAECBAgQIECAAAECBAgQIECAQDkBAUm5liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCcgICkXMsVTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAABAgQIECBAgAABAgQIECBAgAABAgQIECBQTkBAUq7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQKCcgICnXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECJQTEJCUa7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTKCQhIyrVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAEC5QQEJOVarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgXICApJyLVcwAQIECBAgQIAAAQIEZgv8+fbK74Zh+H4Yhv/cfv1pGIbPs1f5/Qv7Gv13p79euay3ESBAgAABAgQIEFgmICBZ5uXVBAgQIECAAAECBAgQOKNADzra3v8+DEMLOH69fb9Xz/j1e9U7Dkpa+PLt7fv496fBTPv1Ft9ehT1CnS2UrUGAAAECBAgQSCYgIEnWENshQIAAAQIECBAgQIDAl5Ma44BiGlbcCwXaCY+vRyc8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ECBAgAABAgQI5BMQkOTriR0RIECAAAECBAgQIECAAAECBAgQIECAAAECwQICkmBgyxMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQL5BAQk+XpiRwQIECBAgAABAgQIECBAgAABAgQIECBAgECwgIAkGNjyBAgQIECAAAECBAgQIECAAAECBAgQIECAQD4BAUm+ntgRAQIECBAgQIAAAQIECBAgQIAAAQIECBAgECwgIAkGtjwBAgQIECBAgAABAgQIECBAgAABAgQIECCQT0BAkq8ndkSAAAECBAgQIECAAAECBAgQIECAAAECBAgECwhIgoEtT4AAAQIECBAgQIAAAQIECBAgQIAAAQIECOQTEJDk64kdESBAgAABAgQIECBAgAABAgQIECBAgAABAsECApJgYMsTIECAAAECBAgQIECAAAECBAgQIECAAAEC+QQEJPl6YkcECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAsICAJBjY8gQIECBAgAABAgQIECBAgAABAgQIECBAgEA+AQFJvp7YEQECBAgQIECAAAECBAgQIECAAAECBAgQIBAsICAJBrY8AQIECBAgQIAAAQIECBAgQIAAAQIECBAgkE9AQJKvJ3ZEgAABAgQIECBAgAABAgQIECBAgAABAgQIBAsISIKBLU+AAAECBAgQIECAAAECBAgQIECAAAECBAjkExCQ5OuJHREgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLBAgKSYGDLEyBAgAABAgQIECBAgAABAgQIECBAgAABAvkEBCT5emJHBAgQIECAAAECBAgQIECAAAECBAgQIECAQLCAgCQY2PIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAPgEBSb6e2BEBAgQIECBAgAABAgQIECBAgAABAgQIECAQLCAgCQa2PAECBAgQIECAAAECBAgQIECAAAECBAgQIJBPQECSryd2RIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAQLCEiCgS1PgAABAgQIECBAgAABAgQIECBAgAABAgQI5BMQkOTriR0RIECAAAECBAgQIECAAAECBAgQIECAAAECwQICkmBgyxMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQL5BAQk+XpiRwQIECBAgAABAgQIECBAgAABAgQIECBAgECwgIAkGNjyBAgQIECAAAECBAgQIECAAAECBAgQIECAQD4BAUm+ntgRAQIECBAgQIAAAQIECBAgQIAAAQIECBAgECwgIAkGtjwBAgQIECBAgAABAgQIECBAgAABAgQIECCQT0BAkq8ndkSAAAECBAgQIECAAAECBAgQIECAAAECBAgECwhIgoEtT4AAAQIECBAgQIAAAQIECBAgQIAAAQIECOQTEJDk64kdESBAgAABAgQIECBAgAABAgQIECBAgAABAsECApJgYMsTIECAAAECBAgQIECAAAECBAgQIECAAAEC+QQEJPl6YkcECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAsICAJBjY8gQIECBAgAABAgQIECBAgAABAgQIECBAgEA+AQFJvp7YEQECBAgQIECAAAECBAgQIECAAAECBAgQIBAsICAJBrY8AQIECBAgQIAAAQIECBAgQIAAAQIECBAgkE9AQJKvJ3ZEgAABAgQIECBAgAABAgQIECBAgAABAgQIBAsISIKBLU+AAAECBAgQIECAAAECBAgQIECAAAECBAjkExCQ5OuJHREgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLBAgKSYGDLEyBAgAABAgQIECBAgAABAgQIECBAgAABAvkEBCT5emJHBAgQIECAAAECBAgQIECAAAECBAgQIECAQLCAgCQY2PIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAPgEBSb6e2BEBAgQIECBAgAABAgQIECBAgAABAgQIECAQLCAgCQa2PAECBAgQIECAAAECBAgQIECAAAECBAgQIJBPQECSryd2RIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAQLCEiCgS1PgAABAgQIECBAgAABAgQIECBAgAABAgQI5BMQkOTriR0RIECAAAECBAgQIECAAAECBAgQIECAAAECwQICkmBgyxMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQL5BAQk+XpiRwQIECBAgAABAgQIECBAgAABAgQIECBAgECwgIAkGNjyBAgQIECAAAECBAgQIECAAAECBAgQIECAQD4BAUm+ntgRAQIECBAgQIAAAQIECBAgQIAAAQIECBAgECwgIAkGtjwBAgQIECBAgAABAgQIECBAgAABAgQIECCQT0BAkq8ndkSAAAECBAgQIECAAAECBAgQIECAAAECBAgECwhIgoEtT4AAAQIECBAgQIAAAQIECBAgQIAAAQIECOQTEJDk64kdESBAgAABAgQIECBAgAABAgQIECBAgAABAsECApJgYMsTIECAAAECBAgQIECAAAECBAgQIECAAAEC+QQEJPl6YkcECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAsICAJBjY8gQIECBAgAABAgQIECBAgAABAgQIECBAgEA+AQFJvp7YEQECBAgQIECAAAECBAgQIECAAAECBAgQIBAsICAJBrY8AQIECBAgQIAAAQIECBAgQIAAAQIECBAgkE9AQJKvJ3ZEgAABAgQIECBAgAABAgQIECBAgAABAgQIBAsISIKBLU+AAAECBAgQIECAAAECBAgQIECAAAECBAjkExCQ5OuJHREgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLBAgKSYGDLEyBAgAABAgQIECBAgAABAgQIECBAgAABAvkEBCT5emJHBAgQIECAAAECBAgQIECAAAECBAgQIECAQLCAgCQY2PIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAPgEBSb6e2BEBAgQIECBAgAABAgQIECBAgAABAgQIECAQLCAgCQa2PAECBAgQIECAAAECBAgQIECAAAECBAgQIJBPQECSryd2RIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAQLCEiCgS1PgAABAgQIECBAgAABAgQIECBAgAABAgQI5BMQkOTriR0RIECAAAECBAgQIECAAAECBAgQIECAAAECwQICkmBgyxMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQL5BAQk+XpiRwQIECBAgAABAgQIECBAgAABAgQIECBAgECwgIAkGNjyBAgQIECAAAECBAgQIECAAAECBAgQIECAQD4BAUm+ntgRAQIECBAgQIAAAQIECBAgQIAAAQIECBAgECwgIAkGtjwBAgQIECBAgAABAgQIECBAgAABAgQIECCQT0BAkq8ndkSAAAECBAgQIECAAAECBAgQIECAAAECBAgECwhIgoEtT4AAAQIECBAgQIAAAQIECBAgQIAAAQIECOQTEJDk64kdESBAgAABAgQIECBAgAABAgQIECBAgAABAsECApJgYMsTIECAAAECBAgQIECAAAECBAgQIECAAAEC+QQEJPl6YkcECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAsICAJBjY8gQIECBAgAABAgQIECBAgAABAgQIECBAgEA+AQFJvp7YEQECBAgQIECAAAECBAgQIECAAAECBAgQIBAsICAJBrY8AQIECBAgQIAAAQIECBAgQIAAAQIECBAgkE9AQJKvJ3ZEgAABAgQIECBAgAABAgQIECBAgAABAgQIBAsISIKBLU+AAAECBAgQIECAAAECBAgQIECAAAECBAjkExCQ5OuJHREgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLBAgKSYGDLEyBAgAABAgQIECBAgAABAgQIECBAgAABAvkEBCT5emJHBAgQIECAAAECBAgQIECAAAECBAgQIECAQLCAgCQY2PIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAPgEBSb6e2BEBAgQIECBAgAABAgQIECBAgAABAgQIECAQLCAgCQa2PAECBAgQIECAAAECBAgQIECAAAECBAgQIJBPQECSryd2RIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAQLCEiCgS1PgAABAgQIECBAgAABAgQIECBAgAABAgQI5BMQkOTriR0RIECAAAECBAgQIECAAAECBAgQIECAAAECwQICkmBgyxMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQL5BAQk+XpiRwQIECBAgAABAgQIECBAgAABAgQIECBAgECwgIAkGNjyBAgQIECAAAECBAgQIECAAAECBAgQIECAQD4BAUm+ntgRAQIECBAgQIAAAQIECBAgQIAAAQIECBAgECwgIAkGtjwBAgQIECBAgAABAgQIECBAgAABAgQIECCQT0BAkq8ndkSAAAECBAgQIECAAAECBAgQIECAAAECBAgECwhIgoEtT4AAAQIECBAgQIAAAQIECBAgQIAAAQIECOQTEJDk64kdESBAgAABAgQIECBAgAABAgQIECBAgAABAsECApJgYMsTIECAAAECBAgQIECAAAECBAgQIECAAAEC+QQEJPl6YkcECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAsICAJBjY8gQIECBAgAABAgQIECBAgAABAgQIECBAgEA+AQFJvp7YEQECBAgQIECAAAECBAgQIECAAAECBAgQIBAsICAJBrY8AQIECBAgQIAAAQIECBAgQIAAAQIECBAgkE9AQJKvJ3ZEgAABAgQIECBAgAABAgQIECBAgAABAgQIBAsISIKBLU+AAAECBAgQIECAAAECBAgQIECAAAECBAjkExCQ5OuJHREgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLBAgKSYGDLEyBAgAABAgQIECBAgAABAgQIECBAgAABAvkEBCT5emJHBAgQIECAAAECBAgQIECAAAECBAgQIECAQLCAgCQY2PIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAPgEBSb6e2BEBAgQIECBAgAABAgQIECBAgAABAgQIECAQLCAgCQa2PAECBAgQIECAAAECBAgQIECAAAECBAgQIJBP4P9hQdSgBhf/6QAAAABJRU5ErkJggg==	t
159	2025-04-07 21:29:28.36903	2025-04-07 21:29:50.575854	\N	\N	t	\N	 [R] Hora entrada ajustada de 21:29 a 23:29	2025-04-07 21:29:28.604542	2025-04-07 21:30:05.328916	46	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkgAAAGQCAYAAADlQuzyAAAAAXNSR0IArs4c6QAAIABJREFUeF7t3Y215MSZBuByBMYZEAIZjImAELAzgAiGjQAyMA6BCMYTgXEGbAaTATu159YeregflaTuLul9+hwOM4xa0vd8371z0dsq/al4ESBAgAABAgQIECBAgAABAgQIECBAgAABAgTCBP4UVq9yCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQJFQGIICBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgTgBAUlcyxVMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAAECBAgQIECAAAECBAgQIECAAAECBAgQIBAnICCJa7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTiBAQkcS1XMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAnICAJK7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQiBMQkMS1XMEECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQMECBAgAABAgQIECBAgAABAgQIECBAgAABAnECApK4liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCBOQEAS13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISM0CAAAECBAgQIECAAAECBAgQIECAAAECBAjECQhI4lquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBOAEBSVzLFUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgECcgIIlruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBOIEBCRxLVcwAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxAwQIECBAgAABAgQIECBAgAABAgQIECBAgECcgIAkruUKJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkZoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBCIExCQxLVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAECcQICkriWK5gAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgBAgQIECBAgAABAgQIECBAgAABAgQIECBAIE5AQBLXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECMQJCEjiWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiBggQIECAAAECBAgQIECAAAECBAgQIECAAIE4AQFJXMsVTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAABAgQIECBAgAABAgQIECBAgAABAgQIECAQJyAgiWu5ggkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiRkgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIE4gQEJHEtVzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEDBAgQIECAAAECBAgQIECAAAECBAgQIECAQJyAgCSu5QomQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCRmgAABAgQIECBAgAABAgQIECBAgAABAgQIEIgTEJDEtVzBBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQJxAgKSuJYrmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgTkBAEtdyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEjNAgAABAgQIECBAgAABAgQIECBAgAABAgQIxAkISOJarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgTgBAUlcyxVMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAAECBAgQIECAAAECBAgQIECAAAECBAgQIBAnICCJa7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTiBAQkcS1XMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAnICAJK7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQiBMQkMS1XMEECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQMECBAgAABAgQIECBAgAABAgQIECBAgAABAnECApK4liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCBOQEAS13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISM0CAAAECBAgQIECAAAECBAgQIECAAAECBAjECQhI4lquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBOAEBSVzLFUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgECcgIIlruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBOIEBCRxLVcwAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxAwQIECBAgAABAgQIECBAgAABAgQIECBAgECcgIAkruUKJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkZoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBCIExCQxLVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAECcQICkriWK5gAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgBAgQIECBAgAABAgQIECBAgAABAgQIECBAIE5AQBLXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECMQJCEjiWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiBggQIECAAAECBAgQIECAAAECBAgQIECAAIE4AQFJXMsVTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAABAgQIECBAgAABAgQIECBAgAABAgQIECAQJyAgiWu5ggkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiRkgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIE4gQEJHEtVzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEDBAgQIECAAAECBAgQIECAAAECBAgQIECAQJyAgCSu5QomQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCRmgAABAgQIECBAgAABAgQIECBAgAABAgQIEIgTEJDEtVzBBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQJxAgKSuJYrmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgTkBAEtdyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEjNAgAABAgQIECBAgAABAgQIECBAgAABAgQIxAkISOJarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgTgBAUlcyxVMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAAECBAgQIECAAAECBAgQIECAAAECBAgQIBAnICCJa7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTiBAQkcS1XMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAnICAJK7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQiBMQkMS1XMEECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQMECBAgAABAgQIECBAgAABAgQIECBAgAABAnECApK4liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCBOQEAS13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISM0CAAAECBAgQIECAAAECBAgQIECAAAECBAjECQhI4lquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBOAEBSVzLFUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgECcgIIlruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBOIEBCRxLVcwAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxAwQIECBAgAABAgQIECBAgAABAgQIECBAgECcgIAkruUKJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkZoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBCIExCQxLVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAECcQICkriWK5gAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgBAgQIECBAgAABAgQIECBAgAABAgQIECBAIE5AQBLXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAgccJfFdKeV9K+U8p5a+PO4w9EyBAgAABAgQIECBAgAABAgQIECDQKyAg6RWzPQECBJYJ/KuU8m626fellJ+Wvd1WBAgQIECAAAECBAgQIECAAAECBAg8UkBA8khd+yZAIFng9wvFfyql/CUZRe0ECBAgQIAAAQIECBAgQIAAAQIERhEQkIzSCedBgMCZBH4upXx7oaCPlto6U5vVQoAAAQIECBAgQIAAAQIECBAgcGQBAcmRu+fcCRAYVeCHt2ePzM9PQDJqx5wXAQIECBAgQIAAAQIECBAgQIBAnICAJK7lCiZA4AkC1wKSrz/fQVKfTeJFgAABAgQIECBAgAABAgQIECBAgMCLBQQkL26AwxMgcEqBD1eW0vI995TtVhQBAgQIEIgU+Otb1f8opXxZSvmvtw+C+DBI5DgomgABAgQIECBwTAEX647ZN2dNgMDYApce0F7P2Pfcsfvm7AgQIECAAIHLAjUMeT/7oxaQzN/h5x1TRIAAAQIECBAgcBgBP7weplVOlACBAwkISA7ULKdKgAABAgQI/EGghR81FLkWhFxjs6SogSJAgAABAgQIEDiMgIDkMK1yogQIHEhAQHKgZjlVAgQIECBA4P8E6nPU3q0IRaaEdamtuh8vAgQIECBAgAAB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FUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgECcgIIlruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBOIEBCRxLVcwAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxAwQIECBAgAABAgQIECBAgAABAgQIECBAgECcgIAkruUKJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkZoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBCIExCQxLVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAECcQICkriWK5gAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgBAgQIECBAgAABAgQIECBAgAABAgQIECBAIE5AQBLXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECMQJCEjiWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiBggQIECAAAECBAgQIECAAAECBAgQIECAAIE4AQFJXMsVTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAABAgQIECBAgAABAgQIECBAgAABAgQIECAQJyAgiWu5ggkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiRkgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIE4gQEJHEtVzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEDBAgQIECAAAECBAgQIECAAAECBAgQIECAQJyAgCSu5QomQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCRmgAABAgQIECBAgAABAgQIECBAgAABAgQIEIgTEJDEtVzBBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQJxAgKSuJYrmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgTkBAEtdyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEjNAgAABAgQIECBAgAABAgQIECBAgAABAgQIxAkISOJarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgTgBAUlcyxVMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAAECBAgQIECAAAECBAgQIECAAAECBAgQIBAnICCJa7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTiBAQkcS1XMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAnICAJK7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQiBMQkMS1XMEECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQMECBAgAABAgQIECBAgAABAgQIECBAgAABAnECApK4liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCBOQEAS13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISM0CAAAECBAgQIECAAAECBAgQIECAAAECBAjECQhI4lquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBOAEBSVzLFUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgECcgIIlruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBOIEBCRxLVcwAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxAwQIECBAgAABAgQIECBAgAABAgQIECBAgECcgIAkruUKJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkZoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBCIExCQxLVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAECcQICkriWK5gAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgBAgQIECBAgAABAgQIECBAgAABAgQIECBAIE5AQBLXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECMQJCEjiWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiBggQIECAAAECBAgQIECAAAECBAgQIECAAIE4AQFJXMsVTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAABAgQIECBAgAABAgQIECBAgAABAgQIECAQJyAgiWu5ggkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiRkgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIE4gQEJHEtVzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEDBAgQIECAAAECBAgQIECAAAECBAgQIECAQJyAgCSu5QomQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCRmgAABAgQIECBAgAABAgQIECBAgAABAgQIEIgTEJDEtVzBBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQJxAgKSuJYrmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgTkBAEtdyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEjNAgAABAgQIECBAgAABAgQIECBAgAABAgQIxAkISOJarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgTgBAUlcyxVMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAAECBAgQIECAAAECBAgQIECAAAECBAgQIBAnICCJa7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTiBAQkcS1XMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAnICAJK7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQiBMQkMS1XMEECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQMECBAgAABAgQIECBAgAABAgQIECBAgAABAnECApK4liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCBOQEAS13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISM0CAAAECBAgQIECAAAECBAgQIECAAAECBAjECQhI4lquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBOAEBSVzLFUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgECcgIIlruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBOIEBCRxLVcwAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxAwQIECBAgAABAgQIECBAgAABAgQIECBAgECcgIAkruUKJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkZoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBCIExCQxLVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAECcQICkriWK5gAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgBAgQIECBAgAABAgQIECBAgAABAgQIECBAIE5AQBLXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECMQJCEjiWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiBggQIECAAAECBAgQIECAAAECBAgQIECAAIE4AQFJXMsVTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAABAgQIECBAgAABAgQIECBAgAABAgQIECAQJyAgiWu5ggkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiRkgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIE4gQEJHEtVzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEDBAgQIECAAAECBAgQIECAAAECBAgQIECAQJyAgCSu5QomQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCRmgAABAgQIECBAgAABAgQIECBAgAABAgQIEIgTEJDEtVzBBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQJxAgKSuJYrmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgTkBAEtdyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEjNAgAABAgQIECBAgAABAgQIECBAgAABAgQIxAkISOJarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgTgBAUlcyxVMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAAECBAgQIECAAAECBAgQIECAAAECBAgQIBAnICCJa7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTiBAQkcS1XMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAnICAJK7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQiBMQkMS1XMEECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQMECBAgAABAgQIECBAgAABAgQIECBAgAABAnECApK4liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCBOQEAS13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISM0CAAAECBAgQIECAAAECBAgQIECAAAECBAjECQhI4lquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBOAEBSVzLFUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgECcgIIlruYIJECBAgAABAgQIECBAgAABAgQIECBAgAABAYkZIECAAAECBAgQIECAAAECBAgQIECAAAECBOIEBCRxLVcwAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxAwQIECBAgAABAgQIECBAgAABAgQIECBAgECcgIAkruUKJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQkZoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBCIExCQxLVcwQQIECBAgAABAgQIECBAgAABAgQIECBAgICAxAwQIECAAAECBAgQIECAAAECBAgQIECAAAECcQICkriWK5gAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgBAgQIECBAgAABAgQIECBAgAABAgQIECBAIE5AQBLXcgUTIECAAAECBAgQIECAAAECBAgQIECAAAECAhIzQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECMQJCEjiWq5gAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiBggQIECAAAECBAgQIECAAAECBAgQIECAAIE4AQFJXMsVTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAABAgQIECBAgAABAgQIECBAgAABAgQIECAQJyAgiWu5ggkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiRkgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIE4gQEJHEtVzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEDBAgQIECAAAECBAgQIECAAAECBAgQIECAQJyAgCSu5QomQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCRmgAABAgQIECBAgAABAgQIECBAgAABAgQIEIgTEJDEtVzBBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEDBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQJxAgKSuJYrmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgTkBAEtdyBRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEjNAgAABAgQIECBAgAABAgQIECBAgAABAgQIxAkISOJarmACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgTgBAUlcyxVMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAAECBAgQIECAAAECBAgQIECAAAECBAgQIBAnICCJa7mCCRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJGSBAgAABAgQIECBAgAABAgQIECBAgAABAgTiBAQkcS1XMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAnICAJK7lCiZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJGaAAAECBAgQIECAAAECBAgQIECAAAECBAgQiBMQkMS1XMEECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQMECBAgAABAgQIECBAgAABAgQIECBAgAABAnECApK4liuYAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCBOQEAS13IFEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISM0CAAAECBAgQIECAAAECBAgQIECAAAECBAjECQhI4lquYAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYgYIECBAgAABAgQIECBAgAABAgQIECBAgACBOAEBSVzLFUyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgECcgIIlruYIJECBAgAABAgQIECBAgAABAgQIECBAgACB/wHmIT6vI75DkQAAAABJRU5ErkJggg==	t
168	2025-04-07 22:42:07.311635	2025-04-07 22:42:43.083059	\N	\N	t	\N	 [R] Hora entrada ajustada de 22:42 a 00:42	2025-04-07 22:42:07.534491	2025-04-07 22:42:58.381917	47	8	data:image/png;base64,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IECAgEBsDBAgQIAAAQIECIQWEIhDl1/nCRAgQIAAAQIEBGJjgAABAgQIECBAILSAQBy6/DpPgAABAgQIECAgEBsDBAgQIECAAAECoQUE4tDl13kCBAgQIECAAAGB2BggQIAAAQIECBAILSAQhy6/zhMgQIAAAQIECAjExgABAgQIECBAgEBoAYE4dPl1ngABAgQIECBAQCA2BggQIECAAAECBEILCMShy6/zBAgQIECAAAECArExQIAAAQIECBAgEFpAIA5dfp0nQIAAAQIECBAQiI0BAgQIECBAgACB0AICcejy6zwBAgQIECBAgIBAbAwQIECAAAECBAiEFhCIQ5df5wkQIECAAAECBARiY4AAAQIECBAgQCC0gEAcuvw6T4AAAQIECBAgIBAbAwQIECBAgAABAqEFBOLQ5dd5AgQIECBAgAABgdgYIECAAAECBAgQCC0gEIcuv84TIECAAAECBAgIxMYAAQIECBAgQIBAaAGBOHT5dZ4AAQIECBAgQEAgNgYIECBAgAABAgRCCwjEocuv8wQIECBAgAABAgKxMUCAAAECBAgQIBBaQCAOXX6dJ0CAAAECBAgQEIiNAQIECBAgQIAAgdACAnHo8us8AQIECBAgQICAQGwMECBAgAABAgQIhBYQiEOXX+cJECBAgAABAgQEYmOAAAECBAgQIEAgtIBAHLr8Ok+AAAECBAgQICAQGwMECBAgQIAAAQKhBQTi0OXXeQIECBAgQIAAAYHYGCBAgAABAgQIEAgtIBCHLr/OEyBAgAABAgQICMTGAAECBAgQIECAQGgBgTh0+XWeAAECBAgQIEBAIDYGCBAgQIAAAQIEQgsIxKHLr/MECBAgQIAAAQICsTFAgAABAgQIECAQWkAgDl1+nSdAgAABAgQIEBCIjQECBAgQIECAAIHQAgJx6PLrPAECBAgQIECAgEBsDBAgQIAAAQIECIQWEIhDl1/nCRAgQIAAAQIEBGJjgAABAgQIECBAILSAQBy6/DpPgAABAgQIECAgEBsDBAgQIECAAAECoQUE4tDl13kCBAgQIECAAAGB2BggQIAAAQIECBAILSAQhy6/zhMgQIAAAQIECAjExgABAgQIECBAgEBoAYE4dPl1ngABAgQIECBAQCA2BggQIECAAAECBEILCMShy6/zBAgQIECAAAECArExQIAAAQIECBAgEFpAIA5dfp0nQIAAAQIECBAQiI0BAgQIECBAgACB0AICcejy6zwBAgQIECBAgIBAbAwQIECAAAECBAiEFhCIQ5df5wkQIECAAAECBARiY4AAAQIECBAgQCC0gEAcuvw6T4AAAQIECBAgIBAbAwQIECBAgAABAqEFBOLQ5dd5AgQIECBAgAABgdgYIECAAAECBAgQCC0gEIcuv84TIECAAAECBAgIxMYAAQIECBAgQIBAaAGBOHT5dZ4AAQIECBAgQOD/AxGTCBxvSyUqAAAAAElFTkSuQmCC	t
160	2025-04-07 21:41:05.995351	2025-04-07 21:46:10.366643	\N	\N	t	\N	 [R] Hora entrada ajustada de 21:41 a 23:41	2025-04-07 21:41:06.226525	2025-04-07 21:46:23.928215	46	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkgAAAGQCAYAAADlQuzyAAAAAXNSR0IArs4c6QAAIABJREFUeF7t3YvVHUV2NuByBhMCkwGOQCiCPwSYCGxHoCGCcQaDIhFEgDMwGXgy4P826EBz6PvpS+2qp9fCwqO+VD270PrOebW7/q04CBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQKdCfxbZ/M1XQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAEZBYBAQIECBAgAABAgQIECBAgAABAgQIECBAgEB3AgKS7kpuwgQIECBAgAABAgQIECBAgAABAgQIECBAgICAxBogQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEuhMQkHRXchMmQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCTWAAECBAgQIECAAAECBAgQIECAAAECBAgQINCdgICku5KbMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgsQYIECBAgAABAgQIECBAgAABAgQIECBAgACB7gQEJN2V3IQJECBAgAABAgQIECBAgAABAgQIECBAgAABAYk1QIAAAQIECBAgQIAAAQIECBAgQIAAAQIECHQnICDpruQmTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIrAECBAgQIECAAAECBAgQIECAAAECBAgQIECgOwEBSXclN2ECBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGINECBAgAABAgQIECBAgAABAgQIECBAgAABAt0JCEi6K7kJEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISa4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBDoTkBA0l3JTZgAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkFgDBAgQIECAAAECBAgQIECAAAECBAgQIECAQHcCApLuSm7CBAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEGiBAgAABAgQIECBAgAABAgQIECBAgAABAgS6ExCQdFdyEyZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJNYAAQIECBAgQIAAAQIECBAgQIAAAQIECBAg0J2AgKS7kpswAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICCxBggQIECAAAECBAgQIECAAAECBAgQIECAAIHuBAQk3ZXchAkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiTVAgAABAgQIECBAgAABAgQIECBAgAABAgQIdCcgIOmu5CZMgAABAgQIECBAgAABAgQIECBAgAABAgQICEisAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKA7AQFJdyU3YQIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYg0QIECAAAECBAgQIECAAAECBAgQIECAAAEC3QkISLoruQkTIECAAAECBAgQIECAAAECBAgQIECAAAECAhJrgAABAgQIECBAgAABAgQIECBAgAABAgQIEOhOQEDSXclNmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQWAMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAdwICku5KbsIECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQaIECAAAECBAgQIECAAAECBAgQIECAAAECBLoTEJB0V3ITJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQk1gABAgQIECBAgAABAgQIECBAgAABAgQIECDQnYCApLuSmzABAgQIECBAgAABAgQIECBAgAABAgQIECAgILEGCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAge4EBCTdldyECRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJNUCAAAECBAgQIECAAAECBAgQIECAAAECBAh0JyAg6a7kJkyAAAECBAgQIECAAAECBAgQIECAAAECBAgISKwBAgQIECBAgAABAgQIECBAgAABAgQIECBAoDsBAUl3JTdhAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiDRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLdCQhIuiu5CRMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEmuAAAECBAgQIECAAAECBAgQIECAAAECBAgQ6E5AQNJdyU2YAAECBAgQIECAAAECBAgQIECAAAECBAgQEJBYAwQIECBAgAABAgQIECBAgAABAgQIECBAgEB3AgKS7kpuwgQIECBAgAABAgReFvjq8x3i13ef//2Hz79+X0qJfxwECBAgQIAAAQIECBCoWkBAUnV5DI4AAQIECBAgQIDArQJjQcjjf1sa2LdvJ/x96SS/T4AAAQIECBAgQIAAgbsEBCR3yXsuAQIE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BAgQIECAQNMCApKmy2tyBAgQIECAAIE/COgeWb8ghkHS46o7wpH1Iy5lKjSxyfoWRecSIECAAAECBAgQINCNgICkm1KbKAECBAgQIECgDAOS+NI89tFw/Flg7LVWtYcj6kiAAAECBAgQIECAAAECGwUEJBvBnE6AAAECBAgQSCzg9VrLxRsLR4RJy27OIECAAAECBAgQIECAQDoBAUm6khkwAQIECBAgQGCXgNdrLbMJR5aNnEGAAAECBAgQIECAAIFmBAQkzZTSRAgQIECAAAECswLDL/+9LurPVGPhSJwVryGzh4f/uAgQIECAAAECBAgQINCggICkwaKaEgECBAgQIEBgRMDrtaaXhXDEfzIECBAgQIAAAQIECBDoUEBA0mHRTZkAAQIECBDoTsDrtYQj3S16EyZAgAABAgQIECBAgMCSgIBkScjvEyBAgAABAgTyC+geGa+hzpH8a9sMCBAgQIAAAQIECBAgsFtAQLKbzoUECBAgQIAAgRQCX5VSIgh4HPYf+VViKhzhk2JZGyQBAgQIECBAgAABAgReFxCQvG7oDgQIECBAgACBmgW8XuvP1RGO1LxijY0AAQIECBAgQIAAAQIXCQhILoL2GAIECBAgQIDATQJer/VHeOHITQvRYwkQIECAAAECBAgQIFCbgICktooYDwECBAgQIEDgOAGv1/rd8tliqOy1WsetOXciQIAAAQIECBAgQIBAGgEBSZpSGSgBAgQIECBAYLOA12v9SiYc2bx0XECAAAECBAgQIECAAIH2BQQk7dfYDAkQIECAAIF+BbxeSzjS7+o3cwIECBAgQIAAAQIECCwICEgsEQIECBAgQIBAmwJeryUcaXNlmxUBAgQIECBAgAABAgQOEhCQHATpNgQIECBAgACBygR6f72W12pVtiANhwABAgQIECBAgAABArUJCEhqq4jxECBAgAABAgSOEfj0ee+NuNv3pZT3x9w2xV2EIynKZJAECBAgQIAAAQIECBC4V0BAcq+/pxMgQIAAAQIEzhLodf+R586Zoe+3b/9P/L6DAAECBAgQIECAAAECBAgUAYlFQIAAAQIECBBoT+A5JIjukegiaf3QOdJ6hc2PAAECBAgQIECAAAECBwoISA7EdCsCBAgQIECAQCUCPe4/onOkksVnGAQIECBAgAABAgQIEMgiICDJUinjJECAAAECBAis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AQIECBDYKSAg2QnnMgIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCvgIAkb+2MnAABAgQIECBAgAABAgQIECBAgAABAgQIENgpICDZCecyAgQIECBAgAABAgQIECBAgAABAgQIECBAIK+AgCRv7YycAAECBAgQIECAAAECBAgQIECAAAECBAgQ2CkgINkJ5zICBAgQIECAAAECBAgQIECAAAECBAgQIEAgr4CAJG/tjJwAAQIECBAgQIAAAQIECBAgQIAAAQIECBDYKSAg2QnnMgIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCvgIAkb+2MnAABAgQIECBAgPTWYiAAAAbSSURBVAABAgQIECBAgAABAgQIENgpICDZCecyAgQIECBAgAABAgQIECBAgAABAgQIECBAIK+AgCRv7YycAAECBAgQIECAAAECBAgQIECAAAECBAgQ2CkgINkJ5zICBAgQIECAAAECBAgQIECAAAECBAgQIEAgr4CAJG/tjJwAAQIECBAgQIAAAQIECBAgQIAAAQIECBDYKSAg2QnnMgIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCvgIAkb+2MnAABAgQIECBAgAABAgQIECBAgAABAgQIENgpICDZCecyAgQIECBAgAABAgQIECBAgAABAgQIECBAIK+AgCRv7YycAAECBAgQIECAAAECBAgQIECAAAECBAgQ2CkgINkJ5zICBAgQIECAAAECBAgQIECAAAECBAgQIEAgr4CAJG/tjJwAAQIECBAgQIAAAQIECBAgQIAAAQIECBDYKSAg2QnnMgIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCvgIAkb+2MnAABAgQIECBAgAABAgQIECBAgAABAgQIENgpICDZCecyAgQIECBAgAABAgQIECBAgAABAgQIECBAIK+AgCRv7YycAAECBAgQIECAAAECBAgQIECAAAECBAgQ2CkgINkJ5zICBAgQIECAAAECBAgQIECAAAECBAgQIEAgr4CAJG/tjJwAAQIECBAgQIAAAQIECBAgQIAAAQIECBDYKSAg2QnnMgIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCvgIAkb+2MnAABAgQIECBAgAABAgQIECBAgAABAgQIENgpICDZCecyAgQIECBAgAABAgQIECBAgAABAgQIECBAIK+AgCRv7YycAAECBAgQIECAAAECBAgQIECAAAECBAgQ2CkgINkJ5zICBAgQIECAAAECBAgQIECAAAECBAgQIEAgr4CAJG/tjJwAAQIECBAgQIAAAQIECBAgQIAAAQIECBDYKSAg2QnnMgIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCvgIAkb+2MnAABAgQIECBAgAABAgQIECBAgAABAgQIENgpICDZCecyAgQIECBAgAABAgQIECBAgAABAgQIECBAIK+AgCRv7YycAAECBAgQIECAAAECBAgQIECAAAECBAgQ2CkgINkJ5zICBAgQIECAAAECBAgQIECAAAECBAgQIEAgr4CAJG/tjJwAAQIECBAgQIAAAQIECBAgQIAAAQIECBDYKSAg2QnnMgIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCvgIAkb+2MnAABAgQIECBAgAABAgQIECBAgAABAgQIENgpICDZCecyAgQIECBAgAABAgQIECBAgAABAgQIECBAIK+AgCRv7YycAAECBAgQIECAAAECBAgQIECAAAECBAgQ2CkgINkJ5zICBAgQIECAAAECBAgQIECAAAECBAgQIEAgr4CAJG/tjJwAAQIECBAgQIAAAQIECBAgQIAAAQIECBDYKSAg2QnnMgIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCvgIAkb+2MnAABAgQIECBAgAABAgQIECBAgAABAgQIENgpICDZCecyAgQIECBAgAABAgQIECBAgAABAgQIECBAIK+AgCRv7YycAAECBAgQIECAAAECBAgQIECAAAECBAgQ2CkgINkJ5zICBAgQIECAAAECBAgQIECAAAECBAgQIEAgr4CAJG/tjJwAAQIECBAgQIAAAQIECBAgQIAAAQIECBDYKSAg2QnnMgIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCvgIAkb+2MnAABAgQIECBAgAABAgQIECBAgAABAgQIENgpICDZCecyAgQIECBAgAABAgQIECBAgAABAgQIECBAIK+AgCRv7YycAAECBAgQIECAAAECBAgQIECAAAECBAgQ2CkgINkJ5zICBAgQIECAAAECBAgQIECAAAECBAgQIEAgr4CAJG/tjJwAAQIECBAgQIAAAQIECBAgQIAAAQIECBDYKSAg2QnnMgIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCvgIAkb+2MnAABAgQIECBAgAABAgQIECBAgAABAgQIENgpICDZCecyAgQIECBAgAABAgQIECBAgAABAgQIECBAIK+AgCRv7YycAAECBAgQIECAAAECBAgQIECAAAECBAgQ2CkgINkJ5zICBAgQIECAAAECBAgQIECAAAECBAgQIEAgr4CAJG/tjJwAAQIECBAgQIAAAQIECBAgQIAAAQIECBDYKSAg2QnnMgIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCvwP8HxExr3AyfDKgAAAAASUVORK5CYII=	t
161	2025-04-07 21:46:59.710881	2025-04-07 21:48:55.495403	\N	\N	t	\N	 [R] Hora entrada ajustada de 21:46 a 23:46	2025-04-07 21:46:59.940582	2025-04-07 21:49:06.403836	46	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkgAAAGQCAYAAADlQuzyAAAAAXNSR0IArs4c6QAAIABJREFUeF7t3d2xJLd5BmAoA2bgVQSmIlifK186BJIZrCPYdQRSBiZDYATrvfTdOgJuBlIGxwfiaWl2tv+n0f0BeLqKRYmnBw08H6ZqZt4C8IfkIkCAAAECBAgQIECAAAECBAgQIECAAAECBAh0JvCHzsZruAQIECBAgAABAgQIECBAgAABAgQIECBAgACBJCAxCQgQIECAAAECBAgQIECAAAECBAgQIECAAIHuBAQk3ZXcgAkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiTlAgAABAgQIECBAgAABAgQIECBAgAABAgQIdCcgIOmu5AZMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKA7AQFJdyU3YAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYg4QIECAAAECBAgQIECAAAECBAgQIECAAAEC3QkISLoruQETIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEOhOQEDSXckNmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAdwICku5KbsAECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQcIECAAAECBAgQIECAAAECBAgQIECAAAECBLoTEJB0V3IDJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQk5gABAgQIECBAgAABAgQIECBAgAABAgQIECDQnYCApLuSGzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEHCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAge4EBCTdldyACRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJOUCAAAECBAgQIECAAAECBAgQIECAAAECBAh0JyAg6a7kBkyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwBAgQIECBAgAABAgQIECBAgAABAgQIECBAoDsBAUl3JTdgAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiDhAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLdCQhIuiu5ARMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQ6E5AQNJdyQ2YAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAwQIECBAgAABAgQIECBAgAABAgQIECBAgEB3AgKS7kpuwAQIECBAgAABAgQIECBAgAABAgQIECBAgICAxBwgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEuhMQkHRXcgMmQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCTmAAECBAgQIECAAAECBAgQIECAAAECBAgQINCdgICku5IbMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQcIECBAgAABAgQIECBAgAABAgQIECBAgACB7gQEJN2V3IAJECBAgAABAgQIECBAgAABAgQIECBAgAABAYk5QIAAAQIECBAgQIAAAQIECBAgQIAAAQIECHQnICDpruQGTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAECBAgQIECAAAECBAgQIECAAAECBAgQIECgOwEBSXclN2ACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIOECBAgAABAgQIECBAgAABAgQIECBAgAABAt0JCEi6K7kBEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBDoTkBA0l3JDZgAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgDBAgQIECAAAECBAgQIECAAAECBAgQIECAQHcCApLuSm7ABAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEHCBAgAABAgQIECBAgAABAgQIECBAgAABAgS6ExCQdFdyAyZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJOYAAQIECBAgQIAAAQIECBAgQIAAAQIECBAg0J2AgKS7khswAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxBwgQIECAAAECBAgQIECAAAECBAgQIECAAIHuBAQk3ZXcgAkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiTlAgAABAgQIECBAgAABAgQIECBAgAABAgQIdCcgIOmu5AZMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKA7AQFJdyU3YAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYg4QIECAAAECBAgQIECAAAECBAgQIECAAAEC3QkISLoruQETIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEOhOQEDSXckNmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAdwICku5KbsAECBAgQIAAAQIECBAgQIAAAQIECBAgQICAgMQcIECAAAECBAgQIECAAAECBAgQIECAAAECBLoTEJB0V3IDJkCAAAECBAgQIECAAAECBAgQIECAAAECBAQk5gABAgQIECBAgAABAgQIECBAgAABAgQIECDQnYCApLuSGzABAgQIECBAgAABAgQIECBAgAABAgQIECAgIDEHCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAge4EBCTdldyACRAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQGJOUCAAAECBAgQIECAAAECBAgQIECAAAECBAh0JyAg6a7kBkyAAAECBAgQIECAAAECBAgQIECAAAECBAgISMwBAgQIECBAgAABAgQIECBAgAABAgQIECBAoDsBAUl3JTdgAgQIECBAgAABAgQIECBAgAABAgQIECBAQEBiDhAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQLdCQhIuiu5ARMgQIAAAQIECBAgQIAAAQIECBAgQIAAAQICEnOAAAECBAgQIECAAAECBAgQIECAAAECBAgQ6E5AQNJdyQ2YAAECBAgQIECAAAECBAgQIECAAAECBAgQEJCYAwQIECBAgAABAgQIECBAgAABAgQIECBAgEB3AgKS7kpuwAQIECBAgAABAgQIECBAgAABAgQIECBAgICAxBwgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEuhMQkHRXcgMmQIAAAQIECBAgQIAAAQIECBAgQIAAAQIEBCTmAAECBAgQIECAAAECBAgQIECAAAECBAgQINCdgICku5IbMAECBAgQIECAAAECBAgQIECAAAECBAgQICAgMQcIECBAgAABAgQIECBAgAABAgQIECBAgACB7gQEJN2V3IAJECBAgAABAgQIECBAgAABAgQIECBAgAABAYk5QIAAAQIECBAgQIAAAQIECBAgQIAAAQIECHQnICDpruQGTIAAAQIECBAgQIAAAQIECBAgQIAAAQIECAhIzAECBAgQIECAAAECBAgQIECAAAECBAgQIECgOwEBSXclN2ACBAgQIECAAAECBAgQIECAAAECBAgQIEBAQGIOECBAgAABAgQIECBAgAABAgQIECBAgAABAt0JCEi6K7kBEyBAgAABAgQIECBAgAABAgQIECBAgAABAgISc4AAAQIECBAgQIAAAQIECBAgQIAAAQIECBDoTkBA0l3JDZgAAQIECBAgQIAAAQIECBAgQIAAAQIECBAQkJgDBAgQIECAAAECBAgQIECAAAECBAgQIECAQHcCApLuSm7ABAgQIECAAAECBAgQIECAAAECBAgQIECAgIDEHCBAgAABAgQIECBAgAABAgQIECBAgAABAgS6ExCQdFdyAyZAgAABAgQIECBAgAABAgQIECBAgAABAgQEJOYAAQIECBAgQIAAAQIECBAgQIAAAQIECBAg0J2AgKS7khswAQIECBAgQIAAAQIECBAgQIAAAQIECBAgICAxBwgQIECAAAECBAgQIECAAAECBAgQIECAAIHuBAQk3ZXcgAkQIECAAAECBAgQIECAAAECBAgQIECAAAEBiTlAgAABAgQIECBAgAABAgQIECBAgAABAgQIdCcgIOmu5AZMgAABAgQIECBAgAABAgQIECBAgAABAgQICEjMAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKA7AQFJdyU3YAIECBAgQIAAAQIECBAgQIAAAQIECBAgQEBAYg4QIECAAAECBAgQIECAAAECBAgQIECAAAEC3QkISLoruQETIECAAAECBAgQIECAAAECBAgQIECAAAECAhJzgAABAgQIECBAgAABAgQIECBAgAABAgQIEOhOQEDSXckNmAABAgQIECBAgAABAgQIECBAgAABAgQIEBCQmAMECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAdwICku5KbsAECBAgQIAAAQIECBAgsFHg317vz/9+e/Pa4b/PNfc/KaV83y8ppZ9f/nf+/y4CBAgQIECAAIEAAgKSAEXQBQIECBAgQIAAAQIECBAIJ5BDjfc3wchRHfycUvr1pbEPRzWoHQIECBAgQIAAgX0CApJ9bl5FgAAB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BAgQIECAAAECBEIL5BUPeTuoHJLcX37U31a6qdUjX1JKf9zWlLsJECBAgAABAgRKCwhISgtrnwABAgQIECBAgAABAnEFpn7Q//TS5fy3vHrEtU5gbmst373XGbqLAAECBAgQIHCqgA9pp3J7GAECBAgQIECAAAECBEII5NUiHyd6YtXIvhLZWmufm1cRIECAAAECBC4TEJBcRu/BBAgQIECAAAECBAgQuEQgByNj22nl1SJPl/So/odOmQqb6q+tERAgQIAAAQINCwhIGi6uoREgQIAAAQIECBAgQOBGYG7VSA5GbKe1b7pMba0lcNrn6VUECBAgQIAAgdMEBCSnUXsQAQIECBAgQIAAAQIELhOYWzWSVzkIR/aVxrkj+9y8igABAgQIECAQQkBAEqIMOkGAAAECBAgQIECAAIEiAs4aKcL690aFI+VstUyAAAECBAgQOEVAQHIKs4cQIECAAAECBAgQIEDgdIG5rZ+sGnmsHFMrcnKrtit7zNarCRAgQIAAAQKnCQhITqP2IAIECBAgQIAAAQIECJwiYNVIOeY5W+FIOXctEyBAgAABAgSKCAhIirBqlAABAgQIECBAgAABApcIOGukHPvcllrCkXLuWiZAgAABAgQIFBMQkBSj1TABAgQIECBAgAABAgROE8grG96/HLae/31/5e208o/7rv0Cc+FIPuDelmX7bb2SAAECBAgQIHCZgIDkMnoPJkCAAAECBAgQIECAwCECzho5hHG0kbngKb8ghyP5zBEXAQIECBAgQIBAhQICkgqLpssECBAgQIAAAQIECBB4XS1i1Ui5qbB03oiVOeXstUyAAAECBAgQOEVAQHIKs4cQIECAAAECBAgQIEDgUAGrRg7l/KYx542U9dU6AQIECBAgQCCEgIAkRBl0ggABAgQIECBAgAABAqsEnDWyimn3TbbU2k3nhQQIECBAgACB+gQEJPXVTI8JECBAgAABAgQIEOhT4OPEIewOCT9mPthS6xhHrRAgQIAAAQIEqhEQkFRTKh0lQIAAAQIECBAgQKBTAatGyhd+Knwanuy8kfI18AQCBAgQIECAwOkCApLTyT2QAAECBAgQIECAAAECqwWcNbKaateNa7bUyuFIXqXjIkCAAAECBAgQaExAQNJYQQ2HAAECBAgQIECAAIFmBOa21HpqZpTXDWTpIHarRq6rjScTIECA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GjkUGYKRLSKCkS1a7iVAgAABAgQIECBAIIyAgCRMKXSEAAECBAgQIECAwFcCZ4Uje1aLDB0tEdSYBgQIECBAgAABAgQIEDhFQEByCrOHECBAgAABAgQIENgkkEOLfCj7/XVkIPFIMGLVyKZyupkAAQIECBAgQIAAgYgCApKIVdEnAgQIECBAgACBngWmwpFs8ujn973baA31EIz0PDONnQABAgQIECBAgEBjAo9+wWqMw3AIECBAgAABAgQIXCowta1W7tQjh7I/slokP1swcum08HACBAgQIECAAAECBEoICEhKqGqTAAECBAgQIECAwHaBuXDkl5TSj9ub/Meh6zkg2XMJRvaoeQ0BAgQIECBAgAABAlUICEiqKJNOEiBAgAABAgQINC6QzxuZCjH2nDsy194aSsHIGiX3ECBAgAABAgQIECBQtYCApOry6TwBAgQIECBAgEADAnMrR7aEI49uo5UpBSMNTChDIECAAAECBAgQIEBgnYCAZJ2TuwgQIECAAAECBAiUEDjizJEjgpFHzjcp4aJNAgQIECBAgAABAgQIFBcQkBQn9gACBAgQIECAAAECowKPhCNHhCJWi5iYBAgQIECAAAECBAh0LSAg6br8Bk+AAAECBAgQIHChwFRAMreaQzByYcE8mgABAgQIECBAgACBtgQEJG3V02gIECBAgAABAgTqEMhBRz5I/f4aO3PkiFAkPye3nVeN5H9cBAgQIECAAAECBAgQ6F5AQNL9FABAgAABAgQIECBwgcBvKaU3I88dVo8cFYrYRuuC4nokAQIECBAgQIAAAQJ1CAhI6qiTXhIgQIAAAQIECLQj8HNK6YfCwxGMFAbWPAECBAgQIECAAAEC9QsISOqvoREQIECAAAECBAjUJfBcqLs5FPlkG61CupolQIAAAQIECBAgQKA5AQFJcyU1IAIECBAgQIAAgeACRwckVosEL7juESBAgAABAgQIECAQU0BAErMuekWAAAECBAgQINCuQD6cPZ8x8ujl0PVHBb2eAAECBAgQIECAAIGuBQQkXZff4AkQIECAAAECBC4S+JBSer/x2bbQ2gjmdgIECBAgQIAAAQIECMwJCEjMDwIECBAgQIAAAQLXCeSVJPmftxOrSmyfdV1tPJkAAQIECBAgQIAAgcYFBCSNF9jwCBAgQIAAAQIEqhK43XorhyMuAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAqvl2/QAAAEbSURBVAQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgroCAJG5t9IwAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCAgKQSrWQIECBAgQIAAAQIECBAgQIAAAQIECBAgQCCugIAkbm30jAABAgQIECBAgAABAgQIECBAgAABAgQIECgkICApBKtZAgQIECBAgAABAgQIECBAgAABAgQIECBAIK6AgCRubfSMAAECBAgQIECAAAECBAgQIECAAAECBAgQKCQgICkEq1kCBAgQIECAAAECBAgQIECAAAECBAgQIEAgrsD/A6/sHc0iKYfyAAAAAElFTkSuQmCC	t
169	2025-04-07 22:45:41.428458	2025-04-07 23:47:41.428458	\N	\N	t	\N	 [Cerrado automáticamente durante ventana de cierre 12:00:00 - 20:00:00] [R] Hora de salida ajustada de 20:00:00 a 01:47:41 por límite de horas contrato.	2025-04-07 22:45:41.663083	2025-04-08 10:57:54.083251	47	8	\N	f
170	2025-04-08 11:42:12.858877	2025-04-08 11:42:32.555583	\N	\N	t	\N	 [R] Hora entrada ajustada de 11:42 a 13:42	2025-04-08 11:42:12.881673	2025-04-08 11:42:44.255396	46	8	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAxgAAALuCAYAAAAtwbDUAAAAAXNSR0IArs4c6QAAAERlWElmTU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAADGKADAAQAAAABAAAC7gAAAACCD6w5AABAAElEQVR4Aey9B9gtNbm/zVF6F5AOe9ObgAoIKGWDVFEEpSkqIIh0LKhYEGwUFUWsoEcsWLAdRRQ5oliwHbso2BDlj6jYUEQEge97frqD2SHJzKw1fd3PdWVPJpM85Z5592TWJJmFFkIgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAAB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65Vt5Pw1S9rxMgECBAgQIECAAAECOyTQPyHolltDHHMz9xNajSgnQIAAAQIECBAgQGA3BboTinL6tMZQT47yst6i+XMabSgmQIAAAQIECBAgQGBHBc6IcdVOEmrDvXujbm39Y2sNKCNAgAABAgQIECBAYLcFLo3h1U4Q+qN+XKNef93391e0TIAAAQIECBAgQIDAfATuFEPtnyTk8oUFwcsbdfrrvaBYxywBAgQIECBAgAABAjMUOD7G3D9RyOVnRj4q8gcbr/fXuSjqSQQIECBAgAABAhsucPSGxye87Re4W2MI+QveNzVe6xefFgX/t19omQABAgQIECBAgACB+Qn8Vgy5/23EmGUnwfPbZoyYAAECBAgQIECAQFNgzMlEWfc3my16gQABAgQIECBAgACB2QqUJw1D558xWy0DJ0CAAAECBAgQIECgKfDQeGXoSUVX71CzNS8QIECAAAECBAgQIDBrgWti9N2Jw5DpmbPWMngCBAgQIECAAAECBBYKDDmp6Ork42wlAgQIECBAgAABAgQIVAUuitLu5GHR9MNR75hqCwoJECBAgAABAgQIECBwWOB9MV10YpGv/eThuiYECBAgQIAAAQIECBBoCpwYr9wcedEJxmOaa3uBAAECBAgQIECAAAEChcCyE4wLi7pmCRAgQIAAAQIECBAgsFTgLVGj9g2GJ0UtpVOBAAECBAgQIECAAIG+wElRkCcZealU5pzPMokAAQIECBAgQIAAAQJ7FsjLpTJLBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAIFdEPj/UNRqYGv0ZuAAAAAASUVORK5CYII=	t
171	2025-04-08 12:36:17.157542	2025-04-08 12:36:25.821526	\N	\N	t	\N	 [R] Hora entrada ajustada de 12:36 a 14:36	2025-04-08 12:36:17.178867	2025-04-08 12:36:31.569149	46	8	data:image/png;base64,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	t
\.


--
-- Data for Name: checkpoints; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.checkpoints (id, name, description, location, status, username, password_hash, created_at, updated_at, company_id, enforce_contract_hours, auto_adjust_overtime, require_signature, operation_start_time, operation_end_time, enforce_operation_hours) FROM stdin;
8	tablet	tablet		ACTIVE	tablet	scrypt:32768:8:1$YfPpkpYMTJAZ9RzG$33e09b768c32b684a9c9aec1fd05e30dd095d3289db9f19d55d41f9ef34213399340bbcfb41e0c3c57edc1743f05f0af84fac70a8cb8d6d13dfc550d5b996e4e	2025-04-04 16:19:36.744585	2025-04-08 10:57:08.24686	17	t	t	t	12:00:00	20:00:00	t
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.companies (id, name, address, city, postal_code, country, sector, tax_id, phone, email, website, created_at, updated_at, is_active, bank_account) FROM stdin;
17	DNLN DISTRIBUCION SL	av libertad 74 bajo	elche	03205	España	RESTAURACION	B09942756	610637752	claudiorad24@gmail.com	https://openai.com/	2025-04-04 16:18:28.811004	2025-04-04 16:18:28.811009	t	\N
\.


--
-- Data for Name: employee_check_ins; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employee_check_ins (id, check_in_time, check_out_time, is_generated, created_at, updated_at, notes, employee_id) FROM stdin;
202	2025-03-31 17:50:15	2025-03-31 20:12:45	t	2025-04-07 17:16:01.68991	2025-04-07 17:16:01.689914	Generado automáticamente	47
203	2025-04-07 17:47:12	2025-04-07 20:13:32	t	2025-04-07 17:16:01.689915	2025-04-07 17:16:01.689916	Generado automáticamente	47
204	2025-04-14 17:49:46	2025-04-14 20:10:28	t	2025-04-07 17:16:01.689916	2025-04-07 17:16:01.689917	Generado automáticamente	47
205	2025-04-21 17:50:46	2025-04-21 20:10:54	t	2025-04-07 17:16:01.689917	2025-04-07 17:16:01.689917	Generado automáticamente	47
206	2025-02-03 17:47:43	2025-02-03 20:13:26	t	2025-04-07 17:19:17.116152	2025-04-07 17:19:17.116156	Generado automáticamente	47
207	2025-02-10 17:47:46	2025-02-10 20:13:30	t	2025-04-07 17:19:17.116157	2025-04-07 17:19:17.116158	Generado automáticamente	47
208	2025-02-17 17:48:02	2025-02-17 20:12:11	t	2025-04-07 17:19:17.116158	2025-04-07 17:19:17.116161	Generado automáticamente	47
209	2025-02-24 17:48:43	2025-02-24 20:10:38	t	2025-04-07 17:19:17.116162	2025-04-07 17:19:17.116162	Generado automáticamente	47
\.


--
-- Data for Name: employee_contract_hours; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employee_contract_hours (id, daily_hours, weekly_hours, allow_overtime, max_overtime_daily, normal_start_time, normal_end_time, checkin_flexibility, checkout_flexibility, created_at, updated_at, employee_id, use_normal_schedule, use_flexibility) FROM stdin;
4	2	40	f	2	\N	\N	15	15	2025-04-04 16:20:47.736053	2025-04-04 16:21:04.541395	46	f	f
5	1	40	f	2	\N	\N	15	15	2025-04-04 17:16:12.924507	2025-04-06 21:14:15.521289	47	f	f
\.


--
-- Data for Name: employee_documents; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employee_documents (id, filename, original_filename, file_path, file_type, file_size, description, uploaded_at, employee_id) FROM stdin;
\.


--
-- Data for Name: employee_history; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employee_history (id, field_name, old_value, new_value, changed_at, employee_id, changed_by_id) FROM stdin;
1	is_active	False	True	2025-04-04 17:58:08.275146	46	8
2	is_active	True	False	2025-04-04 18:02:48.919624	47	8
3	is_active	False	True	2025-04-04 18:02:55.38529	47	8
4	is_active	True	False	2025-04-04 22:04:00.456465	47	8
5	is_active	True	False	2025-04-04 22:16:30.326962	46	8
6	is_active	False	True	2025-04-07 17:17:18.503365	47	8
7	is_active	True	False	2025-04-07 17:17:34.615614	47	8
8	is_active	False	True	2025-04-07 17:43:32.298485	47	8
9	status	activo	inactivo	2025-04-07 17:44:50.487482	47	8
10	status_notes	\N		2025-04-07 17:44:50.487658	47	8
11	is_active	True	False	2025-04-07 17:46:23.083095	47	8
12	status	inactivo	activo	2025-04-07 17:47:52.769669	47	8
13	status_end_date	\N	2025-04-06	2025-04-07 17:47:52.769829	47	8
14	is_active	False	True	2025-04-07 18:01:20.964439	46	8
15	is_active	True	False	2025-04-07 18:01:59.522434	46	8
16	is_active	False	True	2025-04-07 18:04:21.136167	46	8
17	is_active	False	True	2025-04-07 22:25:38.881385	47	8
\.


--
-- Data for Name: employee_notes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employee_notes (id, content, created_at, updated_at, employee_id, created_by_id) FROM stdin;
\.


--
-- Data for Name: employee_schedules; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employee_schedules (id, day_of_week, start_time, end_time, is_working_day, created_at, updated_at, employee_id) FROM stdin;
30	LUNES	17:46:00	20:09:00	t	2025-04-07 15:46:25.292778	2025-04-07 15:46:25.292783	47
31	MARTES	09:00:00	18:00:00	f	2025-04-07 15:46:25.349186	2025-04-07 15:46:25.349191	47
32	MIERCOLES	09:00:00	18:00:00	f	2025-04-07 15:46:25.394048	2025-04-07 15:46:25.394053	47
33	JUEVES	09:00:00	18:00:00	f	2025-04-07 15:46:25.43841	2025-04-07 15:46:25.438415	47
34	VIERNES	09:00:00	18:00:00	f	2025-04-07 15:46:25.483436	2025-04-07 15:46:25.483443	47
35	SABADO	09:00:00	18:00:00	f	2025-04-07 15:46:25.529865	2025-04-07 15:46:25.52987	47
36	DOMINGO	09:00:00	18:00:00	f	2025-04-07 15:46:25.577266	2025-04-07 15:46:25.577271	47
37	LUNES	12:00:00	18:00:00	t	2025-04-07 17:21:08.331821	2025-04-07 17:21:08.331826	46
38	MARTES	09:00:00	18:00:00	f	2025-04-07 17:21:08.434286	2025-04-07 17:21:08.434291	46
39	MIERCOLES	09:00:00	18:00:00	f	2025-04-07 17:21:08.485044	2025-04-07 17:21:08.485048	46
40	JUEVES	09:00:00	18:00:00	f	2025-04-07 17:21:08.531575	2025-04-07 17:21:08.531579	46
41	VIERNES	09:00:00	18:00:00	f	2025-04-07 17:21:08.58537	2025-04-07 17:21:08.585375	46
42	SABADO	09:00:00	18:00:00	f	2025-04-07 17:21:08.640003	2025-04-07 17:21:08.640007	46
43	DOMINGO	09:00:00	18:00:00	f	2025-04-07 17:21:08.696511	2025-04-07 17:21:08.696516	46
44	LUNES	12:00:00	16:00:00	t	2025-04-08 16:00:00.749669	2025-04-08 16:00:00.749674	48
45	MARTES	18:00:00	23:00:00	t	2025-04-08 16:00:00.799251	2025-04-08 16:00:00.799256	48
46	MIERCOLES	17:00:00	22:00:00	t	2025-04-08 16:00:00.844821	2025-04-08 16:00:00.844825	48
47	JUEVES	09:00:00	15:00:00	t	2025-04-08 16:00:00.887875	2025-04-08 16:00:00.88788	48
48	VIERNES	09:00:00	18:00:00	f	2025-04-08 16:00:00.934307	2025-04-08 16:00:00.934311	48
49	SABADO	12:00:00	17:00:00	t	2025-04-08 16:00:00.979537	2025-04-08 16:00:00.979541	48
50	DOMINGO	09:00:00	18:00:00	f	2025-04-08 16:00:01.086156	2025-04-08 16:00:01.086161	48
\.


--
-- Data for Name: employee_vacations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employee_vacations (id, start_date, end_date, status, is_signed, is_enjoyed, created_at, updated_at, notes, employee_id, approved_by_id) FROM stdin;
\.


--
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employees (id, first_name, last_name, dni, "position", contract_type, bank_account, start_date, end_date, created_at, updated_at, is_active, company_id, user_id, status, status_start_date, status_end_date, status_notes, is_on_shift, social_security_number, email, address, phone) FROM stdin;
47	Lucia	Mendez	x83821111d	GERENTE	INDEFINIDO	Es98037498732490879238	2025-02-04	\N	2025-04-04 17:14:36.331836	2025-04-08 10:57:53.629668	t	17	\N	ACTIVO	2025-02-04	2025-04-06		f	\N	\N	\N	\N
46	Claudio	Rad	x8311111x		INDEFINIDO	Es98037498732490879238	2025-02-24	2025-04-30	2025-04-04 16:20:17.930435	2025-04-08 12:36:25.932496	t	17	\N	ACTIVO	2025-02-24	\N	\N	f	\N	\N	\N	\N
48	marcos	menzdes	12121212D	ayudante cocina	INDEFINIDO	ES48975984798675	2025-04-02	\N	2025-04-08 15:12:20.878917	2025-04-08 15:12:20.878921	f	17	\N	ACTIVO	2025-04-02	\N	\N	f	klsdjlsjdl328923729	claudiorad24@gmail.com	av libertad 74 bajo	610637752
\.


--
-- Data for Name: label_templates; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.label_templates (id, name, created_at, updated_at, is_default, titulo_x, titulo_y, titulo_size, titulo_bold, conservacion_x, conservacion_y, conservacion_size, conservacion_bold, preparador_x, preparador_y, preparador_size, preparador_bold, fecha_x, fecha_y, fecha_size, fecha_bold, caducidad_x, caducidad_y, caducidad_size, caducidad_bold, caducidad2_x, caducidad2_y, caducidad2_size, caducidad2_bold, location_id) FROM stdin;
\.


--
-- Data for Name: local_users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.local_users (id, name, username, password_hash, pin, photo_path, created_at, updated_at, is_active, location_id, last_name) FROM stdin;
\.


--
-- Data for Name: locations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.locations (id, name, address, city, postal_code, description, created_at, updated_at, is_active, company_id, portal_username, portal_password_hash) FROM stdin;
6	Chimeneas	av libertad 74 bajo	elche	03205		2025-04-04 22:03:07.641915	2025-04-04 22:03:07.641923	t	17	\N	\N
\.


--
-- Data for Name: printer_configs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.printer_configs (id, printer_name, is_default, is_active, last_check, created_at, updated_at, location_id, local_user_id) FROM stdin;
\.


--
-- Data for Name: product_conservations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.product_conservations (id, conservation_type, created_at, updated_at, product_id, hours_valid) FROM stdin;
\.


--
-- Data for Name: product_labels; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.product_labels (id, created_at, expiry_date, product_id, local_user_id, conservation_type) FROM stdin;
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.products (id, name, description, created_at, updated_at, is_active, location_id, shelf_life_days) FROM stdin;
\.


--
-- Data for Name: task_completions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_completions (id, completion_date, notes, task_id, local_user_id) FROM stdin;
\.


--
-- Data for Name: task_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_groups (id, name, description, color, created_at, updated_at, location_id) FROM stdin;
\.


--
-- Data for Name: task_instances; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_instances (id, scheduled_date, status, notes, created_at, updated_at, task_id, completed_by_id) FROM stdin;
\.


--
-- Data for Name: task_schedules; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_schedules (id, day_of_week, day_of_month, start_time, end_time, created_at, updated_at, task_id) FROM stdin;
\.


--
-- Data for Name: task_weekdays; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_weekdays (id, day_of_week, task_id) FROM stdin;
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tasks (id, title, description, priority, frequency, status, start_date, end_date, created_at, updated_at, location_id, created_by_id, group_id) FROM stdin;
\.


--
-- Data for Name: user_companies; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_companies (user_id, company_id) FROM stdin;
9	17
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, username, email, password_hash, role, first_name, last_name, created_at, updated_at, is_active, company_id) FROM stdin;
8	admin	admin@example.com	scrypt:32768:8:1$CSWgZtxNTKRXVPXK$8de6f9d47617bcffc55c67c4f7541c59cc5bdf9017971dbee1755b23fd7aa1efa837ae47f4d125ad46c7a38612bdada15bcc4d9b0ba0714c5b9d1314c547ad5a	ADMIN	Admin	User	2025-04-04 16:11:58.263931	2025-04-04 16:11:58.263934	t	\N
9	dnln	dnln@gruporad.com	scrypt:32768:8:1$wPTF3l1tINJvBczk$aaa0de4023e296958c7bcfb5524b993f544edda6b383e3e284c8adb91210dd38e9cf26c062be6bfd9075e3c3f25e12ff37dfe01cba80ad9c4fafff472ec0306f	GERENTE	dnln	distribucion 	2025-04-04 16:17:49.6617	2025-04-04 16:17:49.661705	t	\N
\.


--
-- Name: activity_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.activity_logs_id_seq', 6050, true);


--
-- Name: api_tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.api_tasks_id_seq', 5, true);


--
-- Name: checkpoint_incidents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.checkpoint_incidents_id_seq', 41, true);


--
-- Name: checkpoint_original_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.checkpoint_original_records_id_seq', 199, true);


--
-- Name: checkpoint_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.checkpoint_records_id_seq', 171, true);


--
-- Name: checkpoints_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.checkpoints_id_seq', 8, true);


--
-- Name: companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.companies_id_seq', 17, true);


--
-- Name: employee_check_ins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.employee_check_ins_id_seq', 209, true);


--
-- Name: employee_contract_hours_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.employee_contract_hours_id_seq', 5, true);


--
-- Name: employee_documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.employee_documents_id_seq', 1, false);


--
-- Name: employee_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.employee_history_id_seq', 17, true);


--
-- Name: employee_notes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.employee_notes_id_seq', 1, false);


--
-- Name: employee_schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.employee_schedules_id_seq', 50, true);


--
-- Name: employee_vacations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.employee_vacations_id_seq', 6, true);


--
-- Name: employees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.employees_id_seq', 48, true);


--
-- Name: label_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.label_templates_id_seq', 2, true);


--
-- Name: local_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.local_users_id_seq', 8, true);


--
-- Name: locations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.locations_id_seq', 6, true);


--
-- Name: printer_configs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.printer_configs_id_seq', 1, true);


--
-- Name: product_conservations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.product_conservations_id_seq', 28, true);


--
-- Name: product_labels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.product_labels_id_seq', 124, true);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.products_id_seq', 10, true);


--
-- Name: task_completions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_completions_id_seq', 7, true);


--
-- Name: task_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_groups_id_seq', 3, true);


--
-- Name: task_instances_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_instances_id_seq', 1, false);


--
-- Name: task_schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_schedules_id_seq', 4, true);


--
-- Name: task_weekdays_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_weekdays_id_seq', 1, true);


--
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tasks_id_seq', 6, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 9, true);


--
-- Name: activity_logs activity_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: api_tasks api_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_tasks
    ADD CONSTRAINT api_tasks_pkey PRIMARY KEY (id);


--
-- Name: checkpoint_incidents checkpoint_incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_incidents
    ADD CONSTRAINT checkpoint_incidents_pkey PRIMARY KEY (id);


--
-- Name: checkpoint_original_records checkpoint_original_records_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_original_records
    ADD CONSTRAINT checkpoint_original_records_pkey PRIMARY KEY (id);


--
-- Name: checkpoint_records checkpoint_records_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_records
    ADD CONSTRAINT checkpoint_records_pkey PRIMARY KEY (id);


--
-- Name: checkpoints checkpoints_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoints
    ADD CONSTRAINT checkpoints_pkey PRIMARY KEY (id);


--
-- Name: checkpoints checkpoints_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoints
    ADD CONSTRAINT checkpoints_username_key UNIQUE (username);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: companies companies_tax_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_tax_id_key UNIQUE (tax_id);


--
-- Name: employee_check_ins employee_check_ins_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_check_ins
    ADD CONSTRAINT employee_check_ins_pkey PRIMARY KEY (id);


--
-- Name: employee_contract_hours employee_contract_hours_employee_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_contract_hours
    ADD CONSTRAINT employee_contract_hours_employee_id_key UNIQUE (employee_id);


--
-- Name: employee_contract_hours employee_contract_hours_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_contract_hours
    ADD CONSTRAINT employee_contract_hours_pkey PRIMARY KEY (id);


--
-- Name: employee_documents employee_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_documents
    ADD CONSTRAINT employee_documents_pkey PRIMARY KEY (id);


--
-- Name: employee_history employee_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_history
    ADD CONSTRAINT employee_history_pkey PRIMARY KEY (id);


--
-- Name: employee_notes employee_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_notes
    ADD CONSTRAINT employee_notes_pkey PRIMARY KEY (id);


--
-- Name: employee_schedules employee_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_schedules
    ADD CONSTRAINT employee_schedules_pkey PRIMARY KEY (id);


--
-- Name: employee_vacations employee_vacations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_vacations
    ADD CONSTRAINT employee_vacations_pkey PRIMARY KEY (id);


--
-- Name: employees employees_dni_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_dni_key UNIQUE (dni);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: employees employees_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_user_id_key UNIQUE (user_id);


--
-- Name: label_templates label_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.label_templates
    ADD CONSTRAINT label_templates_pkey PRIMARY KEY (id);


--
-- Name: local_users local_users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.local_users
    ADD CONSTRAINT local_users_pkey PRIMARY KEY (id);


--
-- Name: local_users local_users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.local_users
    ADD CONSTRAINT local_users_username_key UNIQUE (username);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);


--
-- Name: locations locations_portal_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_portal_username_key UNIQUE (portal_username);


--
-- Name: printer_configs printer_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.printer_configs
    ADD CONSTRAINT printer_configs_pkey PRIMARY KEY (id);


--
-- Name: product_conservations product_conservations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_conservations
    ADD CONSTRAINT product_conservations_pkey PRIMARY KEY (id);


--
-- Name: product_labels product_labels_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_labels
    ADD CONSTRAINT product_labels_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: task_completions task_completions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_completions
    ADD CONSTRAINT task_completions_pkey PRIMARY KEY (id);


--
-- Name: task_groups task_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_groups
    ADD CONSTRAINT task_groups_pkey PRIMARY KEY (id);


--
-- Name: task_instances task_instances_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_instances
    ADD CONSTRAINT task_instances_pkey PRIMARY KEY (id);


--
-- Name: task_schedules task_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_schedules
    ADD CONSTRAINT task_schedules_pkey PRIMARY KEY (id);


--
-- Name: task_weekdays task_weekdays_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_weekdays
    ADD CONSTRAINT task_weekdays_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: user_companies user_companies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_companies
    ADD CONSTRAINT user_companies_pkey PRIMARY KEY (user_id, company_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: activity_logs activity_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: checkpoint_incidents checkpoint_incidents_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_incidents
    ADD CONSTRAINT checkpoint_incidents_record_id_fkey FOREIGN KEY (record_id) REFERENCES public.checkpoint_records(id);


--
-- Name: checkpoint_incidents checkpoint_incidents_resolved_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_incidents
    ADD CONSTRAINT checkpoint_incidents_resolved_by_id_fkey FOREIGN KEY (resolved_by_id) REFERENCES public.users(id);


--
-- Name: checkpoint_original_records checkpoint_original_records_adjusted_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_original_records
    ADD CONSTRAINT checkpoint_original_records_adjusted_by_id_fkey FOREIGN KEY (adjusted_by_id) REFERENCES public.users(id);


--
-- Name: checkpoint_original_records checkpoint_original_records_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_original_records
    ADD CONSTRAINT checkpoint_original_records_record_id_fkey FOREIGN KEY (record_id) REFERENCES public.checkpoint_records(id);


--
-- Name: checkpoint_records checkpoint_records_checkpoint_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_records
    ADD CONSTRAINT checkpoint_records_checkpoint_id_fkey FOREIGN KEY (checkpoint_id) REFERENCES public.checkpoints(id);


--
-- Name: checkpoint_records checkpoint_records_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_records
    ADD CONSTRAINT checkpoint_records_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: checkpoints checkpoints_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoints
    ADD CONSTRAINT checkpoints_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: employee_check_ins employee_check_ins_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_check_ins
    ADD CONSTRAINT employee_check_ins_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: employee_contract_hours employee_contract_hours_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_contract_hours
    ADD CONSTRAINT employee_contract_hours_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: employee_documents employee_documents_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_documents
    ADD CONSTRAINT employee_documents_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: employee_history employee_history_changed_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_history
    ADD CONSTRAINT employee_history_changed_by_id_fkey FOREIGN KEY (changed_by_id) REFERENCES public.users(id);


--
-- Name: employee_history employee_history_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_history
    ADD CONSTRAINT employee_history_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: employee_notes employee_notes_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_notes
    ADD CONSTRAINT employee_notes_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id);


--
-- Name: employee_notes employee_notes_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_notes
    ADD CONSTRAINT employee_notes_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: employee_schedules employee_schedules_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_schedules
    ADD CONSTRAINT employee_schedules_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: employee_vacations employee_vacations_approved_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_vacations
    ADD CONSTRAINT employee_vacations_approved_by_id_fkey FOREIGN KEY (approved_by_id) REFERENCES public.users(id);


--
-- Name: employee_vacations employee_vacations_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_vacations
    ADD CONSTRAINT employee_vacations_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: employees employees_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: employees employees_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: label_templates label_templates_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.label_templates
    ADD CONSTRAINT label_templates_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: local_users local_users_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.local_users
    ADD CONSTRAINT local_users_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: locations locations_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: printer_configs printer_configs_local_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.printer_configs
    ADD CONSTRAINT printer_configs_local_user_id_fkey FOREIGN KEY (local_user_id) REFERENCES public.local_users(id);


--
-- Name: printer_configs printer_configs_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.printer_configs
    ADD CONSTRAINT printer_configs_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: product_conservations product_conservations_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_conservations
    ADD CONSTRAINT product_conservations_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: product_labels product_labels_local_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_labels
    ADD CONSTRAINT product_labels_local_user_id_fkey FOREIGN KEY (local_user_id) REFERENCES public.local_users(id);


--
-- Name: product_labels product_labels_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_labels
    ADD CONSTRAINT product_labels_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: products products_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: task_completions task_completions_local_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_completions
    ADD CONSTRAINT task_completions_local_user_id_fkey FOREIGN KEY (local_user_id) REFERENCES public.local_users(id);


--
-- Name: task_completions task_completions_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_completions
    ADD CONSTRAINT task_completions_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id);


--
-- Name: task_groups task_groups_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_groups
    ADD CONSTRAINT task_groups_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: task_instances task_instances_completed_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_instances
    ADD CONSTRAINT task_instances_completed_by_id_fkey FOREIGN KEY (completed_by_id) REFERENCES public.local_users(id);


--
-- Name: task_instances task_instances_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_instances
    ADD CONSTRAINT task_instances_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id);


--
-- Name: task_schedules task_schedules_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_schedules
    ADD CONSTRAINT task_schedules_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id);


--
-- Name: task_weekdays task_weekdays_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_weekdays
    ADD CONSTRAINT task_weekdays_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id) ON DELETE CASCADE;


--
-- Name: tasks tasks_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id);


--
-- Name: tasks tasks_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.task_groups(id);


--
-- Name: tasks tasks_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: user_companies user_companies_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_companies
    ADD CONSTRAINT user_companies_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: user_companies user_companies_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_companies
    ADD CONSTRAINT user_companies_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users users_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- PostgreSQL database dump complete
--

