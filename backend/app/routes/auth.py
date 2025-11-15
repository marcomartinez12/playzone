"""
Rutas de Autenticacion
RF-01: Iniciar Sesion
Incluye: Rate Limiting, Refresh Tokens, Logout, Auditoría
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from app.models.usuario import UsuarioLogin, UsuarioCreate, Token
from app.models.security import RefreshTokenRequest, TokenPair
from app.controllers.auth_controller import AuthController
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("/login", response_model=dict, summary="Iniciar sesion con seguridad")
async def login(usuario: UsuarioLogin, request: Request):
    """
    RF-01: Iniciar sesion con características de seguridad

    Características:
    - Rate limiting (máximo 5 intentos por usuario, 10 por IP)
    - Contraseñas hasheadas con bcrypt
    - Refresh tokens para sesiones persistentes
    - Auditoría de intentos de login
    - Bloqueo temporal después de intentos fallidos

    Args:
        usuario: Credenciales (username, password)
        request: Request object para obtener IP y User-Agent

    Returns:
        Par de tokens (access + refresh) y datos del usuario
    """
    # Obtener IP y User-Agent del cliente
    ip_address = request.client.host if request.client else "0.0.0.0"
    user_agent = request.headers.get("user-agent")

    return AuthController.login(usuario, ip_address, user_agent)


@router.post("/register", response_model=dict, summary="Registrar usuario")
async def register(usuario: UsuarioCreate, request: Request):
    """
    Registrar un nuevo usuario administrador con contraseña hasheada

    Args:
        usuario: Datos del usuario (username, email, password)
        request: Request object para auditoría

    Returns:
        Usuario creado
    """
    ip_address = request.client.host if request.client else None
    return AuthController.register(usuario, ip_address)


@router.post("/refresh", response_model=dict, summary="Refrescar access token")
async def refresh_token(token_request: RefreshTokenRequest, request: Request):
    """
    Refresca el access token usando un refresh token válido

    Args:
        token_request: Objeto con el refresh token
        request: Request object

    Returns:
        Nuevo access token
    """
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return AuthController.refresh_access_token(
        token_request.refresh_token,
        ip_address,
        user_agent
    )


@router.post("/logout", response_model=dict, summary="Cerrar sesion")
async def logout(
    token_request: RefreshTokenRequest,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Cierra la sesión revocando el refresh token

    Args:
        token_request: Objeto con el refresh token a revocar
        request: Request object
        current_user: Usuario autenticado

    Returns:
        Confirmación de logout
    """
    ip_address = request.client.host if request.client else None

    return AuthController.logout(
        token_request.refresh_token,
        current_user["id_usuario"],
        current_user["username"],
        ip_address
    )


@router.post("/logout-all", response_model=dict, summary="Cerrar todas las sesiones")
async def logout_all_sessions(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Cierra todas las sesiones del usuario revocando todos sus refresh tokens

    Útil para:
    - Cambio de contraseña
    - Sospecha de cuenta comprometida
    - Cierre de sesión remoto

    Args:
        request: Request object
        current_user: Usuario autenticado

    Returns:
        Número de sesiones cerradas
    """
    ip_address = request.client.host if request.client else None

    return AuthController.logout_all_sessions(
        current_user["id_usuario"],
        current_user["username"],
        ip_address
    )
