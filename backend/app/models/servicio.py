"""
Modelo de Servicio de Reparación
RF-06: Registrar Servicios de Reparación
RF-13: Marcar reparación como lista para entrega
RF-14: Búsqueda de reparaciones por cliente o consola
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class EstadoServicio(str, Enum):
    """Estados posibles de un servicio de reparación"""
    EN_REPARACION = "En reparacion"
    LISTO = "Listo"
    ENTREGADO = "Entregado"


class ServicioBase(BaseModel):
    """Modelo base de Servicio"""
    id_cliente: int
    consola: str = Field(..., min_length=1, max_length=100, description="Tipo/modelo de consola")
    descripcion: str = Field(..., min_length=1, max_length=500, description="Descripción de la falla")
    costo: Optional[float] = Field(None, ge=0, description="Costo del servicio")
    pagado: bool = Field(False, description="Indica si el servicio ha sido pagado")


class ServicioCreate(ServicioBase):
    """RF-06: Modelo para crear un servicio de reparación"""
    id_usuario: int


class ServicioUpdate(BaseModel):
    """RF-13: Modelo para actualizar un servicio"""
    consola: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, min_length=1, max_length=500)
    estado: Optional[EstadoServicio] = None
    costo: Optional[float] = Field(None, ge=0)
    pagado: Optional[bool] = None


class ServicioResponse(ServicioBase):
    """Modelo de respuesta de servicio"""
    id_servicio: int
    id_usuario: int
    estado: EstadoServicio
    fecha_ingreso: datetime
    fecha_entrega: Optional[datetime] = None
    nombre_cliente: Optional[str] = None
    telefono_cliente: Optional[str] = None
    nombre_usuario: Optional[str] = None

    class Config:
        from_attributes = True


class ServicioFiltro(BaseModel):
    """RF-14: Filtros para búsqueda de servicios"""
    estado: Optional[EstadoServicio] = None
    id_cliente: Optional[int] = None
    consola: Optional[str] = None  # Búsqueda por tipo de consola
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None


class ServicioPendiente(BaseModel):
    """Modelo para servicios pendientes - alertas"""
    id_servicio: int
    consola: str
    nombre_cliente: str
    dias_pendientes: int
    estado: EstadoServicio
