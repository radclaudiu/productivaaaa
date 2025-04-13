// Definiciones de tipos para compartir entre cliente y servidor
// Adaptado para coincidir con los modelos SQLAlchemy de la aplicación Flask

export interface Employee {
  id: number;
  firstName: string;  // corresponde a first_name en SQLAlchemy
  lastName: string;   // corresponde a last_name en SQLAlchemy
  position: string;
  department: string; // No existe en nuestro modelo, pero se mantiene para compatibilidad
  contractedHours: number;
}

export interface Schedule {
  id: number;
  name: string;
  start_date: string;  // Cambiado de startDate a start_date para coincidir con la API
  end_date: string;    // Cambiado de endDate a end_date para coincidir con la API
  published: boolean;
  company_id: number;  // Cambiado de locationId a company_id
  company_name?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ScheduleAssignment {
  id: number;
  schedule_id: number;  // Cambiado de scheduleId a schedule_id
  employee_id: number;  // Cambiado de employeeId a employee_id
  employee_name?: string;
  day: string;         // ISO date: '2025-04-15'
  start_time: string;  // Cambiado de startTime a start_time, formato: "HH:MM"
  end_time: string;    // Cambiado de endTime a end_time, formato: "HH:MM"
  break_duration: number; // Cambiado de breakDuration a break_duration, en minutos
}

// Interfaces auxiliares para la UI (no cambian)
export interface TimeSlot {
  id: string;
  startTime: string;
  endTime: string;
  assigned: boolean;
  employee?: Employee;
}

export interface DailySchedule {
  date: string;
  dayName: string;
  timeSlots: TimeSlot[];
}

export interface WeeklySchedule {
  scheduleId: number;
  name: string;
  startDate: string;
  endDate: string;
  days: DailySchedule[];
  employees: Employee[];
}