// Funciones para acceder a la API de Flask
// Este archivo maneja la comunicación entre el frontend React y el backend Flask

import { Schedule, ScheduleAssignment, Employee } from '../shared/schema';

// Utility function to handle API responses
async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Obtiene un horario por su ID
 * @param scheduleId ID del horario
 * @returns Promesa con el horario o null si no existe
 */
export async function getSchedule(scheduleId: number): Promise<Schedule | null> {
  try {
    const response = await fetch(`/horarios/api/schedules/${scheduleId}`);
    return await handleApiResponse<Schedule>(response);
  } catch (error) {
    console.error("Error al obtener horario:", error);
    return null;
  }
}

/**
 * Obtiene todos los horarios
 * @returns Promesa con array de horarios
 */
export async function getSchedules(): Promise<Schedule[]> {
  try {
    const response = await fetch('/horarios/api/schedules');
    return await handleApiResponse<Schedule[]>(response);
  } catch (error) {
    console.error("Error al obtener horarios:", error);
    return [];
  }
}

/**
 * Crea un nuevo horario
 * @param schedule Datos del horario a crear
 * @returns Promesa con el horario creado
 */
export async function createSchedule(schedule: Omit<Schedule, 'id'>): Promise<Schedule | null> {
  try {
    const response = await fetch('/horarios/api/schedules', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(schedule)
    });
    return await handleApiResponse<Schedule>(response);
  } catch (error) {
    console.error("Error al crear horario:", error);
    return null;
  }
}

/**
 * Actualiza un horario existente
 * @param scheduleId ID del horario
 * @param scheduleData Datos a actualizar
 * @returns Promesa con el horario actualizado
 */
export async function updateSchedule(scheduleId: number, scheduleData: Partial<Schedule>): Promise<Schedule | null> {
  try {
    const response = await fetch(`/horarios/api/schedules/${scheduleId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scheduleData)
    });
    return await handleApiResponse<Schedule>(response);
  } catch (error) {
    console.error("Error al actualizar horario:", error);
    return null;
  }
}

/**
 * Obtiene todas las asignaciones de un horario
 * @param scheduleId ID del horario
 * @returns Promesa con un array de asignaciones
 */
export async function getScheduleAssignments(scheduleId: number): Promise<ScheduleAssignment[]> {
  try {
    const response = await fetch(`/horarios/api/schedules/${scheduleId}/assignments`);
    return await handleApiResponse<ScheduleAssignment[]>(response);
  } catch (error) {
    console.error("Error al obtener asignaciones:", error);
    return [];
  }
}

/**
 * Obtiene todos los empleados disponibles para asignar a horarios
 * @returns Promesa con array de empleados
 */
export async function getEmployees(): Promise<Employee[]> {
  try {
    const response = await fetch('/horarios/api/employees');
    return await handleApiResponse<Employee[]>(response);
  } catch (error) {
    console.error("Error al obtener empleados:", error);
    return [];
  }
}

/**
 * Guarda asignaciones de horario
 * @param scheduleId ID del horario
 * @param assignments Array de asignaciones a guardar
 * @returns Respuesta de la API con el resultado
 */
export async function saveScheduleAssignments(scheduleId: number, assignments: Partial<ScheduleAssignment>[]): Promise<{message: string, assignments: ScheduleAssignment[]}> {
  try {
    const response = await fetch(`/horarios/api/schedules/${scheduleId}/assignments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(assignments)
    });
    return await handleApiResponse<{message: string, assignments: ScheduleAssignment[]}>(response);
  } catch (error) {
    console.error("Error al guardar asignaciones:", error);
    throw error;
  }
}

/**
 * Elimina todas las asignaciones de un horario
 * @param scheduleId ID del horario
 * @returns Resultado de la operación
 */
export async function clearScheduleAssignments(scheduleId: number): Promise<{message: string, count: number}> {
  try {
    const response = await fetch(`/horarios/api/schedules/${scheduleId}/assignments`, {
      method: 'DELETE'
    });
    return await handleApiResponse<{message: string, count: number}>(response);
  } catch (error) {
    console.error("Error al eliminar asignaciones:", error);
    throw error;
  }
}

/**
 * Actualiza el estado de publicación de un horario
 * @param scheduleId ID del horario
 * @param published Si el horario está publicado o no
 * @returns Si la operación fue exitosa
 */
export async function updateSchedulePublishStatus(scheduleId: number, published: boolean): Promise<boolean> {
  try {
    const response = await fetch(`/horarios/api/schedules/${scheduleId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ published })
    });
    if (response.ok) {
      return true;
    }
    return false;
  } catch (error) {
    console.error("Error al actualizar estado de publicación:", error);
    return false;
  }
}