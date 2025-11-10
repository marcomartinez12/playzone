// ============================================
// EVENT BUS - SISTEMA DE EVENTOS EN TIEMPO REAL
// ============================================

/**
 * Sistema centralizado de eventos para actualización en tiempo real
 * Permite que diferentes partes de la aplicación se comuniquen sin acoplamiento
 */

const EventBus = {
    /**
     * Emitir un evento
     * @param {string} eventName - Nombre del evento
     * @param {any} data - Datos del evento
     */
    emit(eventName, data = null) {
        const event = new CustomEvent(eventName, { detail: data });
        window.dispatchEvent(event);
        console.log(`[EventBus] Evento emitido: ${eventName}`, data);
    },

    /**
     * Escuchar un evento
     * @param {string} eventName - Nombre del evento
     * @param {function} callback - Función a ejecutar cuando ocurra el evento
     */
    on(eventName, callback) {
        window.addEventListener(eventName, (e) => callback(e.detail));
    },

    /**
     * Dejar de escuchar un evento
     * @param {string} eventName - Nombre del evento
     * @param {function} callback - Función a remover
     */
    off(eventName, callback) {
        window.removeEventListener(eventName, callback);
    }
};

// Eventos disponibles en el sistema
const Events = {
    // Eventos de productos
    PRODUCTO_CREADO: 'producto:creado',
    PRODUCTO_ACTUALIZADO: 'producto:actualizado',
    PRODUCTO_ELIMINADO: 'producto:eliminado',

    // Eventos de ventas
    VENTA_CREADA: 'venta:creada',

    // Eventos de servicios
    SERVICIO_CREADO: 'servicio:creado',
    SERVICIO_ACTUALIZADO: 'servicio:actualizado',
    SERVICIO_ELIMINADO: 'servicio:eliminado',

    // Eventos de clientes
    CLIENTE_CREADO: 'cliente:creado',
    CLIENTE_ACTUALIZADO: 'cliente:actualizado',

    // Evento general de actualización
    DATOS_ACTUALIZADOS: 'datos:actualizados'
};

// Hacer disponible globalmente
window.EventBus = EventBus;
window.Events = Events;
