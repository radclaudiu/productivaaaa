// Definiciones de tipos para compartir entre cliente y servidor

export interface Employee {
  id: number;
  firstName: string;
  lastName: string;
  position: string;
  department: string;
  contractedHours: number;
}

export interface Schedule {
  id: number;
  name: string;
  startDate: string;
  endDate: string;
  published: boolean;
  locationId: number;
}

export interface ScheduleAssignment {
  id: number;
  scheduleId: number;
  employeeId: number;
  day: string; // ISO date: '2025-04-15'
  startTime: string; // format: 'HH:MM'
  endTime: string; // format: 'HH:MM'
  breakDuration: number; // en minutos
}

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