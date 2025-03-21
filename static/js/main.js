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
    const toggle = document.getElementById(toggleId);
    
    if (!input || !toggle) return;
    
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
