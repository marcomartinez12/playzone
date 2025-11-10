// ============================================
// SISTEMA DE NOTIFICACIONES - PLAY ZONE
// ============================================

// Crear contenedor de notificaciones si no existe
function initNotifications() {
    if (!document.getElementById('notificationContainer')) {
        const container = document.createElement('div');
        container.id = 'notificationContainer';
        container.className = 'notification-container';
        document.body.appendChild(container);
    }

    if (!document.getElementById('confirmModalOverlay')) {
        const modalHTML = `
            <div class="confirm-modal-overlay" id="confirmModalOverlay">
                <div class="confirm-modal">
                    <div class="confirm-modal-icon" id="confirmIcon">⚠️</div>
                    <div class="confirm-modal-title" id="confirmTitle">¿Estás seguro?</div>
                    <div class="confirm-modal-message" id="confirmMessage">Esta acción no se puede deshacer</div>
                    <div class="confirm-modal-actions">
                        <button class="confirm-btn confirm-btn-cancel" id="confirmCancel">Cancelar</button>
                        <button class="confirm-btn confirm-btn-confirm" id="confirmOk">Aceptar</button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
}

// Mostrar notificación
function showNotification(message, type = 'info', title = null, duration = 4000) {
    initNotifications();

    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };

    const titles = {
        success: title || 'Éxito',
        error: title || 'Error',
        warning: title || 'Advertencia',
        info: title || 'Información'
    };

    notification.innerHTML = `
        <div class="notification-icon">${icons[type]}</div>
        <div class="notification-content">
            <div class="notification-title">${titles[type]}</div>
            <div class="notification-message">${message}</div>
        </div>
        <button class="notification-close">×</button>
    `;

    container.appendChild(notification);

    // Cerrar al hacer clic en X
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        closeNotification(notification);
    });

    // Auto-cerrar después de la duración especificada
    if (duration > 0) {
        setTimeout(() => {
            closeNotification(notification);
        }, duration);
    }

    return notification;
}

// Cerrar notificación con animación
function closeNotification(notification) {
    notification.classList.add('closing');
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

// Mostrar modal de confirmación
function showConfirm(options = {}) {
    return new Promise((resolve) => {
        initNotifications();

        const overlay = document.getElementById('confirmModalOverlay');
        const icon = document.getElementById('confirmIcon');
        const title = document.getElementById('confirmTitle');
        const message = document.getElementById('confirmMessage');
        const cancelBtn = document.getElementById('confirmCancel');
        const okBtn = document.getElementById('confirmOk');

        // Configurar modal
        const config = {
            title: options.title || '¿Estás seguro?',
            message: options.message || 'Esta acción no se puede deshacer',
            type: options.type || 'warning',
            confirmText: options.confirmText || 'Aceptar',
            cancelText: options.cancelText || 'Cancelar'
        };

        const iconMap = {
            warning: '⚠️',
            danger: '🗑️',
            info: 'ℹ️'
        };

        icon.textContent = iconMap[config.type] || '⚠️';
        icon.className = `confirm-modal-icon ${config.type}`;
        title.textContent = config.title;
        message.textContent = config.message;
        cancelBtn.textContent = config.cancelText;
        okBtn.textContent = config.confirmText;
        okBtn.className = `confirm-btn confirm-btn-confirm ${config.type === 'danger' ? 'danger' : ''}`;

        // Mostrar modal
        overlay.classList.add('active');

        // Manejar eventos
        const handleCancel = () => {
            overlay.classList.remove('active');
            cancelBtn.removeEventListener('click', handleCancel);
            okBtn.removeEventListener('click', handleOk);
            overlay.removeEventListener('click', handleOverlayClick);
            resolve(false);
        };

        const handleOk = () => {
            overlay.classList.remove('active');
            cancelBtn.removeEventListener('click', handleCancel);
            okBtn.removeEventListener('click', handleOk);
            overlay.removeEventListener('click', handleOverlayClick);
            resolve(true);
        };

        const handleOverlayClick = (e) => {
            if (e.target === overlay) {
                handleCancel();
            }
        };

        cancelBtn.addEventListener('click', handleCancel);
        okBtn.addEventListener('click', handleOk);
        overlay.addEventListener('click', handleOverlayClick);
    });
}

// Atajos para diferentes tipos de notificaciones
function showSuccess(message, title = null) {
    return showNotification(message, 'success', title);
}

function showError(message, title = null) {
    return showNotification(message, 'error', title);
}

function showWarning(message, title = null) {
    return showNotification(message, 'warning', title);
}

function showInfo(message, title = null) {
    return showNotification(message, 'info', title);
}

// Mostrar prompt personalizado
async function showPrompt(title, placeholder = '', defaultValue = '') {
    return new Promise((resolve) => {
        initNotifications();

        const overlay = document.getElementById('confirmModalOverlay');
        const modal = overlay.querySelector('.confirm-modal');

        // Guardar contenido original
        const originalContent = modal.innerHTML;

        // Crear prompt
        modal.innerHTML = `
            <div class="confirm-modal-icon info">✏️</div>
            <div class="confirm-modal-title">${title}</div>
            <div style="margin: 20px 0;">
                <input type="text" id="promptInput"
                    placeholder="${placeholder}"
                    value="${defaultValue}"
                    style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px;">
            </div>
            <div class="confirm-modal-actions">
                <button class="confirm-btn confirm-btn-cancel" id="promptCancel">Cancelar</button>
                <button class="confirm-btn confirm-btn-confirm" id="promptOk">Aceptar</button>
            </div>
        `;

        overlay.classList.add('active');

        const input = document.getElementById('promptInput');
        const cancelBtn = document.getElementById('promptCancel');
        const okBtn = document.getElementById('promptOk');

        input.focus();

        const cleanup = (value) => {
            overlay.classList.remove('active');
            setTimeout(() => {
                modal.innerHTML = originalContent;
            }, 300);
            resolve(value);
        };

        cancelBtn.onclick = () => cleanup(null);
        okBtn.onclick = () => cleanup(input.value);
        input.onkeydown = (e) => {
            if (e.key === 'Enter') cleanup(input.value);
            if (e.key === 'Escape') cleanup(null);
        };
    });
}

// Inicializar al cargar el DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNotifications);
} else {
    initNotifications();
}
