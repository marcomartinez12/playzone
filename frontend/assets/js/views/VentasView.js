// ============================================
// VISTA DE LISTADO DE VENTAS - RF-05
// ============================================

let ventasData = [];

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
        document.getElementById('totalHoy').textContent = `$${(reporteData.monto_total || 0).toLocaleString()}`;
        document.getElementById('productosVendidos').textContent = reporteData.productos_vendidos || 0;

        // Obtener lista de ventas
        console.log('Fetching lista de ventas...');
        const ventasResponse = await fetch(`${API_URL}/ventas/`, {
            headers
        });
        console.log('Ventas response status:', ventasResponse.status);
        ventasData = await ventasResponse.json();
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
                <span style="font-weight: 700; color: #38a169; font-size: 15px;">$${venta.total.toLocaleString('es-CO')}</span>
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

        const detallesHTML = venta.detalles.map((d, idx) => `
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 12px 16px;">
                    <div style="font-weight: 500; color: #2d3748;">${d.nombre_producto}</div>
                    <div style="font-size: 12px; color: #718096; margin-top: 2px;">Código: ${d.codigo || 'N/A'}</div>
                </td>
                <td style="padding: 12px 16px; text-align: center;">
                    <span style="display: inline-block; padding: 4px 10px; background: #edf2f7; color: #4a5568; border-radius: 8px; font-weight: 600;">
                        ${d.cantidad}
                    </span>
                </td>
                <td style="padding: 12px 16px; text-align: right; color: #4a5568; font-weight: 500;">
                    $${d.precio_unitario.toLocaleString('es-CO')}
                </td>
                <td style="padding: 12px 16px; text-align: right; font-weight: 700; color: #38a169; font-size: 15px;">
                    $${d.subtotal.toLocaleString('es-CO')}
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

    modal.style.maxWidth = '700px';
    modal.innerHTML = `
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; margin: -20px -20px 20px -20px; border-radius: 12px 12px 0 0;">
            <div style="font-size: 14px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Detalle de Venta</div>
            <div style="font-size: 32px; font-weight: 700; font-family: monospace;">#${String(venta.id_venta).padStart(4, '0')}</div>
        </div>

        <div style="margin: 0 0 24px 0; text-align: left;">
            <!-- Información del Cliente -->
            <div style="background: #f7fafc; padding: 20px; border-radius: 10px; margin-bottom: 24px; border-left: 4px solid #667eea;">
                <h4 style="margin: 0 0 16px 0; color: #2d3748; font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: 8px;">
                    👤 Información del Cliente
                </h4>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; font-size: 14px;">
                    <div>
                        <div style="color: #718096; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Nombre</div>
                        <div style="color: #2d3748; font-weight: 500;">${venta.nombre_cliente}</div>
                    </div>
                    <div>
                        <div style="color: #718096; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Documento</div>
                        <div style="color: #2d3748; font-weight: 500;">${venta.documento}</div>
                    </div>
                    <div>
                        <div style="color: #718096; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Teléfono</div>
                        <div style="color: #2d3748; font-weight: 500;">${venta.telefono || 'No registrado'}</div>
                    </div>
                    <div>
                        <div style="color: #718096; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Email</div>
                        <div style="color: #2d3748; font-weight: 500;">${venta.email || 'No registrado'}</div>
                    </div>
                </div>
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e2e8f0;">
                    <div style="color: #718096; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Fecha de Venta</div>
                    <div style="color: #2d3748; font-weight: 500;">📅 ${formatearFecha(venta.fecha_venta)}</div>
                </div>
            </div>

            <!-- Productos -->
            <h4 style="margin: 0 0 12px 0; color: #2d3748; font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: 8px;">
                📦 Productos
            </h4>
            <div style="border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden;">
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    <thead>
                        <tr style="background: #f7fafc;">
                            <th style="padding: 12px 16px; text-align: left; font-weight: 600; color: #4a5568; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Producto</th>
                            <th style="padding: 12px 16px; text-align: center; font-weight: 600; color: #4a5568; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Cant.</th>
                            <th style="padding: 12px 16px; text-align: right; font-weight: 600; color: #4a5568; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Precio Unit.</th>
                            <th style="padding: 12px 16px; text-align: right; font-weight: 600; color: #4a5568; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>${detallesHTML}</tbody>
                </table>
            </div>

            <!-- Total -->
            <div style="background: linear-gradient(135deg, #38a169 0%, #2f855a 100%); color: white; padding: 20px; border-radius: 10px; margin-top: 20px; text-align: right;">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 4px;">TOTAL DE LA VENTA</div>
                <div style="font-size: 32px; font-weight: 700;">
                    $${venta.total.toLocaleString('es-CO')}
                </div>
            </div>
        </div>

        <div class="confirm-modal-actions" style="margin-top: 24px;">
            <button class="confirm-btn confirm-btn-confirm" id="closeDetail" style="width: 100%; padding: 12px; font-size: 15px; font-weight: 600;">
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
        }, 300);
    };
}

// Descargar reporte en formato CSV
function descargarReporte() {
    if (!ventasData || ventasData.length === 0) {
        showWarning('No hay ventas para descargar', 'Sin datos');
        return;
    }

    const fecha = new Date().toISOString().split('T')[0];
    let csv = 'ID,Cliente,Productos,Total,Fecha,Usuario\n';

    ventasData.forEach(venta => {
        csv += `${venta.id_venta},"${venta.nombre_cliente}",${venta.total_productos || 0},$${venta.total},"${formatearFecha(venta.fecha_venta)}","${venta.nombre_usuario}"\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `ventas_${fecha}.csv`;
    link.click();

    showSuccess('Reporte descargado correctamente', 'Descarga completada');
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
