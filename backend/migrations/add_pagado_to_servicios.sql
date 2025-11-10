-- Migración: Agregar campo 'pagado' a tabla servicios
-- Fecha: 2025-11-10
-- Descripción: Agrega un campo booleano para rastrear si un servicio ha sido pagado

-- Agregar columna pagado (por defecto FALSE)
ALTER TABLE servicios
ADD COLUMN IF NOT EXISTS pagado BOOLEAN DEFAULT FALSE NOT NULL;

-- Comentario en la columna
COMMENT ON COLUMN servicios.pagado IS 'Indica si el servicio ha sido pagado por el cliente';
