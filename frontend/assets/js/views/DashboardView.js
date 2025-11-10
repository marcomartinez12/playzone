// ============================================
// DASHBOARD - VISTA DE INICIO
// ============================================

// Cargar estadísticas del dashboard
async function cargarEstadisticasDashboard() {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            console.log('No hay token disponible');
            return;
        }

        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };

        // Cargar productos (siempre disponible)
        const productosResponse = await fetch(`${API_URL}/productos/`, { headers });
        const productos = productosResponse.ok ? await productosResponse.json() : [];

        // Cargar ventas (puede fallar si no hay permisos)
        let ventas = [];
        try {
            const ventasResponse = await fetch(`${API_URL}/ventas/`, { headers });
            if (ventasResponse.ok) {
                ventas = await ventasResponse.json();
            } else {
                console.log('Error al cargar ventas. Status:', ventasResponse.status);
                const errorData = await ventasResponse.text();
                console.log('Detalle:', errorData);

                // Si el token expiró, redirigir al login
                if (ventasResponse.status === 401) {
                    console.log('Token expirado, redirigiendo al login...');
                    localStorage.removeItem('token');
                    localStorage.removeItem('usuario');
                    localStorage.removeItem('isLoggedIn');
                    showWarning('Tu sesión ha expirado. Por favor inicia sesión nuevamente.', 'Sesión expirada');
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 2000);
                    return;
                }
            }
        } catch (e) {
            console.log('No se pudieron cargar ventas:', e);
        }

        // Cargar servicios (puede fallar si no hay permisos)
        let servicios = [];
        try {
            const serviciosResponse = await fetch(`${API_URL}/servicios/`, { headers });
            if (serviciosResponse.ok) {
                servicios = await serviciosResponse.json();
            } else {
                console.log('Error al cargar servicios. Status:', serviciosResponse.status);
                const errorData = await serviciosResponse.text();
                console.log('Detalle:', errorData);
            }
        } catch (e) {
            console.log('No se pudieron cargar servicios:', e);
        }

        // Asegurar que sean arrays
        const productosArray = Array.isArray(productos) ? productos : [];
        const ventasArray = Array.isArray(ventas) ? ventas : [];
        const serviciosArray = Array.isArray(servicios) ? servicios : [];

        // Calcular estadísticas
        const estadisticas = {
            totalProductos: productosArray.length,
            stockBajo: productosArray.filter(p => p.stock_bajo === true || p.cantidad < 10).length,
            ventasHoy: filtrarVentasHoy(ventasArray).length,
            totalVentas: ventasArray.length,
            serviciosPendientes: serviciosArray.filter(s => s.estado === 'En reparacion').length,
            ingresosMes: calcularIngresosMes(ventasArray),
            productoMasVendido: obtenerProductoMasVendido(ventasArray)
        };

        mostrarEstadisticas(estadisticas);

    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
        // Mostrar estadísticas vacías en caso de error
        mostrarEstadisticas({
            totalProductos: 0,
            stockBajo: 0,
            ventasHoy: 0,
            totalVentas: 0,
            serviciosPendientes: 0,
            ingresosMes: 0,
            productoMasVendido: { nombre: 'N/A', cantidad: 0 }
        });
    }
}

// Filtrar ventas de hoy
function filtrarVentasHoy(ventas) {
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    return ventas.filter(venta => {
        const fechaVenta = new Date(venta.fecha_venta);
        fechaVenta.setHours(0, 0, 0, 0);
        return fechaVenta.getTime() === hoy.getTime();
    });
}

// Calcular ingresos del mes actual
function calcularIngresosMes(ventas) {
    const ahora = new Date();
    const mesActual = ahora.getMonth();
    const añoActual = ahora.getFullYear();

    return ventas
        .filter(venta => {
            const fecha = new Date(venta.fecha_venta);
            return fecha.getMonth() === mesActual && fecha.getFullYear() === añoActual;
        })
        .reduce((total, venta) => total + parseFloat(venta.total), 0);
}

// Obtener producto más vendido
function obtenerProductoMasVendido(ventas) {
    const conteo = {};

    ventas.forEach(venta => {
        if (venta.productos && Array.isArray(venta.productos)) {
            venta.productos.forEach(item => {
                const nombre = item.nombre || 'Producto';
                conteo[nombre] = (conteo[nombre] || 0) + (item.cantidad || 1);
            });
        }
    });

    const entries = Object.entries(conteo);
    if (entries.length === 0) return { nombre: 'N/A', cantidad: 0 };

    const [nombre, cantidad] = entries.reduce((max, current) =>
        current[1] > max[1] ? current : max
    );

    return { nombre, cantidad };
}

// Mostrar estadísticas en el dashboard
function mostrarEstadisticas(stats) {
    // Actualizar tarjetas de estadísticas
    const elemTotalProductos = document.getElementById('stat-total-productos');
    const elemStockBajo = document.getElementById('stat-stock-bajo');
    const elemVentasHoy = document.getElementById('stat-ventas-hoy');
    const elemTotalVentas = document.getElementById('stat-total-ventas');
    const elemServiciosPendientes = document.getElementById('stat-servicios-pendientes');
    const elemIngresosMes = document.getElementById('stat-ingresos-mes');

    if (elemTotalProductos) elemTotalProductos.textContent = stats.totalProductos;
    if (elemStockBajo) elemStockBajo.textContent = stats.stockBajo;
    if (elemVentasHoy) elemVentasHoy.textContent = stats.ventasHoy;
    if (elemTotalVentas) elemTotalVentas.textContent = stats.totalVentas;
    if (elemServiciosPendientes) elemServiciosPendientes.textContent = stats.serviciosPendientes;

    // Formatear ingresos del mes
    const ingresosFormateados = new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
    }).format(stats.ingresosMes);

    if (elemIngresosMes) elemIngresosMes.textContent = ingresosFormateados;

    // Mostrar producto más vendido
    const productoMasVendido = document.getElementById('producto-mas-vendido');
    if (productoMasVendido) {
        productoMasVendido.innerHTML = `
            <div style="font-size: 24px; font-weight: 700; color: #0066cc;">${stats.productoMasVendido.nombre}</div>
            <div style="color: #718096; font-size: 14px; margin-top: 4px;">${stats.productoMasVendido.cantidad} unidades vendidas</div>
        `;
    }
}

// Cargar al iniciar
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('home')) {
        // Cargar estadísticas al cargar la página
        cargarEstadisticasDashboard();

        // Recargar cada 60 segundos
        setInterval(cargarEstadisticasDashboard, 60000);

        // Escuchar eventos en tiempo real para actualizar dashboard
        EventBus.on(Events.PRODUCTO_CREADO, () => {
            console.log('[Dashboard] Producto creado - Actualizando...');
            cargarEstadisticasDashboard();
        });

        EventBus.on(Events.PRODUCTO_ACTUALIZADO, () => {
            console.log('[Dashboard] Producto actualizado - Actualizando...');
            cargarEstadisticasDashboard();
        });

        EventBus.on(Events.PRODUCTO_ELIMINADO, () => {
            console.log('[Dashboard] Producto eliminado - Actualizando...');
            cargarEstadisticasDashboard();
        });

        EventBus.on(Events.VENTA_CREADA, () => {
            console.log('[Dashboard] Venta creada - Actualizando...');
            cargarEstadisticasDashboard();
        });

        EventBus.on(Events.SERVICIO_CREADO, () => {
            console.log('[Dashboard] Servicio creado - Actualizando...');
            cargarEstadisticasDashboard();
        });

        EventBus.on(Events.SERVICIO_ACTUALIZADO, () => {
            console.log('[Dashboard] Servicio actualizado - Actualizando...');
            cargarEstadisticasDashboard();
        });
    }
});
