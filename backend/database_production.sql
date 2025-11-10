-- ============================================================
-- PLAYZONE INVENTORY SYSTEM - PRODUCTION SCHEMA
-- Solo estructura de tablas (sin datos de ejemplo)
-- PostgreSQL / Supabase
-- ============================================================

-- ============================================================
-- TABLA: USUARIOS
-- ============================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);

-- ============================================================
-- TABLA: CLIENTES
-- ============================================================
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    documento VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(15),
    email VARCHAR(100),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_clientes_documento ON clientes(documento);
CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes(nombre);

-- ============================================================
-- TABLA: PRODUCTOS
-- ============================================================
CREATE TABLE IF NOT EXISTS productos (
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

CREATE INDEX IF NOT EXISTS idx_productos_codigo ON productos(codigo);
CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria);
CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos(nombre);
CREATE INDEX IF NOT EXISTS idx_productos_cantidad ON productos(cantidad);

-- ============================================================
-- TABLA: VENTAS
-- ============================================================
CREATE TABLE IF NOT EXISTS ventas (
    id_venta SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente),
    total DECIMAL(10, 2) NOT NULL CHECK (total >= 0),
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha_venta DESC);
CREATE INDEX IF NOT EXISTS idx_ventas_cliente ON ventas(id_cliente);
CREATE INDEX IF NOT EXISTS idx_ventas_usuario ON ventas(id_usuario);

-- ============================================================
-- TABLA: DETALLE_VENTAS
-- ============================================================
CREATE TABLE IF NOT EXISTS detalle_ventas (
    id_detalle SERIAL PRIMARY KEY,
    id_venta INTEGER NOT NULL REFERENCES ventas(id_venta) ON DELETE CASCADE,
    id_producto INTEGER NOT NULL REFERENCES productos(id_producto),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10, 2) NOT NULL CHECK (precio_unitario > 0)
);

CREATE INDEX IF NOT EXISTS idx_detalle_ventas_venta ON detalle_ventas(id_venta);
CREATE INDEX IF NOT EXISTS idx_detalle_ventas_producto ON detalle_ventas(id_producto);

-- ============================================================
-- TABLA: SERVICIOS
-- ============================================================
CREATE TABLE IF NOT EXISTS servicios (
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

CREATE INDEX IF NOT EXISTS idx_servicios_estado ON servicios(estado);
CREATE INDEX IF NOT EXISTS idx_servicios_cliente ON servicios(id_cliente);
CREATE INDEX IF NOT EXISTS idx_servicios_consola ON servicios(consola);
CREATE INDEX IF NOT EXISTS idx_servicios_fecha_ingreso ON servicios(fecha_ingreso DESC);

-- ============================================================
-- VISTAS
-- ============================================================

CREATE OR REPLACE VIEW vista_productos_stock_bajo AS
SELECT
    id_producto, codigo, nombre, categoria, precio, cantidad,
    descripcion, imagen_url, fecha_registro
FROM productos
WHERE cantidad <= 5
ORDER BY cantidad ASC, nombre;

CREATE OR REPLACE VIEW vista_ventas_diarias AS
SELECT
    v.id_venta, v.id_usuario, v.id_cliente, v.total, v.fecha_venta,
    c.nombre as nombre_cliente, u.username as nombre_usuario,
    COUNT(dv.id_detalle) as total_productos
FROM ventas v
JOIN clientes c ON v.id_cliente = c.id_cliente
JOIN usuarios u ON v.id_usuario = u.id_usuario
LEFT JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
WHERE DATE(v.fecha_venta) = CURRENT_DATE
GROUP BY v.id_venta, c.nombre, u.username
ORDER BY v.fecha_venta DESC;

CREATE OR REPLACE VIEW vista_servicios_pendientes AS
SELECT
    s.id_servicio, s.consola, s.descripcion, s.estado, s.costo, s.fecha_ingreso,
    c.nombre as nombre_cliente, c.telefono as telefono_cliente,
    u.username as nombre_usuario,
    EXTRACT(DAY FROM (CURRENT_TIMESTAMP - s.fecha_ingreso)) as dias_pendientes
FROM servicios s
JOIN clientes c ON s.id_cliente = c.id_cliente
JOIN usuarios u ON s.id_usuario = u.id_usuario
WHERE s.estado = 'En reparacion'
ORDER BY s.fecha_ingreso ASC;

-- ============================================================
-- TRIGGERS
-- ============================================================

CREATE OR REPLACE FUNCTION actualizar_fecha_entrega_servicio()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.estado IN ('Listo', 'Entregado') AND OLD.estado = 'En reparacion' THEN
        NEW.fecha_entrega = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_actualizar_fecha_entrega ON servicios;
CREATE TRIGGER trigger_actualizar_fecha_entrega
BEFORE UPDATE ON servicios
FOR EACH ROW
EXECUTE FUNCTION actualizar_fecha_entrega_servicio();

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

DROP TRIGGER IF EXISTS trigger_validar_stock ON detalle_ventas;
CREATE TRIGGER trigger_validar_stock
BEFORE INSERT ON detalle_ventas
FOR EACH ROW
EXECUTE FUNCTION validar_stock_venta();
