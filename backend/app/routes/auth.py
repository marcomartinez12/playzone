"""
Rutas de Autenticacion
RF-01: Iniciar Sesion
"""
from fastapi import APIRouter, HTTPException
from app.models.usuario import UsuarioLogin, UsuarioCreate, Token
from app.controllers.auth_controller import AuthController

router = APIRouter()


@router.post("/login", response_model=dict, summary="Iniciar sesion")
async def login(usuario: UsuarioLogin):
    """
    RF-01: Iniciar sesion

    Valida las credenciales del usuario y retorna un token JWT

    Args:
        usuario: Credenciales (username, password)

    Returns:
        Token de acceso y datos del usuario
    """
    return AuthController.login(usuario)


@router.post("/register", response_model=dict, summary="Registrar usuario")
async def register(usuario: UsuarioCreate):
    """
    Registrar un nuevo usuario administrador

    Args:
        usuario: Datos del usuario (username, email, password)

    Returns:
        Usuario creado
    """
    return AuthController.register(usuario)
