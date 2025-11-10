"""
Modelo de Usuario
RF-01: Iniciar Sesión
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UsuarioBase(BaseModel):
    """Modelo base de Usuario"""
    username: str
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    """Modelo para crear un usuario"""
    password: str


class UsuarioLogin(BaseModel):
    """RF-01: Modelo para inicio de sesión"""
    username: str
    password: str


class UsuarioResponse(UsuarioBase):
    """Modelo de respuesta de usuario (sin contraseña)"""
    id_usuario: int
    fecha_registro: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsuarioInDB(UsuarioResponse):
    """Modelo de usuario en la base de datos"""
    password_hash: str


class Token(BaseModel):
    """Modelo de token de autenticación"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Datos contenidos en el token"""
    username: Optional[str] = None
    id_usuario: Optional[int] = None
