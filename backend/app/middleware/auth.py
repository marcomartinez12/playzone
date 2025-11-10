"""
Middleware de autenticacion
RF-01: Validacion de tokens JWT para proteger endpoints
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.utils.security import decode_access_token
from app.config.database import get_db_cursor

# Sistema de seguridad Bearer Token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Obtiene el usuario actual desde el token JWT

    Args:
        credentials: Credenciales Bearer del header

    Returns:
        Datos del usuario autenticado

    Raises:
        HTTPException: Si el token es invalido o el usuario no existe
    """
    token = credentials.credentials

    # Decodificar token
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("sub")
    id_usuario: int = payload.get("id_usuario")

    if username is None or id_usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar que el usuario existe en la base de datos
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT id_usuario, username, email FROM usuarios WHERE id_usuario = %s",
            (id_usuario,)
        )
        user = cursor.fetchone()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return dict(user)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Obtiene el usuario actual si el token esta presente, sino retorna None
    Util para endpoints que pueden funcionar con o sin autenticacion

    Args:
        credentials: Credenciales Bearer del header (opcional)

    Returns:
        Datos del usuario autenticado o None
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
