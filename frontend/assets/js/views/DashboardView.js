// ============================================
// DASHBOARD - VISTA DE INICIO
// ============================================

// Variable global para la gráfica
let ventasDiariasChart = null;

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
        const ingresosVentas = calcularIngresosMes(ventasArray);
        const ingresosServicios = calcularIngresosServiciosMes(serviciosArray);

        const estadisticas = {
            totalProductos: productosArray.length,
            stockBajo: productosArray.filter(p => p.stock_bajo === true || p.cantidad < 10).length,
            ventasHoy: filtrarVentasHoy(ventasArray).length,
            totalVentas: ventasArray.length,
            serviciosPendientes: serviciosArray.filter(s => s.estado === 'En reparacion').length,
            ingresosMes: ingresosVentas + ingresosServicios,
            ingresosVentas: ingresosVentas,
            ingresosServicios: ingresosServicios,
            productoMasVendido: obtenerProductoMasVendido(ventasArray)
        };

        mostrarEstadisticas(estadisticas);
        crearGraficaVentasDiarias(ventasArray);

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
            ingresosVentas: 0,
            ingresosServicios: 0,
            productoMasVendido: { nombre: 'N/A', cantidad: 0, imagen_url: null }
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

// Calcular ingresos de servicios del mes actual
function calcularIngresosServiciosMes(servicios) {
    const ahora = new Date();
    const mesActual = ahora.getMonth();
    const añoActual = ahora.getFullYear();

    return servicios
        .filter(servicio => {
            // Solo contar servicios que estén pagados
            if (!servicio.pagado) return false;

            const fecha = new Date(servicio.fecha_ingreso || servicio.fecha_creacion);
            return fecha.getMonth() === mesActual && fecha.getFullYear() === añoActual;
        })
        .reduce((total, servicio) => total + parseFloat(servicio.costo || 0), 0);
}

// Obtener producto más vendido
function obtenerProductoMasVendido(ventas) {
    const conteo = {};
    const productosInfo = {}; // Guardar info completa del producto

    ventas.forEach(venta => {
        if (venta.productos && Array.isArray(venta.productos)) {
            venta.productos.forEach(item => {
                const id = item.id_producto || item.id;
                if (id) {
                    if (!conteo[id]) {
                        conteo[id] = 0;
                        productosInfo[id] = {
                            nombre: item.nombre || 'Producto',
                            imagen_url: item.imagen_url || null
                        };
                    }
                    conteo[id] += (item.cantidad || 1);
                }
            });
        }
    });

    const entries = Object.entries(conteo);
    if (entries.length === 0) return { nombre: 'N/A', cantidad: 0, imagen_url: null };

    const [id, cantidad] = entries.reduce((max, current) =>
        current[1] > max[1] ? current : max
    );

    return {
        nombre: productosInfo[id].nombre,
        cantidad,
        imagen_url: productosInfo[id].imagen_url
    };
}

// Mostrar estadísticas en el dashboard
function mostrarEstadisticas(stats) {
    // Actualizar tarjetas de estadísticas
    const elemTotalProductos = document.getElementById('stat-total-productos');
    const elemStockBajo = document.getElementById('stat-stock-bajo');
    const elemVentasHoy = document.getElementById('stat-ventas-hoy');
    const elemServiciosPendientes = document.getElementById('stat-servicios-pendientes');
    const elemIngresosMes = document.getElementById('stat-ingresos-mes');
    const elemIngresosVentas = document.getElementById('stat-ingresos-ventas');
    const elemIngresosServicios = document.getElementById('stat-ingresos-servicios');

    if (elemTotalProductos) elemTotalProductos.textContent = stats.totalProductos;
    if (elemStockBajo) elemStockBajo.textContent = stats.stockBajo;
    if (elemVentasHoy) elemVentasHoy.textContent = stats.ventasHoy;
    if (elemServiciosPendientes) elemServiciosPendientes.textContent = stats.serviciosPendientes;

    // Formatear ingresos
    const ingresosTotalesFormateados = formatCurrency(stats.ingresosMes);
    const ingresosVentasFormateados = formatCurrency(stats.ingresosVentas || 0);
    const ingresosServiciosFormateados = formatCurrency(stats.ingresosServicios || 0);

    if (elemIngresosMes) elemIngresosMes.textContent = ingresosTotalesFormateados;
    if (elemIngresosVentas) elemIngresosVentas.textContent = ingresosVentasFormateados;
    if (elemIngresosServicios) elemIngresosServicios.textContent = ingresosServiciosFormateados;

    // Mostrar producto más vendido
    const productoMasVendido = document.getElementById('producto-mas-vendido');
    if (productoMasVendido) {
        const imagenHTML = stats.productoMasVendido.imagen_url
            ? `<img src="${stats.productoMasVendido.imagen_url}" alt="${stats.productoMasVendido.nombre}"
                    style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">`
            : `<div style="width: 80px; height: 80px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 36px; margin-bottom: 12px;">📦</div>`;

        productoMasVendido.innerHTML = `
            ${imagenHTML}
            <div style="font-size: 24px; font-weight: 700; color: #0066cc;">${stats.productoMasVendido.nombre}</div>
            <div style="color: #718096; font-size: 14px; margin-top: 4px;">${stats.productoMasVendido.cantidad} unidades vendidas</div>
        `;
    }
}

// Crear gráfica de ventas diarias (últimos 7 días)
function crearGraficaVentasDiarias(ventas) {
    // Obtener los últimos 7 días
    const hoy = new Date();
    const dias = [];
    const labels = [];
    const ventasPorDia = {};
    const ingresosPorDia = {};

    // Inicializar los últimos 7 días
    for (let i = 6; i >= 0; i--) {
        const fecha = new Date(hoy);
        fecha.setDate(fecha.getDate() - i);
        fecha.setHours(0, 0, 0, 0);

        const fechaStr = fecha.toISOString().split('T')[0];
        dias.push(fechaStr);

        // Formatear etiqueta (ej: "Lun 10")
        const opciones = { weekday: 'short', day: 'numeric' };
        labels.push(fecha.toLocaleDateString('es', opciones));

        ventasPorDia[fechaStr] = 0;
        ingresosPorDia[fechaStr] = 0;
    }

    // Contar ventas e ingresos por día
    ventas.forEach(venta => {
        const fechaVenta = new Date(venta.fecha_venta);
        fechaVenta.setHours(0, 0, 0, 0);
        const fechaStr = fechaVenta.toISOString().split('T')[0];

        if (ventasPorDia.hasOwnProperty(fechaStr)) {
            ventasPorDia[fechaStr]++;
            ingresosPorDia[fechaStr] += parseFloat(venta.total || 0);
        }
    });

    // Preparar datos para la gráfica
    const dataVentas = dias.map(dia => ventasPorDia[dia]);
    const dataIngresos = dias.map(dia => ingresosPorDia[dia]);

    // Destruir gráfica anterior si existe
    if (ventasDiariasChart) {
        ventasDiariasChart.destroy();
    }

    // Crear nueva gráfica
    const ctx = document.getElementById('ventasDiariasChart');
    if (!ctx) return;

    // Crear gradientes
    const gradientVentas = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    gradientVentas.addColorStop(0, 'rgba(102, 126, 234, 0.4)');
    gradientVentas.addColorStop(1, 'rgba(102, 126, 234, 0.0)');

    const gradientIngresos = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    gradientIngresos.addColorStop(0, 'rgba(5, 150, 105, 0.4)');
    gradientIngresos.addColorStop(1, 'rgba(5, 150, 105, 0.0)');

    ventasDiariasChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Número de Ventas',
                    data: dataVentas,
                    backgroundColor: gradientVentas,
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 3,
                    pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y'
                },
                {
                    label: 'Ingresos ($)',
                    data: dataIngresos,
                    backgroundColor: gradientIngresos,
                    borderColor: 'rgba(5, 150, 105, 1)',
                    borderWidth: 3,
                    pointBackgroundColor: 'rgba(5, 150, 105, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            animation: {
                duration: 1500,
                easing: 'easeInOutQuart'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 20,
                        font: {
                            size: 13,
                            family: 'system-ui, -apple-system, sans-serif',
                            weight: '500'
                        },
                        color: '#4a5568'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#2d3748',
                    bodyColor: '#4a5568',
                    borderColor: '#e2e8f0',
                    borderWidth: 1,
                    padding: 16,
                    cornerRadius: 8,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    boxPadding: 6,
                    usePointStyle: true,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.datasetIndex === 1) {
                                // Ingresos en formato moneda
                                label += new Intl.NumberFormat('es-CO', {
                                    style: 'currency',
                                    currency: 'COP',
                                    minimumFractionDigits: 0
                                }).format(context.parsed.y);
                            } else {
                                label += context.parsed.y + ' ventas';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Número de Ventas',
                        color: '#667eea',
                        font: {
                            size: 13,
                            weight: '600',
                            family: 'system-ui, -apple-system, sans-serif'
                        }
                    },
                    ticks: {
                        stepSize: 1,
                        color: '#718096',
                        font: {
                            size: 12
                        },
                        padding: 8
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.03)',
                        lineWidth: 1,
                        drawBorder: false
                    },
                    border: {
                        display: false
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Ingresos (COP)',
                        color: '#059669',
                        font: {
                            size: 13,
                            weight: '600',
                            family: 'system-ui, -apple-system, sans-serif'
                        }
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + new Intl.NumberFormat('es-CO', {
                                notation: 'compact',
                                compactDisplay: 'short'
                            }).format(value);
                        },
                        color: '#718096',
                        font: {
                            size: 12
                        },
                        padding: 8
                    },
                    grid: {
                        drawOnChartArea: false
                    },
                    border: {
                        display: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#4a5568',
                        font: {
                            size: 12,
                            weight: '500'
                        },
                        padding: 8
                    },
                    border: {
                        color: '#e2e8f0'
                    }
                }
            }
        }
    });
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
