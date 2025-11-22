// ============================================
// VISTA DE LISTADO DE VENTAS - RF-05
// ============================================

let ventasData = [];
let ventasOriginales = []; // Para guardar todas las ventas sin filtrar

// Cargar ventas del día
async function cargarVentasDelDia() {
    console.log('Iniciando carga de ventas...');
    try {
        const token = localStorage.getItem('token');
        console.log('Token:', token ? 'Presente' : 'No encontrado');
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };

        // Obtener reporte diario
        console.log('Fetching reporte diario...');
        const reporteResponse = await fetch(`${API_URL}/ventas/diarias`, {
            headers
        });
        console.log('Reporte response status:', reporteResponse.status);
        const reporteData = await reporteResponse.json();
        console.log('Reporte data:', reporteData);

        // Actualizar estadísticas
        document.getElementById('ventasHoy').textContent = reporteData.total_ventas || 0;
        document.getElementById('totalHoy').textContent = formatCurrency(reporteData.monto_total || 0);
        document.getElementById('productosVendidos').textContent = reporteData.productos_vendidos || 0;

        // Obtener lista de ventas
        console.log('Fetching lista de ventas...');
        const ventasResponse = await fetch(`${API_URL}/ventas/`, {
            headers
        });
        console.log('Ventas response status:', ventasResponse.status);
        ventasData = await ventasResponse.json();
        ventasOriginales = [...ventasData]; // Guardar copia de todas las ventas
        console.log('Ventas data:', ventasData);

        renderVentasTable(ventasData);
    } catch (error) {
        console.error('Error cargando ventas:', error);
        showError('Error al cargar las ventas', 'Error de conexión');
        document.getElementById('ventasTableBody').innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 40px; color: #dc3545;">
                    Error al cargar ventas. Intenta de nuevo.
                </td>
            </tr>
        `;
    }
}

// Renderizar tabla de ventas
function renderVentasTable(ventas) {
    const tbody = document.getElementById('ventasTableBody');

    if (!ventas || ventas.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 60px 20px;">
                    <div style="display: inline-block;">
                        <div style="font-size: 48px; margin-bottom: 16px;">📋</div>
                        <div style="font-size: 16px; color: #718096; font-weight: 500;">No hay ventas registradas</div>
                        <div style="font-size: 14px; color: #a0aec0; margin-top: 8px;">Las ventas aparecerán aquí cuando se registren</div>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = ventas.map((venta, index) => `
        <tr style="border-bottom: 1px solid #e2e8f0; transition: background-color 0.2s;"
            onmouseover="this.style.backgroundColor='#f7fafc'"
            onmouseout="this.style.backgroundColor='white'">
            <td style="padding: 16px 20px;">
                <span style="font-weight: 600; color: #4a5568; font-family: monospace;">#${String(venta.id_venta).padStart(4, '0')}</span>
            </td>
            <td style="padding: 16px 20px;">
                <div style="font-weight: 500; color: #2d3748; margin-bottom: 2px;">${venta.nombre_cliente}</div>
            </td>
            <td style="padding: 16px 20px; text-align: center;">
                <span style="display: inline-block; padding: 4px 12px; background: #edf2f7; color: #4a5568; border-radius: 12px; font-weight: 600; font-size: 13px;">
                    ${venta.total_productos || 0}
                </span>
            </td>
            <td style="padding: 16px 20px; text-align: right;">
                <span style="font-weight: 700; color: #38a169; font-size: 15px;">${formatCurrency(venta.total)}</span>
            </td>
            <td style="padding: 16px 20px;">
                <div style="color: #4a5568; font-size: 14px;">${formatearFecha(venta.fecha_venta)}</div>
            </td>
            <td style="padding: 16px 20px; text-align: center;">
                <button onclick="verDetalleVenta(${venta.id_venta})"
                    style="padding: 8px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);"
                    onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 8px rgba(102, 126, 234, 0.3)'"
                    onmouseout="this.style.transform=''; this.style.boxShadow='0 2px 4px rgba(102, 126, 234, 0.2)'">
                    👁️ Ver Detalle
                </button>
            </td>
        </tr>
    `).join('');
}

// Formatear fecha
function formatearFecha(fecha) {
    const date = new Date(fecha);
    const opciones = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('es-CO', opciones);
}

// Ver detalle de una venta
async function verDetalleVenta(idVenta) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/ventas/${idVenta}`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        const venta = await response.json();

        const isMobile = window.innerWidth <= 768;

        const detallesHTML = venta.detalles.map((d, idx) => `
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: ${isMobile ? '10px 8px' : '10px 12px'};">
                    <div style="font-weight: 500; color: #2d3748; font-size: ${isMobile ? '12px' : '13px'};">${d.nombre_producto}</div>
                    <div style="font-size: ${isMobile ? '10px' : '11px'}; color: #718096; margin-top: 2px;">Cód: ${d.codigo || 'N/A'}</div>
                </td>
                <td style="padding: ${isMobile ? '10px 8px' : '10px 12px'}; text-align: center;">
                    <span style="display: inline-block; padding: ${isMobile ? '3px 8px' : '4px 10px'}; background: #edf2f7; color: #4a5568; border-radius: 6px; font-weight: 600; font-size: ${isMobile ? '11px' : '12px'};">
                        ${d.cantidad}
                    </span>
                </td>
                <td style="padding: ${isMobile ? '10px 8px' : '10px 12px'}; text-align: right; color: #4a5568; font-weight: 500; font-size: ${isMobile ? '11px' : '12px'};">
                    ${formatCurrency(d.precio_unitario)}
                </td>
                <td style="padding: ${isMobile ? '10px 8px' : '10px 12px'}; text-align: right; font-weight: 700; color: #38a169; font-size: ${isMobile ? '12px' : '14px'};">
                    ${formatCurrency(d.subtotal)}
                </td>
            </tr>
        `).join('');

        mostrarModalDetalle(venta, detallesHTML);
    } catch (error) {
        console.error('Error:', error);
        showError('Error al cargar detalle de venta', 'Error');
    }
}

// Mostrar modal con detalle
function mostrarModalDetalle(venta, detallesHTML) {
    const overlay = document.getElementById('confirmModalOverlay');
    const modal = overlay.querySelector('.confirm-modal');
    const originalContent = modal.innerHTML;

    // Detectar si es móvil
    const isMobile = window.innerWidth <= 768;

    modal.style.maxWidth = isMobile ? '95vw' : '600px';
    modal.style.maxHeight = isMobile ? '90vh' : '85vh';
    modal.style.overflowY = 'auto';
    modal.style.margin = isMobile ? '10px' : '20px';

    modal.innerHTML = `
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: ${isMobile ? '14px 16px' : '18px 20px'}; margin: -20px -20px 14px -20px; border-radius: 12px 12px 0 0; position: sticky; top: -20px; z-index: 10;">
            <div style="font-size: ${isMobile ? '11px' : '12px'}; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">Detalle de Venta</div>
            <div style="font-size: ${isMobile ? '22px' : '26px'}; font-weight: 700; font-family: monospace;">#${String(venta.id_venta).padStart(4, '0')}</div>
        </div>

        <div style="margin: 0; text-align: left;">
            <!-- Información del Cliente -->
            <div style="background: #f7fafc; padding: ${isMobile ? '14px' : '16px'}; border-radius: 8px; margin-bottom: ${isMobile ? '14px' : '18px'}; border-left: 3px solid #667eea;">
                <h4 style="margin: 0 0 ${isMobile ? '10px' : '12px'} 0; color: #2d3748; font-size: ${isMobile ? '13px' : '14px'}; font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    👤 Información del Cliente
                </h4>
                <div style="display: grid; grid-template-columns: ${isMobile ? '1fr' : 'repeat(2, 1fr)'}; gap: ${isMobile ? '8px' : '10px'}; font-size: ${isMobile ? '12px' : '13px'};">
                    <div>
                        <div style="color: #718096; font-size: ${isMobile ? '10px' : '11px'}; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 3px;">Nombre</div>
                        <div style="color: #2d3748; font-weight: 500;">${venta.nombre_cliente}</div>
                    </div>
                    <div>
                        <div style="color: #718096; font-size: ${isMobile ? '10px' : '11px'}; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 3px;">Documento</div>
                        <div style="color: #2d3748; font-weight: 500;">${venta.documento}</div>
                    </div>
                    <div>
                        <div style="color: #718096; font-size: ${isMobile ? '10px' : '11px'}; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 3px;">Teléfono</div>
                        <div style="color: #2d3748; font-weight: 500;">${venta.telefono || 'No registrado'}</div>
                    </div>
                    <div>
                        <div style="color: #718096; font-size: ${isMobile ? '10px' : '11px'}; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 3px;">Email</div>
                        <div style="color: #2d3748; font-weight: 500;">${venta.email || 'No registrado'}</div>
                    </div>
                </div>
                <div style="margin-top: ${isMobile ? '8px' : '10px'}; padding-top: ${isMobile ? '8px' : '10px'}; border-top: 1px solid #e2e8f0;">
                    <div style="color: #718096; font-size: ${isMobile ? '10px' : '11px'}; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 3px;">Fecha de Venta</div>
                    <div style="color: #2d3748; font-weight: 500; font-size: ${isMobile ? '12px' : '13px'};">📅 ${formatearFecha(venta.fecha_venta)}</div>
                </div>
            </div>

            <!-- Productos -->
            <h4 style="margin: 0 0 ${isMobile ? '8px' : '10px'} 0; color: #2d3748; font-size: ${isMobile ? '13px' : '14px'}; font-weight: 600; display: flex; align-items: center; gap: 6px;">
                📦 Productos
            </h4>
            <div style="border: 1px solid #e2e8f0; border-radius: 8px; overflow: ${isMobile ? 'auto' : 'hidden'}; -webkit-overflow-scrolling: touch;">
                <table style="width: 100%; border-collapse: collapse; font-size: ${isMobile ? '11px' : '13px'};">
                    <thead>
                        <tr style="background: #f7fafc;">
                            <th style="padding: ${isMobile ? '8px 10px' : '10px 12px'}; text-align: left; font-weight: 600; color: #4a5568; font-size: ${isMobile ? '10px' : '11px'}; text-transform: uppercase; letter-spacing: 0.3px;">Producto</th>
                            <th style="padding: ${isMobile ? '8px 10px' : '10px 12px'}; text-align: center; font-weight: 600; color: #4a5568; font-size: ${isMobile ? '10px' : '11px'}; text-transform: uppercase; letter-spacing: 0.3px;">Cant.</th>
                            <th style="padding: ${isMobile ? '8px 10px' : '10px 12px'}; text-align: right; font-weight: 600; color: #4a5568; font-size: ${isMobile ? '10px' : '11px'}; text-transform: uppercase; letter-spacing: 0.3px;">P. Unit.</th>
                            <th style="padding: ${isMobile ? '8px 10px' : '10px 12px'}; text-align: right; font-weight: 600; color: #4a5568; font-size: ${isMobile ? '10px' : '11px'}; text-transform: uppercase; letter-spacing: 0.3px;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>${detallesHTML}</tbody>
                </table>
            </div>

            <!-- Total -->
            <div style="background: linear-gradient(135deg, #38a169 0%, #2f855a 100%); color: white; padding: ${isMobile ? '14px 16px' : '16px 18px'}; border-radius: 8px; margin-top: ${isMobile ? '14px' : '16px'}; text-align: right; position: sticky; bottom: ${isMobile ? '-20px' : '-10px'}; z-index: 10;">
                <div style="font-size: ${isMobile ? '11px' : '12px'}; opacity: 0.9; margin-bottom: 3px;">TOTAL DE LA VENTA</div>
                <div style="font-size: ${isMobile ? '24px' : '28px'}; font-weight: 700;">
                    ${formatCurrency(venta.total)}
                </div>
            </div>
        </div>

        <div class="confirm-modal-actions" style="margin-top: ${isMobile ? '14px' : '18px'};">
            <button class="confirm-btn confirm-btn-confirm" id="closeDetail" style="width: 100%; padding: ${isMobile ? '12px' : '10px'}; font-size: ${isMobile ? '14px' : '14px'}; font-weight: 600; min-height: ${isMobile ? '44px' : 'auto'};">
                Cerrar
            </button>
        </div>
    `;

    overlay.classList.add('active');

    document.getElementById('closeDetail').onclick = () => {
        overlay.classList.remove('active');
        setTimeout(() => {
            modal.innerHTML = originalContent;
            modal.style.maxWidth = '';
            modal.style.maxHeight = '';
            modal.style.overflowY = '';
            modal.style.margin = '';
        }, 300);
    };
}

// Descargar reporte profesional en formato PDF
async function descargarReporte() {
    if (!ventasData || ventasData.length === 0) {
        showWarning('No hay ventas para descargar', 'Sin datos');
        return;
    }

    try {
        const token = localStorage.getItem('token');

        // Mostrar mensaje de generación
        showInfo('Generando reporte PDF profesional...', 'Procesando');

        // Llamar al endpoint del backend para generar el PDF
        const response = await fetch(`${API_URL}/ventas/reporte/pdf`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Error al generar el reporte PDF');
        }

        // Obtener el blob del PDF
        const blob = await response.blob();

        // Obtener el nombre del archivo de los headers (si está disponible)
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'PlayZone_Reporte_Ventas.pdf';

        if (contentDisposition) {
            const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
            if (matches != null && matches[1]) {
                filename = matches[1].replace(/['"]/g, '');
            }
        }

        // Crear enlace de descarga
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();

        // Limpiar
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        showSuccess('Reporte PDF descargado correctamente', 'Descarga completada');
    } catch (error) {
        console.error('Error descargando reporte:', error);
        showError('Error al descargar el reporte PDF', 'Error de descarga');
    }
}

// Filtrar ventas por rango de fechas
function filtrarVentasPorFecha() {
    const fechaInicial = document.getElementById('fechaInicial').value;
    const fechaFinal = document.getElementById('fechaFinal').value;

    if (!fechaInicial && !fechaFinal) {
        showWarning('Selecciona al menos una fecha para filtrar', 'Filtro vacío');
        return;
    }

    let ventasFiltradas = [...ventasOriginales];

    if (fechaInicial) {
        const fechaIni = new Date(fechaInicial + 'T00:00:00');
        ventasFiltradas = ventasFiltradas.filter(venta => {
            const fechaVenta = new Date(venta.fecha_venta);
            return fechaVenta >= fechaIni;
        });
    }

    if (fechaFinal) {
        const fechaFin = new Date(fechaFinal + 'T23:59:59');
        ventasFiltradas = ventasFiltradas.filter(venta => {
            const fechaVenta = new Date(venta.fecha_venta);
            return fechaVenta <= fechaFin;
        });
    }

    ventasData = ventasFiltradas;
    renderVentasTable(ventasFiltradas);

    // Actualizar estadísticas con las ventas filtradas
    actualizarEstadisticasFiltradas(ventasFiltradas);

    showSuccess(`Se encontraron ${ventasFiltradas.length} venta(s)`, 'Filtro aplicado');
}

// Limpiar filtros y mostrar todas las ventas
function limpiarFiltros() {
    document.getElementById('fechaInicial').value = '';
    document.getElementById('fechaFinal').value = '';
    ventasData = [...ventasOriginales];
    renderVentasTable(ventasOriginales);

    // Recargar estadísticas completas
    cargarVentasDelDia();

    showInfo('Mostrando todas las ventas', 'Filtros limpiados');
}

// Actualizar estadísticas basadas en ventas filtradas
function actualizarEstadisticasFiltradas(ventas) {
    const totalVentas = ventas.length;
    const montoTotal = ventas.reduce((sum, venta) => sum + parseFloat(venta.total || 0), 0);
    const productosVendidos = ventas.reduce((sum, venta) => sum + parseInt(venta.total_productos || 0), 0);

    document.getElementById('ventasHoy').textContent = totalVentas;
    document.getElementById('totalHoy').textContent = formatCurrency(montoTotal);
    document.getElementById('productosVendidos').textContent = productosVendidos;
}

// Cargar ventas cuando se accede a la sección
document.addEventListener('DOMContentLoaded', function() {
    // Detectar cuando se muestra la sección de ventas
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            const verVentasSection = document.getElementById('verventas');
            if (verVentasSection && verVentasSection.classList.contains('active-section')) {
                cargarVentasDelDia();
            }
        });
    });

    const config = { attributes: true, subtree: true, attributeFilter: ['class'] };
    const targetNode = document.querySelector('main');
    if (targetNode) {
        observer.observe(targetNode, config);
    }
});
