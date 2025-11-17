"""
Controlador de Autenticacion
RF-01: Iniciar Sesion
Incluye: Rate Limiting, Refresh Tokens, Auditoría, Hashing de contraseñas, Recuperación de contraseña
"""
from datetime import timedelta, datetime, timezone
from typing import Optional
from fastapi import HTTPException, status
from app.models.usuario import UsuarioLogin, UsuarioCreate, UsuarioResponse, Token
from app.models.security import TokenPair
from app.utils.security import verify_password, create_access_token, hash_password
from app.utils.rate_limiter import RateLimiter
from app.utils.refresh_token import RefreshTokenManager
from app.utils.audit import AuditLogger
from app.config.database import get_db_cursor
from app.config.settings import settings
from app.services.email_service import email_service
import secrets
import json


class AuthController:
    """Controlador para operaciones de autenticacion"""

    @staticmethod
    def login(usuario_login: UsuarioLogin, ip_address: str = "0.0.0.0", user_agent: Optional[str] = None) -> dict:
        """
        RF-01: Iniciar sesion - Valida credenciales y retorna tokens

        Incluye:
        - Rate limiting (prevención de fuerza bruta)
        - Hashing de contraseñas con bcrypt
        - Refresh tokens para sesiones persistentes
        - Auditoría de intentos de login

        Args:
            usuario_login: Datos de login (username, password)
            ip_address: Dirección IP del cliente
            user_agent: User agent del navegador

        Returns:
            Par de tokens (access + refresh) y datos del usuario

        Raises:
            HTTPException: Si las credenciales son invalidas o usuario bloqueado
        """
        # 1. VERIFICAR RATE LIMITING
        puede_intentar, mensaje_bloqueo = RateLimiter.puede_intentar_login(
            usuario_login.username,
            ip_address
        )

        if not puede_intentar:
            # Registrar intento bloqueado
            RateLimiter.registrar_intento(
                usuario_login.username,
                ip_address,
                exitoso=False,
                razon_fallo="Bloqueado por rate limiting",
                user_agent=user_agent
            )
            AuditLogger.log_login(
                usuario_login.username,
                exitoso=False,
                ip_address=ip_address,
                user_agent=user_agent,
                razon="Rate limiting"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=mensaje_bloqueo
            )

        # 2. BUSCAR USUARIO Y VERIFICAR ESTADO
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id_usuario, username, email, password, activo, eliminado
                FROM usuarios
                WHERE username = %s
                """,
                (usuario_login.username,)
            )
            user = cursor.fetchone()

        # Validar si el usuario existe
        if not user:
            RateLimiter.registrar_intento(
                usuario_login.username,
                ip_address,
                exitoso=False,
                razon_fallo="Usuario no existe",
                user_agent=user_agent
            )
            AuditLogger.log_login(
                usuario_login.username,
                exitoso=False,
                ip_address=ip_address,
                user_agent=user_agent,
                razon="Usuario no encontrado"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos"
            )

        # Verificar si el usuario está eliminado (soft delete)
        if user['eliminado']:
            RateLimiter.registrar_intento(
                usuario_login.username,
                ip_address,
                exitoso=False,
                razon_fallo="Usuario eliminado",
                user_agent=user_agent
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario desactivado. Contacte al administrador"
            )

        # Verificar si el usuario está activo
        if not user['activo']:
            RateLimiter.registrar_intento(
                usuario_login.username,
                ip_address,
                exitoso=False,
                razon_fallo="Usuario inactivo",
                user_agent=user_agent
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo. Contacte al administrador"
            )

        # 3. VALIDAR CONTRASEÑA
        # Intentar con hash bcrypt primero (nuevas contraseñas)
        password_valida = False
        necesita_rehash = False

        if user["password"].startswith("$2b$"):
            # Es un hash bcrypt
            password_valida = verify_password(usuario_login.password, user["password"])
        else:
            # Es texto plano (contraseñas antiguas)
            if usuario_login.password == user["password"]:
                password_valida = True
                necesita_rehash = True

        if not password_valida:
            RateLimiter.registrar_intento(
                usuario_login.username,
                ip_address,
                exitoso=False,
                razon_fallo="Contraseña incorrecta",
                user_agent=user_agent
            )
            AuditLogger.log_login(
                usuario_login.username,
                exitoso=False,
                ip_address=ip_address,
                user_agent=user_agent,
                razon="Contraseña incorrecta"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos"
            )

        # 4. ACTUALIZAR HASH SI ES NECESARIO (migración de texto plano a bcrypt)
        if necesita_rehash:
            with get_db_cursor() as cursor:
                nuevo_hash = hash_password(usuario_login.password)
                cursor.execute(
                    "UPDATE usuarios SET password = %s WHERE id_usuario = %s",
                    (nuevo_hash, user["id_usuario"])
                )

        # 5. LOGIN EXITOSO - GENERAR TOKENS
        # Crear access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={
                "sub": user["username"],
                "id_usuario": user["id_usuario"]
            },
            expires_delta=access_token_expires
        )

        # Crear refresh token
        refresh_token = RefreshTokenManager.crear_refresh_token(
            id_usuario=user["id_usuario"],
            ip_address=ip_address,
            user_agent=user_agent
        )

        # 6. ACTUALIZAR USUARIO
        with get_db_cursor() as cursor:
            cursor.execute(
                "UPDATE usuarios SET fecha_ultima_sesion = NOW() WHERE id_usuario = %s",
                (user["id_usuario"],)
            )

        # 7. REGISTRAR ÉXITO
        RateLimiter.registrar_intento(
            usuario_login.username,
            ip_address,
            exitoso=True,
            user_agent=user_agent
        )
        AuditLogger.log_login(
            usuario_login.username,
            exitoso=True,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": {
                "id_usuario": user["id_usuario"],
                "username": user["username"],
                "email": user["email"]
            }
        }

    @staticmethod
    def register(usuario: UsuarioCreate, ip_address: Optional[str] = None) -> dict:
        """
        Registrar un nuevo usuario con contraseña hasheada

        Args:
            usuario: Datos del usuario a crear
            ip_address: IP del solicitante (para auditoría)

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

            # Hashear la contraseña
            password_hash = hash_password(usuario.password)

            # Insertar usuario con contraseña hasheada
            cursor.execute(
                """
                INSERT INTO usuarios (username, email, password)
                VALUES (%s, %s, %s)
                RETURNING id_usuario, username, email, fecha_registro
                """,
                (usuario.username, usuario.email, password_hash)
            )
            new_user = cursor.fetchone()

        # Auditoría
        AuditLogger.log(
            accion="REGISTRO_USUARIO",
            modulo="auth",
            username=usuario.username,
            entidad="usuario",
            id_entidad=new_user["id_usuario"],
            datos_nuevos={"username": usuario.username, "email": usuario.email},
            ip_address=ip_address
        )

        return {
            "success": True,
            "message": "Usuario registrado exitosamente",
            "user": dict(new_user)
        }

    @staticmethod
    def refresh_access_token(refresh_token: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> dict:
        """
        Refresca el access token usando un refresh token válido

        Args:
            refresh_token: Refresh token válido
            ip_address: IP del cliente
            user_agent: User agent

        Returns:
            Nuevo access token

        Raises:
            HTTPException: Si el refresh token es inválido
        """
        # Validar refresh token
        valido, id_usuario, error = RefreshTokenManager.validar_refresh_token(refresh_token)

        if not valido:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error or "Refresh token inválido"
            )

        # Obtener datos del usuario
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id_usuario, username, email
                FROM usuarios
                WHERE id_usuario = %s AND activo = TRUE AND eliminado = FALSE
                """,
                (id_usuario,)
            )
            user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no válido"
            )

        # Generar nuevo access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={
                "sub": user["username"],
                "id_usuario": user["id_usuario"]
            },
            expires_delta=access_token_expires
        )

        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }

    @staticmethod
    def logout(refresh_token: str, id_usuario: int, username: str, ip_address: Optional[str] = None) -> dict:
        """
        Cierra sesión revocando el refresh token

        Args:
            refresh_token: Token a revocar
            id_usuario: ID del usuario
            username: Nombre del usuario
            ip_address: IP del cliente

        Returns:
            Confirmación de logout
        """
        # Revocar refresh token
        revocado = RefreshTokenManager.revocar_token(refresh_token)

        # Auditoría
        AuditLogger.log_logout(id_usuario, username, ip_address or "0.0.0.0")

        return {
            "success": True,
            "message": "Sesión cerrada exitosamente"
        }

    @staticmethod
    def logout_all_sessions(id_usuario: int, username: str, ip_address: Optional[str] = None) -> dict:
        """
        Cierra todas las sesiones del usuario revocando todos sus refresh tokens

        Args:
            id_usuario: ID del usuario
            username: Nombre del usuario
            ip_address: IP del cliente

        Returns:
            Número de sesiones cerradas
        """
        # Revocar todos los tokens del usuario
        tokens_revocados = RefreshTokenManager.revocar_todos_tokens_usuario(id_usuario)

        # Auditoría
        AuditLogger.log(
            accion="LOGOUT_ALL_SESSIONS",
            modulo="auth",
            id_usuario=id_usuario,
            username=username,
            datos_nuevos={"tokens_revocados": tokens_revocados},
            ip_address=ip_address
        )

        return {
            "success": True,
            "message": f"{tokens_revocados} sesiones cerradas exitosamente",
            "sessions_closed": tokens_revocados
        }

    @staticmethod
    def request_password_reset(email: str, ip_address: Optional[str] = None) -> dict:
        """
        Solicita recuperación de contraseña enviando email con token

        Args:
            email: Email del usuario
            ip_address: IP del solicitante

        Returns:
            Mensaje de confirmación

        Raises:
            HTTPException: Si hay errores
        """
        # Buscar usuario por email
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id_usuario, username, email, activo, eliminado
                FROM usuarios
                WHERE email = %s
                """,
                (email,)
            )
            user = cursor.fetchone()

        # Por seguridad, siempre retornar mensaje genérico
        # (no revelar si el email existe o no)
        mensaje_generico = "Si el email está registrado, recibirás un enlace de recuperación"

        if not user:
            # Registrar intento en auditoría
            AuditLogger.log(
                accion="PASSWORD_RESET_REQUEST_FAILED",
                modulo="auth",
                datos_nuevos={"email": email, "razon": "Email no encontrado"},
                ip_address=ip_address
            )
            return {
                "success": True,
                "message": mensaje_generico
            }

        # Verificar si el usuario está activo
        if not user['activo'] or user['eliminado']:
            AuditLogger.log(
                accion="PASSWORD_RESET_REQUEST_FAILED",
                modulo="auth",
                id_usuario=user['id_usuario'],
                username=user['username'],
                datos_nuevos={"email": email, "razon": "Usuario inactivo o eliminado"},
                ip_address=ip_address
            )
            return {
                "success": True,
                "message": mensaje_generico
            }

        # Generar token seguro
        reset_token = secrets.token_urlsafe(32)

        # Calcular fecha de expiración (UTC)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.reset_token_expire_minutes)

        # Guardar token en BD (hasheado)
        with get_db_cursor() as cursor:
            token_hash = hash_password(reset_token)
            cursor.execute(
                """
                UPDATE usuarios
                SET reset_token = %s, reset_token_expires = %s
                WHERE id_usuario = %s
                """,
                (token_hash, expires_at, user['id_usuario'])
            )

        # Enviar email
        email_enviado = email_service.send_password_reset_email(user['email'], reset_token)

        # Auditoría
        AuditLogger.log(
            accion="PASSWORD_RESET_REQUEST",
            modulo="auth",
            id_usuario=user['id_usuario'],
            username=user['username'],
            datos_nuevos={
                "email": user['email'],
                "email_enviado": email_enviado,
                "token_expires": expires_at.isoformat()
            },
            ip_address=ip_address
        )

        return {
            "success": True,
            "message": mensaje_generico
        }

    @staticmethod
    def reset_password(token: str, new_password: str, ip_address: Optional[str] = None) -> dict:
        """
        Restablece la contraseña usando el token de recuperación

        Args:
            token: Token de recuperación
            new_password: Nueva contraseña
            ip_address: IP del solicitante

        Returns:
            Mensaje de confirmación

        Raises:
            HTTPException: Si el token es inválido o expiró
        """
        # Buscar usuario con token válido
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id_usuario, username, email, reset_token, reset_token_expires
                FROM usuarios
                WHERE reset_token IS NOT NULL
                AND reset_token_expires > NOW()
                AND activo = TRUE
                AND eliminado = FALSE
                """
            )
            usuarios_con_token = cursor.fetchall()

        # Buscar el usuario cuyo token hash coincida
        user = None
        for usuario in usuarios_con_token:
            if verify_password(token, usuario['reset_token']):
                user = usuario
                break

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de recuperación inválido o expirado"
            )

        # Hashear nueva contraseña
        new_password_hash = hash_password(new_password)

        # Actualizar contraseña y limpiar token
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                UPDATE usuarios
                SET password = %s,
                    reset_token = NULL,
                    reset_token_expires = NULL
                WHERE id_usuario = %s
                """,
                (new_password_hash, user['id_usuario'])
            )

        # Revocar todos los refresh tokens (cerrar sesiones activas)
        RefreshTokenManager.revocar_todos_tokens_usuario(user['id_usuario'])

        # Enviar email de confirmación
        email_service.send_password_changed_notification(user['email'])

        # Auditoría
        AuditLogger.log(
            accion="PASSWORD_RESET_COMPLETED",
            modulo="auth",
            id_usuario=user['id_usuario'],
            username=user['username'],
            datos_nuevos={"email": user['email']},
            ip_address=ip_address
        )

        return {
            "success": True,
            "message": "Contraseña actualizada exitosamente"
        }
