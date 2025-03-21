/**
 * Script para mejorar la interacción con el formulario de horarios semanales
 */
document.addEventListener('DOMContentLoaded', function() {
    // Manejar la visibilidad y habilitación de los campos de hora basados en el checkbox de día laborable
    const days = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"];
    
    // Función para actualizar el estado de los campos de hora
    function updateTimeFields(dayName) {
        const checkbox = document.getElementById(`${dayName}_is_working_day`);
        const startTimeField = document.getElementById(`${dayName}_start_time`);
        const endTimeField = document.getElementById(`${dayName}_end_time`);
        
        if (checkbox && startTimeField && endTimeField) {
            // Si el día no es laborable, deshabilitar campos de hora
            startTimeField.disabled = !checkbox.checked;
            endTimeField.disabled = !checkbox.checked;
            
            // Aplicar estilo para mostrar visualmente que los campos están deshabilitados
            const timeFields = document.querySelectorAll(`.${dayName}-time-field`);
            timeFields.forEach(field => {
                if (checkbox.checked) {
                    field.classList.remove('text-muted');
                    field.classList.remove('bg-light');
                } else {
                    field.classList.add('text-muted');
                    field.classList.add('bg-light');
                }
            });
        }
    }
    
    // Configurar listeners para todos los días
    days.forEach(day => {
        const checkbox = document.getElementById(`${day}_is_working_day`);
        if (checkbox) {
            // Inicializar estado
            updateTimeFields(day);
            
            // Añadir listener para cambios
            checkbox.addEventListener('change', function() {
                updateTimeFields(day);
            });
        }
    });
});