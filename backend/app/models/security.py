"""
Modelos de Seguridad
Roles, Permisos, Auditoría, Refresh Tokens
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================
# ENUMS
# ============================================

class RolEnum(str, Enum):
    """Roles disponibles en el sistema"""
    ADMIN = "ADMIN"
    VENDEDOR = "VENDEDOR"
    CAJERO = "CAJERO"


class ModuloEnum(str, Enum):
    """Módulos del sistema"""
    USUARIOS = "usuarios"
    PRODUCTOS = "productos"
    VENTAS = "ventas"
    CLIENTES = "clientes"
    SERVICIOS = "servicios"
    AUDITORIA = "auditoria"


# ============================================
# ROLES Y PERMISOS
# ============================================

class RolBase(BaseModel):
    """Modelo base de Rol"""
    nombre: str
    descripcion: Optional[str] = None


class RolResponse(RolBase):
    """Respuesta de Rol"""
    id_rol: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class PermisoBase(BaseModel):
    """Modelo base de Permiso"""
    nombre: str
    descripcion: Optional[str] = None
    modulo: str


class PermisoResponse(PermisoBase):
    """Respuesta de Permiso"""
    id_permiso: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class RolConPermisos(RolResponse):
    """Rol con sus permisos asignados"""
    permisos: List[PermisoResponse] = []


# ============================================
# REFRESH TOKENS
# ============================================

class RefreshTokenCreate(BaseModel):
    """Crear refresh token"""
    id_usuario: int
    token: str
    token_hash: str
    expira_en: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class RefreshTokenResponse(BaseModel):
    """Respuesta de refresh token"""
    id_refresh_token: int
    id_usuario: int
    token: str
    expira_en: datetime
    revocado: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class TokenPair(BaseModel):
    """Par de tokens (access + refresh)"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos


class RefreshTokenRequest(BaseModel):
    """Request para refrescar token"""
    refresh_token: str


# ============================================
# AUDITORÍA
# ============================================

class AuditoriaCreate(BaseModel):
    """Crear registro de auditoría"""
    id_usuario: Optional[int] = None
    username: Optional[str] = None
    accion: str
    modulo: str
    entidad: Optional[str] = None
    id_entidad: Optional[int] = None
    datos_anteriores: Optional[dict] = None
    datos_nuevos: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditoriaResponse(BaseModel):
    """Respuesta de auditoría"""
    id_auditoria: int
    id_usuario: Optional[int]
    username: Optional[str]
    accion: str
    modulo: str
    entidad: Optional[str]
    id_entidad: Optional[int]
    datos_anteriores: Optional[dict]
    datos_nuevos: Optional[dict]
    ip_address: Optional[str]
    fecha_accion: datetime

    class Config:
        from_attributes = True


# ============================================
# LOGIN ATTEMPTS (Rate Limiting)
# ============================================

class LoginAttemptCreate(BaseModel):
    """Crear intento de login"""
    username: str
    ip_address: str
    exitoso: bool = False
    razon_fallo: Optional[str] = None
    user_agent: Optional[str] = None


class LoginAttemptResponse(BaseModel):
    """Respuesta de intento de login"""
    id_intento: int
    username: str
    ip_address: str
    exitoso: bool
    razon_fallo: Optional[str]
    fecha_intento: datetime

    class Config:
        from_attributes = True


# ============================================
# USUARIO EXTENDIDO CON SEGURIDAD
# ============================================

class UsuarioConRol(BaseModel):
    """Usuario con información de rol"""
    id_usuario: int
    username: str
    email: str
    id_rol: int
    nombre_rol: str
    activo: bool
    fecha_registro: datetime
    fecha_ultima_sesion: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsuarioConPermisos(UsuarioConRol):
    """Usuario con rol y permisos completos"""
    permisos: List[str] = []  # Lista de nombres de permisos


# ============================================
# VALIDACIÓN DE PERMISOS
# ============================================

class PermisoCheck(BaseModel):
    """Verificar si un usuario tiene un permiso"""
    id_usuario: int
    permiso: str
