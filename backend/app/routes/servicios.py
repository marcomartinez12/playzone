"""
Rutas de Servicios de Reparacion
RF-06, RF-13, RF-14
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.models.servicio import ServicioCreate, ServicioUpdate, ServicioResponse, EstadoServicio
from app.controllers.servicio_controller import ServicioController
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=dict, summary="Crear servicio de reparacion")
async def crear_servicio(
    servicio: ServicioCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    RF-06: Registrar un nuevo servicio de reparacion

    Requiere autenticacion
    """
    return ServicioController.crear_servicio(servicio)


@router.get("/", response_model=List[dict], summary="Listar servicios")
async def obtener_servicios(
    estado: Optional[EstadoServicio] = Query(None, description="Filtrar por estado"),
    id_cliente: Optional[int] = Query(None, description="Filtrar por cliente"),
    consola: Optional[str] = Query(None, description="Buscar por tipo de consola"),
    current_user: dict = Depends(get_current_user)
):
    """
    RF-14: Listar servicios con filtros opcionales

    Requiere autenticacion
    """
    return ServicioController.obtener_servicios(
        estado=estado,
        id_cliente=id_cliente,
        consola=consola
    )


@router.get("/pendientes", response_model=List[dict], summary="Servicios pendientes")
async def obtener_servicios_pendientes(
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener servicios en reparacion (para alertas)

    Requiere autenticacion
    """
    return ServicioController.obtener_servicios_pendientes()


@router.get("/buscar", response_model=List[dict], summary="Buscar servicios")
async def buscar_servicios(
    termino: str = Query(..., description="Buscar por cliente o consola"),
    current_user: dict = Depends(get_current_user)
):
    """
    RF-14: Buscar servicios por nombre de cliente o tipo de consola

    Requiere autenticacion
    """
    return ServicioController.buscar_por_cliente_o_consola(termino)


@router.get("/{id_servicio}", response_model=dict, summary="Obtener servicio")
async def obtener_servicio(
    id_servicio: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener un servicio especifico por ID

    Requiere autenticacion
    """
    return ServicioController.obtener_servicio(id_servicio)


@router.put("/{id_servicio}", response_model=dict, summary="Actualizar servicio")
async def actualizar_servicio(
    id_servicio: int,
    servicio: ServicioUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    RF-13: Actualizar un servicio (marcar como listo, cambiar estado, etc)

    Requiere autenticacion
    """
    return ServicioController.actualizar_servicio(id_servicio, servicio)


@router.delete("/{id_servicio}", response_model=dict, summary="Eliminar servicio")
async def eliminar_servicio(
    id_servicio: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Eliminar un servicio

    Requiere autenticacion
    """
    return ServicioController.eliminar_servicio(id_servicio)
