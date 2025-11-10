"""
Modelo de Cliente
RF-07: Datos Básicos Clientes
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class ClienteBase(BaseModel):
    """Modelo base de Cliente"""
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre completo del cliente")
    documento: str = Field(..., min_length=5, max_length=20, description="Documento de identidad")
    telefono: str = Field(..., min_length=7, max_length=15, description="Número telefónico (obligatorio)")
    email: Optional[EmailStr] = Field(None, description="Correo electrónico (opcional)")


class ClienteCreate(ClienteBase):
    """RF-07: Modelo para crear un cliente"""
    pass


class ClienteUpdate(BaseModel):
    """Modelo para actualizar un cliente"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    documento: Optional[str] = Field(None, min_length=5, max_length=20)
    telefono: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None


class ClienteResponse(ClienteBase):
    """Modelo de respuesta de cliente"""
    id_cliente: int
    fecha_registro: Optional[datetime] = None
    total_compras: int = 0
    total_servicios: int = 0

    class Config:
        from_attributes = True
