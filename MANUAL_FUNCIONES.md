# Manual de Funciones - PlayZone

## Frontend

### NavigationController.js

#### `showSection(sectionId)`
- **Descripción**: Muestra una sección específica del sistema y oculta las demás
- **Parámetros**:
  - `sectionId` (string): ID de la sección a mostrar (ej: 'inicio', 'productos', 'ventas')
- **Retorna**: void

---

### DashboardView.js

#### `cargarEstadisticasDashboard()`
- **Descripción**: Carga todas las estadísticas del dashboard (productos, ventas, servicios)
- **Parámetros**: ninguno
- **Retorna**: Promise<void>

#### `obtenerProductoMasVendido(ventas)`
- **Descripción**: Calcula el producto más vendido basado en las ventas
- **Parámetros**:
  - `ventas` (Array): Array de objetos de ventas con sus productos
- **Retorna**: Object `{ nombre, cantidad, imagen_url }`

#### `mostrarEstadisticas(stats)`
- **Descripción**: Actualiza el DOM con las estadísticas del dashboard
- **Parámetros**:
  - `stats` (Object): Objeto con todas las estadísticas a mostrar
- **Retorna**: void

#### `crearGraficaVentasDiarias(ventas)`
- **Descripción**: Crea gráfica de barras con ventas de los últimos 7 días usando Chart.js
- **Parámetros**:
  - `ventas` (Array): Array de ventas
- **Retorna**: void

#### `filtrarVentasHoy(ventas)`
- **Descripción**: Filtra ventas que fueron realizadas hoy
- **Parámetros**:
  - `ventas` (Array): Array de todas las ventas
- **Retorna**: Array de ventas del día

#### `calcularIngresosMes(ventas)`
- **Descripción**: Calcula ingresos totales del mes actual
- **Parámetros**:
  - `ventas` (Array): Array de ventas
- **Retorna**: number (monto total)

#### `calcularIngresosServiciosMes(servicios)`
- **Descripción**: Calcula ingresos de servicios del mes actual
- **Parámetros**:
  - `servicios` (Array): Array de servicios
- **Retorna**: number (monto total)

---

### VentaController.js

#### `buscarClientePorDocumento(documento)`
- **Descripción**: Busca un cliente en la base de datos por su documento
- **Parámetros**:
  - `documento` (string): Número de documento del cliente
- **Retorna**: Promise<Object|null> (datos del cliente o null)

#### `mostrarFormularioCliente()`
- **Descripción**: Muestra modal con formulario para capturar datos del cliente
- **Parámetros**: ninguno
- **Retorna**: Promise<Object|null> (datos del cliente o null si cancela)

#### `saveCart()`
- **Descripción**: Guarda el carrito como una venta (RF-04)
- **Parámetros**: ninguno
- **Retorna**: Promise<void>

#### `addToCart(productId)`
- **Descripción**: Agrega un producto al carrito de compras
- **Parámetros**:
  - `productId` (number): ID del producto a agregar
- **Retorna**: void

#### `removeFromCart(productId)`
- **Descripción**: Elimina un producto del carrito
- **Parámetros**:
  - `productId` (number): ID del producto a eliminar
- **Retorna**: void

#### `updateQuantity(productId, quantity)`
- **Descripción**: Actualiza la cantidad de un producto en el carrito
- **Parámetros**:
  - `productId` (number): ID del producto
  - `quantity` (number): Nueva cantidad
- **Retorna**: void

#### `renderCart()`
- **Descripción**: Renderiza el carrito de compras en el DOM
- **Parámetros**: ninguno
- **Retorna**: void

---

### VentasView.js

#### `cargarVentasDelDia()`
- **Descripción**: Carga las ventas del día y estadísticas (RF-05)
- **Parámetros**: ninguno
- **Retorna**: Promise<void>

#### `renderVentasTable(ventas)`
- **Descripción**: Renderiza la tabla de ventas
- **Parámetros**:
  - `ventas` (Array): Array de objetos de ventas
- **Retorna**: void

#### `verDetalleVenta(idVenta)`
- **Descripción**: Muestra modal con detalles completos de una venta
- **Parámetros**:
  - `idVenta` (number): ID de la venta
- **Retorna**: Promise<void>

#### `formatearFecha(fecha)`
- **Descripción**: Formatea una fecha a formato local colombiano
- **Parámetros**:
  - `fecha` (string|Date): Fecha a formatear
- **Retorna**: string (fecha formateada)

#### `descargarReporte()`
- **Descripción**: Descarga reporte PDF de ventas
- **Parámetros**: ninguno
- **Retorna**: Promise<void>

#### `filtrarVentasPorFecha()`
- **Descripción**: Filtra ventas por rango de fechas seleccionado
- **Parámetros**: ninguno (lee del DOM)
- **Retorna**: void

#### `limpiarFiltros()`
- **Descripción**: Limpia filtros y muestra todas las ventas
- **Parámetros**: ninguno
- **Retorna**: void

#### `actualizarEstadisticasFiltradas(ventas)`
- **Descripción**: Actualiza estadísticas basadas en ventas filtradas
- **Parámetros**:
  - `ventas` (Array): Ventas filtradas
- **Retorna**: void

---

### ServiciosView.js

#### `cargarServicios()`
- **Descripción**: Carga y muestra todos los servicios
- **Parámetros**: ninguno
- **Retorna**: Promise<void>

#### `renderServiciosTable(servicios)`
- **Descripción**: Renderiza tabla de servicios
- **Parámetros**:
  - `servicios` (Array): Array de servicios
- **Retorna**: void

#### `mostrarFormularioServicio(esEdicion, servicio)`
- **Descripción**: Muestra modal para crear/editar servicio
- **Parámetros**:
  - `esEdicion` (boolean): true si es edición, false si es nuevo
  - `servicio` (Object): Datos del servicio (solo en edición)
- **Retorna**: void

#### `buscarClienteParaServicio()`
- **Descripción**: Busca cliente por documento para asociarlo al servicio
- **Parámetros**: ninguno (lee del DOM)
- **Retorna**: Promise<void>

#### `guardarServicio()`
- **Descripción**: Guarda un nuevo servicio
- **Parámetros**: ninguno (lee del formulario)
- **Retorna**: Promise<void>

#### `actualizarServicio()`
- **Descripción**: Actualiza un servicio existente
- **Parámetros**: ninguno (lee del formulario)
- **Retorna**: Promise<void>

#### `eliminarServicio(idServicio)`
- **Descripción**: Elimina un servicio con confirmación
- **Parámetros**:
  - `idServicio` (number): ID del servicio
- **Retorna**: Promise<void>

---

### notifications.js

#### `initNotifications()`
- **Descripción**: Inicializa el sistema de notificaciones (crea contenedores en DOM)
- **Parámetros**: ninguno
- **Retorna**: void

#### `showNotification(message, type, title, duration)`
- **Descripción**: Muestra una notificación toast
- **Parámetros**:
  - `message` (string): Mensaje a mostrar
  - `type` (string): 'success', 'error', 'warning', 'info'
  - `title` (string): Título opcional
  - `duration` (number): Duración en ms (default: 4000)
- **Retorna**: void

#### `showSuccess(message, title)`
- **Descripción**: Muestra notificación de éxito
- **Parámetros**:
  - `message` (string): Mensaje
  - `title` (string): Título opcional
- **Retorna**: void

#### `showError(message, title)`
- **Descripción**: Muestra notificación de error
- **Parámetros**:
  - `message` (string): Mensaje
  - `title` (string): Título opcional
- **Retorna**: void

#### `showWarning(message, title)`
- **Descripción**: Muestra notificación de advertencia
- **Parámetros**:
  - `message` (string): Mensaje
  - `title` (string): Título opcional
- **Retorna**: void

#### `showInfo(message, title)`
- **Descripción**: Muestra notificación informativa
- **Parámetros**:
  - `message` (string): Mensaje
  - `title` (string): Título opcional
- **Retorna**: void

#### `showConfirm(options)`
- **Descripción**: Muestra modal de confirmación
- **Parámetros**:
  - `options` (Object): { title, message, type, confirmText, cancelText }
- **Retorna**: Promise<boolean> (true si confirma, false si cancela)

---

### eventBus.js

#### `EventBus.emit(event, data)`
- **Descripción**: Emite un evento para comunicación entre componentes
- **Parámetros**:
  - `event` (string): Nombre del evento
  - `data` (any): Datos a enviar
- **Retorna**: void

#### `EventBus.on(event, callback)`
- **Descripción**: Escucha un evento
- **Parámetros**:
  - `event` (string): Nombre del evento
  - `callback` (Function): Función a ejecutar
- **Retorna**: void

#### `EventBus.off(event, callback)`
- **Descripción**: Deja de escuchar un evento
- **Parámetros**:
  - `event` (string): Nombre del evento
  - `callback` (Function): Función registrada
- **Retorna**: void

---

### utils.js

#### `formatCurrency(amount)`
- **Descripción**: Formatea un número como moneda colombiana (COP)
- **Parámetros**:
  - `amount` (number): Monto a formatear
- **Retorna**: string (ej: "$1.234.567")

#### `getAuthHeaders()`
- **Descripción**: Obtiene headers de autenticación con token JWT
- **Parámetros**: ninguno
- **Retorna**: Object con headers

---

## Backend

### VentaController

#### `crear_venta(venta: VentaCreate)`
- **Descripción**: Crea una nueva venta y actualiza inventario (RF-04)
- **Parámetros**:
  - `venta` (VentaCreate): Datos de la venta con productos
- **Retorna**: dict con venta creada
- **Excepciones**: HTTPException si no hay stock o producto no existe

#### `obtener_ventas(fecha_inicio, fecha_fin, id_cliente)`
- **Descripción**: Obtiene lista de ventas con filtros (RF-05)
- **Parámetros**:
  - `fecha_inicio` (datetime): Fecha inicial (opcional)
  - `fecha_fin` (datetime): Fecha final (opcional)
  - `id_cliente` (int): ID cliente (opcional)
- **Retorna**: List[dict] con ventas y productos

#### `obtener_venta(id_venta: int)`
- **Descripción**: Obtiene una venta específica con detalles
- **Parámetros**:
  - `id_venta` (int): ID de la venta
- **Retorna**: dict con venta completa
- **Excepciones**: HTTPException 404 si no existe

#### `obtener_ventas_diarias(fecha: date)`
- **Descripción**: Obtiene reporte de ventas diarias
- **Parámetros**:
  - `fecha` (date): Fecha (opcional, default: hoy)
- **Retorna**: dict con estadísticas del día

---

### ProductoController

#### `crear_producto(producto: ProductoCreate)`
- **Descripción**: Crea un nuevo producto (RF-02)
- **Parámetros**:
  - `producto` (ProductoCreate): Datos del producto
- **Retorna**: dict con producto creado

#### `obtener_productos(categoria, busqueda)`
- **Descripción**: Obtiene lista de productos con filtros (RF-09, RF-10)
- **Parámetros**:
  - `categoria` (str): Categoría (opcional)
  - `busqueda` (str): Búsqueda por nombre/código (opcional)
- **Retorna**: List[dict] con productos

#### `obtener_producto(id_producto: int)`
- **Descripción**: Obtiene un producto específico
- **Parámetros**:
  - `id_producto` (int): ID del producto
- **Retorna**: dict con producto
- **Excepciones**: HTTPException 404 si no existe

#### `actualizar_producto(id_producto: int, producto: ProductoUpdate)`
- **Descripción**: Actualiza un producto (RF-03)
- **Parámetros**:
  - `id_producto` (int): ID del producto
  - `producto` (ProductoUpdate): Datos a actualizar
- **Retorna**: dict con producto actualizado

#### `eliminar_producto(id_producto: int)`
- **Descripción**: Elimina un producto
- **Parámetros**:
  - `id_producto` (int): ID del producto
- **Retorna**: dict con mensaje de éxito

---

### ClienteController

#### `crear_cliente(cliente: ClienteCreate)`
- **Descripción**: Crea o actualiza un cliente
- **Parámetros**:
  - `cliente` (ClienteCreate): Datos del cliente
- **Retorna**: dict con cliente creado/actualizado

#### `obtener_clientes()`
- **Descripción**: Obtiene lista de todos los clientes
- **Parámetros**: ninguno
- **Retorna**: List[dict] con clientes

#### `buscar_cliente_por_documento(documento: str)`
- **Descripción**: Busca un cliente por su documento
- **Parámetros**:
  - `documento` (str): Número de documento
- **Retorna**: dict con cliente o None

---

### ServicioController

#### `crear_servicio(servicio: ServicioCreate)`
- **Descripción**: Crea un nuevo servicio de reparación
- **Parámetros**:
  - `servicio` (ServicioCreate): Datos del servicio
- **Retorna**: dict con servicio creado

#### `obtener_servicios(estado)`
- **Descripción**: Obtiene lista de servicios con filtro opcional
- **Parámetros**:
  - `estado` (str): Estado del servicio (opcional)
- **Retorna**: List[dict] con servicios

#### `actualizar_servicio(id_servicio: int, servicio: ServicioUpdate)`
- **Descripción**: Actualiza un servicio existente
- **Parámetros**:
  - `id_servicio` (int): ID del servicio
  - `servicio` (ServicioUpdate): Datos a actualizar
- **Retorna**: dict con servicio actualizado

#### `eliminar_servicio(id_servicio: int)`
- **Descripción**: Elimina un servicio
- **Parámetros**:
  - `id_servicio` (int): ID del servicio
- **Retorna**: dict con mensaje de éxito

---

### AuthController

#### `login(credenciales: UsuarioLogin)`
- **Descripción**: Autentica un usuario y genera token JWT (RF-01)
- **Parámetros**:
  - `credenciales` (UsuarioLogin): username y password
- **Retorna**: dict con access_token
- **Excepciones**: HTTPException 401 si credenciales incorrectas

#### `get_current_user(token: str)`
- **Descripción**: Obtiene usuario actual desde token JWT
- **Parámetros**:
  - `token` (str): Token JWT
- **Retorna**: dict con datos del usuario
- **Excepciones**: HTTPException 401 si token inválido

---

### PDFGenerator

#### `generate_ventas_report(ventas: List[dict])`
- **Descripción**: Genera reporte PDF de ventas
- **Parámetros**:
  - `ventas` (List[dict]): Lista de ventas
- **Retorna**: BytesIO con PDF generado

---

## Utilidades Backend

### database.py

#### `get_db_connection()`
- **Descripción**: Obtiene conexión a PostgreSQL
- **Parámetros**: ninguno
- **Retorna**: psycopg2.connection

#### `get_db_cursor()`
- **Descripción**: Context manager para cursor de BD
- **Parámetros**: ninguno
- **Retorna**: RealDictCursor (devuelve diccionarios)

---

### auth.py

#### `hash_password(password: str)`
- **Descripción**: Hash de contraseña con bcrypt
- **Parámetros**:
  - `password` (str): Contraseña en texto plano
- **Retorna**: str (hash)

#### `verify_password(password: str, hashed: str)`
- **Descripción**: Verifica contraseña contra hash
- **Parámetros**:
  - `password` (str): Contraseña en texto plano
  - `hashed` (str): Hash almacenado
- **Retorna**: bool

#### `create_access_token(data: dict, expires_delta: timedelta)`
- **Descripción**: Crea token JWT
- **Parámetros**:
  - `data` (dict): Datos a codificar
  - `expires_delta` (timedelta): Tiempo de expiración
- **Retorna**: str (token JWT)
