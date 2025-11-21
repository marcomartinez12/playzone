"""
Controlador de Servicios de Reparacion
RF-06: Registrar Servicios de Reparacion
RF-13: Marcar reparacion como lista para entrega
RF-14: Busqueda de reparaciones por cliente o consola
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.models.servicio import ServicioCreate, ServicioUpdate, EstadoServicio
from app.utils.generators import generar_codigo_servicio
from app.config.database import get_db_cursor


class ServicioController:
    """Controlador para operaciones de servicios de reparacion"""

    @staticmethod
    def crear_servicio(servicio: ServicioCreate) -> dict:
        """
        RF-06: Crear un nuevo servicio de reparacion

        Args:
            servicio: Datos del servicio a crear

        Returns:
            Servicio creado

        Raises:
            HTTPException: Si el cliente no existe
        """
        with get_db_cursor() as cursor:
            # Verificar que el cliente existe
            cursor.execute(
                "SELECT id_cliente FROM clientes WHERE id_cliente = %s",
                (servicio.id_cliente,)
            )
            cliente = cursor.fetchone()

            if not cliente:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente no encontrado"
                )

            # Insertar servicio
            cursor.execute(
                """
                INSERT INTO servicios (id_usuario, id_cliente, consola, descripcion, estado, costo, pagado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id_servicio, id_usuario, id_cliente, consola, descripcion,
                          estado, costo, pagado, fecha_ingreso, fecha_entrega
                """,
                (servicio.id_usuario, servicio.id_cliente, servicio.consola,
                 servicio.descripcion, EstadoServicio.EN_REPARACION.value, servicio.costo, servicio.pagado)
            )
            nuevo_servicio = cursor.fetchone()

            # Obtener datos completos
            cursor.execute(
                """
                SELECT s.*, c.nombre as nombre_cliente, c.telefono as telefono_cliente,
                       c.email as email_cliente, u.username as nombre_usuario
                FROM servicios s
                JOIN clientes c ON s.id_cliente = c.id_cliente
                JOIN usuarios u ON s.id_usuario = u.id_usuario
                WHERE s.id_servicio = %s
                """,
                (nuevo_servicio["id_servicio"],)
            )
            servicio_completo = cursor.fetchone()

        return {
            "success": True,
            "message": "Servicio registrado exitosamente",
            "data": dict(servicio_completo)
        }

    @staticmethod
    def obtener_servicios(
        estado: Optional[EstadoServicio] = None,
        id_cliente: Optional[int] = None,
        consola: Optional[str] = None
    ) -> List[dict]:
        """
        RF-14: Obtener lista de servicios con filtros

        Args:
            estado: Filtrar por estado (opcional)
            id_cliente: Filtrar por cliente (opcional)
            consola: Buscar por tipo de consola (opcional)

        Returns:
            Lista de servicios
        """
        with get_db_cursor() as cursor:
            query = """
                SELECT s.id_servicio, s.id_usuario, s.id_cliente, s.consola,
                       s.descripcion, s.estado, s.costo, s.pagado, s.fecha_ingreso, s.fecha_entrega,
                       c.nombre as nombre_cliente, c.documento as documento_cliente,
                       c.telefono as telefono_cliente, c.email as email_cliente,
                       u.username as nombre_usuario,
                       EXTRACT(DAY FROM (COALESCE(s.fecha_entrega, NOW()) - s.fecha_ingreso)) as dias_en_servicio
                FROM servicios s
                JOIN clientes c ON s.id_cliente = c.id_cliente
                JOIN usuarios u ON s.id_usuario = u.id_usuario
                WHERE 1=1
            """
            params = []

            if estado:
                query += " AND s.estado = %s"
                params.append(estado.value)

            if id_cliente:
                query += " AND s.id_cliente = %s"
                params.append(id_cliente)

            if consola:
                query += " AND LOWER(s.consola) LIKE LOWER(%s)"
                params.append(f"%{consola}%")

            query += " ORDER BY s.fecha_ingreso DESC"

            cursor.execute(query, params)
            servicios = cursor.fetchall()

        return [dict(s) for s in servicios]

    @staticmethod
    def obtener_servicio(id_servicio: int) -> dict:
        """
        Obtener un servicio por ID

        Args:
            id_servicio: ID del servicio

        Returns:
            Datos del servicio

        Raises:
            HTTPException: Si el servicio no existe
        """
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT s.id_servicio, s.id_usuario, s.id_cliente, s.consola,
                       s.descripcion, s.estado, s.costo, s.pagado, s.fecha_ingreso, s.fecha_entrega,
                       c.nombre as nombre_cliente, c.documento as documento_cliente,
                       c.telefono as telefono_cliente, c.email as email_cliente,
                       u.username as nombre_usuario,
                       EXTRACT(DAY FROM (COALESCE(s.fecha_entrega, NOW()) - s.fecha_ingreso)) as dias_en_servicio
                FROM servicios s
                JOIN clientes c ON s.id_cliente = c.id_cliente
                JOIN usuarios u ON s.id_usuario = u.id_usuario
                WHERE s.id_servicio = %s
                """,
                (id_servicio,)
            )
            servicio = cursor.fetchone()

        if not servicio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )

        return dict(servicio)

    @staticmethod
    def actualizar_servicio(id_servicio: int, servicio: ServicioUpdate) -> dict:
        """
        RF-13: Actualizar un servicio (marcar como listo, etc)

        Args:
            id_servicio: ID del servicio a actualizar
            servicio: Datos a actualizar

        Returns:
            Servicio actualizado

        Raises:
            HTTPException: Si el servicio no existe
        """
        # Verificar que el servicio existe
        ServicioController.obtener_servicio(id_servicio)

        # Construir query dinamica
        updates = []
        params = []

        if servicio.consola is not None:
            updates.append("consola = %s")
            params.append(servicio.consola)

        if servicio.descripcion is not None:
            updates.append("descripcion = %s")
            params.append(servicio.descripcion)

        if servicio.estado is not None:
            updates.append("estado = %s")
            params.append(servicio.estado.value)

            # RF-13: Si se marca como "Listo" o "Entregado", actualizar fecha_entrega
            if servicio.estado in [EstadoServicio.LISTO, EstadoServicio.ENTREGADO]:
                updates.append("fecha_entrega = NOW()")

        if servicio.costo is not None:
            updates.append("costo = %s")
            params.append(servicio.costo)

        if servicio.pagado is not None:
            updates.append("pagado = %s")
            params.append(servicio.pagado)

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar"
            )

        params.append(id_servicio)

        with get_db_cursor() as cursor:
            query = f"""
                UPDATE servicios
                SET {', '.join(updates)}
                WHERE id_servicio = %s
                RETURNING id_servicio, id_usuario, id_cliente, consola, descripcion,
                          estado, costo, fecha_ingreso, fecha_entrega
            """
            cursor.execute(query, params)
            updated_servicio = cursor.fetchone()

            # Obtener datos completos
            cursor.execute(
                """
                SELECT s.*, c.nombre as nombre_cliente, c.telefono as telefono_cliente,
                       c.email as email_cliente, u.username as nombre_usuario
                FROM servicios s
                JOIN clientes c ON s.id_cliente = c.id_cliente
                JOIN usuarios u ON s.id_usuario = u.id_usuario
                WHERE s.id_servicio = %s
                """,
                (id_servicio,)
            )
            servicio_completo = cursor.fetchone()

        return {
            "success": True,
            "message": "Servicio actualizado exitosamente",
            "data": dict(servicio_completo)
        }

    @staticmethod
    def eliminar_servicio(id_servicio: int) -> dict:
        """
        Eliminar un servicio

        Args:
            id_servicio: ID del servicio a eliminar

        Returns:
            Confirmacion de eliminacion

        Raises:
            HTTPException: Si el servicio no existe
        """
        with get_db_cursor() as cursor:
            cursor.execute(
                "DELETE FROM servicios WHERE id_servicio = %s RETURNING id_servicio",
                (id_servicio,)
            )
            deleted = cursor.fetchone()

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )

        return {
            "success": True,
            "message": "Servicio eliminado exitosamente"
        }

    @staticmethod
    def obtener_servicios_pendientes() -> List[dict]:
        """
        Obtener servicios pendientes (alertas para el administrador)

        Returns:
            Lista de servicios en reparacion
        """
        return ServicioController.obtener_servicios(estado=EstadoServicio.EN_REPARACION)

    @staticmethod
    def buscar_por_cliente_o_consola(termino: str) -> List[dict]:
        """
        RF-14: Buscar servicios por nombre de cliente o tipo de consola

        Args:
            termino: Termino de busqueda

        Returns:
            Lista de servicios que coinciden
        """
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT s.id_servicio, s.id_usuario, s.id_cliente, s.consola,
                       s.descripcion, s.estado, s.costo, s.fecha_ingreso, s.fecha_entrega,
                       c.nombre as nombre_cliente, c.telefono as telefono_cliente,
                       c.email as email_cliente, u.username as nombre_usuario
                FROM servicios s
                JOIN clientes c ON s.id_cliente = c.id_cliente
                JOIN usuarios u ON s.id_usuario = u.id_usuario
                WHERE LOWER(c.nombre) LIKE LOWER(%s) OR LOWER(s.consola) LIKE LOWER(%s)
                ORDER BY s.fecha_ingreso DESC
                """,
                (f"%{termino}%", f"%{termino}%")
            )
            servicios = cursor.fetchall()

        return [dict(s) for s in servicios]
