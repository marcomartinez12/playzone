"""
Controlador de Ventas
RF-04: Registro Ventas
RF-05: Listado de Ventas
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import HTTPException, status
from app.models.venta import VentaCreate
from app.utils.generators import generar_codigo_venta
from app.config.database import get_db_cursor


class VentaController:
    """Controlador para operaciones de ventas"""

    @staticmethod
    def crear_venta(venta: VentaCreate) -> dict:
        """
        RF-04: Crear una nueva venta y actualizar inventario

        Args:
            venta: Datos de la venta incluyendo productos

        Returns:
            Venta creada con detalles

        Raises:
            HTTPException: Si hay stock insuficiente o productos no existen
        """
        with get_db_cursor() as cursor:
            # Validar que todos los productos existen y hay stock suficiente
            for detalle in venta.productos:
                cursor.execute(
                    "SELECT id_producto, nombre, cantidad, precio FROM productos WHERE id_producto = %s",
                    (detalle.id_producto,)
                )
                producto = cursor.fetchone()

                if not producto:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Producto con ID {detalle.id_producto} no encontrado"
                    )

                if producto["cantidad"] < detalle.cantidad:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Stock insuficiente para {producto['nombre']}. Disponible: {producto['cantidad']}, Solicitado: {detalle.cantidad}"
                    )

            # Calcular total si no se proporciona
            total = venta.total
            if total is None:
                total = sum(detalle.cantidad * detalle.precio_unitario for detalle in venta.productos)

            # Insertar venta
            cursor.execute(
                """
                INSERT INTO ventas (id_usuario, id_cliente, total)
                VALUES (%s, %s, %s)
                RETURNING id_venta, id_usuario, id_cliente, total, fecha_venta
                """,
                (venta.id_usuario, venta.id_cliente, total)
            )
            nueva_venta = cursor.fetchone()
            id_venta = nueva_venta["id_venta"]

            # Insertar detalles de venta y actualizar stock
            detalles_creados = []
            for detalle in venta.productos:
                # Insertar detalle
                cursor.execute(
                    """
                    INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id_detalle, id_venta, id_producto, cantidad, precio_unitario
                    """,
                    (id_venta, detalle.id_producto, detalle.cantidad, detalle.precio_unitario)
                )
                detalle_creado = cursor.fetchone()
                detalles_creados.append(dict(detalle_creado))

                # Actualizar stock del producto
                cursor.execute(
                    """
                    UPDATE productos
                    SET cantidad = cantidad - %s
                    WHERE id_producto = %s
                    """,
                    (detalle.cantidad, detalle.id_producto)
                )

            # Obtener datos completos de la venta
            cursor.execute(
                """
                SELECT v.id_venta, v.id_usuario, v.id_cliente, v.total, v.fecha_venta,
                       c.nombre as nombre_cliente, u.username as nombre_usuario
                FROM ventas v
                JOIN clientes c ON v.id_cliente = c.id_cliente
                JOIN usuarios u ON v.id_usuario = u.id_usuario
                WHERE v.id_venta = %s
                """,
                (id_venta,)
            )
            venta_completa = cursor.fetchone()

        return {
            "success": True,
            "message": "Venta registrada exitosamente",
            "data": {
                **dict(venta_completa),
                "detalles": detalles_creados
            }
        }

    @staticmethod
    def obtener_ventas(
        fecha_inicio: Optional[datetime] = None,
        fecha_fin: Optional[datetime] = None,
        id_cliente: Optional[int] = None
    ) -> List[dict]:
        """
        RF-05: Obtener lista de ventas con filtros

        Args:
            fecha_inicio: Fecha inicial (opcional)
            fecha_fin: Fecha final (opcional)
            id_cliente: Filtrar por cliente (opcional)

        Returns:
            Lista de ventas
        """
        with get_db_cursor() as cursor:
            query = """
                SELECT v.id_venta, v.id_usuario, v.id_cliente, v.total, v.fecha_venta,
                       c.nombre as nombre_cliente, u.username as nombre_usuario,
                       COUNT(dv.id_detalle) as total_productos
                FROM ventas v
                JOIN clientes c ON v.id_cliente = c.id_cliente
                JOIN usuarios u ON v.id_usuario = u.id_usuario
                LEFT JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
                WHERE 1=1
            """
            params = []

            if fecha_inicio:
                query += " AND v.fecha_venta >= %s"
                params.append(fecha_inicio)

            if fecha_fin:
                query += " AND v.fecha_venta <= %s"
                params.append(fecha_fin)

            if id_cliente:
                query += " AND v.id_cliente = %s"
                params.append(id_cliente)

            query += " GROUP BY v.id_venta, c.nombre, u.username ORDER BY v.fecha_venta DESC"

            cursor.execute(query, params)
            ventas = cursor.fetchall()

        return [dict(v) for v in ventas]

    @staticmethod
    def obtener_venta(id_venta: int) -> dict:
        """
        Obtener una venta con sus detalles

        Args:
            id_venta: ID de la venta

        Returns:
            Datos completos de la venta

        Raises:
            HTTPException: Si la venta no existe
        """
        with get_db_cursor() as cursor:
            # Obtener venta
            cursor.execute(
                """
                SELECT v.id_venta, v.id_usuario, v.id_cliente, v.total, v.fecha_venta,
                       c.nombre as nombre_cliente, c.documento, c.telefono, c.email,
                       u.username as nombre_usuario
                FROM ventas v
                JOIN clientes c ON v.id_cliente = c.id_cliente
                JOIN usuarios u ON v.id_usuario = u.id_usuario
                WHERE v.id_venta = %s
                """,
                (id_venta,)
            )
            venta = cursor.fetchone()

            if not venta:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Venta no encontrada"
                )

            # Obtener detalles
            cursor.execute(
                """
                SELECT dv.id_detalle, dv.id_producto, dv.cantidad, dv.precio_unitario,
                       p.nombre as nombre_producto, p.codigo,
                       (dv.cantidad * dv.precio_unitario) as subtotal
                FROM detalle_ventas dv
                JOIN productos p ON dv.id_producto = p.id_producto
                WHERE dv.id_venta = %s
                """,
                (id_venta,)
            )
            detalles = cursor.fetchall()

        return {
            **dict(venta),
            "detalles": [dict(d) for d in detalles]
        }

    @staticmethod
    def obtener_ventas_diarias(fecha: Optional[date] = None) -> dict:
        """
        RF-05: Obtener reporte de ventas diarias

        Args:
            fecha: Fecha especifica (por defecto hoy)

        Returns:
            Resumen de ventas del dia
        """
        if fecha is None:
            fecha = date.today()

        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(v.id_venta) as total_ventas,
                    COALESCE(SUM(v.total), 0) as monto_total,
                    COALESCE(SUM(dv.cantidad), 0) as productos_vendidos
                FROM ventas v
                LEFT JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
                WHERE DATE(v.fecha_venta) = %s
                """,
                (fecha,)
            )
            reporte = cursor.fetchone()

        return {
            "fecha": fecha.isoformat(),
            **dict(reporte)
        }
