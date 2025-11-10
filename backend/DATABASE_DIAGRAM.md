# Diagrama de Base de Datos - PlayZone

## Modelo Entidad-Relación

```
┌──────────────────┐
│    USUARIOS      │
├──────────────────┤
│ id_usuario (PK)  │
│ username         │
│ email            │
│ password_hash    │
│ fecha_registro   │
│ activo           │
└────────┬─────────┘
         │
         │ (1 a N)
         │
    ┌────┴─────────────────────────┐
    │                              │
    │                              │
┌───┴──────────┐          ┌────────┴──────┐
│   VENTAS     │          │   SERVICIOS   │
├──────────────┤          ├───────────────┤
│ id_venta(PK) │          │id_servicio(PK)│
│ id_usuario   │◄─────────┤id_usuario     │
│ id_cliente   │          │id_cliente     │
│ total        │          │consola        │
│ fecha_venta  │          │descripcion    │
└──────┬───────┘          │estado         │
       │                  │costo          │
       │ (1 a N)          │fecha_ingreso  │
       │                  │fecha_entrega  │
┌──────┴──────────┐       └───────────────┘
│ DETALLE_VENTAS  │              │
├─────────────────┤              │
│ id_detalle (PK) │              │ (N a 1)
│ id_venta        │              │
│ id_producto     │              │
│ cantidad        │         ┌────┴─────────┐
│ precio_unitario │         │   CLIENTES   │
└────────┬────────┘         ├──────────────┤
         │                  │id_cliente(PK)│
         │ (N a 1)          │nombre        │
         │                  │documento     │
    ┌────┴──────────┐       │telefono      │
    │   PRODUCTOS   │       │email         │
    ├───────────────┤       │fecha_registro│
    │id_producto(PK)│       └──────────────┘
    │codigo         │
    │nombre         │
    │categoria      │
    │precio         │
    │cantidad       │
    │descripcion    │
    │imagen_url     │
    │fecha_registro │
    └───────────────┘
```

## Relaciones

### 1-N (Uno a Muchos)

- **USUARIOS → VENTAS**: Un usuario puede registrar muchas ventas
- **USUARIOS → SERVICIOS**: Un usuario puede registrar muchos servicios
- **CLIENTES → VENTAS**: Un cliente puede tener muchas compras
- **CLIENTES → SERVICIOS**: Un cliente puede solicitar muchos servicios
- **VENTAS → DETALLE_VENTAS**: Una venta tiene varios productos
- **PRODUCTOS → DETALLE_VENTAS**: Un producto puede estar en varias ventas

## Descripción de Tablas

### USUARIOS
Almacena los administradores del sistema.
- **RF-01:** Autenticación con JWT
- Contraseña hasheada con bcrypt

### CLIENTES
Información de clientes que compran o solicitan servicios.
- **RF-07:** Datos básicos (nombre, documento, teléfono, email)
- `documento` es único para evitar duplicados

### PRODUCTOS
Inventario de productos (videojuegos, consolas, accesorios).
- **RF-02:** Registro con código autogenerado
- **RF-03:** Actualización y eliminación
- **RF-08:** Listado en tablero
- **RF-09:** Filtrado por categoría
- **RF-10:** Búsqueda específica
- **RF-11:** Alertas de stock bajo (cantidad <= 5)
- Categorías: `videojuego`, `consola`, `accesorio`

### VENTAS
Registro de ventas realizadas.
- **RF-04:** Creación de venta
- **RF-05:** Listado y reportes
- Actualiza automáticamente el stock de productos

### DETALLE_VENTAS
Productos específicos en cada venta.
- Almacena cantidad y precio al momento de la venta
- Valida stock disponible antes de insertar (trigger)

### SERVICIOS
Servicios de reparación de consolas.
- **RF-06:** Registro de servicio
- **RF-13:** Cambio de estado (En reparación → Listo → Entregado)
- **RF-14:** Búsqueda por cliente o consola
- Estados: `En reparacion`, `Listo`, `Entregado`

## Vistas Útiles

### vista_productos_stock_bajo
```sql
SELECT * FROM vista_productos_stock_bajo;
```
Muestra productos con cantidad <= 5 para alertas (RF-11)

### vista_ventas_diarias
```sql
SELECT * FROM vista_ventas_diarias;
```
Reporte de ventas del día actual (RF-05)

### vista_servicios_pendientes
```sql
SELECT * FROM vista_servicios_pendientes;
```
Servicios en estado "En reparación" con días pendientes

## Triggers Implementados

### 1. actualizar_fecha_entrega_servicio
- **Tabla:** servicios
- **Evento:** BEFORE UPDATE
- **Función:** Actualiza `fecha_entrega` cuando el estado cambia a "Listo" o "Entregado"
- **RF-13:** Marcación automática de fecha de finalización

### 2. validar_stock_venta
- **Tabla:** detalle_ventas
- **Evento:** BEFORE INSERT
- **Función:** Valida que haya stock suficiente antes de registrar una venta
- **RF-04:** Previene ventas con stock insuficiente

## Índices para Performance

- `usuarios`: username, email
- `clientes`: documento, nombre
- `productos`: codigo, categoria, nombre, cantidad
- `ventas`: fecha_venta, id_cliente, id_usuario
- `detalle_ventas`: id_venta, id_producto
- `servicios`: estado, id_cliente, consola, fecha_ingreso

## Constraints (Restricciones)

### Check Constraints
- `productos.precio > 0`
- `productos.cantidad >= 0`
- `productos.categoria IN ('videojuego', 'consola', 'accesorio')`
- `ventas.total >= 0`
- `detalle_ventas.cantidad > 0`
- `detalle_ventas.precio_unitario > 0`
- `servicios.estado IN ('En reparacion', 'Listo', 'Entregado')`
- `servicios.costo >= 0`

### Unique Constraints
- `usuarios.username`
- `usuarios.email`
- `clientes.documento`
- `productos.codigo`

### Foreign Keys
- `ventas.id_usuario → usuarios.id_usuario`
- `ventas.id_cliente → clientes.id_cliente`
- `detalle_ventas.id_venta → ventas.id_venta` (ON DELETE CASCADE)
- `detalle_ventas.id_producto → productos.id_producto`
- `servicios.id_usuario → usuarios.id_usuario`
- `servicios.id_cliente → clientes.id_cliente`

## Datos de Ejemplo Incluidos

El script `database_schema.sql` incluye:
- 1 usuario admin (username: admin, password: admin123)
- 3 clientes de ejemplo
- 6 productos (2 videojuegos, 2 consolas, 2 accesorios)

## Consultas Útiles

### Productos más vendidos
```sql
SELECT
    p.nombre,
    p.categoria,
    SUM(dv.cantidad) as total_vendido,
    SUM(dv.cantidad * dv.precio_unitario) as monto_total
FROM detalle_ventas dv
JOIN productos p ON dv.id_producto = p.id_producto
GROUP BY p.id_producto, p.nombre, p.categoria
ORDER BY total_vendido DESC
LIMIT 10;
```

### Reporte de ventas por categoría
```sql
SELECT
    p.categoria,
    COUNT(DISTINCT v.id_venta) as total_ventas,
    SUM(dv.cantidad) as productos_vendidos,
    SUM(dv.cantidad * dv.precio_unitario) as monto_total
FROM detalle_ventas dv
JOIN productos p ON dv.id_producto = p.id_producto
JOIN ventas v ON dv.id_venta = v.id_venta
GROUP BY p.categoria;
```

### Clientes con más compras
```sql
SELECT
    c.nombre,
    c.documento,
    COUNT(v.id_venta) as total_compras,
    SUM(v.total) as monto_total
FROM clientes c
JOIN ventas v ON c.id_cliente = v.id_cliente
GROUP BY c.id_cliente, c.nombre, c.documento
ORDER BY total_compras DESC;
```

### Servicios por estado
```sql
SELECT
    estado,
    COUNT(*) as total,
    AVG(EXTRACT(DAY FROM (COALESCE(fecha_entrega, NOW()) - fecha_ingreso))) as dias_promedio
FROM servicios
GROUP BY estado;
```
