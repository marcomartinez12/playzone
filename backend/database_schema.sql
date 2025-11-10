-- ============================================================
-- PLAYZONE INVENTORY SYSTEM - DATABASE SCHEMA
-- Sistema de gestion de inventario y servicios de reparacion
-- PostgreSQL / Supabase
-- ============================================================

-- Eliminar tablas si existen (para desarrollo)
DROP TABLE IF EXISTS detalle_ventas CASCADE;
DROP TABLE IF EXISTS ventas CASCADE;
DROP TABLE IF EXISTS servicios CASCADE;
DROP TABLE IF EXISTS productos CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

-- ============================================================
-- TABLA: USUARIOS
-- RF-01: Almacena usuarios del sistema (administradores)
-- ============================================================
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT true
);

-- Indices para usuarios
CREATE INDEX idx_usuarios_username ON usuarios(username);
CREATE INDEX idx_usuarios_email ON usuarios(email);

-- ============================================================
-- TABLA: CLIENTES
-- RF-07: Datos basicos de clientes
-- ============================================================
CREATE TABLE clientes (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    documento VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(15),
    email VARCHAR(100),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices para clientes
CREATE INDEX idx_clientes_documento ON clientes(documento);
CREATE INDEX idx_clientes_nombre ON clientes(nombre);

-- ============================================================
-- TABLA: PRODUCTOS
-- RF-02, RF-03: Gestion de productos del inventario
-- RF-08: Tablero inicial
-- RF-09: Filtrado de productos
-- RF-10: Busqueda especifica
-- RF-11: Alertas de stock bajo
-- ============================================================
CREATE TABLE productos (
    id_producto SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    categoria VARCHAR(50) NOT NULL CHECK (categoria IN ('videojuego', 'consola', 'accesorio')),
    precio DECIMAL(10, 2) NOT NULL CHECK (precio > 0),
    cantidad INTEGER NOT NULL DEFAULT 0 CHECK (cantidad >= 0),
    descripcion TEXT,
    imagen_url TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices para productos
CREATE INDEX idx_productos_codigo ON productos(codigo);
CREATE INDEX idx_productos_categoria ON productos(categoria);
CREATE INDEX idx_productos_nombre ON productos(nombre);
CREATE INDEX idx_productos_cantidad ON productos(cantidad); -- Para stock bajo

-- ============================================================
-- TABLA: VENTAS
-- RF-04, RF-05: Registro y listado de ventas
-- ============================================================
CREATE TABLE ventas (
    id_venta SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente),
    total DECIMAL(10, 2) NOT NULL CHECK (total >= 0),
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices para ventas
CREATE INDEX idx_ventas_fecha ON ventas(fecha_venta DESC);
CREATE INDEX idx_ventas_cliente ON ventas(id_cliente);
CREATE INDEX idx_ventas_usuario ON ventas(id_usuario);

-- ============================================================
-- TABLA: DETALLE_VENTAS
-- RF-04: Detalle de productos vendidos en cada venta
-- ============================================================
CREATE TABLE detalle_ventas (
    id_detalle SERIAL PRIMARY KEY,
    id_venta INTEGER NOT NULL REFERENCES ventas(id_venta) ON DELETE CASCADE,
    id_producto INTEGER NOT NULL REFERENCES productos(id_producto),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10, 2) NOT NULL CHECK (precio_unitario > 0)
);

-- Indices para detalle_ventas
CREATE INDEX idx_detalle_ventas_venta ON detalle_ventas(id_venta);
CREATE INDEX idx_detalle_ventas_producto ON detalle_ventas(id_producto);

-- ============================================================
-- TABLA: SERVICIOS
-- RF-06: Registrar servicios de reparacion
-- RF-13: Marcar reparacion como lista para entrega
-- RF-14: Busqueda de reparaciones
-- ============================================================
CREATE TABLE servicios (
    id_servicio SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente),
    consola VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    estado VARCHAR(50) NOT NULL DEFAULT 'En reparacion' CHECK (estado IN ('En reparacion', 'Listo', 'Entregado')),
    costo DECIMAL(10, 2) CHECK (costo >= 0),
    fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega TIMESTAMP
);

-- Indices para servicios
CREATE INDEX idx_servicios_estado ON servicios(estado);
CREATE INDEX idx_servicios_cliente ON servicios(id_cliente);
CREATE INDEX idx_servicios_consola ON servicios(consola);
CREATE INDEX idx_servicios_fecha_ingreso ON servicios(fecha_ingreso DESC);

-- ============================================================
-- VISTAS UTILES
-- ============================================================

-- Vista: Productos con stock bajo (RF-11)
CREATE OR REPLACE VIEW vista_productos_stock_bajo AS
SELECT
    id_producto,
    codigo,
    nombre,
    categoria,
    precio,
    cantidad,
    descripcion,
    imagen_url,
    fecha_registro
FROM productos
WHERE cantidad <= 5
ORDER BY cantidad ASC, nombre;

-- Vista: Ventas del dia
CREATE OR REPLACE VIEW vista_ventas_diarias AS
SELECT
    v.id_venta,
    v.id_usuario,
    v.id_cliente,
    v.total,
    v.fecha_venta,
    c.nombre as nombre_cliente,
    u.username as nombre_usuario,
    COUNT(dv.id_detalle) as total_productos
FROM ventas v
JOIN clientes c ON v.id_cliente = c.id_cliente
JOIN usuarios u ON v.id_usuario = u.id_usuario
LEFT JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
WHERE DATE(v.fecha_venta) = CURRENT_DATE
GROUP BY v.id_venta, c.nombre, u.username
ORDER BY v.fecha_venta DESC;

-- Vista: Servicios pendientes
CREATE OR REPLACE VIEW vista_servicios_pendientes AS
SELECT
    s.id_servicio,
    s.consola,
    s.descripcion,
    s.estado,
    s.costo,
    s.fecha_ingreso,
    c.nombre as nombre_cliente,
    c.telefono as telefono_cliente,
    u.username as nombre_usuario,
    EXTRACT(DAY FROM (CURRENT_TIMESTAMP - s.fecha_ingreso)) as dias_pendientes
FROM servicios s
JOIN clientes c ON s.id_cliente = c.id_cliente
JOIN usuarios u ON s.id_usuario = u.id_usuario
WHERE s.estado = 'En reparacion'
ORDER BY s.fecha_ingreso ASC;

-- ============================================================
-- FUNCIONES Y TRIGGERS
-- ============================================================

-- Funcion: Actualizar fecha_entrega cuando servicio cambia a "Listo" o "Entregado"
CREATE OR REPLACE FUNCTION actualizar_fecha_entrega_servicio()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.estado IN ('Listo', 'Entregado') AND OLD.estado = 'En reparacion' THEN
        NEW.fecha_entrega = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar fecha_entrega automaticamente
CREATE TRIGGER trigger_actualizar_fecha_entrega
BEFORE UPDATE ON servicios
FOR EACH ROW
EXECUTE FUNCTION actualizar_fecha_entrega_servicio();

-- Funcion: Validar stock antes de venta
CREATE OR REPLACE FUNCTION validar_stock_venta()
RETURNS TRIGGER AS $$
DECLARE
    stock_actual INTEGER;
BEGIN
    SELECT cantidad INTO stock_actual
    FROM productos
    WHERE id_producto = NEW.id_producto;

    IF stock_actual < NEW.cantidad THEN
        RAISE EXCEPTION 'Stock insuficiente para el producto ID %. Disponible: %, Solicitado: %',
            NEW.id_producto, stock_actual, NEW.cantidad;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para validar stock antes de insertar detalle de venta
CREATE TRIGGER trigger_validar_stock
BEFORE INSERT ON detalle_ventas
FOR EACH ROW
EXECUTE FUNCTION validar_stock_venta();

-- ============================================================
-- DATOS INICIALES DE PRUEBA
-- ============================================================

-- Usuario administrador por defecto
-- Username: admin | Password: admin123
INSERT INTO usuarios (username, email, password) VALUES
('admin', 'admin@playzone.com', 'admin123');

-- Clientes de ejemplo
INSERT INTO clientes (nombre, documento, telefono, email) VALUES
('Juan Perez', '1234567890', '3001234567', 'juan@example.com'),
('Maria Lopez', '0987654321', '3009876543', 'maria@example.com'),
('Carlos Rodriguez', '1122334455', '3112233445', 'carlos@example.com');

-- Productos de ejemplo
INSERT INTO productos (codigo, nombre, categoria, precio, cantidad, descripcion, imagen_url) VALUES
('VJ-20250105-A1B2', 'FIFA 24', 'videojuego', 250000, 10, 'Videojuego FIFA 24 para PS5', 'https://example.com/fifa24.jpg'),
('VJ-20250105-C3D4', 'Call of Duty MW3', 'videojuego', 280000, 8, 'Call of Duty Modern Warfare 3', 'https://example.com/cod.jpg'),
('CS-20250105-E5F6', 'PlayStation 5', 'consola', 2500000, 3, 'Consola PlayStation 5 Standard', 'https://example.com/ps5.jpg'),
('CS-20250105-G7H8', 'Xbox Series S', 'consola', 1200000, 5, 'Consola Xbox Series S 512GB', 'https://example.com/xbox.jpg'),
('AC-20250105-I9J0', 'Control DualSense', 'accesorio', 320000, 15, 'Control inalambrico DualSense para PS5', 'https://example.com/dualsense.jpg'),
('AC-20250105-K1L2', 'Control Xbox Wireless', 'accesorio', 280000, 12, 'Control inalambrico para Xbox', 'https://example.com/xbox-controller.jpg');

-- ============================================================
-- CONSULTAS UTILES PARA DESARROLLO
-- ============================================================

-- Ver todos los productos con stock bajo
-- SELECT * FROM vista_productos_stock_bajo;

-- Ver ventas del dia
-- SELECT * FROM vista_ventas_diarias;

-- Ver servicios pendientes
-- SELECT * FROM vista_servicios_pendientes;

-- Reporte de ventas por categoria
-- SELECT
--     p.categoria,
--     COUNT(DISTINCT v.id_venta) as total_ventas,
--     SUM(dv.cantidad) as productos_vendidos,
--     SUM(dv.cantidad * dv.precio_unitario) as monto_total
-- FROM detalle_ventas dv
-- JOIN productos p ON dv.id_producto = p.id_producto
-- JOIN ventas v ON dv.id_venta = v.id_venta
-- GROUP BY p.categoria;

-- Productos mas vendidos
-- SELECT
--     p.id_producto,
--     p.nombre,
--     p.categoria,
--     SUM(dv.cantidad) as total_vendido
-- FROM detalle_ventas dv
-- JOIN productos p ON dv.id_producto = p.id_producto
-- GROUP BY p.id_producto, p.nombre, p.categoria
-- ORDER BY total_vendido DESC
-- LIMIT 10;

-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================

-- Mensaje de confirmacion
DO $$
BEGIN
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Schema creado exitosamente!';
    RAISE NOTICE 'Base de datos: PlayZone Inventory System';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Tablas creadas: 6';
    RAISE NOTICE '  - usuarios';
    RAISE NOTICE '  - clientes';
    RAISE NOTICE '  - productos';
    RAISE NOTICE '  - ventas';
    RAISE NOTICE '  - detalle_ventas';
    RAISE NOTICE '  - servicios';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Vistas creadas: 3';
    RAISE NOTICE 'Triggers creados: 2';
    RAISE NOTICE 'Usuario admin: admin / admin123';
    RAISE NOTICE '==============================================';
END $$;
