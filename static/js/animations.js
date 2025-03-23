/**
 * Animations.js - Manejo de animaciones y microinteracciones
 * 
 * Este archivo contiene funciones para manejar animaciones y microinteracciones
 * que mejoran la experiencia de usuario en la aplicación.
 */

// Namespace para evitar colisiones
const Animations = {
    /**
     * Muestra un overlay de carga con mensaje personalizado
     * @param {string} message - Mensaje a mostrar (opcional)
     */
    showLoadingOverlay: function(message = 'Cargando...') {
        // Crear overlay si no existe
        let overlay = document.getElementById('loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loading-overlay';
            overlay.className = 'loading-overlay';
            
            const content = document.createElement('div');
            content.className = 'loading-content';
            
            // Spinner
            const spinner = document.createElement('div');
            spinner.className = 'spinner';
            content.appendChild(spinner);
            
            // Mensaje
            const messageElem = document.createElement('div');
            messageElem.id = 'loading-message';
            messageElem.className = 'mt-3';
            content.appendChild(messageElem);
            
            overlay.appendChild(content);
            document.body.appendChild(overlay);
        }
        
        // Actualizar mensaje
        document.getElementById('loading-message').textContent = message;
        
        // Mostrar overlay con animación
        setTimeout(() => {
            overlay.classList.add('show');
        }, 10);
    },
    
    /**
     * Oculta el overlay de carga
     */
    hideLoadingOverlay: function() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('show');
            setTimeout(() => {
                if (overlay.parentNode) {
                    overlay.parentNode.removeChild(overlay);
                }
            }, 300); // Esperar a que termine la transición
        }
    },
    
    /**
     * Muestra una animación de éxito
     * @param {HTMLElement} container - Contenedor donde mostrar la animación
     * @param {string} message - Mensaje a mostrar (opcional)
     * @param {Function} callback - Función a ejecutar al finalizar (opcional)
     */
    showSuccess: function(container, message = 'Operación completada con éxito', callback = null) {
        // Limpiar contenedor
        container.innerHTML = '';
        
        // Crear SVG para checkmark
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', 'checkmark');
        svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
        svg.setAttribute('viewBox', '0 0 52 52');
        
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('class', 'checkmark-circle');
        circle.setAttribute('cx', '26');
        circle.setAttribute('cy', '26');
        circle.setAttribute('r', '25');
        circle.setAttribute('fill', 'none');
        
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('class', 'checkmark-check');
        path.setAttribute('fill', 'none');
        path.setAttribute('d', 'M14.1 27.2l7.1 7.2 16.7-16.8');
        
        svg.appendChild(circle);
        svg.appendChild(path);
        
        // Crear mensaje
        const messageElem = document.createElement('p');
        messageElem.className = 'text-center mt-3 fade-in-up';
        messageElem.textContent = message;
        
        // Añadir elementos al contenedor
        container.appendChild(svg);
        container.appendChild(messageElem);
        
        // Ejecutar callback después de la animación si existe
        if (callback) {
            setTimeout(callback, 1500);
        }
    },
    
    /**
     * Muestra una animación de error
     * @param {HTMLElement} container - Contenedor donde mostrar la animación
     * @param {string} message - Mensaje a mostrar (opcional)
     * @param {Function} callback - Función a ejecutar al finalizar (opcional)
     */
    showError: function(container, message = 'Se ha producido un error', callback = null) {
        // Limpiar contenedor
        container.innerHTML = '';
        
        // Crear SVG para cross
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', 'cross');
        svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
        svg.setAttribute('viewBox', '0 0 52 52');
        
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('class', 'cross-circle');
        circle.setAttribute('cx', '26');
        circle.setAttribute('cy', '26');
        circle.setAttribute('r', '25');
        circle.setAttribute('fill', 'none');
        
        const path1 = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path1.setAttribute('class', 'cross-line');
        path1.setAttribute('fill', 'none');
        path1.setAttribute('d', 'M16 16 36 36');
        
        const path2 = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path2.setAttribute('class', 'cross-line');
        path2.setAttribute('fill', 'none');
        path2.setAttribute('d', 'M36 16 16 36');
        
        svg.appendChild(circle);
        svg.appendChild(path1);
        svg.appendChild(path2);
        
        // Crear mensaje
        const messageElem = document.createElement('p');
        messageElem.className = 'text-center mt-3 fade-in-up text-danger';
        messageElem.textContent = message;
        
        // Añadir elementos al contenedor
        container.appendChild(svg);
        container.appendChild(messageElem);
        
        // Ejecutar callback después de la animación si existe
        if (callback) {
            setTimeout(callback, 1500);
        }
    },
    
    /**
     * Inicializa los puntos de carga en el elemento dado
     * @param {HTMLElement} element - Elemento donde crear los puntos
     */
    createLoadingDots: function(element) {
        const dots = document.createElement('div');
        dots.className = 'loading-dots';
        dots.innerHTML = '<span></span><span></span><span></span>';
        
        element.appendChild(dots);
        return dots;
    },
    
    /**
     * Crea un efecto shimmer para contenido en carga
     * @param {HTMLElement} element - Elemento al que aplicar el efecto
     */
    applyShimmerEffect: function(element) {
        // Guardar el contenido original
        const originalContent = element.innerHTML;
        const originalHeight = element.offsetHeight;
        
        // Limpiar y aplicar efecto
        element.innerHTML = '';
        element.style.height = `${originalHeight}px`;
        element.classList.add('shimmer');
        
        return {
            // Método para restaurar el contenido original
            restore: function() {
                element.classList.remove('shimmer');
                element.style.height = 'auto';
                element.innerHTML = originalContent;
            }
        };
    },
    
    /**
     * Inicializa un indicador de progreso
     * @param {HTMLElement} container - Contenedor donde mostrar el progreso
     */
    createProgressBar: function(container) {
        const progress = document.createElement('div');
        progress.className = 'progress-load';
        
        container.appendChild(progress);
        return progress;
    },
    
    /**
     * Inicializa las animaciones de hover en los elementos seleccionados
     */
    initHoverAnimations: function() {
        // Botones con efecto de onda
        document.querySelectorAll('.btn:not(.btn-animated)').forEach(btn => {
            btn.classList.add('btn-animated');
        });
        
        // Elementos con hover float
        document.querySelectorAll('[data-hover="float"]').forEach(elem => {
            elem.classList.add('hover-float');
        });
        
        // Elementos con hover grow
        document.querySelectorAll('[data-hover="grow"]').forEach(elem => {
            elem.classList.add('hover-grow');
        });
    },
    
    /**
     * Anima la entrada de elementos a medida que se hacen visibles
     */
    initScrollAnimations: function() {
        const animateOnScroll = (entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const elem = entry.target;
                    const animationType = elem.dataset.animate;
                    
                    if (animationType) {
                        elem.classList.add(animationType);
                        observer.unobserve(elem);
                    }
                }
            });
        };
        
        // Configurar Intersection Observer
        const observer = new IntersectionObserver(animateOnScroll, {
            root: null,
            threshold: 0.1
        });
        
        // Observar elementos con atributo data-animate
        document.querySelectorAll('[data-animate]').forEach(elem => {
            observer.observe(elem);
        });
    },
    
    /**
     * Función para inicializar todas las animaciones
     */
    init: function() {
        // Agregar CSS de animaciones si no está ya incluido
        if (!document.getElementById('animations-css')) {
            const link = document.createElement('link');
            link.id = 'animations-css';
            link.rel = 'stylesheet';
            link.href = '/static/css/animations.css';
            document.head.appendChild(link);
        }
        
        // Inicializar animaciones de hover
        this.initHoverAnimations();
        
        // Inicializar animaciones de scroll
        this.initScrollAnimations();
        
        // Agregar animación de carga para peticiones AJAX
        $(document).ajaxStart(() => {
            this.showLoadingOverlay();
        });
        
        $(document).ajaxStop(() => {
            this.hideLoadingOverlay();
        });
        
        // Agregar animación a los botones de formulario
        document.querySelectorAll('form button[type="submit"]').forEach(button => {
            button.addEventListener('click', function(e) {
                // No animar si el formulario no es válido
                const form = this.closest('form');
                if (form && !form.checkValidity()) {
                    return;
                }
                
                // Guardar texto original y mostrar animación
                const originalText = this.innerHTML;
                this.innerHTML = `
                    <div class="loading-dots">
                        <span></span><span></span><span></span>
                    </div>
                `;
                this.disabled = true;
                
                // Restaurar después de 10 segundos (por si hay algún problema)
                setTimeout(() => {
                    if (this.disabled) {
                        this.innerHTML = originalText;
                        this.disabled = false;
                    }
                }, 10000);
            });
        });
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    Animations.init();
});