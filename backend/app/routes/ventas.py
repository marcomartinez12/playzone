"""
Rutas de Ventas
RF-04: Registro Ventas
RF-05: Listado de Ventas
"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime, date
from app.models.venta import VentaCreate, VentaResponse
from app.controllers.venta_controller import VentaController
from app.middleware.auth import get_current_user
from app.utils.pdf_generator import PDFGenerator

router = APIRouter()


@router.post("/", response_model=dict, summary="Crear venta")
async def crear_venta(
    venta: VentaCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    RF-04: Registrar una nueva venta

    Crea la venta, actualiza el inventario y genera la factura

    Requiere autenticacion
    """
    return VentaController.crear_venta(venta)


@router.get("/", response_model=List[dict], summary="Listar ventas")
async def obtener_ventas(
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha inicial"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha final"),
    id_cliente: Optional[int] = Query(None, description="Filtrar por cliente"),
    current_user: dict = Depends(get_current_user)
):
    """
    RF-05: Listar ventas con filtros opcionales

    Requiere autenticacion
    """
    return VentaController.obtener_ventas(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        id_cliente=id_cliente
    )


@router.get("/diarias", response_model=dict, summary="Reporte de ventas diarias")
async def obtener_ventas_diarias(
    fecha: Optional[date] = Query(None, description="Fecha (por defecto hoy)"),
    current_user: dict = Depends(get_current_user)
):
    """
    RF-05: Obtener reporte de ventas del dia

    Requiere autenticacion
    """
    return VentaController.obtener_ventas_diarias(fecha)


@router.get("/{id_venta}", response_model=dict, summary="Obtener venta")
async def obtener_venta(
    id_venta: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener una venta especifica con sus detalles

    Requiere autenticacion
    """
    return VentaController.obtener_venta(id_venta)


@router.get("/reporte/pdf", summary="Descargar reporte de ventas en PDF")
async def descargar_reporte_pdf(
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha inicial"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha final"),
    id_cliente: Optional[int] = Query(None, description="Filtrar por cliente"),
    current_user: dict = Depends(get_current_user)
):
    """
    Genera y descarga un reporte profesional de ventas en formato PDF
    con branding de PlayZone, fecha automática y diseño profesional.

    Requiere autenticacion
    """
    # Obtener datos de ventas
    ventas = VentaController.obtener_ventas(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        id_cliente=id_cliente
    )

    # Generar PDF
    pdf_buffer = PDFGenerator.generar_reporte_ventas(ventas)

    # Nombre del archivo con fecha actual
    fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"PlayZone_Reporte_Ventas_{fecha_actual}.pdf"

    # Retornar como descarga
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
