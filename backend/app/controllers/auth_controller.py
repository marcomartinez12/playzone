"""
Controlador de Autenticacion
RF-01: Iniciar Sesion
"""
from datetime import timedelta
from fastapi import HTTPException, status
from app.models.usuario import UsuarioLogin, UsuarioCreate, UsuarioResponse, Token
from app.utils.security import verify_password, create_access_token, hash_password
from app.config.database import get_db_cursor
from app.config.settings import settings


class AuthController:
    """Controlador para operaciones de autenticacion"""

    @staticmethod
    def login(usuario_login: UsuarioLogin) -> dict:
        """
        RF-01: Iniciar sesion - Valida credenciales y retorna token

        Args:
            usuario_login: Datos de login (username, password)

        Returns:
            Token de acceso y datos del usuario

        Raises:
            HTTPException: Si las credenciales son invalidas
        """
        with get_db_cursor() as cursor:
            # Buscar usuario por username
            cursor.execute(
                """
                SELECT id_usuario, username, email, password
                FROM usuarios
                WHERE username = %s
                """,
                (usuario_login.username,)
            )
            user = cursor.fetchone()

        # Validar si el usuario existe
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contrasena incorrectos",
            )

        # Validar contraseña (texto plano para desarrollo)
        if usuario_login.password != user["password"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contrasena incorrectos",
            )

        # Crear token de acceso
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user["username"], "id_usuario": user["id_usuario"]},
            expires_delta=access_token_expires
        )

        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id_usuario": user["id_usuario"],
                "username": user["username"],
                "email": user["email"]
            }
        }

    @staticmethod
    def register(usuario: UsuarioCreate) -> dict:
        """
        Registrar un nuevo usuario (administrador)

        Args:
            usuario: Datos del usuario a crear

        Returns:
            Datos del usuario creado

        Raises:
            HTTPException: Si el usuario ya existe
        """
        with get_db_cursor() as cursor:
            # Verificar si el usuario ya existe
            cursor.execute(
                "SELECT id_usuario FROM usuarios WHERE username = %s OR email = %s",
                (usuario.username, usuario.email)
            )
            existing_user = cursor.fetchone()

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El usuario o email ya esta registrado"
                )

            # Insertar usuario con contraseña en texto plano
            cursor.execute(
                """
                INSERT INTO usuarios (username, email, password)
                VALUES (%s, %s, %s)
                RETURNING id_usuario, username, email, fecha_registro
                """,
                (usuario.username, usuario.email, usuario.password)
            )
            new_user = cursor.fetchone()

        return {
            "success": True,
            "message": "Usuario registrado exitosamente",
            "user": dict(new_user)
        }
