"""
Modelo de Producto
RF-02: Registro de productos
RF-03: Actualización de productos
RF-08: Tablero Inicial
RF-09: Filtrado de productos
RF-10: Búsqueda Específica de productos
RF-11: Alertas visuales por bajo stock
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class CategoriaProducto(str, Enum):
    """Categorías de productos según requisitos"""
    VIDEOJUEGO = "videojuego"
    CONSOLA = "consola"
    ACCESORIO = "accesorio"


class ProductoBase(BaseModel):
    """Modelo base de Producto"""
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre del producto")
    categoria: CategoriaProducto = Field(..., description="Categoría del producto")
    precio: float = Field(..., gt=0, description="Precio unitario del producto")
    cantidad: int = Field(..., ge=0, description="Cantidad disponible en inventario")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción del producto")
    imagen_url: Optional[str] = Field(None, description="URL de la imagen del producto")


class ProductoCreate(ProductoBase):
    """RF-02: Modelo para crear un producto"""
    pass


class ProductoUpdate(BaseModel):
    """RF-03: Modelo para actualizar un producto"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    categoria: Optional[CategoriaProducto] = None
    precio: Optional[float] = Field(None, gt=0)
    cantidad: Optional[int] = Field(None, ge=0)
    descripcion: Optional[str] = Field(None, max_length=500)
    imagen_url: Optional[str] = None


class ProductoResponse(ProductoBase):
    """Modelo de respuesta de producto"""
    id_producto: int
    codigo: str
    fecha_registro: Optional[datetime] = None
    stock_bajo: bool = False  # RF-11: Alerta de stock bajo

    class Config:
        from_attributes = True


class ProductoFiltro(BaseModel):
    """RF-09: Filtros para búsqueda de productos"""
    categoria: Optional[CategoriaProducto] = None
    precio_min: Optional[float] = Field(None, ge=0)
    precio_max: Optional[float] = Field(None, ge=0)
    stock_minimo: Optional[int] = Field(None, ge=0)
    busqueda: Optional[str] = None  # RF-10: Búsqueda específica


class StockBajo(BaseModel):
    """RF-11: Modelo para productos con stock bajo"""
    id_producto: int
    nombre: str
    cantidad_actual: int
    stock_minimo: int = 5
