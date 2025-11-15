-- ============================================
-- AGREGAR TABLAS DE SEGURIDAD - PlayZone
-- Script para agregar solo las funcionalidades de seguridad
-- NO elimina ni modifica datos existentes
-- ============================================

-- ============================================
-- 1. AGREGAR COLUMNAS DE SEGURIDAD A USUARIOS
-- ============================================
ALTER TABLE usuarios
ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS fecha_ultima_sesion TIMESTAMP,
ADD COLUMN IF NOT EXISTS intentos_fallidos INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS bloqueado_hasta TIMESTAMP,
ADD COLUMN IF NOT EXISTS eliminado BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS fecha_eliminacion TIMESTAMP;

-- ============================================
-- 2. TABLA DE REFRESH TOKENS
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
-- 3. TABLA DE INTENTOS DE LOGIN
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
-- 4. TABLA DE AUDITORIA
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
-- 5. AGREGAR SOFT DELETE A TABLAS EXISTENTES
-- ============================================

-- Clientes
ALTER TABLE clientes
ADD COLUMN IF NOT EXISTS eliminado BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS fecha_eliminacion TIMESTAMP,
ADD COLUMN IF NOT EXISTS eliminado_por INTEGER REFERENCES usuarios(id_usuario);

-- Productos
ALTER TABLE productos
ADD COLUMN IF NOT EXISTS eliminado BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS fecha_eliminacion TIMESTAMP,
ADD COLUMN IF NOT EXISTS eliminado_por INTEGER REFERENCES usuarios(id_usuario);

-- Servicios
ALTER TABLE servicios
ADD COLUMN IF NOT EXISTS eliminado BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS fecha_eliminacion TIMESTAMP,
ADD COLUMN IF NOT EXISTS eliminado_por INTEGER REFERENCES usuarios(id_usuario);

-- ============================================
-- 6. FUNCIONES DE MANTENIMIENTO
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
-- RESUMEN
-- ============================================
-- ✅ Agregadas columnas de seguridad a usuarios existentes
-- ✅ Creadas tablas: refresh_tokens, login_attempts, auditoria
-- ✅ Agregado soft delete a clientes, productos, servicios
-- ✅ Creadas funciones de mantenimiento
-- ✅ NO se eliminó ni modificó ningún dato existente
--
-- LISTO PARA USAR:
-- - Login con rate limiting
-- - Refresh tokens para sesiones persistentes
-- - Auditoría completa de acciones
-- - Soft delete (borrado lógico)
-- ============================================
