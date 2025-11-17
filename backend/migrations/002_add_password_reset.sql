-- Migration: Add password reset functionality
-- Description: Adds columns for password reset token and expiration
-- Date: 2025-01-16

-- Add password reset columns to usuarios table
ALTER TABLE usuarios
ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255),
ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP;

-- Create index for faster token lookups
CREATE INDEX IF NOT EXISTS idx_usuarios_reset_token ON usuarios(reset_token);

-- Add comment to columns
COMMENT ON COLUMN usuarios.reset_token IS 'Hash del token de recuperación de contraseña';
COMMENT ON COLUMN usuarios.reset_token_expires IS 'Fecha de expiración del token de recuperación';
