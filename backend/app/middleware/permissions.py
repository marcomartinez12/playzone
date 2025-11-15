"""
Middleware de Permisos
Verifica que el usuario tenga los permisos necesarios para acceder a recursos
"""
from fastapi import Depends, HTTPException, status
from typing import List
from app.middleware.auth import get_current_user
from app.config.database import get_db_cursor


class PermissionChecker:
    """Verificador de permisos"""

    def __init__(self, permisos_requeridos: List[str]):
        """
        Inicializa el verificador de permisos

        Args:
            permisos_requeridos: Lista de permisos necesarios (OR - con uno basta)
        """
        self.permisos_requeridos = permisos_requeridos

    async def __call__(self, current_user: dict = Depends(get_current_user)) -> dict:
        """
        Verifica que el usuario tenga al menos uno de los permisos requeridos

        Args:
            current_user: Usuario actual autenticado

        Returns:
            Usuario con información de permisos

        Raises:
            HTTPException: Si no tiene permisos
        """
        id_usuario = current_user['id_usuario']

        # Obtener permisos del usuario
        permisos_usuario = await self.obtener_permisos_usuario(id_usuario)

        # Verificar si tiene al menos uno de los permisos requeridos
        tiene_permiso = any(
            permiso in permisos_usuario
            for permiso in self.permisos_requeridos
        )

        if not tiene_permiso:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permisos suficientes. Se requiere uno de: {', '.join(self.permisos_requeridos)}"
            )

        # Agregar permisos al objeto de usuario
        current_user['permisos'] = permisos_usuario

        return current_user

    @staticmethod
    async def obtener_permisos_usuario(id_usuario: int) -> List[str]:
        """
        Obtiene todos los permisos de un usuario

        Args:
            id_usuario: ID del usuario

        Returns:
            Lista de nombres de permisos
        """
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT p.nombre
                FROM permisos p
                JOIN rol_permisos rp ON p.id_permiso = rp.id_permiso
                JOIN usuarios u ON u.id_rol = rp.id_rol
                WHERE u.id_usuario = %s
                """,
                (id_usuario,)
            )
            permisos = cursor.fetchall()
            return [permiso['nombre'] for permiso in permisos]

    @staticmethod
    async def usuario_tiene_permiso(id_usuario: int, permiso: str) -> bool:
        """
        Verifica si un usuario tiene un permiso específico

        Args:
            id_usuario: ID del usuario
            permiso: Nombre del permiso

        Returns:
            True si tiene el permiso
        """
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS(
                    SELECT 1
                    FROM permisos p
                    JOIN rol_permisos rp ON p.id_permiso = rp.id_permiso
                    JOIN usuarios u ON u.id_rol = rp.id_rol
                    WHERE u.id_usuario = %s AND p.nombre = %s
                ) as tiene_permiso
                """,
                (id_usuario, permiso)
            )
            result = cursor.fetchone()
            return result['tiene_permiso']

    @staticmethod
    async def obtener_rol_usuario(id_usuario: int) -> dict:
        """
        Obtiene el rol de un usuario

        Args:
            id_usuario: ID del usuario

        Returns:
            Información del rol
        """
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT r.id_rol, r.nombre, r.descripcion
                FROM roles r
                JOIN usuarios u ON u.id_rol = r.id_rol
                WHERE u.id_usuario = %s
                """,
                (id_usuario,)
            )
            rol = cursor.fetchone()
            return dict(rol) if rol else None


# Helpers para verificaciones comunes
def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Requiere rol de administrador"""
    return PermissionChecker(['usuarios.crear', 'usuarios.eliminar'])(current_user)


async def require_permissions(*permisos: str):
    """
    Decorator/dependency para requerir permisos específicos

    Uso:
        @router.get("/productos")
        async def listar_productos(user = Depends(require_permissions("productos.ver"))):
            ...
    """
    return PermissionChecker(list(permisos))
