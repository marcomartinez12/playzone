"""
Sistema de Rate Limiting
Previene ataques de fuerza bruta limitando intentos de login
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from app.config.database import get_db_cursor


class RateLimiter:
    """Rate limiter para prevenir ataques de fuerza bruta"""

    # Configuración
    MAX_INTENTOS_POR_USUARIO = 5  # Máximo de intentos fallidos
    MAX_INTENTOS_POR_IP = 10  # Máximo de intentos desde una IP
    TIEMPO_BLOQUEO_MINUTOS = 15  # Tiempo de bloqueo en minutos
    VENTANA_TIEMPO_MINUTOS = 10  # Ventana de tiempo para contar intentos

    @staticmethod
    def registrar_intento(username: str, ip_address: str, exitoso: bool, razon_fallo: Optional[str] = None, user_agent: Optional[str] = None):
        """
        Registra un intento de login

        Args:
            username: Usuario que intenta iniciar sesión
            ip_address: Dirección IP
            exitoso: Si el intento fue exitoso
            razon_fallo: Razón del fallo (opcional)
            user_agent: User agent del navegador
        """
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO login_attempts (username, ip_address, exitoso, razon_fallo, user_agent)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (username, ip_address, exitoso, razon_fallo, user_agent)
            )

            # Si fue exitoso, resetear contador de intentos fallidos del usuario
            if exitoso:
                cursor.execute(
                    "UPDATE usuarios SET intentos_fallidos = 0, bloqueado_hasta = NULL WHERE username = %s",
                    (username,)
                )
            else:
                # Incrementar contador de intentos fallidos
                cursor.execute(
                    """
                    UPDATE usuarios
                    SET intentos_fallidos = intentos_fallidos + 1
                    WHERE username = %s
                    """,
                    (username,)
                )

    @staticmethod
    def verificar_bloqueo_usuario(username: str) -> Tuple[bool, Optional[str]]:
        """
        Verifica si un usuario está bloqueado

        Args:
            username: Usuario a verificar

        Returns:
            Tuple (bloqueado: bool, mensaje: str)
        """
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT intentos_fallidos, bloqueado_hasta
                FROM usuarios
                WHERE username = %s
                """,
                (username,)
            )
            user = cursor.fetchone()

            if not user:
                return False, None

            # Verificar si tiene un bloqueo temporal activo
            if user['bloqueado_hasta'] and user['bloqueado_hasta'] > datetime.now():
                tiempo_restante = (user['bloqueado_hasta'] - datetime.now()).seconds // 60
                return True, f"Usuario bloqueado temporalmente. Intente nuevamente en {tiempo_restante} minutos."

            # Si el bloqueo expiró, limpiar
            if user['bloqueado_hasta'] and user['bloqueado_hasta'] <= datetime.now():
                cursor.execute(
                    "UPDATE usuarios SET intentos_fallidos = 0, bloqueado_hasta = NULL WHERE username = %s",
                    (username,)
                )
                return False, None

            # Verificar si alcanzó el máximo de intentos
            if user['intentos_fallidos'] >= RateLimiter.MAX_INTENTOS_POR_USUARIO:
                # Bloquear usuario
                bloqueado_hasta = datetime.now() + timedelta(minutes=RateLimiter.TIEMPO_BLOQUEO_MINUTOS)
                cursor.execute(
                    "UPDATE usuarios SET bloqueado_hasta = %s WHERE username = %s",
                    (bloqueado_hasta, username)
                )
                return True, f"Demasiados intentos fallidos. Usuario bloqueado por {RateLimiter.TIEMPO_BLOQUEO_MINUTOS} minutos."

            return False, None

    @staticmethod
    def verificar_bloqueo_ip(ip_address: str) -> Tuple[bool, Optional[str]]:
        """
        Verifica si una IP está bloqueada por demasiados intentos

        Args:
            ip_address: Dirección IP a verificar

        Returns:
            Tuple (bloqueado: bool, mensaje: str)
        """
        ventana_inicio = datetime.now() - timedelta(minutes=RateLimiter.VENTANA_TIEMPO_MINUTOS)

        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) as intentos
                FROM login_attempts
                WHERE ip_address = %s
                AND exitoso = FALSE
                AND fecha_intento >= %s
                """,
                (ip_address, ventana_inicio)
            )
            result = cursor.fetchone()
            intentos = result['intentos']

            if intentos >= RateLimiter.MAX_INTENTOS_POR_IP:
                return True, f"Demasiados intentos desde esta IP. Intente nuevamente en {RateLimiter.VENTANA_TIEMPO_MINUTOS} minutos."

            return False, None

    @staticmethod
    def puede_intentar_login(username: str, ip_address: str) -> Tuple[bool, Optional[str]]:
        """
        Verifica si se puede intentar un login

        Args:
            username: Usuario
            ip_address: Dirección IP

        Returns:
            Tuple (permitido: bool, mensaje_error: str)
        """
        # Verificar bloqueo por usuario
        bloqueado, mensaje = RateLimiter.verificar_bloqueo_usuario(username)
        if bloqueado:
            return False, mensaje

        # Verificar bloqueo por IP
        bloqueado, mensaje = RateLimiter.verificar_bloqueo_ip(ip_address)
        if bloqueado:
            return False, mensaje

        return True, None

    @staticmethod
    def obtener_intentos_recientes(username: Optional[str] = None, ip_address: Optional[str] = None, limite: int = 20) -> list:
        """
        Obtiene intentos de login recientes

        Args:
            username: Filtrar por usuario (opcional)
            ip_address: Filtrar por IP (opcional)
            limite: Número máximo de registros

        Returns:
            Lista de intentos de login
        """
        with get_db_cursor() as cursor:
            query = "SELECT * FROM login_attempts WHERE 1=1"
            params = []

            if username:
                query += " AND username = %s"
                params.append(username)

            if ip_address:
                query += " AND ip_address = %s"
                params.append(ip_address)

            query += " ORDER BY fecha_intento DESC LIMIT %s"
            params.append(limite)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def limpiar_intentos_antiguos(dias: int = 30) -> int:
        """
        Limpia intentos de login antiguos

        Args:
            dias: Eliminar intentos más antiguos que X días

        Returns:
            Número de registros eliminados
        """
        fecha_limite = datetime.now() - timedelta(days=dias)

        with get_db_cursor() as cursor:
            cursor.execute(
                "DELETE FROM login_attempts WHERE fecha_intento < %s",
                (fecha_limite,)
            )
            return cursor.rowcount
