"""
Utilidades para respuestas estandarizadas de la API
RF-15: Confirmacion de Registro
"""
from typing import Any, Optional
from fastapi.responses import JSONResponse


def success_response(
    message: str,
    data: Any = None,
    status_code: int = 200
) -> JSONResponse:
    """
    Respuesta exitosa estandarizada

    Args:
        message: Mensaje de exito
        data: Datos a retornar (opcional)
        status_code: Codigo HTTP

    Returns:
        JSONResponse con formato estandarizado
    """
    response = {
        "success": True,
        "message": message,
    }

    if data is not None:
        response["data"] = data

    return JSONResponse(content=response, status_code=status_code)


def error_response(
    message: str,
    error: Optional[str] = None,
    status_code: int = 400
) -> JSONResponse:
    """
    Respuesta de error estandarizada

    Args:
        message: Mensaje de error
        error: Detalle del error (opcional)
        status_code: Codigo HTTP

    Returns:
        JSONResponse con formato estandarizado
    """
    response = {
        "success": False,
        "message": message,
    }

    if error:
        response["error"] = error

    return JSONResponse(content=response, status_code=status_code)
