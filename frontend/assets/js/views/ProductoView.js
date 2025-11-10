// ============================================
// GESTIÓN DE PRODUCTOS - PLAY ZONE
// ============================================

// API_URL definido en config.js
let productoEditando = null;

// Obtener headers con token
function getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// ============================================
// MODAL FUNCTIONS
// ============================================

function abrirModal(producto = null) {
    productoEditando = producto;
    const modal = document.getElementById('modalOverlay');
    const tituloModal = modal.querySelector('.modal-header h2');
    const form = document.getElementById('formProducto');

    if (producto) {
        // Modo edición
        tituloModal.textContent = 'Editar Producto';
        document.getElementById('nombre').value = producto.nombre || '';
        document.getElementById('categoria').value = producto.categoria || '';
        document.getElementById('precio').value = producto.precio || '';
        document.getElementById('stock').value = producto.cantidad || '';
        document.getElementById('descripcion').value = producto.descripcion || '';
        document.getElementById('imagen').value = producto.imagen_url || '';
        // Configurar búsqueda automática de imágenes también en modo edición
        configurarBusquedaAutomaticaImagen();
    } else {
        // Modo creación
        tituloModal.textContent = 'Agregar Nuevo Producto';
        form.reset();
        // Configurar búsqueda automática de imágenes
        configurarBusquedaAutomaticaImagen();
    }

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// Buscar imágenes manualmente al hacer clic en el botón
async function buscarImagenesManual() {
    const nombreInput = document.getElementById('nombre');
    const categoriaSelect = document.getElementById('categoria');
    const imagenInput = document.getElementById('imagen');
    const searchContainer = document.getElementById('imageSearchContainer');

    const nombre = nombreInput.value.trim();
    const categoria = categoriaSelect.value;

    if (!nombre || nombre.length < 3) {
        showWarning('Ingresa el nombre del producto (mínimo 3 caracteres) para buscar imágenes', 'Campo requerido');
        nombreInput.focus();
        return;
    }

    if (!categoria) {
        showWarning('Selecciona una categoría para buscar imágenes', 'Categoría requerida');
        categoriaSelect.focus();
        return;
    }

    // Validar categoría soportada
    if (categoria !== 'videojuego' && categoria !== 'consola' && categoria !== 'accesorio') {
        showWarning('La búsqueda automática solo está disponible para Videojuegos, Consolas y Accesorios', 'Categoría no soportada');
        return;
    }

    // Mostrar indicador de búsqueda
    if (searchContainer) {
        searchContainer.innerHTML = '<div style="font-size: 12px; color: #667eea; padding: 8px; background: #eef2ff; border-radius: 6px; border-left: 3px solid #667eea;">🔍 Buscando imágenes...</div>';
    }

    try {
        const resultados = await buscarImagenesMultiples(nombre, categoria);

        if (resultados.length > 0) {
            mostrarResultadosBusqueda(resultados, imagenInput, searchContainer);
            showSuccess(`Se encontraron ${resultados.length} imagen(es). Haz clic en una para seleccionarla.`, 'Imágenes encontradas');
        } else {
            if (searchContainer) {
                searchContainer.innerHTML = `
                    <div style="font-size: 12px; color: #d97706; padding: 8px; background: #fef3c7; border-radius: 6px; border-left: 3px solid #f59e0b;">
                        ⚠️ No se encontraron imágenes para "${nombre}". Puedes:
                        <ul style="margin: 4px 0 0 20px; font-size: 11px;">
                            <li>Dejar vacío para usar imagen por categoría</li>
                            <li>Ingresar una URL personalizada</li>
                        </ul>
                    </div>
                `;
            }
            showWarning(`No se encontraron imágenes para "${nombre}". Intenta con otro nombre o ingresa una URL personalizada.`, 'Sin resultados');
        }
    } catch (error) {
        console.error('Error al buscar imagen:', error);
        if (searchContainer) {
            searchContainer.innerHTML = '<div style="font-size: 12px; color: #ef4444; padding: 8px; background: #fee2e2; border-radius: 6px; border-left: 3px solid #ef4444;">✗ Error al buscar imágenes. Intenta nuevamente.</div>';
        }
        showError('Error al buscar imágenes. Verifica tu conexión.', 'Error de búsqueda');
    }
}

// Configurar búsqueda automática de imágenes
function configurarBusquedaAutomaticaImagen() {
    const nombreInput = document.getElementById('nombre');
    const categoriaSelect = document.getElementById('categoria');
    const imagenInput = document.getElementById('imagen');

    // Crear contenedor de búsqueda
    const searchContainer = document.createElement('div');
    searchContainer.id = 'imageSearchContainer';
    searchContainer.style.cssText = 'margin-top: 10px;';

    const imagenGroup = imagenInput.closest('.form-group');
    if (!document.getElementById('imageSearchContainer')) {
        imagenGroup.appendChild(searchContainer);
    }

    // Mostrar mensaje informativo sobre el botón de búsqueda
    searchContainer.innerHTML = '<div style="font-size: 11px; color: #718096; padding: 6px; background: #f7fafc; border-radius: 4px;">💡 Haz clic en "🔍 Buscar" para encontrar imágenes del producto</div>';

    // Limpiar resultados si el usuario edita manualmente la URL
    imagenInput.addEventListener('input', () => {
        if (imagenInput.value.trim() !== '') {
            searchContainer.innerHTML = '<div style="font-size: 11px; color: #059669; padding: 6px; background: #d1fae5; border-radius: 4px; margin-top: 4px;">✓ URL personalizada</div>';
        }
    });
}

// Mostrar resultados de búsqueda con preview
function mostrarResultadosBusqueda(resultados, imagenInput, container) {
    const html = `
        <div style="font-size: 12px; color: #059669; margin-bottom: 8px; font-weight: 500;">
            ✓ ${resultados.length} opción(es) encontrada(s). Haz clic para seleccionar:
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 10px; max-height: 250px; overflow-y: auto; padding: 8px; background: #f7fafc; border-radius: 8px;">
            ${resultados.map((img, index) => `
                <div class="imagen-seleccionable" data-url="${escapeHtml(img.url)}" data-nombre="${escapeHtml(img.nombre)}"
                     style="cursor: pointer; border: 2px solid #e2e8f0; border-radius: 8px; overflow: hidden; transition: all 0.2s; background: white;"
                     onmouseover="this.style.borderColor='#0066cc'; this.style.transform='scale(1.05)'; this.style.boxShadow='0 4px 12px rgba(0,102,204,0.2)'"
                     onmouseout="this.style.borderColor='#e2e8f0'; this.style.transform='scale(1)'; this.style.boxShadow='none'">
                    <img src="${img.url}"
                         alt="${escapeHtml(img.nombre)}"
                         style="width: 100%; height: 90px; object-fit: cover; display: block;"
                         onerror="this.parentElement.style.display='none'">
                    <div style="padding: 6px; font-size: 10px; color: #4a5568; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500;">
                        ${escapeHtml(img.nombre)}
                    </div>
                </div>
            `).join('')}
        </div>
        <div style="margin-top: 8px; font-size: 11px; color: #718096; background: #edf2f7; padding: 6px; border-radius: 4px;">
            💡 Haz clic en una imagen para seleccionarla, o ingresa una URL personalizada arriba
        </div>
    `;

    container.innerHTML = html;

    // Agregar event listeners a cada imagen
    container.querySelectorAll('.imagen-seleccionable').forEach(div => {
        div.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            const nombre = this.getAttribute('data-nombre');
            seleccionarImagen(url, nombre);
        });
    });
}

// Escape HTML para prevenir XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/'/g, '&apos;');
}

// Seleccionar imagen
window.seleccionarImagen = function(url, nombre) {
    const imagenInput = document.getElementById('imagen');
    imagenInput.value = url;

    const searchContainer = document.getElementById('imageSearchContainer');
    if (searchContainer) {
        searchContainer.innerHTML = `
            <div style="font-size: 12px; color: #059669; margin-top: 5px; padding: 8px; background: #d1fae5; border-radius: 6px; border-left: 3px solid #059669;">
                ✓ Imagen seleccionada: <strong>${escapeHtml(nombre)}</strong>
            </div>
        `;
    }
}

function cerrarModal() {
    document.getElementById('modalOverlay').classList.remove('active');
    document.body.style.overflow = 'auto';
    document.getElementById('formProducto').reset();
    productoEditando = null;
}

function cerrarModalOverlay(event) {
    if (event.target === event.currentTarget) {
        cerrarModal();
    }
}

// ============================================
// CRUD PRODUCTOS
// ============================================

// Cargar todos los productos
async function cargarProductos() {
    try {
        const response = await fetch(`${API_URL}/productos/`);
        const productos = await response.json();

        todosLosProductos = productos; // Guardar para búsqueda
        mostrarProductosEnTabla(productos);
        mostrarProductosEnVentas(productos);
        verificarAlertasStock(productos); // RF-11: Verificar stock bajo
    } catch (error) {
        console.error('Error al conectar con el servidor:', error);
        showError('No se pudo conectar con el servidor', 'Error de conexión');
    }
}

// Mostrar productos en la tabla de inventario
function mostrarProductosEnTabla(productos) {
    const tbody = document.getElementById('inventoryTableBody');
    if (!tbody) return;

    if (productos.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 60px 20px;">
                    <div style="display: inline-block;">
                        <div style="font-size: 48px; margin-bottom: 16px;">📦</div>
                        <div style="font-size: 16px; color: #718096; font-weight: 500;">No hay productos registrados</div>
                        <div style="font-size: 14px; color: #a0aec0; margin-top: 8px;">Comienza agregando tu primer producto</div>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    // Color badges para categorías
    const categoriaColors = {
        'Consolas': '#667eea',
        'Accesorios': '#f59e0b',
        'Videojuegos': '#10b981',
        'Componentes': '#3b82f6',
        'Otros': '#6b7280'
    };

    tbody.innerHTML = productos.map(producto => {
        // Simplificado: rojo (0), naranja (1-9), verde (10+)
        const stockColor = producto.cantidad === 0 ? '#ef4444' : producto.cantidad < 10 ? '#f59e0b' : '#10b981';
        const categoriaBg = categoriaColors[producto.categoria] || '#6b7280';

        return `
        <tr style="border-bottom: 1px solid #e2e8f0; transition: all 0.2s;"
            onmouseover="this.style.backgroundColor='#f7fafc'"
            onmouseout="this.style.backgroundColor='white'">

            <td style="padding: 16px 20px;">
                <span style="font-weight: 600; color: #4a5568; font-family: monospace; font-size: 13px;">${producto.codigo}</span>
            </td>

            <td style="padding: 16px 20px;">
                <span style="font-weight: 600; color: #2d3748; font-size: 14px;">${producto.nombre}</span>
            </td>

            <td style="padding: 16px 20px; text-align: center;">
                <img src="${producto.imagen_url || '../assets/images/logo.png'}"
                     alt="${producto.nombre}"
                     style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            </td>

            <td style="padding: 16px 20px;">
                <span style="display: inline-flex; align-items: center; padding: 6px 12px; background: ${categoriaBg}15; color: ${categoriaBg}; border-radius: 12px; font-size: 13px; font-weight: 600;">
                    ${producto.categoria}
                </span>
            </td>

            <td style="padding: 16px 20px; max-width: 200px;">
                <span style="color: #718096; font-size: 13px; display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    ${producto.descripcion || 'Sin descripción'}
                </span>
            </td>

            <td style="padding: 16px 20px; text-align: right;">
                <span style="font-weight: 700; color: #2d3748; font-size: 15px;">$${parseFloat(producto.precio).toLocaleString('es-CO', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
            </td>

            <td style="padding: 16px 20px; text-align: center;">
                <span style="display: inline-flex; align-items: center; justify-content: center; min-width: 40px; padding: 6px 12px; background: ${stockColor}15; color: ${stockColor}; border-radius: 8px; font-weight: 700; font-size: 14px;">
                    ${producto.cantidad}
                </span>
            </td>

            <td style="padding: 16px 20px; text-align: center;">
                <div style="display: flex; gap: 8px; justify-content: center;">
                    <button onclick="editarProducto(${producto.id_producto})"
                            style="padding: 8px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 13px; transition: transform 0.2s, box-shadow 0.2s;"
                            onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(102, 126, 234, 0.4)'"
                            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                        ✏️ Editar
                    </button>
                    <button onclick="eliminarProducto(${producto.id_producto})"
                            style="padding: 8px 16px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 13px; transition: transform 0.2s, box-shadow 0.2s;"
                            onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(239, 68, 68, 0.4)'; this.style.background='#dc2626'"
                            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'; this.style.background='#ef4444'">
                        🗑️ Eliminar
                    </button>
                </div>
            </td>
        </tr>
        `;
    }).join('');
}

// Guardar producto (crear o actualizar)
async function guardarProducto(event) {
    event.preventDefault();

    const formData = new FormData(event.target);

    // RF-01: Validación de campos obligatorios
    const nombre = formData.get('nombre')?.trim();
    const categoria = formData.get('categoria');
    const precio = formData.get('precio');
    const cantidad = formData.get('stock');

    // Validar nombre
    if (!nombre) {
        showError('El nombre del producto es obligatorio', 'Campo requerido');
        document.getElementById('nombre').focus();
        return;
    }

    // Validar categoría
    if (!categoria) {
        showError('Debes seleccionar una categoría', 'Campo requerido');
        document.getElementById('categoria').focus();
        return;
    }

    // Validar precio
    if (!precio || parseFloat(precio) <= 0) {
        showError('El precio debe ser mayor a 0', 'Campo requerido');
        document.getElementById('precio').focus();
        return;
    }

    // Validar cantidad
    if (cantidad === null || cantidad === '' || parseInt(cantidad) < 0) {
        showError('La cantidad debe ser un número válido', 'Campo requerido');
        document.getElementById('stock').focus();
        return;
    }

    const producto = {
        nombre: nombre,
        categoria: categoria,
        precio: parseFloat(precio),
        cantidad: parseInt(cantidad),
        descripcion: formData.get('descripcion')?.trim() || '',
        imagen_url: formData.get('imagen')?.trim() || ''
    };

    try {
        let response;
        if (productoEditando) {
            // Actualizar producto existente
            response = await fetch(`${API_URL}/productos/${productoEditando.id_producto}`, {
                method: 'PUT',
                headers: getAuthHeaders(),
                body: JSON.stringify(producto)
            });
        } else {
            // Crear nuevo producto
            response = await fetch(`${API_URL}/productos/`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(producto)
            });
        }

        const data = await response.json();

        if (data.success || response.ok) {
            showSuccess(
                productoEditando ? 'El producto ha sido actualizado correctamente' : 'El producto ha sido registrado en el inventario',
                productoEditando ? 'Producto actualizado' : 'Producto registrado'
            );
            cerrarModal();
            cargarProductos();

            // Emitir evento de actualización en tiempo real
            if (productoEditando) {
                EventBus.emit(Events.PRODUCTO_ACTUALIZADO, data.data || producto);
            } else {
                EventBus.emit(Events.PRODUCTO_CREADO, data.data || producto);
            }
        } else {
            showError(data.message || data.detail || 'No se pudo guardar el producto', 'Error');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Ocurrió un error al guardar el producto. Intenta nuevamente.', 'Error de conexión');
    }
}

// Editar producto
async function editarProducto(idProducto) {
    try {
        const response = await fetch(`${API_URL}/productos/${idProducto}`);
        const producto = await response.json();

        if (response.ok && producto) {
            abrirModal(producto);
        } else {
            showError('No se encontró el producto', 'Error');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('No se pudo cargar la información del producto', 'Error al editar');
    }
}

// Eliminar producto
async function eliminarProducto(idProducto) {
    const confirmado = await showConfirm({
        title: '¿Eliminar producto?',
        message: 'Esta acción no se puede deshacer. El producto será eliminado permanentemente del inventario.',
        type: 'danger',
        confirmText: 'Eliminar',
        cancelText: 'Cancelar'
    });

    if (!confirmado) return;

    try {
        const response = await fetch(`${API_URL}/productos/${idProducto}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });

        const data = await response.json();

        if (data.success || response.ok) {
            showSuccess('El producto ha sido eliminado del inventario', 'Producto eliminado');
            cargarProductos();

            // Emitir evento de eliminación en tiempo real
            EventBus.emit(Events.PRODUCTO_ELIMINADO, { id_producto: idProducto });
        } else {
            showError('No se pudo eliminar el producto: ' + (data.message || data.detail), 'Error');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Ocurrió un error al eliminar el producto', 'Error de conexión');
    }
}

// ============================================
// PRODUCTOS PARA VENTAS
// ============================================

function mostrarProductosEnVentas(productos) {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    if (productos.length === 0) {
        grid.innerHTML = '<p style="text-align:center;width:100%;">No hay productos disponibles</p>';
        return;
    }

    grid.innerHTML = productos.filter(p => p.cantidad > 0).map(producto => `
        <div class="product-card" data-categoria="${producto.categoria}">
            <img src="${producto.imagen_url || '../assets/images/logo.png'}" alt="${producto.nombre}" class="product-image">
            <div class="product-info">
                <h3 class="product-name">${producto.nombre}</h3>
                <p class="product-price">$${parseFloat(producto.precio).toFixed(2)}</p>
                <p class="product-stock">Stock: ${producto.cantidad}</p>
                <button class="add-to-cart-btn" onclick="agregarAlCarrito(${producto.id_producto}, '${producto.nombre}', ${producto.precio}, ${producto.cantidad})">
                    Agregar al Carrito
                </button>
            </div>
        </div>
    `).join('');
}

// ============================================
// BÚSQUEDA Y FILTRADO DE PRODUCTOS - RF-09
// ============================================

let todosLosProductos = [];

// Función de búsqueda por texto
function buscarProductos() {
    aplicarFiltros();
}

// RF-09: Aplicar todos los filtros combinados
function aplicarFiltros() {
    const searchInput = document.getElementById('searchProductInput');
    const precioMin = document.getElementById('filtroPrecioMin');
    const precioMax = document.getElementById('filtroPrecioMax');
    const filtroStock = document.getElementById('filtroStock');

    let productosFiltrados = [...todosLosProductos];

    // Filtro por búsqueda de texto
    if (searchInput && searchInput.value.trim()) {
        const termino = searchInput.value.toLowerCase().trim();
        productosFiltrados = productosFiltrados.filter(producto => {
            return (
                producto.nombre.toLowerCase().includes(termino) ||
                producto.codigo.toLowerCase().includes(termino) ||
                producto.categoria.toLowerCase().includes(termino) ||
                (producto.descripcion && producto.descripcion.toLowerCase().includes(termino))
            );
        });
    }

    // Filtro por rango de precio
    if (precioMin && precioMin.value) {
        const minPrecio = parseFloat(precioMin.value);
        productosFiltrados = productosFiltrados.filter(producto => producto.precio >= minPrecio);
    }

    if (precioMax && precioMax.value) {
        const maxPrecio = parseFloat(precioMax.value);
        productosFiltrados = productosFiltrados.filter(producto => producto.precio <= maxPrecio);
    }

    // Filtro por estado de stock
    if (filtroStock && filtroStock.value) {
        const estadoStock = filtroStock.value;
        productosFiltrados = productosFiltrados.filter(producto => {
            switch (estadoStock) {
                case 'disponible':
                    return producto.cantidad >= 10;
                case 'bajo':
                    return producto.cantidad >= 1 && producto.cantidad < 10;
                case 'agotado':
                    return producto.cantidad === 0;
                default:
                    return true;
            }
        });
    }

    mostrarProductosEnTabla(productosFiltrados);
}

// RF-09: Limpiar todos los filtros
function limpiarFiltros() {
    const searchInput = document.getElementById('searchProductInput');
    const precioMin = document.getElementById('filtroPrecioMin');
    const precioMax = document.getElementById('filtroPrecioMax');
    const filtroStock = document.getElementById('filtroStock');

    if (searchInput) searchInput.value = '';
    if (precioMin) precioMin.value = '';
    if (precioMax) precioMax.value = '';
    if (filtroStock) filtroStock.value = '';

    mostrarProductosEnTabla(todosLosProductos);
}

// ============================================
// RF-11: ALERTAS DE STOCK BAJO
// ============================================

// Verificar y mostrar alertas de stock bajo
function verificarAlertasStock(productos) {
    const stockBajo = 10; // Nivel mínimo de stock
    const productosBajoStock = productos.filter(p => p.cantidad < stockBajo);

    const alertaPanel = document.getElementById('alertaStockPanel');
    const alertaCount = document.getElementById('alertaStockCount');

    if (!alertaPanel || !alertaCount) return;

    if (productosBajoStock.length > 0) {
        alertaCount.textContent = productosBajoStock.length;
        alertaPanel.style.display = 'block';
    } else {
        alertaPanel.style.display = 'none';
    }
}

// Mostrar solo productos con stock bajo
function mostrarProductosBajoStock() {
    const stockBajo = 10;
    const productosBajoStock = todosLosProductos.filter(p => p.cantidad < stockBajo);

    if (productosBajoStock.length === 0) {
        showSuccess('¡Excelente! Todos los productos tienen stock suficiente', 'Stock Saludable');
        return;
    }

    // Limpiar filtros y aplicar filtro de stock bajo
    const searchInput = document.getElementById('searchProductInput');
    const precioMin = document.getElementById('filtroPrecioMin');
    const precioMax = document.getElementById('filtroPrecioMax');
    const filtroStock = document.getElementById('filtroStock');

    if (searchInput) searchInput.value = '';
    if (precioMin) precioMin.value = '';
    if (precioMax) precioMax.value = '';
    if (filtroStock) {
        filtroStock.value = 'bajo';
        // Aplicar filtros para mostrar productos con stock bajo y crítico
        aplicarFiltros();
    } else {
        // Si no existe el select, mostrar directamente
        mostrarProductosEnTabla(productosBajoStock);
    }
}

// ============================================
// EVENTOS
// ============================================

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        cerrarModal();
    }
});

// Cargar productos al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('home')) {
        cargarProductos();

        // Agregar evento de búsqueda
        const searchInput = document.getElementById('searchProductInput');
        if (searchInput) {
            searchInput.addEventListener('input', buscarProductos);
        }
    }
});
