"""
Controlador de Clientes
RF-07: Datos Basicos Clientes
"""
from typing import List, Optional
from fastapi import HTTPException, status
from app.models.cliente import ClienteCreate, ClienteUpdate
from app.config.database import get_db_cursor


class ClienteController:
    """Controlador para operaciones de clientes"""

    @staticmethod
    def crear_cliente(cliente: ClienteCreate) -> dict:
        """
        RF-07: Crear un nuevo cliente

        Args:
            cliente: Datos del cliente a crear

        Returns:
            Cliente creado

        Raises:
            HTTPException: Si el documento ya esta registrado
        """
        with get_db_cursor() as cursor:
            # Verificar si ya existe un cliente con ese documento
            cursor.execute(
                "SELECT id_cliente FROM clientes WHERE documento = %s",
                (cliente.documento,)
            )
            existing = cursor.fetchone()

            if existing:
                # Actualizar datos del cliente existente si vienen nuevos valores
                updates = []
                params = []

                if cliente.nombre:
                    updates.append("nombre = %s")
                    params.append(cliente.nombre)

                if cliente.telefono:
                    updates.append("telefono = %s")
                    params.append(cliente.telefono)

                if cliente.email:
                    updates.append("email = %s")
                    params.append(cliente.email)

                # Si hay algo que actualizar, hacerlo
                if updates:
                    params.append(cliente.documento)
                    cursor.execute(
                        f"""
                        UPDATE clientes
                        SET {', '.join(updates)}
                        WHERE documento = %s
                        RETURNING id_cliente, nombre, documento, telefono, email, fecha_registro
                        """,
                        params
                    )
                    updated_cliente = cursor.fetchone()
                    return {
                        "success": True,
                        "message": "Cliente actualizado",
                        "id_cliente": updated_cliente["id_cliente"],
                        "data": dict(updated_cliente)
                    }

                # Si no hay nada que actualizar, retornar el existente
                cursor.execute(
                    """
                    SELECT id_cliente, nombre, documento, telefono, email, fecha_registro
                    FROM clientes
                    WHERE documento = %s
                    """,
                    (cliente.documento,)
                )
                existing_cliente = cursor.fetchone()
                return {
                    "success": True,
                    "message": "Cliente ya existe",
                    "id_cliente": existing_cliente["id_cliente"],
                    "data": dict(existing_cliente)
                }

            # Insertar nuevo cliente
            cursor.execute(
                """
                INSERT INTO clientes (nombre, documento, telefono, email)
                VALUES (%s, %s, %s, %s)
                RETURNING id_cliente, nombre, documento, telefono, email, fecha_registro
                """,
                (cliente.nombre, cliente.documento, cliente.telefono, cliente.email)
            )
            new_cliente = cursor.fetchone()

        return {
            "success": True,
            "message": "Cliente registrado exitosamente",
            "id_cliente": new_cliente["id_cliente"],
            "data": dict(new_cliente)
        }

    @staticmethod
    def obtener_clientes(busqueda: Optional[str] = None) -> List[dict]:
        """
        Obtener lista de clientes con busqueda opcional

        Args:
            busqueda: Buscar por nombre o documento (opcional)

        Returns:
            Lista de clientes
        """
        with get_db_cursor() as cursor:
            query = """
                SELECT c.id_cliente, c.nombre, c.documento, c.telefono, c.email, c.fecha_registro,
                       COUNT(DISTINCT v.id_venta) as total_compras,
                       COUNT(DISTINCT s.id_servicio) as total_servicios
                FROM clientes c
                LEFT JOIN ventas v ON c.id_cliente = v.id_cliente
                LEFT JOIN servicios s ON c.id_cliente = s.id_cliente
                WHERE 1=1
            """
            params = []

            if busqueda:
                query += " AND (LOWER(c.nombre) LIKE LOWER(%s) OR c.documento LIKE %s)"
                params.extend([f"%{busqueda}%", f"%{busqueda}%"])

            query += " GROUP BY c.id_cliente ORDER BY c.fecha_registro DESC"

            cursor.execute(query, params)
            clientes = cursor.fetchall()

        return [dict(c) for c in clientes]

    @staticmethod
    def buscar_por_documento(documento: str) -> dict:
        """
        Buscar un cliente por su número de documento

        Args:
            documento: Número de documento del cliente

        Returns:
            Datos del cliente o mensaje indicando que no existe
        """
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id_cliente, nombre, documento, telefono, email, fecha_registro
                FROM clientes
                WHERE documento = %s
                """,
                (documento,)
            )
            cliente = cursor.fetchone()

        if not cliente:
            return {
                "success": False,
                "message": "Cliente no encontrado",
                "cliente": None
            }

        return {
            "success": True,
            "message": "Cliente encontrado",
            "cliente": dict(cliente)
        }

    @staticmethod
    def obtener_cliente(id_cliente: int) -> dict:
        """
        Obtener un cliente por ID

        Args:
            id_cliente: ID del cliente

        Returns:
            Datos del cliente

        Raises:
            HTTPException: Si el cliente no existe
        """
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT c.id_cliente, c.nombre, c.documento, c.telefono, c.email, c.fecha_registro,
                       COUNT(DISTINCT v.id_venta) as total_compras,
                       COUNT(DISTINCT s.id_servicio) as total_servicios
                FROM clientes c
                LEFT JOIN ventas v ON c.id_cliente = v.id_cliente
                LEFT JOIN servicios s ON c.id_cliente = s.id_cliente
                WHERE c.id_cliente = %s
                GROUP BY c.id_cliente
                """,
                (id_cliente,)
            )
            cliente = cursor.fetchone()

        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado"
            )

        return dict(cliente)

    @staticmethod
    def actualizar_cliente(id_cliente: int, cliente: ClienteUpdate) -> dict:
        """
        Actualizar un cliente existente

        Args:
            id_cliente: ID del cliente a actualizar
            cliente: Datos a actualizar

        Returns:
            Cliente actualizado

        Raises:
            HTTPException: Si el cliente no existe
        """
        # Verificar que el cliente existe
        ClienteController.obtener_cliente(id_cliente)

        # Construir query dinamica
        updates = []
        params = []

        if cliente.nombre is not None:
            updates.append("nombre = %s")
            params.append(cliente.nombre)

        if cliente.documento is not None:
            updates.append("documento = %s")
            params.append(cliente.documento)

        if cliente.telefono is not None:
            updates.append("telefono = %s")
            params.append(cliente.telefono)

        if cliente.email is not None:
            updates.append("email = %s")
            params.append(cliente.email)

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar"
            )

        params.append(id_cliente)

        with get_db_cursor() as cursor:
            query = f"""
                UPDATE clientes
                SET {', '.join(updates)}
                WHERE id_cliente = %s
                RETURNING id_cliente, nombre, documento, telefono, email, fecha_registro
            """
            cursor.execute(query, params)
            updated_cliente = cursor.fetchone()

        return {
            "success": True,
            "message": "Cliente actualizado exitosamente",
            "data": dict(updated_cliente)
        }

    @staticmethod
    def eliminar_cliente(id_cliente: int) -> dict:
        """
        Eliminar un cliente

        Args:
            id_cliente: ID del cliente a eliminar

        Returns:
            Confirmacion de eliminacion

        Raises:
            HTTPException: Si el cliente no existe o tiene ventas/servicios asociados
        """
        with get_db_cursor() as cursor:
            # Verificar si tiene ventas o servicios asociados
            cursor.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM ventas WHERE id_cliente = %s) as ventas,
                    (SELECT COUNT(*) FROM servicios WHERE id_cliente = %s) as servicios
                """,
                (id_cliente, id_cliente)
            )
            result = cursor.fetchone()

            if result["ventas"] > 0 or result["servicios"] > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede eliminar el cliente porque tiene ventas o servicios asociados"
                )

            # Eliminar cliente
            cursor.execute(
                "DELETE FROM clientes WHERE id_cliente = %s RETURNING id_cliente",
                (id_cliente,)
            )
            deleted = cursor.fetchone()

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado"
            )

        return {
            "success": True,
            "message": "Cliente eliminado exitosamente"
        }
