"""
Sistema de Auditoría
Registra todas las acciones importantes del sistema
"""
from typing import Optional
from datetime import datetime
from app.config.database import get_db_cursor
from app.models.security import AuditoriaCreate
import json


class AuditLogger:
    """Logger de auditoría para el sistema"""

    @staticmethod
    def log(
        accion: str,
        modulo: str,
        id_usuario: Optional[int] = None,
        username: Optional[str] = None,
        entidad: Optional[str] = None,
        id_entidad: Optional[int] = None,
        datos_anteriores: Optional[dict] = None,
        datos_nuevos: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> int:
        """
        Registra una acción en el log de auditoría

        Args:
            accion: Acción realizada (ej: 'LOGIN', 'CREAR_PRODUCTO', 'ELIMINAR_CLIENTE')
            modulo: Módulo del sistema (ej: 'auth', 'productos', 'ventas')
            id_usuario: ID del usuario que realizó la acción
            username: Username del usuario
            entidad: Tipo de entidad afectada (ej: 'producto', 'cliente')
            id_entidad: ID de la entidad afectada
            datos_anteriores: Estado anterior de los datos (JSON)
            datos_nuevos: Estado nuevo de los datos (JSON)
            ip_address: Dirección IP del usuario
            user_agent: User agent del navegador

        Returns:
            ID del registro de auditoría creado
        """
        # Convertir diccionarios a JSON si es necesario
        datos_anteriores_json = json.dumps(datos_anteriores) if datos_anteriores else None
        datos_nuevos_json = json.dumps(datos_nuevos) if datos_nuevos else None

        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO auditoria (
                    id_usuario, username, accion, modulo, entidad, id_entidad,
                    datos_anteriores, datos_nuevos, ip_address, user_agent
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_auditoria
                """,
                (
                    id_usuario, username, accion, modulo, entidad, id_entidad,
                    datos_anteriores_json, datos_nuevos_json, ip_address, user_agent
                )
            )
            result = cursor.fetchone()
            return result['id_auditoria']

    @staticmethod
    def log_login(username: str, exitoso: bool, ip_address: str, user_agent: Optional[str] = None, razon: Optional[str] = None):
        """Registra un intento de login"""
        accion = "LOGIN_EXITOSO" if exitoso else "LOGIN_FALLIDO"
        datos = {"razon": razon} if not exitoso and razon else None

        return AuditLogger.log(
            accion=accion,
            modulo="auth",
            username=username,
            datos_nuevos=datos,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def log_logout(id_usuario: int, username: str, ip_address: str):
        """Registra un cierre de sesión"""
        return AuditLogger.log(
            accion="LOGOUT",
            modulo="auth",
            id_usuario=id_usuario,
            username=username,
            ip_address=ip_address
        )

    @staticmethod
    def log_create(modulo: str, entidad: str, id_entidad: int, datos: dict, id_usuario: int, username: str, ip_address: Optional[str] = None):
        """Registra la creación de una entidad"""
        return AuditLogger.log(
            accion=f"CREAR_{entidad.upper()}",
            modulo=modulo,
            entidad=entidad,
            id_entidad=id_entidad,
            datos_nuevos=datos,
            id_usuario=id_usuario,
            username=username,
            ip_address=ip_address
        )

    @staticmethod
    def log_update(modulo: str, entidad: str, id_entidad: int, datos_anteriores: dict, datos_nuevos: dict, id_usuario: int, username: str, ip_address: Optional[str] = None):
        """Registra la actualización de una entidad"""
        return AuditLogger.log(
            accion=f"ACTUALIZAR_{entidad.upper()}",
            modulo=modulo,
            entidad=entidad,
            id_entidad=id_entidad,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            id_usuario=id_usuario,
            username=username,
            ip_address=ip_address
        )

    @staticmethod
    def log_delete(modulo: str, entidad: str, id_entidad: int, datos: dict, id_usuario: int, username: str, ip_address: Optional[str] = None):
        """Registra la eliminación de una entidad"""
        return AuditLogger.log(
            accion=f"ELIMINAR_{entidad.upper()}",
            modulo=modulo,
            entidad=entidad,
            id_entidad=id_entidad,
            datos_anteriores=datos,
            id_usuario=id_usuario,
            username=username,
            ip_address=ip_address
        )

    @staticmethod
    def obtener_logs(
        modulo: Optional[str] = None,
        id_usuario: Optional[int] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        limite: int = 100
    ) -> list:
        """
        Obtiene logs de auditoría con filtros

        Args:
            modulo: Filtrar por módulo
            id_usuario: Filtrar por usuario
            fecha_desde: Fecha inicial
            fecha_hasta: Fecha final
            limite: Número máximo de registros

        Returns:
            Lista de logs de auditoría
        """
        with get_db_cursor() as cursor:
            query = "SELECT * FROM auditoria WHERE 1=1"
            params = []

            if modulo:
                query += " AND modulo = %s"
                params.append(modulo)

            if id_usuario:
                query += " AND id_usuario = %s"
                params.append(id_usuario)

            if fecha_desde:
                query += " AND fecha_accion >= %s"
                params.append(fecha_desde)

            if fecha_hasta:
                query += " AND fecha_accion <= %s"
                params.append(fecha_hasta)

            query += " ORDER BY fecha_accion DESC LIMIT %s"
            params.append(limite)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
