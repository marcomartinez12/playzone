"""
Modelo de Venta
RF-04: Registro Ventas
RF-05: Listado de Ventas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DetalleVentaBase(BaseModel):
    """Detalle de productos en una venta"""
    id_producto: int
    cantidad: int = Field(..., gt=0, description="Cantidad del producto")
    precio_unitario: float = Field(..., gt=0, description="Precio al momento de la venta")


class DetalleVentaCreate(DetalleVentaBase):
    """Modelo para crear detalle de venta"""
    pass


class DetalleVentaResponse(DetalleVentaBase):
    """Modelo de respuesta de detalle de venta"""
    id_detalle: int
    id_venta: int
    nombre_producto: Optional[str] = None
    subtotal: float = 0.0

    class Config:
        from_attributes = True


class VentaBase(BaseModel):
    """Modelo base de Venta"""
    id_cliente: int
    total: float = Field(..., ge=0, description="Total de la venta")


class VentaCreate(BaseModel):
    """RF-04: Modelo para crear una venta"""
    id_usuario: int
    id_cliente: int
    productos: List[DetalleVentaCreate] = Field(..., min_length=1, description="Productos de la venta")
    total: Optional[float] = None  # Se puede calcular automáticamente


class VentaResponse(VentaBase):
    """RF-05: Modelo de respuesta de venta"""
    id_venta: int
    id_usuario: int
    fecha_venta: datetime
    nombre_cliente: Optional[str] = None
    nombre_usuario: Optional[str] = None
    detalles: List[DetalleVentaResponse] = []

    class Config:
        from_attributes = True


class VentaFiltro(BaseModel):
    """RF-05: Filtros para listar ventas"""
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    id_cliente: Optional[int] = None
    id_usuario: Optional[int] = None


class VentasDiarias(BaseModel):
    """Reporte de ventas diarias"""
    fecha: datetime
    total_ventas: int
    monto_total: float
    productos_vendidos: int
