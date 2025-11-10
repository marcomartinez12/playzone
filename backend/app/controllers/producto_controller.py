"""
Controlador de Productos
RF-02: Registro de productos
RF-03: Actualizacion de productos
RF-08: Tablero Inicial
RF-09: Filtrado de productos
RF-10: Busqueda Especifica de productos
RF-11: Alertas visuales por bajo stock
"""
from typing import List, Optional
from fastapi import HTTPException, status
from app.models.producto import ProductoCreate, ProductoUpdate, ProductoResponse
from app.utils.generators import generar_codigo_producto
from app.config.database import get_db_cursor


class ProductoController:
    """Controlador para operaciones de productos"""

    STOCK_MINIMO = 5  # RF-11: Umbral para alerta de stock bajo

    @staticmethod
    def crear_producto(producto: ProductoCreate) -> dict:
        """
        RF-02: Crear un nuevo producto en el inventario

        Args:
            producto: Datos del producto a crear

        Returns:
            Producto creado con codigo autogenerado

        Raises:
            HTTPException: Si hay error en la creacion
        """
        # Generar codigo unico
        codigo = generar_codigo_producto(producto.categoria.value)

        with get_db_cursor() as cursor:
            # Verificar si ya existe un producto con el mismo nombre
            cursor.execute(
                "SELECT id_producto FROM productos WHERE LOWER(nombre) = LOWER(%s)",
                (producto.nombre,)
            )
            existing = cursor.fetchone()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un producto con ese nombre"
                )

            # Insertar producto
            cursor.execute(
                """
                INSERT INTO productos (codigo, nombre, categoria, precio, cantidad, descripcion, imagen_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id_producto, codigo, nombre, categoria, precio, cantidad, descripcion, imagen_url, fecha_registro
                """,
                (codigo, producto.nombre, producto.categoria.value, producto.precio,
                 producto.cantidad, producto.descripcion, producto.imagen_url)
            )
            new_producto = cursor.fetchone()

        return {
            "success": True,
            "message": "Producto registrado exitosamente",
            "data": dict(new_producto)
        }

    @staticmethod
    def obtener_productos(
        categoria: Optional[str] = None,
        busqueda: Optional[str] = None,
        stock_bajo: bool = False
    ) -> List[dict]:
        """
        RF-08, RF-09, RF-10, RF-11: Obtener lista de productos con filtros

        Args:
            categoria: Filtrar por categoria (opcional)
            busqueda: Busqueda por nombre (opcional)
            stock_bajo: Solo productos con stock bajo (opcional)

        Returns:
            Lista de productos
        """
        with get_db_cursor() as cursor:
            query = """
                SELECT id_producto, codigo, nombre, categoria, precio, cantidad,
                       descripcion, imagen_url, fecha_registro,
                       CASE WHEN cantidad <= %s THEN true ELSE false END as stock_bajo
                FROM productos
                WHERE 1=1
            """
            params = [ProductoController.STOCK_MINIMO]

            # RF-09: Filtrar por categoria
            if categoria:
                query += " AND categoria = %s"
                params.append(categoria)

            # RF-10: Busqueda especifica por nombre
            if busqueda:
                query += " AND LOWER(nombre) LIKE LOWER(%s)"
                params.append(f"%{busqueda}%")

            # RF-11: Filtrar solo stock bajo
            if stock_bajo:
                query += f" AND cantidad <= %s"
                params.append(ProductoController.STOCK_MINIMO)

            query += " ORDER BY fecha_registro DESC"

            cursor.execute(query, params)
            productos = cursor.fetchall()

        return [dict(p) for p in productos]

    @staticmethod
    def obtener_producto(id_producto: int) -> dict:
        """
        Obtener un producto por ID

        Args:
            id_producto: ID del producto

        Returns:
            Datos del producto

        Raises:
            HTTPException: Si el producto no existe
        """
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id_producto, codigo, nombre, categoria, precio, cantidad,
                       descripcion, imagen_url, fecha_registro,
                       CASE WHEN cantidad <= %s THEN true ELSE false END as stock_bajo
                FROM productos
                WHERE id_producto = %s
                """,
                (ProductoController.STOCK_MINIMO, id_producto)
            )
            producto = cursor.fetchone()

        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )

        return dict(producto)

    @staticmethod
    def actualizar_producto(id_producto: int, producto: ProductoUpdate) -> dict:
        """
        RF-03: Actualizar un producto existente

        Args:
            id_producto: ID del producto a actualizar
            producto: Datos a actualizar

        Returns:
            Producto actualizado

        Raises:
            HTTPException: Si el producto no existe
        """
        # Verificar que el producto existe
        ProductoController.obtener_producto(id_producto)

        # Construir query dinamica solo con campos presentes
        updates = []
        params = []

        if producto.nombre is not None:
            updates.append("nombre = %s")
            params.append(producto.nombre)

        if producto.categoria is not None:
            updates.append("categoria = %s")
            params.append(producto.categoria.value)

        if producto.precio is not None:
            updates.append("precio = %s")
            params.append(producto.precio)

        if producto.cantidad is not None:
            updates.append("cantidad = %s")
            params.append(producto.cantidad)

        if producto.descripcion is not None:
            updates.append("descripcion = %s")
            params.append(producto.descripcion)

        if producto.imagen_url is not None:
            updates.append("imagen_url = %s")
            params.append(producto.imagen_url)

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar"
            )

        params.append(id_producto)

        with get_db_cursor() as cursor:
            query = f"""
                UPDATE productos
                SET {', '.join(updates)}
                WHERE id_producto = %s
                RETURNING id_producto, codigo, nombre, categoria, precio, cantidad,
                          descripcion, imagen_url, fecha_registro
            """
            cursor.execute(query, params)
            updated_producto = cursor.fetchone()

        return {
            "success": True,
            "message": "Producto actualizado exitosamente",
            "data": dict(updated_producto)
        }

    @staticmethod
    def eliminar_producto(id_producto: int) -> dict:
        """
        RF-03: Eliminar un producto del inventario

        Args:
            id_producto: ID del producto a eliminar

        Returns:
            Confirmacion de eliminacion

        Raises:
            HTTPException: Si el producto no existe o tiene ventas asociadas
        """
        with get_db_cursor() as cursor:
            # Verificar si el producto tiene ventas asociadas
            cursor.execute(
                "SELECT COUNT(*) as count FROM detalle_ventas WHERE id_producto = %s",
                (id_producto,)
            )
            result = cursor.fetchone()

            if result["count"] > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede eliminar el producto porque tiene ventas asociadas"
                )

            # Eliminar producto
            cursor.execute(
                "DELETE FROM productos WHERE id_producto = %s RETURNING id_producto",
                (id_producto,)
            )
            deleted = cursor.fetchone()

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )

        return {
            "success": True,
            "message": "Producto eliminado exitosamente"
        }

    @staticmethod
    def obtener_productos_stock_bajo() -> List[dict]:
        """
        RF-11: Obtener productos con stock bajo para alertas

        Returns:
            Lista de productos con stock bajo
        """
        return ProductoController.obtener_productos(stock_bajo=True)
