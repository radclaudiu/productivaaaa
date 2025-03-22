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

// Función para cargar credenciales del portal
function loadPortalCredentials(locationId) {
    // Verificar que los elementos existen
    const usernameElement = document.getElementById('portal-username');
    const passwordElement = document.getElementById('portal-password');
    const passwordContainer = document.getElementById('password-container');
    
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
            
            // Crear botón para mostrar contraseña solo si tenemos username
            if (data.username) {
                passwordContainer.innerHTML = `
                    <div class="input-group">
                        <input type="password" class="form-control" id="portal-password-field" value="Haga clic para mostrar" readonly>
                        <button class="btn btn-outline-secondary" type="button" onclick="showPortalPassword(${locationId})">
                            <i class="bi bi-eye"></i>
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

// Función para mostrar la contraseña del portal
function showPortalPassword(locationId) {
    const passwordField = document.getElementById('portal-password-field');
    const passwordButton = passwordField.nextElementSibling;
    
    if (!passwordField || !passwordButton) return;
    
    // Obtener el token CSRF
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Si ya está mostrando la contraseña, ocultarla
    if (passwordField.type === 'text') {
        passwordField.type = 'password';
        passwordField.value = 'Haga clic para mostrar';
        passwordButton.innerHTML = '<i class="bi bi-eye"></i>';
        return;
    }
    
    // Mostrar indicador de carga
    passwordButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    passwordField.value = 'Cargando...';
    
    // Realizar la solicitud AJAX para obtener la contraseña
    fetch(`/tasks/api/regenerate-password/${locationId}?show_only=true`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            passwordField.type = 'text';
            passwordField.value = data.password;
            passwordButton.innerHTML = '<i class="bi bi-eye-slash"></i>';
        } else {
            passwordField.value = 'Error al cargar';
            passwordButton.innerHTML = '<i class="bi bi-eye"></i>';
            alert('Error: ' + (data.error || 'No se pudo cargar la contraseña'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        passwordField.value = 'Error de conexión';
        passwordButton.innerHTML = '<i class="bi bi-eye"></i>';
    });
}

// Función para regenerar la contraseña del portal
function regeneratePortalPassword(locationId) {
    if (!confirm('¿Está seguro de que desea regenerar la contraseña del portal? La contraseña actual dejará de funcionar.')) {
        return;
    }
    
    // Obtener el token CSRF
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Mostrar indicador de carga
    const regenerateButton = document.querySelector('.regenerate-password');
    const originalContent = regenerateButton.innerHTML;
    regenerateButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Regenerando...';
    regenerateButton.disabled = true;
    
    // Realizar la solicitud AJAX
    fetch(`/tasks/api/regenerate-password/${locationId}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostrar la nueva contraseña
            alert(`Contraseña regenerada con éxito: ${data.password}\n\nGuarde esta contraseña en un lugar seguro.`);
            
            // Actualizar el campo de contraseña si está visible
            const passwordField = document.getElementById('portal-password-field');
            if (passwordField && passwordField.type === 'text') {
                passwordField.value = data.password;
            }
        } else {
            alert('Error: ' + (data.error || 'No se pudo regenerar la contraseña'));
        }
        
        // Restaurar el botón
        regenerateButton.innerHTML = originalContent;
        regenerateButton.disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error de conexión al intentar regenerar la contraseña');
        
        // Restaurar el botón
        regenerateButton.innerHTML = originalContent;
        regenerateButton.disabled = false;
    });
}
