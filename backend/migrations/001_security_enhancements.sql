-- ============================================
-- MIGRACION DE SEGURIDAD - PlayZone
-- Implementa: Roles, Permisos, Audit Logs, Rate Limiting, Refresh Tokens, Soft Delete
-- ============================================

-- 1. TABLA DE ROLES
CREATE TABLE IF NOT EXISTS roles (
    id_rol SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar roles por defecto
INSERT INTO roles (nombre, descripcion) VALUES
    ('ADMIN', 'Administrador con acceso total al sistema'),
    ('VENDEDOR', 'Usuario que puede registrar ventas y ver inventario'),
    ('CAJERO', 'Usuario que solo puede registrar ventas')
ON CONFLICT (nombre) DO NOTHING;

-- 2. TABLA DE PERMISOS
CREATE TABLE IF NOT EXISTS permisos (
    id_permiso SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    modulo VARCHAR(50) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar permisos por defecto
INSERT INTO permisos (nombre, descripcion, modulo) VALUES
    -- Permisos de Usuarios
    ('usuarios.crear', 'Crear nuevos usuarios', 'usuarios'),
    ('usuarios.editar', 'Editar usuarios existentes', 'usuarios'),
    ('usuarios.eliminar', 'Eliminar usuarios', 'usuarios'),
    ('usuarios.ver', 'Ver lista de usuarios', 'usuarios'),

    -- Permisos de Productos
    ('productos.crear', 'Crear nuevos productos', 'productos'),
    ('productos.editar', 'Editar productos existentes', 'productos'),
    ('productos.eliminar', 'Eliminar productos', 'productos'),
    ('productos.ver', 'Ver inventario de productos', 'productos'),

    -- Permisos de Ventas
    ('ventas.crear', 'Registrar nuevas ventas', 'ventas'),
    ('ventas.ver', 'Ver historial de ventas', 'ventas'),
    ('ventas.reportes', 'Generar reportes de ventas', 'ventas'),

    -- Permisos de Clientes
    ('clientes.crear', 'Crear nuevos clientes', 'clientes'),
    ('clientes.editar', 'Editar clientes existentes', 'clientes'),
    ('clientes.eliminar', 'Eliminar clientes', 'clientes'),
    ('clientes.ver', 'Ver lista de clientes', 'clientes'),

    -- Permisos de Servicios
    ('servicios.crear', 'Crear nuevos servicios', 'servicios'),
    ('servicios.editar', 'Editar servicios existentes', 'servicios'),
    ('servicios.eliminar', 'Eliminar servicios', 'servicios'),
    ('servicios.ver', 'Ver lista de servicios', 'servicios'),

    -- Permisos de Auditoría
    ('auditoria.ver', 'Ver logs de auditoría', 'auditoria')
ON CONFLICT (nombre) DO NOTHING;

-- 3. TABLA DE RELACION ROL-PERMISO
CREATE TABLE IF NOT EXISTS rol_permisos (
    id_rol_permiso SERIAL PRIMARY KEY,
    id_rol INTEGER NOT NULL REFERENCES roles(id_rol) ON DELETE CASCADE,
    id_permiso INTEGER NOT NULL REFERENCES permisos(id_permiso) ON DELETE CASCADE,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id_rol, id_permiso)
);

-- Asignar permisos a roles
-- ADMIN: Todos los permisos
INSERT INTO rol_permisos (id_rol, id_permiso)
SELECT r.id_rol, p.id_permiso
FROM roles r
CROSS JOIN permisos p
WHERE r.nombre = 'ADMIN'
ON CONFLICT DO NOTHING;

-- VENDEDOR: Ventas, productos, clientes, servicios (sin eliminar)
INSERT INTO rol_permisos (id_rol, id_permiso)
SELECT r.id_rol, p.id_permiso
FROM roles r
CROSS JOIN permisos p
WHERE r.nombre = 'VENDEDOR'
AND p.nombre IN (
    'productos.ver', 'productos.crear', 'productos.editar',
    'ventas.crear', 'ventas.ver', 'ventas.reportes',
    'clientes.crear', 'clientes.editar', 'clientes.ver',
    'servicios.crear', 'servicios.editar', 'servicios.ver'
)
ON CONFLICT DO NOTHING;

-- CAJERO: Solo ventas y ver productos/clientes
INSERT INTO rol_permisos (id_rol, id_permiso)
SELECT r.id_rol, p.id_permiso
FROM roles r
CROSS JOIN permisos p
WHERE r.nombre = 'CAJERO'
AND p.nombre IN (
    'productos.ver',
    'ventas.crear', 'ventas.ver',
    'clientes.ver',
    'servicios.ver'
)
ON CONFLICT DO NOTHING;

-- 4. AGREGAR COLUMNAS A USUARIOS
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS id_rol INTEGER REFERENCES roles(id_rol) DEFAULT 1;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS fecha_ultima_sesion TIMESTAMP;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS intentos_fallidos INTEGER DEFAULT 0;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS bloqueado_hasta TIMESTAMP;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS eliminado BOOLEAN DEFAULT FALSE;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS fecha_eliminacion TIMESTAMP;

-- Actualizar usuarios existentes como ADMIN
UPDATE usuarios SET id_rol = (SELECT id_rol FROM roles WHERE nombre = 'ADMIN' LIMIT 1) WHERE id_rol IS NULL;

-- 5. TABLA DE REFRESH TOKENS
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

-- 6. TABLA DE INTENTOS DE LOGIN
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

-- 7. TABLA DE AUDITORIA
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

-- 8. AGREGAR SOFT DELETE A OTRAS TABLAS
ALTER TABLE productos ADD COLUMN IF NOT EXISTS eliminado BOOLEAN DEFAULT FALSE;
ALTER TABLE productos ADD COLUMN IF NOT EXISTS fecha_eliminacion TIMESTAMP;
ALTER TABLE productos ADD COLUMN IF NOT EXISTS eliminado_por INTEGER REFERENCES usuarios(id_usuario);

ALTER TABLE clientes ADD COLUMN IF NOT EXISTS eliminado BOOLEAN DEFAULT FALSE;
ALTER TABLE clientes ADD COLUMN IF NOT EXISTS fecha_eliminacion TIMESTAMP;
ALTER TABLE clientes ADD COLUMN IF NOT EXISTS eliminado_por INTEGER REFERENCES usuarios(id_usuario);

ALTER TABLE servicios ADD COLUMN IF NOT EXISTS eliminado BOOLEAN DEFAULT FALSE;
ALTER TABLE servicios ADD COLUMN IF NOT EXISTS fecha_eliminacion TIMESTAMP;
ALTER TABLE servicios ADD COLUMN IF NOT EXISTS eliminado_por INTEGER REFERENCES usuarios(id_usuario);

-- 9. FUNCIÓN PARA LIMPIAR TOKENS EXPIRADOS (ejecutar periódicamente)
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

-- 10. FUNCIÓN PARA LIMPIAR INTENTOS DE LOGIN ANTIGUOS (más de 30 días)
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

-- Comentarios finales
COMMENT ON TABLE roles IS 'Roles de usuario del sistema';
COMMENT ON TABLE permisos IS 'Permisos granulares del sistema';
COMMENT ON TABLE rol_permisos IS 'Relación muchos a muchos entre roles y permisos';
COMMENT ON TABLE refresh_tokens IS 'Tokens de refresco para mantener sesiones activas';
COMMENT ON TABLE login_attempts IS 'Registro de intentos de inicio de sesión (rate limiting)';
COMMENT ON TABLE auditoria IS 'Registro de auditoría de todas las acciones del sistema';

-- Fin de migración
