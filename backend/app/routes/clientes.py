"""
Rutas de Clientes
RF-07: Datos Basicos Clientes
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.models.cliente import ClienteCreate, ClienteUpdate, ClienteResponse
from app.controllers.cliente_controller import ClienteController
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=dict, summary="Crear cliente")
async def crear_cliente(cliente: ClienteCreate):
    """
    RF-07: Crear o buscar un cliente

    Si el cliente ya existe (por documento), retorna el existente
    """
    return ClienteController.crear_cliente(cliente)


@router.get("/", response_model=List[dict], summary="Listar clientes")
async def obtener_clientes(
    busqueda: Optional[str] = Query(None, description="Buscar por nombre o documento"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener lista de clientes con busqueda opcional

    Requiere autenticacion
    """
    return ClienteController.obtener_clientes(busqueda=busqueda)


@router.get("/buscar/{documento}", response_model=dict, summary="Buscar cliente por documento")
async def buscar_cliente_por_documento(
    documento: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Buscar un cliente por su número de documento

    Requiere autenticacion
    """
    return ClienteController.buscar_por_documento(documento)


@router.get("/{id_cliente}", response_model=dict, summary="Obtener cliente")
async def obtener_cliente(
    id_cliente: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener un cliente especifico por ID

    Requiere autenticacion
    """
    return ClienteController.obtener_cliente(id_cliente)


@router.put("/{id_cliente}", response_model=dict, summary="Actualizar cliente")
async def actualizar_cliente(
    id_cliente: int,
    cliente: ClienteUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualizar datos de un cliente

    Requiere autenticacion
    """
    return ClienteController.actualizar_cliente(id_cliente, cliente)


@router.delete("/{id_cliente}", response_model=dict, summary="Eliminar cliente")
async def eliminar_cliente(
    id_cliente: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Eliminar un cliente

    Requiere autenticacion
    """
    return ClienteController.eliminar_cliente(id_cliente)
