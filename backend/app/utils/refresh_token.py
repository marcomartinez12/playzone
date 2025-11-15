"""
Sistema de Refresh Tokens
Permite mantener sesiones activas de forma segura
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
from app.config.database import get_db_cursor
from app.config.settings import settings


class RefreshTokenManager:
    """Gestor de refresh tokens"""

    # Configuración
    REFRESH_TOKEN_EXPIRE_DAYS = 30  # Tokens de refresco duran 30 días
    TOKEN_LENGTH = 64  # Longitud del token en bytes

    @staticmethod
    def _hash_token(token: str) -> str:
        """Hashea un token para almacenamiento seguro"""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def crear_refresh_token(
        id_usuario: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Crea un nuevo refresh token

        Args:
            id_usuario: ID del usuario
            ip_address: Dirección IP del cliente
            user_agent: User agent del navegador

        Returns:
            Token de refresco (string seguro)
        """
        # Generar token aleatorio seguro
        token = secrets.token_urlsafe(RefreshTokenManager.TOKEN_LENGTH)
        token_hash = RefreshTokenManager._hash_token(token)

        # Calcular fecha de expiración
        expira_en = datetime.now() + timedelta(days=RefreshTokenManager.REFRESH_TOKEN_EXPIRE_DAYS)

        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO refresh_tokens (id_usuario, token, token_hash, expira_en, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id_refresh_token
                """,
                (id_usuario, token, token_hash, expira_en, ip_address, user_agent)
            )

        return token

    @staticmethod
    def validar_refresh_token(token: str) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Valida un refresh token

        Args:
            token: Token a validar

        Returns:
            Tuple (valido: bool, id_usuario: int, mensaje_error: str)
        """
        token_hash = RefreshTokenManager._hash_token(token)

        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT rt.id_refresh_token, rt.id_usuario, rt.expira_en, rt.revocado,
                       u.username, u.activo
                FROM refresh_tokens rt
                JOIN usuarios u ON rt.id_usuario = u.id_usuario
                WHERE rt.token_hash = %s
                """,
                (token_hash,)
            )
            result = cursor.fetchone()

            if not result:
                return False, None, "Token inválido"

            if result['revocado']:
                return False, None, "Token revocado"

            if result['expira_en'] < datetime.now():
                return False, None, "Token expirado"

            if not result['activo']:
                return False, None, "Usuario inactivo"

            # Actualizar última uso
            cursor.execute(
                "UPDATE refresh_tokens SET ultima_uso = %s WHERE id_refresh_token = %s",
                (datetime.now(), result['id_refresh_token'])
            )

            return True, result['id_usuario'], None

    @staticmethod
    def revocar_token(token: str) -> bool:
        """
        Revoca un refresh token

        Args:
            token: Token a revocar

        Returns:
            True si se revocó exitosamente
        """
        token_hash = RefreshTokenManager._hash_token(token)

        with get_db_cursor() as cursor:
            cursor.execute(
                """
                UPDATE refresh_tokens
                SET revocado = TRUE, fecha_revocacion = %s
                WHERE token_hash = %s AND revocado = FALSE
                """,
                (datetime.now(), token_hash)
            )
            return cursor.rowcount > 0

    @staticmethod
    def revocar_todos_tokens_usuario(id_usuario: int) -> int:
        """
        Revoca todos los tokens de un usuario (logout de todas las sesiones)

        Args:
            id_usuario: ID del usuario

        Returns:
            Número de tokens revocados
        """
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                UPDATE refresh_tokens
                SET revocado = TRUE, fecha_revocacion = %s
                WHERE id_usuario = %s AND revocado = FALSE
                """,
                (datetime.now(), id_usuario)
            )
            return cursor.rowcount

    @staticmethod
    def rotar_token(token_actual: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Optional[str]:
        """
        Rota un refresh token (crea uno nuevo y revoca el actual)
        Útil para refresh token rotation security

        Args:
            token_actual: Token actual a rotar
            ip_address: IP del cliente
            user_agent: User agent

        Returns:
            Nuevo token o None si falló
        """
        valido, id_usuario, error = RefreshTokenManager.validar_refresh_token(token_actual)

        if not valido:
            return None

        # Revocar token actual
        RefreshTokenManager.revocar_token(token_actual)

        # Crear nuevo token
        return RefreshTokenManager.crear_refresh_token(id_usuario, ip_address, user_agent)

    @staticmethod
    def limpiar_tokens_expirados() -> int:
        """
        Elimina tokens expirados y revocados de la base de datos

        Returns:
            Número de tokens eliminados
        """
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM refresh_tokens
                WHERE (expira_en < %s) OR (revocado = TRUE AND fecha_revocacion < %s)
                """,
                (datetime.now(), datetime.now() - timedelta(days=7))
            )
            return cursor.rowcount

    @staticmethod
    def obtener_tokens_activos_usuario(id_usuario: int) -> list:
        """
        Obtiene todos los tokens activos de un usuario

        Args:
            id_usuario: ID del usuario

        Returns:
            Lista de tokens activos
        """
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id_refresh_token, ip_address, user_agent, fecha_creacion, ultima_uso, expira_en
                FROM refresh_tokens
                WHERE id_usuario = %s AND revocado = FALSE AND expira_en > %s
                ORDER BY fecha_creacion DESC
                """,
                (id_usuario, datetime.now())
            )
            return [dict(row) for row in cursor.fetchall()]
