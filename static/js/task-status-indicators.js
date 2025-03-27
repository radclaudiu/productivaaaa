/**
 * Script para gestionar los indicadores de estado de tareas
 */
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar todos los indicadores de estado
    initializeTaskStatusIndicators();
    
    // Aplicar clases a filas de tareas basadas en estado y prioridad
    applyTaskRowStyles();
    
    // Actualizar los contadores de tareas por estado
    updateTaskCounters();
});

/**
 * Inicializa todos los indicadores de estado en la página
 */
function initializeTaskStatusIndicators() {
    const indicators = document.querySelectorAll('.task-status-indicator');
    
    indicators.forEach(indicator => {
        // Si es un estado de alta prioridad o vencido, añadir animación de pulso
        if (indicator.classList.contains('pending-urgente') || 
            indicator.classList.contains('expired')) {
            indicator.classList.add('pulse');
        }
        
        // Añadir listener para hover si queremos efectos adicionales
        indicator.addEventListener('mouseenter', function() {
            // Podemos añadir efectos adicionales aquí
        });
        
        indicator.addEventListener('mouseleave', function() {
            // Restaurar el estado por defecto
        });
    });
}

/**
 * Aplica clases de estilo a las filas de la tabla basadas en el estado y prioridad de la tarea
 */
function applyTaskRowStyles() {
    const taskRows = document.querySelectorAll('.task-row');
    
    taskRows.forEach(row => {
        const statusClass = row.getAttribute('data-status');
        const priorityClass = row.getAttribute('data-priority');
        
        // Limpiar clases previas
        row.classList.remove(
            'pending-baja', 'pending-media', 'pending-alta', 'pending-urgente',
            'completed', 'expired', 'cancelled'
        );
        
        // Aplicar clase basada en estado
        if (statusClass === 'pendiente') {
            row.classList.add(`pending-${priorityClass}`);
        } else {
            row.classList.add(statusClass === 'completada' ? 'completed' : 
                             statusClass === 'vencida' ? 'expired' : 'cancelled');
        }
    });
}

/**
 * Actualiza los contadores de tareas por estado
 */
function updateTaskCounters() {
    // Contar tareas por estado
    const totalTasks = document.querySelectorAll('.task-row').length;
    const pendingTasks = document.querySelectorAll('.task-row[data-status="pendiente"]').length;
    const completedTasks = document.querySelectorAll('.task-row[data-status="completada"]').length;
    const expiredTasks = document.querySelectorAll('.task-row[data-status="vencida"]').length;
    const cancelledTasks = document.querySelectorAll('.task-row[data-status="cancelada"]').length;
    
    // Actualizar contadores en la interfaz si existen
    updateCounter('total-tasks-counter', totalTasks);
    updateCounter('pending-tasks-counter', pendingTasks);
    updateCounter('completed-tasks-counter', completedTasks);
    updateCounter('expired-tasks-counter', expiredTasks);
    updateCounter('cancelled-tasks-counter', cancelledTasks);
    
    // Actualizar contadores en los botones de filtro
    updateFilterButtonCounter('all', totalTasks);
    updateFilterButtonCounter('pendiente', pendingTasks);
    updateFilterButtonCounter('completada', completedTasks);
    updateFilterButtonCounter('vencida', expiredTasks);
}

/**
 * Actualiza un contador en la interfaz
 */
function updateCounter(id, count) {
    const counterElement = document.getElementById(id);
    if (counterElement) {
        counterElement.textContent = count;
        
        // Añadir clases basadas en la cantidad
        if (count > 0) {
            if (id === 'expired-tasks-counter') {
                counterElement.classList.add('text-danger', 'fw-bold');
            } else if (id === 'pending-tasks-counter') {
                counterElement.classList.add('text-warning', 'fw-bold');
            } else if (id === 'completed-tasks-counter') {
                counterElement.classList.add('text-success', 'fw-bold');
            }
        } else {
            counterElement.classList.remove('text-danger', 'text-warning', 'text-success', 'fw-bold');
        }
    }
}

/**
 * Actualiza el contador en los botones de filtro
 */
function updateFilterButtonCounter(filter, count) {
    const filterBtn = document.querySelector(`.filter-btn[data-filter="${filter}"]`);
    if (filterBtn) {
        // Buscar o crear el badge
        let badge = filterBtn.querySelector('.badge');
        if (!badge) {
            badge = document.createElement('span');
            badge.classList.add('badge', 'rounded-pill', 'ms-1');
            filterBtn.appendChild(badge);
        }
        
        // Actualizar el contenido y estilo
        badge.textContent = count;
        badge.className = 'badge rounded-pill ms-1';
        
        if (filter === 'all') {
            badge.classList.add('bg-primary');
        } else if (filter === 'pendiente') {
            badge.classList.add('bg-warning');
        } else if (filter === 'completada') {
            badge.classList.add('bg-success');
        } else if (filter === 'vencida') {
            badge.classList.add('bg-danger');
        }
    }
}