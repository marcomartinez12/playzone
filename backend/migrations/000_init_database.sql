-- ============================================
-- INICIALIZACIÓN COMPLETA BASE DE DATOS - PlayZone
-- Script para crear toda la base de datos desde cero
-- Sistema simplificado para UN SOLO ADMINISTRADOR
-- ============================================

-- LIMPIAR BASE DE DATOS (CUIDADO: ELIMINA TODO)
-- Descomentar solo si quieres empezar desde cero
-- DROP TABLE IF EXISTS detalle_ventas CASCADE;
-- DROP TABLE IF EXISTS ventas CASCADE;
-- DROP TABLE IF EXISTS servicios CASCADE;
-- DROP TABLE IF EXISTS productos CASCADE;
-- DROP TABLE IF EXISTS clientes CASCADE;
-- DROP TABLE IF EXISTS refresh_tokens CASCADE;
-- DROP TABLE IF EXISTS login_attempts CASCADE;
-- DROP TABLE IF EXISTS auditoria CASCADE;
-- DROP TABLE IF EXISTS usuarios CASCADE;

-- ============================================
-- 1. TABLA DE USUARIOS
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima_sesion TIMESTAMP,
    intentos_fallidos INTEGER DEFAULT 0,
    bloqueado_hasta TIMESTAMP,
    eliminado BOOLEAN DEFAULT FALSE,
    fecha_eliminacion TIMESTAMP
);

-- Usuario administrador por defecto (contraseña: admin123)
-- IMPORTANTE: Cambiar la contraseña en producción
INSERT INTO usuarios (username, email, password) VALUES
    ('admin', 'admin@playzone.com', 'admin123')
ON CONFLICT (username) DO NOTHING;

-- ============================================
-- 2. TABLA DE CLIENTES
-- ============================================
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    documento VARCHAR(50) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(255),
    direccion TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    eliminado BOOLEAN DEFAULT FALSE,
    fecha_eliminacion TIMESTAMP,
    eliminado_por INTEGER REFERENCES usuarios(id_usuario)
);

-- ============================================
-- 3. TABLA DE PRODUCTOS
-- ============================================
CREATE TABLE IF NOT EXISTS productos (
    id_producto SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    categoria VARCHAR(100) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 0,
    imagen_url TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    eliminado BOOLEAN DEFAULT FALSE,
    fecha_eliminacion TIMESTAMP,
    eliminado_por INTEGER REFERENCES usuarios(id_usuario)
);

-- Índice para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria);
CREATE INDEX IF NOT EXISTS idx_productos_codigo ON productos(codigo);

-- ============================================
-- 4. TABLA DE VENTAS
-- ============================================
CREATE TABLE IF NOT EXISTS ventas (
    id_venta SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente),
    total DECIMAL(10, 2) NOT NULL,
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 5. TABLA DE DETALLE DE VENTAS
-- ============================================
CREATE TABLE IF NOT EXISTS detalle_ventas (
    id_detalle SERIAL PRIMARY KEY,
    id_venta INTEGER NOT NULL REFERENCES ventas(id_venta) ON DELETE CASCADE,
    id_producto INTEGER NOT NULL REFERENCES productos(id_producto),
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL
);

-- ============================================
-- 6. TABLA DE SERVICIOS
-- ============================================
CREATE TABLE IF NOT EXISTS servicios (
    id_servicio SERIAL PRIMARY KEY,
    id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente),
    consola VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    costo DECIMAL(10, 2) NOT NULL,
    pagado BOOLEAN DEFAULT FALSE,
    estado VARCHAR(50) DEFAULT 'En Reparacion',
    fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega TIMESTAMP,
    eliminado BOOLEAN DEFAULT FALSE,
    fecha_eliminacion TIMESTAMP,
    eliminado_por INTEGER REFERENCES usuarios(id_usuario)
);

-- ============================================
-- 7. TABLA DE REFRESH TOKENS
-- ============================================
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id_refresh_token SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expira_en TIMESTAMP NOT NULL,
    revocado BOOLEAN DEFAULT FALSE,
    fecha_revocacion TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_uso TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_usuario ON refresh_tokens(id_usuario);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expira ON refresh_tokens(expira_en);

-- ============================================
-- 8. TABLA DE INTENTOS DE LOGIN
-- ============================================
CREATE TABLE IF NOT EXISTS login_attempts (
    id_intento SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    exitoso BOOLEAN DEFAULT FALSE,
    razon_fallo VARCHAR(255),
    user_agent TEXT,
    fecha_intento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_login_attempts_username ON login_attempts(username);
CREATE INDEX IF NOT EXISTS idx_login_attempts_ip ON login_attempts(ip_address);
CREATE INDEX IF NOT EXISTS idx_login_attempts_fecha ON login_attempts(fecha_intento);

-- ============================================
-- 9. TABLA DE AUDITORIA
-- ============================================
CREATE TABLE IF NOT EXISTS auditoria (
    id_auditoria SERIAL PRIMARY KEY,
    id_usuario INTEGER REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    username VARCHAR(100),
    accion VARCHAR(100) NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    entidad VARCHAR(50),
    id_entidad INTEGER,
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    fecha_accion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria(id_usuario);
CREATE INDEX IF NOT EXISTS idx_auditoria_modulo ON auditoria(modulo);
CREATE INDEX IF NOT EXISTS idx_auditoria_accion ON auditoria(accion);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria(fecha_accion);
CREATE INDEX IF NOT EXISTS idx_auditoria_entidad ON auditoria(entidad, id_entidad);

-- ============================================
-- 10. FUNCIONES AUXILIARES
-- ============================================

-- Función para limpiar tokens expirados
CREATE OR REPLACE FUNCTION limpiar_tokens_expirados()
RETURNS INTEGER AS $$
DECLARE
    tokens_eliminados INTEGER;
BEGIN
    DELETE FROM refresh_tokens
    WHERE expira_en < NOW() AND revocado = TRUE;

    GET DIAGNOSTICS tokens_eliminados = ROW_COUNT;
    RETURN tokens_eliminados;
END;
$$ LANGUAGE plpgsql;

-- Función para limpiar intentos de login antiguos
CREATE OR REPLACE FUNCTION limpiar_login_attempts()
RETURNS INTEGER AS $$
DECLARE
    intentos_eliminados INTEGER;
BEGIN
    DELETE FROM login_attempts
    WHERE fecha_intento < NOW() - INTERVAL '30 days';

    GET DIAGNOSTICS intentos_eliminados = ROW_COUNT;
    RETURN intentos_eliminados;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- COMENTARIOS FINALES
-- ============================================
COMMENT ON DATABASE postgres IS 'Base de datos del Sistema de Inventario PlayZone';
COMMENT ON TABLE usuarios IS 'Usuario administrador único del sistema';
COMMENT ON TABLE productos IS 'Inventario de productos (videojuegos, consolas, accesorios)';
COMMENT ON TABLE clientes IS 'Clientes del negocio';
COMMENT ON TABLE ventas IS 'Registro de ventas realizadas';
COMMENT ON TABLE detalle_ventas IS 'Detalle de productos vendidos en cada venta';
COMMENT ON TABLE servicios IS 'Servicios de reparación de consolas';
COMMENT ON TABLE refresh_tokens IS 'Tokens de refresco para sesiones persistentes';
COMMENT ON TABLE login_attempts IS 'Registro de intentos de login (rate limiting)';
COMMENT ON TABLE auditoria IS 'Registro de auditoría de todas las acciones del sistema';

-- ============================================
-- RESUMEN
-- ============================================
-- Base de datos creada exitosamente con:
-- ✅ 9 tablas principales
-- ✅ Usuario admin único (username: admin, password: admin123)
-- ✅ Sistema de seguridad: JWT + Refresh Tokens + Rate Limiting
-- ✅ Índices para optimización
-- ✅ Funciones de mantenimiento
-- ✅ Soft delete en tablas principales
-- ✅ Sistema de auditoría completo
--
-- SIGUIENTE PASO:
-- 1. Cambiar la contraseña del usuario admin
-- 2. Configurar las variables de entorno (.env)
-- 3. Iniciar el servidor backend
-- ============================================
