// ============================================
// SISTEMA DE VENTAS - PLAY ZONE
// ============================================

const cart = [];

// Obtener headers con token
function getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// ============================================
// CARRITO DE COMPRAS
// ============================================

function agregarAlCarrito(idProducto, nombre, precio, stockDisponible) {
    const existingItem = cart.find(item => item.id === idProducto);

    if (existingItem) {
        if (existingItem.quantity < stockDisponible) {
            existingItem.quantity++;
            showSuccess(`Cantidad actualizada: ${existingItem.quantity}`, nombre);
        } else {
            showWarning('No hay más unidades disponibles en stock', 'Stock agotado');
            return;
        }
    } else {
        cart.push({
            id: idProducto,
            name: nombre,
            price: parseFloat(precio),
            quantity: 1,
            maxStock: stockDisponible
        });
        showSuccess('Producto agregado al carrito', nombre);
    }

    renderCart();
}

function updateQuantity(productId, change) {
    const item = cart.find(item => item.id === productId);

    if (item) {
        const newQuantity = item.quantity + change;

        if (newQuantity <= 0) {
            const index = cart.indexOf(item);
            cart.splice(index, 1);
        } else if (newQuantity <= item.maxStock) {
            item.quantity = newQuantity;
        } else {
            showWarning('No hay más unidades disponibles en stock', 'Stock agotado');
            return;
        }

        renderCart();
    }
}

function renderCart() {
    const cartItemsDiv = document.getElementById('cartItems');
    const totalAmountDiv = document.getElementById('totalAmount');
    const cartBadge = document.getElementById('cartBadge'); // RF-12: Badge para móvil

    if (!cartItemsDiv || !totalAmountDiv) return;

    if (cart.length === 0) {
        cartItemsDiv.innerHTML = '<div class="cart-empty">No hay productos en el carrito</div>';
        totalAmountDiv.textContent = '0';

        // RF-12: Ocultar badge cuando está vacío
        if (cartBadge) cartBadge.style.display = 'none';
        return;
    }

    cartItemsDiv.innerHTML = cart.map(item => `
        <div class="cart-item">
            <div class="cart-item-header">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">$${item.price.toFixed(2)}</div>
            </div>
            <div class="cart-item-controls">
                <div class="quantity-controls">
                    <button class="qty-btn minus" onclick="updateQuantity(${item.id}, -1)">−</button>
                    <div class="quantity-display">${item.quantity}</div>
                    <button class="qty-btn plus" onclick="updateQuantity(${item.id}, 1)">+</button>
                </div>
            </div>
        </div>
    `).join('');

    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

    totalAmountDiv.textContent = total.toFixed(2);

    // RF-12: Actualizar badge en móvil
    if (cartBadge && window.innerWidth <= 480) {
        cartBadge.style.display = 'inline-block';
        cartBadge.textContent = `${totalItems} • $${total.toFixed(2)}`;
    }
}

async function clearCart() {
    if (cart.length === 0) {
        showInfo('No hay productos en el carrito', 'Carrito vacío');
        return;
    }

    const confirmado = await showConfirm({
        title: '¿Vaciar carrito?',
        message: 'Se eliminarán todos los productos del carrito. Esta acción no se puede deshacer.',
        type: 'warning',
        confirmText: 'Vaciar',
        cancelText: 'Cancelar'
    });

    if (confirmado) {
        cart.length = 0;
        renderCart();
        showInfo('El carrito ha sido vaciado', 'Carrito limpio');
    }
}

// ============================================
// GUARDAR VENTA
// ============================================

// Buscar cliente por documento
async function buscarClientePorDocumento(documento) {
    try {
        const response = await fetch(`${API_URL}/clientes/buscar/${documento}`, {
            method: 'GET',
            headers: getAuthHeaders()
        });

        if (response.ok) {
            const data = await response.json();
            return data.success ? data.cliente : null;
        }
        return null;
    } catch (error) {
        console.error('Error al buscar cliente:', error);
        return null;
    }
}

function mostrarFormularioCliente() {
    return new Promise((resolve) => {
        const overlay = document.getElementById('confirmModalOverlay');
        const modal = overlay.querySelector('.confirm-modal');
        const originalContent = modal.innerHTML;

        modal.innerHTML = `
            <div class="confirm-modal-icon info">👤</div>
            <div class="confirm-modal-title">Datos del Cliente</div>
            <div style="margin: 20px 0;">
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 500;">Documento *</label>
                    <div style="display: flex; gap: 8px;">
                        <input type="text" id="clienteDocumento" required inputmode="numeric"
                            placeholder="Cédula o NIT"
                            style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px;">
                        <button id="btnBuscarCliente"
                            style="padding: 10px 16px; background: #0066cc; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; white-space: nowrap;">
                            🔍 Buscar
                        </button>
                    </div>
                    <div id="clienteStatus" style="margin-top: 5px; font-size: 12px; color: #718096;"></div>
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 500;">Nombre completo *</label>
                    <input type="text" id="clienteNombre" required
                        placeholder="Ej: Juan Pérez"
                        style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px;">
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 500;">Teléfono *</label>
                    <input type="tel" id="clienteTelefono" required inputmode="tel"
                        placeholder="3001234567"
                        style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px;">
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 500;">Email (opcional)</label>
                    <input type="email" id="clienteEmail" inputmode="email"
                        placeholder="cliente@ejemplo.com"
                        style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px;">
                </div>
            </div>
            <div class="confirm-modal-actions">
                <button class="confirm-btn confirm-btn-cancel" id="formCancel">Cancelar</button>
                <button class="confirm-btn confirm-btn-confirm" id="formOk">Continuar</button>
            </div>
        `;

        overlay.classList.add('active');

        const documentoInput = document.getElementById('clienteDocumento');
        const nombreInput = document.getElementById('clienteNombre');
        const telefonoInput = document.getElementById('clienteTelefono');
        const emailInput = document.getElementById('clienteEmail');
        const btnBuscar = document.getElementById('btnBuscarCliente');
        const statusDiv = document.getElementById('clienteStatus');
        const cancelBtn = document.getElementById('formCancel');
        const okBtn = document.getElementById('formOk');

        documentoInput.focus();

        // Buscar cliente al hacer clic en el botón
        btnBuscar.onclick = async () => {
            const documento = documentoInput.value.trim();
            if (!documento) {
                statusDiv.innerHTML = '<span style="color: #f5576c;">⚠️ Ingresa un documento</span>';
                return;
            }

            btnBuscar.disabled = true;
            btnBuscar.textContent = '⏳ Buscando...';
            statusDiv.innerHTML = '<span style="color: #718096;">Buscando cliente...</span>';

            const cliente = await buscarClientePorDocumento(documento);

            btnBuscar.disabled = false;
            btnBuscar.innerHTML = '🔍 Buscar';

            if (cliente) {
                nombreInput.value = cliente.nombre || '';
                telefonoInput.value = cliente.telefono || '';
                emailInput.value = cliente.email || '';
                statusDiv.innerHTML = '<span style="color: #059669;">✓ Cliente encontrado</span>';
                nombreInput.focus();
            } else {
                nombreInput.value = '';
                telefonoInput.value = '';
                emailInput.value = '';
                statusDiv.innerHTML = '<span style="color: #d97706;">⚠️ Cliente no encontrado - Ingresa los datos para registrarlo</span>';
                nombreInput.focus();
            }
        };

        // Buscar también al presionar Enter en el campo de documento
        documentoInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                btnBuscar.click();
            }
        });

        nombreInput.focus();

        const cleanup = (data) => {
            overlay.classList.remove('active');
            setTimeout(() => {
                modal.innerHTML = originalContent;
                resolve(data);
            }, 350);
        };

        cancelBtn.onclick = () => cleanup(null);
        okBtn.onclick = () => {
            const nombre = nombreInput.value.trim();
            const documento = documentoInput.value.trim();
            const telefono = telefonoInput.value.trim();

            if (!nombre || !documento || !telefono) {
                showWarning('Debes completar nombre, documento y teléfono', 'Datos incompletos');
                return;
            }

            cleanup({
                nombre,
                documento,
                telefono,
                email: emailInput.value.trim()
            });
        };
    });
}

async function saveCart() {
    if (cart.length === 0) {
        showWarning('Agrega productos al carrito antes de guardar', 'Carrito vacío');
        return;
    }

    // Mostrar formulario de cliente
    const clienteData = await mostrarFormularioCliente();
    if (!clienteData) return;

    // Pequeño delay para restaurar el modal
    await new Promise(resolve => setTimeout(resolve, 400));

    // Confirmación antes de guardar (RF-04)
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const confirmado = await showConfirm({
        title: '¿Confirmar venta?',
        message: `Cliente: ${clienteData.nombre}\nDocumento: ${clienteData.documento}\nTotal: $${total.toLocaleString()}\nProductos: ${cart.length}`,
        type: 'info',
        confirmText: 'Confirmar venta',
        cancelText: 'Cancelar'
    });

    if (!confirmado) return;

    try {
        // 1. Crear o buscar cliente
        let clienteResponse = await fetch(`${API_URL}/clientes/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(clienteData)
        });

        const clienteResult = await clienteResponse.json();
        if (!clienteResult.success) {
            showError('No se pudo registrar el cliente: ' + clienteResult.message, 'Error');
            return;
        }

        // 2. Crear la venta
        const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const usuario = JSON.parse(localStorage.getItem('usuario'));

        const ventaResponse = await fetch(`${API_URL}/ventas/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                id_usuario: usuario.id_usuario,
                id_cliente: clienteResult.id_cliente || clienteResult.data.id_cliente,
                total: total,
                productos: cart.map(item => ({
                    id_producto: item.id,
                    cantidad: item.quantity,
                    precio_unitario: item.price
                }))
            })
        });

        const ventaData = await ventaResponse.json();

        if (ventaData.success) {
            showSuccess(
                `Venta registrada por $${total.toFixed(2)} - ${cart.length} producto(s)`,
                '¡Venta completada!'
            );
            cart.length = 0;
            renderCart();

            // Recargar productos para actualizar stock
            if (typeof cargarProductos === 'function') {
                cargarProductos();
            }

            // Emitir evento de venta creada para actualización en tiempo real
            EventBus.emit(Events.VENTA_CREADA, ventaData.data);
        } else {
            showError('No se pudo registrar la venta: ' + ventaData.message, 'Error en venta');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Ocurrió un error al procesar la venta. Intenta nuevamente.', 'Error de conexión');
    }
}

// ============================================
// FILTRO DE PRODUCTOS
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // RF-12: Carrito colapsable en móvil
    const cartTitle = document.querySelector('.cart-title');
    const cartSidebar = document.querySelector('.cart-sidebar');

    if (cartTitle && cartSidebar && window.innerWidth <= 480) {
        cartTitle.addEventListener('click', function() {
            cartSidebar.classList.toggle('expanded');
        });
    }

    // Manejo del filtro dropdown
    const dropdownBtn = document.getElementById('dropdownBtn');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    const selectedFilter = document.getElementById('selectedFilter');

    if (dropdownBtn && dropdownMenu) {
        dropdownBtn.addEventListener('click', function() {
            dropdownMenu.classList.toggle('active');
        });

        dropdownItems.forEach(item => {
            item.addEventListener('click', function() {
                // Actualizar filtro seleccionado
                dropdownItems.forEach(i => i.classList.remove('active'));
                this.classList.add('active');

                const filter = this.getAttribute('data-filter');
                selectedFilter.textContent = this.textContent;

                // Filtrar productos
                const productCards = document.querySelectorAll('.product-card');
                productCards.forEach(card => {
                    if (filter === 'todos') {
                        card.style.display = 'block';
                    } else {
                        const categoria = card.getAttribute('data-categoria');
                        card.style.display = categoria === filter ? 'block' : 'none';
                    }
                });

                dropdownMenu.classList.remove('active');
            });
        });

        // Cerrar dropdown al hacer clic fuera
        document.addEventListener('click', function(e) {
            if (!dropdownBtn.contains(e.target) && !dropdownMenu.contains(e.target)) {
                dropdownMenu.classList.remove('active');
            }
        });
    }
});
