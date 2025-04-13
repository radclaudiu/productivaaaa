import React, { useState, useEffect } from 'react';
import { Schedule, DailySchedule, TimeSlot, Employee } from '../../../shared/schema';

interface ScheduleTableProps {
  scheduleId: number;
  onSave: (assignments: any[]) => void;
}

const ScheduleTable: React.FC<ScheduleTableProps> = ({ scheduleId, onSave }) => {
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [weeklySchedule, setWeeklySchedule] = useState<DailySchedule[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCells, setSelectedCells] = useState<Set<string>>(new Set());
  const [dragStart, setDragStart] = useState<string | null>(null);

  // Horario de trabajo: 8:00 - 22:00 con intervalos de 30 minutos
  const timeSlots = [
    '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', 
    '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30',
    '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
    '20:00', '20:30', '21:00', '21:30', '22:00'
  ];

  // Cargar datos de horario
  useEffect(() => {
    const fetchScheduleData = async () => {
      try {
        setLoading(true);
        
        // En una implementación real, esto sería una llamada a la API
        // Datos de ejemplo para mostrar el concepto
        const mockSchedule = {
          id: scheduleId,
          name: `Horario semana ${scheduleId}`,
          startDate: '2025-04-15',
          endDate: '2025-04-21',
          published: false,
          locationId: 1
        };
        
        const mockEmployees = [
          { id: 1, firstName: 'Ana', lastName: 'García', position: 'Cajera', department: 'Ventas', contractedHours: 40 },
          { id: 2, firstName: 'Carlos', lastName: 'Martínez', position: 'Reponedor', department: 'Logística', contractedHours: 30 },
          { id: 3, firstName: 'Elena', lastName: 'López', position: 'Dependienta', department: 'Atención al Cliente', contractedHours: 25 }
        ];
        
        // Crear datos de horario semanal
        const days = [
          'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'
        ];
        
        // Generar fechas para la semana a partir de la fecha de inicio
        const startDate = new Date(mockSchedule.startDate);
        const weeklyData = days.map((dayName, index) => {
          const date = new Date(startDate);
          date.setDate(startDate.getDate() + index);
          
          return {
            date: date.toISOString().split('T')[0],
            dayName,
            timeSlots: []
          };
        });
        
        setSchedule(mockSchedule);
        setEmployees(mockEmployees);
        setWeeklySchedule(weeklyData);
        setLoading(false);
      } catch (err) {
        setError('Error al cargar los datos del horario');
        setLoading(false);
        console.error(err);
      }
    };
    
    fetchScheduleData();
  }, [scheduleId]);

  // Manejadores de eventos para la selección de celdas
  const handleCellMouseDown = (employeeId: number, day: string, time: string) => {
    const cellId = `${employeeId}-${day}-${time}`;
    setDragStart(cellId);
    
    // Alternar selección
    const newSelection = new Set(selectedCells);
    if (newSelection.has(cellId)) {
      newSelection.delete(cellId);
    } else {
      newSelection.add(cellId);
    }
    
    setSelectedCells(newSelection);
  };
  
  const handleCellMouseEnter = (employeeId: number, day: string, time: string) => {
    // Solo procesar si estamos en modo arrastre
    if (dragStart) {
      const cellId = `${employeeId}-${day}-${time}`;
      setSelectedCells(prev => new Set(prev).add(cellId));
    }
  };
  
  const handleCellMouseUp = () => {
    setDragStart(null);
  };
  
  const handleSaveSchedule = () => {
    // Convertir celdas seleccionadas a asignaciones
    const assignments = Array.from(selectedCells).map(cellId => {
      const [employeeId, day, time] = cellId.split('-');
      return {
        scheduleId,
        employeeId: parseInt(employeeId, 10),
        day,
        startTime: time,
        // En una implementación real, calcularíamos la hora de fin basada en la duración del turno
        endTime: '18:00',
        breakDuration: 30
      };
    });
    
    onSave(assignments);
    alert(`Se guardaron ${assignments.length} asignaciones de horario`);
  };

  if (loading) {
    return <div className="text-center my-5"><div className="spinner-border text-primary" role="status"></div></div>;
  }

  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }

  return (
    <div className="schedule-container">
      <div className="schedule-header d-flex justify-content-between align-items-center">
        <h3>{schedule?.name}</h3>
        <button className="btn btn-primary" onClick={handleSaveSchedule}>
          <i className="fas fa-save me-2"></i>Guardar Horario
        </button>
      </div>
      
      <div className="schedule-grid" onMouseUp={handleCellMouseUp}>
        <div className="table-responsive">
          <table className="table table-bordered">
            <thead>
              <tr>
                <th style={{ minWidth: '150px' }}>Empleado</th>
                {weeklySchedule.map(day => (
                  <th key={day.date} colSpan={timeSlots.length} className="text-center">
                    {day.dayName} ({day.date})
                  </th>
                ))}
              </tr>
              <tr>
                <th></th>
                {weeklySchedule.map(day => (
                  timeSlots.map(time => (
                    <th key={`${day.date}-${time}`} className="time-header" style={{ fontSize: '0.8rem' }}>
                      {time}
                    </th>
                  ))
                ))}
              </tr>
            </thead>
            <tbody>
              {employees.map(employee => (
                <tr key={employee.id}>
                  <td className="employee-name">
                    {employee.firstName} {employee.lastName}
                    <div><small>{employee.position}</small></div>
                  </td>
                  {weeklySchedule.map(day => (
                    timeSlots.map(time => {
                      const cellId = `${employee.id}-${day.date}-${time}`;
                      const isSelected = selectedCells.has(cellId);
                      
                      return (
                        <td
                          key={cellId}
                          className={`time-cell ${isSelected ? 'selected' : ''}`}
                          onMouseDown={() => handleCellMouseDown(employee.id, day.date, time)}
                          onMouseEnter={() => handleCellMouseEnter(employee.id, day.date, time)}
                        >
                          {isSelected && <i className="fas fa-check"></i>}
                        </td>
                      );
                    })
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ScheduleTable;