// ============================================
// VISTA DE SERVICIOS DE REPARACIÓN - RF-06
// ============================================

let serviciosData = [];
let servicioEditando = null;

// Cargar servicios
async function cargarServicios() {
    console.log('Cargando servicios...');
    try {
        const token = localStorage.getItem('token');
        const filtroEstado = document.getElementById('filtroEstadoServicio').value;

        let url = `${API_URL}/servicios/`;
        if (filtroEstado) {
            url += `?estado=${encodeURIComponent(filtroEstado)}`;
        }

        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        serviciosData = await response.json();
        console.log('Servicios cargados:', serviciosData);
        renderServiciosTable(serviciosData);
    } catch (error) {
        console.error('Error cargando servicios:', error);
        showError('Error al cargar servicios', 'Error de conexión');
        document.getElementById('serviciosTableBody').innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 60px 20px;">
                    <div style="color: #dc3545;">Error al cargar servicios. Intenta de nuevo.</div>
                </td>
            </tr>
        `;
    }
}

// Buscar servicios
async function buscarServicios() {
    const termino = document.getElementById('buscarServicio').value.trim();

    if (!termino) {
        cargarServicios();
        return;
    }

    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/servicios/buscar?termino=${encodeURIComponent(termino)}`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        serviciosData = await response.json();
        renderServiciosTable(serviciosData);
    } catch (error) {
        console.error('Error buscando servicios:', error);
        showError('Error al buscar servicios', 'Error');
    }
}

// Renderizar tabla de servicios
function renderServiciosTable(servicios) {
    const tbody = document.getElementById('serviciosTableBody');

    if (!servicios || servicios.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 60px 20px;">
                    <div style="display: inline-block;">
                        <div style="font-size: 48px; margin-bottom: 16px;">🔧</div>
                        <div style="font-size: 16px; color: #718096; font-weight: 500;">No hay servicios registrados</div>
                        <div style="font-size: 14px; color: #a0aec0; margin-top: 8px;">Registra un nuevo servicio para comenzar</div>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = servicios.map(servicio => {
        const estadoColor = {
            'En reparacion': '#f59e0b',
            'Listo': '#10b981',
            'Entregado': '#6b7280'
        };

        const estadoIcon = {
            'En reparacion': '⚙️',
            'Listo': '✅',
            'Entregado': '📦'
        };

        const estadoTexto = {
            'En reparacion': 'En reparación',
            'Listo': 'Listo',
            'Entregado': 'Entregado'
        };

        return `
            <tr style="border-bottom: 1px solid #e2e8f0; transition: background-color 0.2s;"
                onmouseover="this.style.backgroundColor='#f7fafc'"
                onmouseout="this.style.backgroundColor='white'">
                <td style="padding: 16px 20px;">
                    <span style="font-weight: 600; color: #4a5568; font-family: monospace;">#${String(servicio.id_servicio).padStart(4, '0')}</span>
                </td>
                <td style="padding: 16px 20px;">
                    <div style="font-weight: 500; color: #2d3748;">${servicio.nombre_cliente || 'Cliente desconocido'}</div>
                    ${servicio.telefono_cliente ? `<div style="font-size: 12px; color: #718096; margin-top: 2px;">📞 ${servicio.telefono_cliente}</div>` : ''}
                </td>
                <td style="padding: 16px 20px;">
                    <div style="font-weight: 500; color: #2d3748;">🎮 ${servicio.consola}</div>
                </td>
                <td style="padding: 16px 20px;">
                    <div style="color: #4a5568; max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        ${servicio.descripcion}
                    </div>
                </td>
                <td style="padding: 16px 20px; text-align: center;">
                    <span style="display: inline-flex; align-items: center; gap: 4px; padding: 6px 12px; background: ${estadoColor[servicio.estado]}15; color: ${estadoColor[servicio.estado]}; border-radius: 12px; font-weight: 600; font-size: 12px;">
                        ${estadoIcon[servicio.estado]} ${estadoTexto[servicio.estado]}
                    </span>
                </td>
                <td style="padding: 16px 20px; text-align: right;">
                    <span style="font-weight: 700; color: #2d3748; font-size: 15px;">
                        ${servicio.costo ? formatCurrency(servicio.costo) : 'Por definir'}
                    </span>
                </td>
                <td style="padding: 16px 20px; text-align: center;">
                    <div style="display: flex; gap: 8px; justify-content: center;">
                        <button onclick="editarServicio(${servicio.id_servicio})" title="Editar"
                            style="padding: 6px 12px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; transition: background 0.2s;"
                            onmouseover="this.style.background='#5568d3'"
                            onmouseout="this.style.background='#667eea'">
                            ✏️
                        </button>
                        <button onclick="eliminarServicio(${servicio.id_servicio})" title="Eliminar"
                            style="padding: 6px 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; transition: background 0.2s;"
                            onmouseover="this.style.background='#dc2626'"
                            onmouseout="this.style.background='#ef4444'">
                            🗑️
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

// Abrir modal para nuevo servicio
function abrirModalServicio() {
    servicioEditando = null;
    mostrarModalServicio();
}

// Mostrar modal de servicio
function mostrarModalServicio(servicio = null) {
    const overlay = document.getElementById('confirmModalOverlay');
    const modal = overlay.querySelector('.confirm-modal');
    const originalContent = modal.innerHTML;

    const esEdicion = servicio !== null;
    servicioEditando = servicio;

    // Detectar si es móvil
    const isMobile = window.innerWidth <= 768;

    modal.style.maxWidth = isMobile ? '95vw' : '500px';
    modal.style.maxHeight = isMobile ? '90vh' : '85vh';
    modal.style.overflowY = 'auto';
    modal.style.margin = isMobile ? '10px' : '20px';

    modal.innerHTML = `
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: ${isMobile ? '12px 14px' : '14px 18px'}; margin: -20px -20px 14px -20px; border-radius: 12px 12px 0 0; position: sticky; top: -20px; z-index: 10;">
            <div style="font-size: ${isMobile ? '10px' : '11px'}; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">
                ${esEdicion ? 'Editar Servicio' : 'Nuevo Servicio'}
            </div>
            <div style="font-size: ${isMobile ? '16px' : '18px'}; font-weight: 700;">
                ${esEdicion ? `#${String(servicio.id_servicio).padStart(4, '0')}` : '🔧 Registrar'}
            </div>
        </div>

        <div style="margin: 0; text-align: left;">
            <form id="formServicio">
                <!-- Datos del Cliente -->
                <div style="margin-bottom: ${isMobile ? '10px' : '12px'};">
                    <label style="display: block; font-size: ${isMobile ? '10px' : '11px'}; font-weight: 600; color: #4a5568; margin-bottom: 4px;">
                        Documento *
                    </label>
                    <div style="display: flex; gap: 6px;">
                        <input type="text" id="servicioClienteDocumento" required inputmode="numeric"
                            value="${esEdicion && servicio.documento_cliente ? servicio.documento_cliente : ''}"
                            ${esEdicion ? 'readonly' : ''}
                            placeholder="Cédula o NIT"
                            style="flex: 1; padding: ${isMobile ? '10px 8px' : '8px 10px'}; border: 1px solid #e2e8f0; border-radius: 6px; font-size: ${isMobile ? '14px' : '13px'}; ${esEdicion ? 'background: #f7fafc; cursor: not-allowed;' : ''}">
                        ${!esEdicion ? `
                        <button type="button" id="btnBuscarClienteServicio"
                            style="padding: ${isMobile ? '10px' : '8px 12px'}; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; white-space: nowrap; transition: background 0.2s; font-size: ${isMobile ? '16px' : '13px'}; min-width: ${isMobile ? '44px' : 'auto'};"
                            onmouseover="this.style.background='#5568d3'"
                            onmouseout="this.style.background='#667eea'">
                            🔍
                        </button>
                        ` : ''}
                    </div>
                    <div id="servicioClienteStatus" style="margin-top: 3px; font-size: ${isMobile ? '9px' : '10px'}; color: #718096;"></div>
                </div>
                <div style="margin-bottom: ${isMobile ? '10px' : '12px'};">
                    <label style="display: block; font-size: ${isMobile ? '10px' : '11px'}; font-weight: 600; color: #4a5568; margin-bottom: 4px;">
                        Nombre completo *
                    </label>
                    <input type="text" id="servicioClienteNombre" required
                        value="${esEdicion && servicio.nombre_cliente ? servicio.nombre_cliente : ''}"
                        ${esEdicion ? 'readonly' : ''}
                        placeholder="Ej: Juan Pérez"
                        style="width: 100%; padding: ${isMobile ? '10px 8px' : '8px 10px'}; border: 1px solid #e2e8f0; border-radius: 6px; font-size: ${isMobile ? '14px' : '13px'}; ${esEdicion ? 'background: #f7fafc; cursor: not-allowed;' : ''}">
                </div>
                <div style="margin-bottom: ${isMobile ? '10px' : '12px'};">
                    <label style="display: block; font-size: ${isMobile ? '10px' : '11px'}; font-weight: 600; color: #4a5568; margin-bottom: 4px;">
                        Teléfono *
                    </label>
                    <input type="tel" id="servicioClienteTelefono" inputmode="numeric"
                        value="${esEdicion && servicio.telefono_cliente ? servicio.telefono_cliente : ''}"
                        ${esEdicion ? 'readonly' : ''}
                        placeholder="Ej: 3001234567"
                        style="width: 100%; padding: ${isMobile ? '10px 8px' : '8px 10px'}; border: 1px solid #e2e8f0; border-radius: 6px; font-size: ${isMobile ? '14px' : '13px'}; ${esEdicion ? 'background: #f7fafc; cursor: not-allowed;' : ''}">
                    <div id="servicioClienteTelefonoHint" style="font-size: ${isMobile ? '9px' : '10px'}; color: #718096; margin-top: 2px; display: none;">Cliente nuevo - ingresa el teléfono</div>
                </div>
                <input type="hidden" id="servicioClienteId" value="${esEdicion && servicio.id_cliente ? servicio.id_cliente : ''}">

                <!-- Consola -->
                <div style="margin-bottom: ${isMobile ? '10px' : '12px'};">
                    <label style="display: block; font-size: ${isMobile ? '10px' : '11px'}; font-weight: 600; color: #4a5568; margin-bottom: 4px;">
                        Consola / Equipo *
                    </label>
                    <input type="text" id="servicioConsola" required
                        value="${esEdicion ? servicio.consola : ''}"
                        placeholder="Ej: PlayStation 5..."
                        style="width: 100%; padding: ${isMobile ? '10px 8px' : '8px 10px'}; border: 1px solid #e2e8f0; border-radius: 6px; font-size: ${isMobile ? '14px' : '13px'};">
                </div>

                <!-- Descripción de la falla -->
                <div style="margin-bottom: ${isMobile ? '10px' : '12px'};">
                    <label style="display: block; font-size: ${isMobile ? '10px' : '11px'}; font-weight: 600; color: #4a5568; margin-bottom: 4px;">
                        Descripción de la Falla *
                    </label>
                    <textarea id="servicioDescripcion" required rows="2"
                        placeholder="Describe el problema..."
                        style="width: 100%; padding: ${isMobile ? '10px 8px' : '8px 10px'}; border: 1px solid #e2e8f0; border-radius: 6px; font-size: ${isMobile ? '14px' : '13px'}; resize: vertical; min-height: ${isMobile ? '60px' : '50px'};">${esEdicion ? servicio.descripcion : ''}</textarea>
                </div>

                <!-- Estado y Costo en 2 columnas (solo en edición) -->
                ${esEdicion ? `
                <div style="display: grid; grid-template-columns: ${isMobile ? '1fr' : '1fr 1fr'}; gap: ${isMobile ? '10px' : '10px'}; margin-bottom: ${isMobile ? '10px' : '12px'};">
                    <div>
                        <label style="display: block; font-size: ${isMobile ? '10px' : '11px'}; font-weight: 600; color: #4a5568; margin-bottom: 4px;">
                            Estado *
                        </label>
                        <select id="servicioEstado" required
                            style="width: 100%; padding: ${isMobile ? '10px 8px' : '8px 10px'}; border: 1px solid #e2e8f0; border-radius: 6px; font-size: ${isMobile ? '14px' : '13px'}; color: #2d3748;">
                            <option value="En reparacion" ${servicio.estado === 'En reparacion' ? 'selected' : ''}>⚙️ En reparación</option>
                            <option value="Listo" ${servicio.estado === 'Listo' ? 'selected' : ''}>✅ Listo</option>
                            <option value="Entregado" ${servicio.estado === 'Entregado' ? 'selected' : ''}>📦 Entregado</option>
                        </select>
                    </div>
                    <div>
                        <label style="display: block; font-size: ${isMobile ? '10px' : '11px'}; font-weight: 600; color: #4a5568; margin-bottom: 4px;">
                            Costo ${servicio.costo ? `<span style="color: #38a169; font-weight: 700;">(${formatCurrency(servicio.costo)})</span>` : ''}
                        </label>
                        <input type="number" id="servicioCosto" min="0" step="1000"
                            value="${servicio.costo ? servicio.costo : ''}"
                            placeholder="150000"
                            style="width: 100%; padding: ${isMobile ? '10px 8px' : '8px 10px'}; border: 1px solid #e2e8f0; border-radius: 6px; font-size: ${isMobile ? '14px' : '13px'};">
                    </div>
                </div>
                ` : `
                <!-- Costo (solo en creación) -->
                <div style="margin-bottom: ${isMobile ? '10px' : '12px'};">
                    <label style="display: block; font-size: ${isMobile ? '10px' : '11px'}; font-weight: 600; color: #4a5568; margin-bottom: 4px;">
                        Costo del Servicio
                    </label>
                    <input type="number" id="servicioCosto" min="0" step="1000"
                        placeholder="Ej: 150000"
                        style="width: 100%; padding: ${isMobile ? '10px 8px' : '8px 10px'}; border: 1px solid #e2e8f0; border-radius: 6px; font-size: ${isMobile ? '14px' : '13px'};">
                    <div style="font-size: ${isMobile ? '9px' : '10px'}; color: #718096; margin-top: 2px;">Opcional - Puedes definirlo más tarde</div>
                </div>
                `}

                <!-- Pagado (solo en edición) -->
                ${esEdicion ? `
                <div style="margin-bottom: ${isMobile ? '10px' : '12px'};">
                    <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: ${isMobile ? '10px 8px' : '8px'}; background: #f7fafc; border-radius: 6px; border: 1px solid #e2e8f0;">
                        <input type="checkbox" id="servicioPagado" ${servicio.pagado ? 'checked' : ''}
                            style="width: ${isMobile ? '18px' : '16px'}; height: ${isMobile ? '18px' : '16px'}; cursor: pointer;">
                        <span style="font-size: ${isMobile ? '13px' : '12px'}; font-weight: 600; color: #4a5568;">
                            💰 Servicio pagado
                        </span>
                    </label>
                </div>
                ` : ''}
            </form>
        </div>

        <div class="confirm-modal-actions" style="margin-top: ${isMobile ? '12px' : '14px'}; display: flex; gap: ${isMobile ? '6px' : '8px'}; position: sticky; bottom: -20px; background: white; padding-top: ${isMobile ? '12px' : '10px'}; margin-left: -20px; margin-right: -20px; padding-left: 20px; padding-right: 20px; padding-bottom: 20px; margin-bottom: -20px;">
            <button id="btnCancelar" class="confirm-btn confirm-btn-cancel" style="flex: 1; padding: ${isMobile ? '12px' : '9px'}; font-size: ${isMobile ? '14px' : '13px'}; font-weight: 600; min-height: ${isMobile ? '44px' : 'auto'};">
                Cancelar
            </button>
            <button id="btnGuardar" class="confirm-btn confirm-btn-confirm" style="flex: 1; padding: ${isMobile ? '12px' : '9px'}; font-size: ${isMobile ? '14px' : '13px'}; font-weight: 600; min-height: ${isMobile ? '44px' : 'auto'};">
                ${esEdicion ? 'Actualizar' : 'Registrar'}
            </button>
        </div>
    `;

    overlay.classList.add('active');

    // Configurar evento de búsqueda de cliente (solo para nuevo servicio)
    if (!esEdicion) {
        const btnBuscar = document.getElementById('btnBuscarClienteServicio');
        const inputDocumento = document.getElementById('servicioClienteDocumento');

        btnBuscar.onclick = () => buscarClienteParaServicio();
        inputDocumento.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                buscarClienteParaServicio();
            }
        });
    }

    // Botones
    document.getElementById('btnCancelar').onclick = () => {
        overlay.classList.remove('active');
        setTimeout(() => {
            modal.innerHTML = originalContent;
            modal.style.maxWidth = '';
        }, 300);
    };

    document.getElementById('btnGuardar').onclick = () => {
        if (esEdicion) {
            actualizarServicio();
        } else {
            guardarServicio();
        }
    };
}

// Buscar cliente por documento para servicio
async function buscarClienteParaServicio() {
    const documento = document.getElementById('servicioClienteDocumento').value.trim();
    const statusDiv = document.getElementById('servicioClienteStatus');
    const nombreInput = document.getElementById('servicioClienteNombre');
    const clienteIdInput = document.getElementById('servicioClienteId');
    const telefonoInput = document.getElementById('servicioClienteTelefono');
    const telefonoHint = document.getElementById('servicioClienteTelefonoHint');

    if (!documento) {
        statusDiv.innerHTML = '<span style="color: #f59e0b;">⚠️ Ingresa un documento</span>';
        return;
    }

    try {
        statusDiv.innerHTML = '<span style="color: #667eea;">🔍 Buscando...</span>';
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/clientes/buscar/${encodeURIComponent(documento)}`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            if (data.success && data.cliente) {
                // Cliente encontrado - mostrar datos y hacer readonly
                nombreInput.value = data.cliente.nombre;
                nombreInput.setAttribute('readonly', 'readonly');
                nombreInput.style.background = '#f7fafc';
                nombreInput.style.cursor = 'not-allowed';

                telefonoInput.value = data.cliente.telefono || '';
                telefonoInput.setAttribute('readonly', 'readonly');
                telefonoInput.style.background = '#f7fafc';
                telefonoInput.style.cursor = 'not-allowed';
                telefonoInput.removeAttribute('required');

                clienteIdInput.value = data.cliente.id_cliente;
                telefonoHint.style.display = 'none';
                statusDiv.innerHTML = '<span style="color: #10b981;">✓ Cliente encontrado</span>';
            } else {
                // Cliente nuevo - habilitar campos para edición
                nombreInput.value = '';
                nombreInput.removeAttribute('readonly');
                nombreInput.style.background = '';
                nombreInput.style.cursor = '';
                nombreInput.focus();

                telefonoInput.value = '';
                telefonoInput.removeAttribute('readonly');
                telefonoInput.style.background = '';
                telefonoInput.style.cursor = '';
                telefonoInput.setAttribute('required', 'required');

                clienteIdInput.value = '';
                telefonoHint.style.display = 'block';
                statusDiv.innerHTML = '<span style="color: #f59e0b;">ℹ️ Cliente nuevo - Ingresa nombre y teléfono</span>';
            }
        } else {
            // Cliente nuevo - habilitar campos para edición
            nombreInput.value = '';
            nombreInput.removeAttribute('readonly');
            nombreInput.style.background = '';
            nombreInput.style.cursor = '';
            nombreInput.focus();

            telefonoInput.value = '';
            telefonoInput.removeAttribute('readonly');
            telefonoInput.style.background = '';
            telefonoInput.style.cursor = '';
            telefonoInput.setAttribute('required', 'required');

            clienteIdInput.value = '';
            telefonoHint.style.display = 'block';
            statusDiv.innerHTML = '<span style="color: #f59e0b;">ℹ️ Cliente nuevo - Ingresa nombre y teléfono</span>';
        }
    } catch (error) {
        console.error('Error buscando cliente:', error);
        statusDiv.innerHTML = '<span style="color: #ef4444;">✗ Error al buscar</span>';
    }
}

// Guardar nuevo servicio
async function guardarServicio() {
    const documento = document.getElementById('servicioClienteDocumento').value.trim();
    const nombre = document.getElementById('servicioClienteNombre').value.trim();
    let idCliente = document.getElementById('servicioClienteId').value;
    const telefono = document.getElementById('servicioClienteTelefono').value.trim();
    const consola = document.getElementById('servicioConsola').value.trim();
    const descripcion = document.getElementById('servicioDescripcion').value.trim();
    const costo = document.getElementById('servicioCosto').value;

    if (!documento || !nombre || !consola || !descripcion) {
        showWarning('Por favor completa todos los campos obligatorios', 'Campos incompletos');
        return;
    }

    // Si no hay ID de cliente, validar que tenga teléfono
    if (!idCliente && !telefono) {
        showWarning('Por favor ingresa el teléfono del cliente', 'Campo requerido');
        document.getElementById('servicioClienteTelefono').focus();
        return;
    }

    try {
        const token = localStorage.getItem('token');
        const usuario = JSON.parse(localStorage.getItem('usuario'));

        // Si no hay ID de cliente, crear uno nuevo
        if (!idCliente) {
            const clienteResponse = await fetch(`${API_URL}/clientes/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    nombre: nombre,
                    documento: documento,
                    telefono: telefono
                })
            });

            const clienteData = await clienteResponse.json();
            if (clienteData.success) {
                idCliente = clienteData.data.id_cliente;
            } else {
                showError('Error al registrar el cliente: ' + (clienteData.message || clienteData.detail || 'Error desconocido'), 'Error');
                return;
            }
        }

        // Registrar servicio
        const response = await fetch(`${API_URL}/servicios/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                id_usuario: usuario.id_usuario,
                id_cliente: parseInt(idCliente),
                consola: consola,
                descripcion: descripcion,
                costo: costo ? parseFloat(costo) : null
            })
        });

        const data = await response.json();

        if (data.success) {
            showSuccess('Servicio registrado exitosamente', '¡Éxito!');
            document.getElementById('confirmModalOverlay').classList.remove('active');
            cargarServicios();

            // Emitir evento de servicio creado
            EventBus.emit(Events.SERVICIO_CREADO, data.data);
        } else {
            showError('No se pudo registrar el servicio: ' + data.message, 'Error');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Error al registrar el servicio', 'Error de conexión');
    }
}

// Editar servicio
async function editarServicio(idServicio) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/servicios/${idServicio}`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        const servicio = await response.json();
        mostrarModalServicio(servicio);
    } catch (error) {
        console.error('Error:', error);
        showError('Error al cargar servicio', 'Error');
    }
}

// Actualizar servicio
async function actualizarServicio() {
    const consola = document.getElementById('servicioConsola').value.trim();
    const descripcion = document.getElementById('servicioDescripcion').value.trim();
    const estado = document.getElementById('servicioEstado').value;
    const costo = document.getElementById('servicioCosto').value;
    const pagadoCheckbox = document.getElementById('servicioPagado');
    const pagado = pagadoCheckbox ? pagadoCheckbox.checked : false;

    if (!consola || !descripcion || !estado) {
        showWarning('Por favor completa todos los campos obligatorios', 'Campos incompletos');
        return;
    }

    try {
        const token = localStorage.getItem('token');

        const response = await fetch(`${API_URL}/servicios/${servicioEditando.id_servicio}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                consola: consola,
                descripcion: descripcion,
                estado: estado,
                costo: costo ? parseFloat(costo) : null,
                pagado: pagado
            })
        });

        const data = await response.json();

        if (data.success) {
            showSuccess('Servicio actualizado exitosamente', '¡Éxito!');
            document.getElementById('confirmModalOverlay').classList.remove('active');
            cargarServicios();

            // Emitir evento de servicio actualizado
            EventBus.emit(Events.SERVICIO_ACTUALIZADO, data.data);
        } else {
            showError('No se pudo actualizar el servicio: ' + data.message, 'Error');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Error al actualizar el servicio', 'Error de conexión');
    }
}

// Eliminar servicio
async function eliminarServicio(idServicio) {
    const confirmado = await showConfirm({
        title: '¿Eliminar servicio?',
        message: 'Esta acción no se puede deshacer. ¿Estás seguro de eliminar este servicio?',
        type: 'danger',
        confirmText: 'Eliminar',
        cancelText: 'Cancelar'
    });

    if (!confirmado) return;

    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/servicios/${idServicio}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();

        if (data.success) {
            showSuccess('Servicio eliminado correctamente', 'Eliminado');
            cargarServicios();
        } else {
            showError('No se pudo eliminar el servicio: ' + data.message, 'Error');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Error al eliminar el servicio', 'Error de conexión');
    }
}

// Cargar servicios cuando se accede a la sección
document.addEventListener('DOMContentLoaded', function() {
    let cargandoServicios = false;
    let timeoutId = null;

    const observer = new MutationObserver(function(mutations) {
        const serviciosSection = document.getElementById('servicios');
        if (serviciosSection && serviciosSection.classList.contains('active') && !cargandoServicios) {
            // Debounce: cancelar llamadas anteriores y esperar 100ms
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                cargandoServicios = true;
                cargarServicios().finally(() => {
                    cargandoServicios = false;
                });
            }, 100);
        }
    });

    const config = { attributes: true, subtree: true, attributeFilter: ['class'] };
    const targetNode = document.querySelector('main');
    if (targetNode) {
        observer.observe(targetNode, config);
    }
});
