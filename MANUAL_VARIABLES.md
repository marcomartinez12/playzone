# Manual de Variables - PlayZone

## Variables Globales Frontend

### config.js

#### `API_URL`
- **Tipo**: string
- **Valor**: `'http://localhost:8000/api'`
- **Descripción**: URL base del API backend
- **Uso**: Todas las peticiones HTTP al servidor

---

### VentaController.js

#### `cart`
- **Tipo**: Array<Object>
- **Valor inicial**: `[]`
- **Descripción**: Carrito de compras con productos agregados
- **Estructura**:
  ```javascript
  {
    id: number,
    name: string,
    price: number,
    quantity: number,
    codigo: string
  }
  ```

#### `originalModalContent`
- **Tipo**: string (HTML)
- **Descripción**: Contenido original del modal antes de modificarlo
- **Uso**: Restaurar modal después de mostrar formulario de cliente

---

### VentasView.js

#### `ventasData`
- **Tipo**: Array<Object>
- **Valor inicial**: `[]`
- **Descripción**: Array con ventas actuales (puede estar filtrado)

#### `ventasOriginales`
- **Tipo**: Array<Object>
- **Valor inicial**: `[]`
- **Descripción**: Copia de todas las ventas sin filtrar
- **Uso**: Restaurar vista completa al limpiar filtros

---

### ServiciosView.js

#### `servicioEnEdicion`
- **Tipo**: Object | null
- **Descripción**: Servicio que está siendo editado actualmente
- **Estructura**:
  ```javascript
  {
    id_servicio: number,
    id_cliente: number,
    dispositivo: string,
    descripcion: string,
    costo: number,
    estado: string,
    fecha_ingreso: string
  }
  ```

---

### DashboardView.js

#### `ventasChart`
- **Tipo**: Chart | null
- **Descripción**: Instancia de Chart.js para la gráfica de ventas
- **Uso**: Actualizar/destruir gráfica al recargar datos

---

### eventBus.js

#### `Events`
- **Tipo**: Object
- **Descripción**: Constantes con nombres de eventos del sistema
- **Valores**:
  ```javascript
  {
    PRODUCTO_CREADO: 'producto:creado',
    PRODUCTO_ACTUALIZADO: 'producto:actualizado',
    PRODUCTO_ELIMINADO: 'producto:eliminado',
    VENTA_CREADA: 'venta:creada',
    SERVICIO_CREADO: 'servicio:creado',
    SERVICIO_ACTUALIZADO: 'servicio:actualizado',
    CLIENTE_CREADO: 'cliente:creado',
    CLIENTE_ACTUALIZADO: 'cliente:actualizado'
  }
  ```

#### `EventBus.events`
- **Tipo**: Object
- **Descripción**: Mapa de eventos y sus listeners registrados
- **Estructura**: `{ eventName: [callback1, callback2, ...] }`

---

## Variables de Estado en LocalStorage

### `token`
- **Tipo**: string (JWT)
- **Descripción**: Token de autenticación del usuario
- **Uso**: Enviado en header Authorization de todas las peticiones

### `usuario`
- **Tipo**: string (JSON)
- **Descripción**: Datos del usuario autenticado
- **Estructura**:
  ```javascript
  {
    id_usuario: number,
    username: string,
    email: string
  }
  ```

---

## Variables de Entorno Backend

### `.env`

#### `DATABASE_URL`
- **Tipo**: string
- **Descripción**: URL de conexión a PostgreSQL
- **Formato**: `postgresql://usuario:password@host:puerto/nombre_bd`

#### `SECRET_KEY`
- **Tipo**: string
- **Descripción**: Clave secreta para firmar tokens JWT
- **Seguridad**: Debe ser aleatoria y segura

#### `ALGORITHM`
- **Tipo**: string
- **Valor**: `'HS256'`
- **Descripción**: Algoritmo de encriptación para JWT

#### `ACCESS_TOKEN_EXPIRE_MINUTES`
- **Tipo**: int
- **Valor**: `30`
- **Descripción**: Tiempo de expiración del token en minutos

#### `DB_HOST`
- **Tipo**: string
- **Valor**: `'localhost'`
- **Descripción**: Host de la base de datos PostgreSQL

#### `DB_PORT`
- **Tipo**: int
- **Valor**: `5432`
- **Descripción**: Puerto de PostgreSQL

#### `DB_NAME`
- **Tipo**: string
- **Valor**: `'playzone'`
- **Descripción**: Nombre de la base de datos

#### `DB_USER`
- **Tipo**: string
- **Descripción**: Usuario de PostgreSQL

#### `DB_PASSWORD`
- **Tipo**: string
- **Descripción**: Contraseña de PostgreSQL

---

## Constantes Backend

### models/producto.py

#### `CategoriaProducto`
- **Tipo**: Enum
- **Valores**:
  - `VIDEOJUEGO = "videojuego"`
  - `CONSOLA = "consola"`
  - `ACCESORIO = "accesorio"`
- **Descripción**: Categorías válidas para productos

---

### models/servicio.py

#### `EstadoServicio`
- **Tipo**: Enum
- **Valores**:
  - `EN_REPARACION = "En reparacion"`
  - `LISTO = "Listo"`
  - `ENTREGADO = "Entregado"`
- **Descripción**: Estados posibles de un servicio

---

## Variables de Configuración Backend

### config/database.py

#### `DATABASE_CONFIG`
- **Tipo**: dict
- **Descripción**: Configuración de conexión a PostgreSQL
- **Estructura**:
  ```python
  {
    'host': str,
    'port': int,
    'database': str,
    'user': str,
    'password': str
  }
  ```

---

## Variables de Sesión/Request

### FastAPI Dependency Injection

#### `current_user`
- **Tipo**: dict
- **Descripción**: Usuario autenticado actual (inyectado vía Depends)
- **Estructura**:
  ```python
  {
    'id_usuario': int,
    'username': str,
    'email': str
  }
  ```

---

## Variables de Base de Datos

### Tabla: usuarios

- `id_usuario` (SERIAL PRIMARY KEY): ID único del usuario
- `username` (VARCHAR UNIQUE): Nombre de usuario
- `email` (VARCHAR UNIQUE): Email del usuario
- `password_hash` (VARCHAR): Contraseña hasheada
- `fecha_registro` (TIMESTAMP): Fecha de creación

### Tabla: productos

- `id_producto` (SERIAL PRIMARY KEY): ID único del producto
- `codigo` (VARCHAR UNIQUE): Código único del producto
- `nombre` (VARCHAR): Nombre del producto
- `categoria` (VARCHAR): Categoría (videojuego/consola/accesorio)
- `precio` (DECIMAL): Precio unitario
- `cantidad` (INTEGER): Stock disponible
- `descripcion` (TEXT): Descripción del producto
- `imagen_url` (TEXT): URL de la imagen
- `fecha_registro` (TIMESTAMP): Fecha de creación

### Tabla: clientes

- `id_cliente` (SERIAL PRIMARY KEY): ID único del cliente
- `nombre` (VARCHAR): Nombre completo
- `documento` (VARCHAR UNIQUE): Número de documento
- `telefono` (VARCHAR): Teléfono de contacto
- `email` (VARCHAR): Email del cliente
- `fecha_registro` (TIMESTAMP): Fecha de creación

### Tabla: ventas

- `id_venta` (SERIAL PRIMARY KEY): ID único de la venta
- `id_usuario` (INTEGER FK): Usuario que registró la venta
- `id_cliente` (INTEGER FK): Cliente que compró
- `total` (DECIMAL): Monto total de la venta
- `fecha_venta` (TIMESTAMP): Fecha y hora de la venta

### Tabla: detalle_ventas

- `id_detalle` (SERIAL PRIMARY KEY): ID único del detalle
- `id_venta` (INTEGER FK): Venta asociada
- `id_producto` (INTEGER FK): Producto vendido
- `cantidad` (INTEGER): Cantidad vendida
- `precio_unitario` (DECIMAL): Precio al momento de la venta

### Tabla: servicios

- `id_servicio` (SERIAL PRIMARY KEY): ID único del servicio
- `id_cliente` (INTEGER FK): Cliente del servicio
- `dispositivo` (VARCHAR): Tipo de dispositivo
- `descripcion` (TEXT): Descripción del problema/servicio
- `costo` (DECIMAL): Costo del servicio
- `estado` (VARCHAR): Estado actual (En reparacion/Listo/Entregado)
- `fecha_ingreso` (TIMESTAMP): Fecha de ingreso del servicio
- `fecha_entrega` (TIMESTAMP): Fecha de entrega

---

## Variables de Formularios HTML

### Formulario de Cliente (VentaController)

- `clienteDocumento`: Input del documento
- `clienteNombre`: Input del nombre
- `clienteTelefono`: Input del teléfono
- `clienteEmail`: Input del email (opcional)
- `clienteStatus`: Div de estado de búsqueda
- `btnBuscarCliente`: Botón de búsqueda

### Formulario de Servicio (ServiciosView)

- `servicioClienteDocumento`: Input del documento del cliente
- `servicioClienteNombre`: Input del nombre del cliente
- `servicioClienteTelefono`: Input del teléfono
- `servicioClienteEmail`: Input del email
- `servicioDispositivo`: Input del tipo de dispositivo
- `servicioDescripcion`: Textarea de descripción
- `servicioCosto`: Input del costo
- `servicioEstado`: Select del estado

### Filtros de Ventas

- `fechaInicial`: Input date para fecha inicial
- `fechaFinal`: Input date para fecha final

---

## IDs de Elementos DOM Importantes

### Dashboard (inicio)

- `stat-total-productos`: Tarjeta total de productos
- `stat-stock-bajo`: Tarjeta productos con stock bajo
- `stat-ventas-hoy`: Tarjeta ventas de hoy
- `stat-servicios-pendientes`: Tarjeta servicios pendientes
- `stat-ingresos-mes`: Tarjeta ingresos del mes
- `stat-ingresos-ventas`: Tarjeta ingresos por ventas
- `stat-ingresos-servicios`: Tarjeta ingresos por servicios
- `producto-mas-vendido`: Sección del producto más vendido
- `graficaVentasDiarias`: Canvas para gráfica de ventas

### Ventas

- `ventasHoy`: Contador de ventas hoy
- `totalHoy`: Total recaudado hoy
- `productosVendidos`: Total productos vendidos
- `ventasTableBody`: Tbody de tabla de ventas

### Modales

- `confirmModalOverlay`: Overlay del modal de confirmación
- `confirmIcon`: Icono del modal
- `confirmTitle`: Título del modal
- `confirmMessage`: Mensaje del modal
- `confirmCancel`: Botón cancelar
- `confirmOk`: Botón confirmar

### Notificaciones

- `notificationContainer`: Contenedor de notificaciones toast
