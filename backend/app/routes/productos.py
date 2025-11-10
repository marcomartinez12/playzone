"""
Rutas de Productos
RF-02, RF-03, RF-08, RF-09, RF-10, RF-11
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.models.producto import ProductoCreate, ProductoUpdate, ProductoResponse
from app.controllers.producto_controller import ProductoController
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=dict, summary="Crear producto")
async def crear_producto(
    producto: ProductoCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    RF-02: Crear un nuevo producto en el inventario

    Requiere autenticacion
    """
    return ProductoController.crear_producto(producto)


@router.get("/", response_model=List[dict], summary="Listar productos")
async def obtener_productos(
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    busqueda: Optional[str] = Query(None, description="Buscar por nombre"),
    stock_bajo: bool = Query(False, description="Solo productos con stock bajo")
):
    """
    RF-08: Tablero Inicial - Listar productos
    RF-09: Filtrado de productos por categoria
    RF-10: Busqueda especifica de productos por nombre
    RF-11: Productos con stock bajo
    """
    return ProductoController.obtener_productos(
        categoria=categoria,
        busqueda=busqueda,
        stock_bajo=stock_bajo
    )


@router.get("/stock-bajo", response_model=List[dict], summary="Productos con stock bajo")
async def obtener_productos_stock_bajo(
    current_user: dict = Depends(get_current_user)
):
    """
    RF-11: Obtener productos con stock bajo para alertas

    Requiere autenticacion
    """
    return ProductoController.obtener_productos_stock_bajo()


@router.get("/{id_producto}", response_model=dict, summary="Obtener producto")
async def obtener_producto(id_producto: int):
    """
    Obtener un producto especifico por ID
    """
    return ProductoController.obtener_producto(id_producto)


@router.put("/{id_producto}", response_model=dict, summary="Actualizar producto")
async def actualizar_producto(
    id_producto: int,
    producto: ProductoUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    RF-03: Actualizar un producto existente

    Requiere autenticacion
    """
    return ProductoController.actualizar_producto(id_producto, producto)


@router.delete("/{id_producto}", response_model=dict, summary="Eliminar producto")
async def eliminar_producto(
    id_producto: int,
    current_user: dict = Depends(get_current_user)
):
    """
    RF-03: Eliminar un producto del inventario

    Requiere autenticacion
    """
    return ProductoController.eliminar_producto(id_producto)
