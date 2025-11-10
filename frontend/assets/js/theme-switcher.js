// ============================================
// SISTEMA DE CAMBIO DE TEMA
// ============================================

// Inicializar tema al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    // Obtener tema guardado
    const savedTheme = localStorage.getItem('theme') || 'light';

    // Aplicar tema guardado al body también (por si acaso)
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        document.documentElement.classList.add('dark-theme');
    }
});

// Función para cambiar el tema
function toggleTheme() {
    const html = document.documentElement;
    const body = document.body;
    const isDark = html.classList.contains('dark-theme') || body.classList.contains('dark-theme');

    if (isDark) {
        // Cambiar a tema claro
        html.classList.remove('dark-theme');
        body.classList.remove('dark-theme');
        localStorage.setItem('theme', 'light');

        // Mostrar notificación
        if (typeof showSuccess === 'function') {
            showSuccess('Tema claro activado', 'Tema cambiado');
        }
    } else {
        // Cambiar a tema oscuro
        html.classList.add('dark-theme');
        body.classList.add('dark-theme');
        localStorage.setItem('theme', 'dark');

        // Mostrar notificación
        if (typeof showSuccess === 'function') {
            showSuccess('Tema oscuro activado', 'Tema cambiado');
        }
    }

    // Agregar animación al botón
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.style.transform = 'rotate(360deg) scale(1.2)';
        setTimeout(() => {
            themeToggle.style.transform = '';
        }, 300);
    }
}
