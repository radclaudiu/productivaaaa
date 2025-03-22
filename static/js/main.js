// main.js - General JavaScript functionality for the application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Handle confirmation dialogs
    document.querySelectorAll('.confirm-action').forEach(button => {
        button.addEventListener('click', function(e) {
            if(!confirm(this.getAttribute('data-confirm-message') || '¿Estás seguro de realizar esta acción?')) {
                e.preventDefault();
                return false;
            }
        });
    });

    // File input custom display
    document.querySelectorAll('.custom-file-input').forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0].name;
            const fileLabel = this.nextElementSibling;
            fileLabel.textContent = fileName;
        });
    });

    // Handle search form
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[name="query"]');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                return false;
            }
        });
    }

    // Handle sidebar toggle on mobile
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('d-none');
        });
    }

    // Handle date inputs (for browsers that don't support date input)
    document.querySelectorAll('input[type="date"]').forEach(input => {
        if (input.type !== 'date') {
            // Add a fallback datepicker if browser doesn't support date input
            console.log('Browser does not support date input, consider adding a datepicker library');
        }
    });

    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        document.querySelectorAll('.alert-dismissible').forEach(alert => {
            if (alert && !alert.classList.contains('alert-danger')) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
    }, 5000);

    // Handle table row click to navigate to detail view
    document.querySelectorAll('tr[data-href]').forEach(row => {
        row.addEventListener('click', function(e) {
            // Ignore clicks on buttons or links within the row
            if (
                e.target.tagName === 'A' ||
                e.target.tagName === 'BUTTON' ||
                e.target.closest('a') ||
                e.target.closest('button')
            ) {
                return;
            }
            
            window.location.href = this.dataset.href;
        });
        
        // Add pointer cursor to indicate clickable
        row.classList.add('cursor-pointer');
    });

    // Form validation styles
    document.querySelectorAll('.form-control').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.checkValidity()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else if (this.value !== '') {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
        });
    });
});

// Function to handle form confirmation before submission
function confirmFormSubmit(formId, message) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        if (!confirm(message || '¿Estás seguro de enviar este formulario?')) {
            e.preventDefault();
            return false;
        }
    });
}

// Function to toggle password visibility
function togglePasswordVisibility(inputId, toggleId) {
    const input = document.getElementById(inputId);
    
    if (!input) return;
    
    // Si no se proporciona toggleId, asumimos que se está llamando directamente (onclick)
    if (!toggleId) {
        const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
        input.setAttribute('type', type);
        
        // Buscamos el botón adjunto
        const button = document.querySelector(`button[onclick*="togglePasswordVisibility('${inputId}')"]`);
        if (button) {
            if (type === 'password') {
                button.innerHTML = '<i class="bi bi-eye"></i>';
            } else {
                button.innerHTML = '<i class="bi bi-eye-slash"></i>';
            }
        }
        return;
    }
    
    // Comportamiento para escuchador de eventos
    const toggle = document.getElementById(toggleId);
    if (!toggle) return;
    
    toggle.addEventListener('click', function() {
        const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
        input.setAttribute('type', type);
        
        // Toggle icon
        if (type === 'password') {
            this.innerHTML = '<i class="bi bi-eye"></i>';
        } else {
            this.innerHTML = '<i class="bi bi-eye-slash"></i>';
        }
    });
}

// Función para copiar texto al portapapeles
function copyToClipboard(text) {
    // Si recibimos un ID en lugar de texto, obtenemos el valor del campo
    if (typeof text === 'string' && document.getElementById(text)) {
        const element = document.getElementById(text);
        text = element.value || element.textContent;
    }
    
    // Crear un elemento temporal
    const tempElement = document.createElement('textarea');
    tempElement.value = text;
    document.body.appendChild(tempElement);
    
    // Seleccionar y copiar
    tempElement.select();
    document.execCommand('copy');
    
    // Eliminar el elemento temporal
    document.body.removeChild(tempElement);
    
    // Mostrar notificación
    const toast = `<div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">
        <div class="toast align-items-center text-white bg-success border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-check-circle me-2"></i> Texto copiado al portapapeles
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    </div>`;
    
    document.body.insertAdjacentHTML('beforeend', toast);
    const toastElement = document.querySelector('.toast:last-child');
    const bsToast = new bootstrap.Toast(toastElement);
    bsToast.show();
}

// Función para cargar credenciales del portal
function loadPortalCredentials(locationId) {
    // Verificar que los elementos existen
    const usernameElement = document.getElementById('portal-username');
    const passwordContainer = document.getElementById('password-container');
    
    // Chequear si estamos en la página de detalles del local (tiene otro formato)
    const portalPasswordField = document.getElementById('portalPassword');
    if (portalPasswordField) {
        // Estamos en la página de detalles del local
        return loadLocationDetailCredentials(locationId);
    }
    
    if (!usernameElement || !passwordContainer) {
        console.error('Elementos necesarios no encontrados');
        return;
    }
    
    // Obtener el token CSRF
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Mostrar indicador de carga
    passwordContainer.innerHTML = '<div class="spinner-border spinner-border-sm text-primary" role="status"><span class="visually-hidden">Cargando...</span></div>';
    
    // Realizar la solicitud AJAX
    fetch(`/tasks/api/get-portal-credentials/${locationId}`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Actualizar el username
            if (usernameElement) {
                usernameElement.textContent = data.username || 'No configurado';
            }
            
            // Mostrar la contraseña
            if (data.username) {
                passwordContainer.innerHTML = `
                    <div class="input-group">
                        <input type="text" class="form-control" id="portal-password-field" value="${data.password}" readonly>
                        <button class="btn btn-outline-secondary" type="button" onclick="copyToClipboard('portal-password-field')">
                            <i class="bi bi-clipboard"></i>
                        </button>
                    </div>`;
            } else {
                passwordContainer.innerHTML = '<em>No configurado</em>';
            }
        } else {
            passwordContainer.innerHTML = `<span class="text-danger">Error: ${data.error || 'No se pudo cargar'}</span>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        passwordContainer.innerHTML = '<span class="text-danger">Error de conexión</span>';
    });
}

// Función específica para cargar las credenciales en la página de detalles del local
function loadLocationDetailCredentials(locationId) {
    // Verificar que el elemento existe
    const portalPasswordField = document.getElementById('portalPassword');
    const portalUsernameField = document.getElementById('portalUsername');
    
    if (!portalPasswordField) {
        console.error('Campo de contraseña no encontrado');
        return;
    }
    
    // Obtener el token CSRF
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Mostrar indicador de carga
    if (portalPasswordField) {
        portalPasswordField.value = 'Cargando...';
    }
    
    // Realizar la solicitud AJAX
    fetch(`/tasks/api/get-portal-credentials/${locationId}`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Actualizar los campos
            if (portalUsernameField) {
                portalUsernameField.value = data.username;
            }
            
            if (portalPasswordField) {
                portalPasswordField.value = data.password;
            }
        } else {
            if (portalPasswordField) {
                portalPasswordField.value = 'Error al cargar las credenciales';
            }
            console.error('Error:', data.error || 'No se pudo cargar las credenciales');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (portalPasswordField) {
            portalPasswordField.value = 'Error de conexión';
        }
    });
}

// Función para mostrar/ocultar la contraseña del portal
function showPortalPassword(locationId) {
    const passwordField = document.getElementById('portal-password-field');
    const passwordButton = passwordField.nextElementSibling;
    
    if (!passwordField || !passwordButton) return;
    
    // Alternar entre mostrar y ocultar la contraseña
    if (passwordField.type === 'text') {
        passwordField.type = 'password';
        passwordButton.innerHTML = '<i class="bi bi-eye"></i>';
    } else {
        passwordField.type = 'text';
        passwordButton.innerHTML = '<i class="bi bi-eye-slash"></i>';
    }
}

// Esta función ya no se usa ya que las credenciales son fijas
// Se mantiene por compatibilidad con versiones anteriores
function regeneratePortalPassword(locationId) {
    alert('Las credenciales del portal son fijas y no pueden ser regeneradas. Use las credenciales proporcionadas.');
}
