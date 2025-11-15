"""
Controlador de Autenticacion
RF-01: Iniciar Sesion
Incluye: Rate Limiting, Refresh Tokens, Auditoría, Hashing de contraseñas
"""
from datetime import timedelta
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
                SELECT u.id_usuario, u.username, u.email, u.password, u.activo, u.eliminado,
                       r.nombre as rol
                FROM usuarios u
                LEFT JOIN roles r ON u.id_rol = r.id_rol
                WHERE u.username = %s
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
                "id_usuario": user["id_usuario"],
                "rol": user["rol"]
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
                "email": user["email"],
                "rol": user["rol"]
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
            # Por defecto, se asigna rol ADMIN (id_rol = 1)
            cursor.execute(
                """
                INSERT INTO usuarios (username, email, password, id_rol)
                VALUES (%s, %s, %s, (SELECT id_rol FROM roles WHERE nombre = 'ADMIN' LIMIT 1))
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
                SELECT u.id_usuario, u.username, u.email, r.nombre as rol
                FROM usuarios u
                LEFT JOIN roles r ON u.id_rol = r.id_rol
                WHERE u.id_usuario = %s AND u.activo = TRUE AND u.eliminado = FALSE
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
                "id_usuario": user["id_usuario"],
                "rol": user["rol"]
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
