"""
Generadores de codigos y utilidades
RF-02: Codigo autogenerado para productos
"""
import random
import string
from datetime import datetime


def generar_codigo_producto(categoria: str) -> str:
    """
    Genera un codigo unico para un producto
    Formato: CAT-YYYYMMDD-XXXX
    Ejemplo: VJ-20250105-A3F2

    Args:
        categoria: Categoria del producto (videojuego, consola, accesorio)

    Returns:
        Codigo unico generado
    """
    # Prefijo segun categoria
    prefijos = {
        "videojuego": "VJ",
        "consola": "CS",
        "accesorio": "AC"
    }

    prefijo = prefijos.get(categoria.lower(), "PR")
    fecha = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

    return f"{prefijo}-{fecha}-{random_part}"


def generar_codigo_venta() -> str:
    """
    Genera un codigo unico para una venta
    Formato: VT-YYYYMMDD-HHMMSS-XXX
    Ejemplo: VT-20250105-143022-A4B

    Returns:
        Codigo de venta unico
    """
    fecha_hora = datetime.now().strftime("%Y%m%d-%H%M%S")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))

    return f"VT-{fecha_hora}-{random_part}"


def generar_codigo_servicio() -> str:
    """
    Genera un codigo unico para un servicio de reparacion
    Formato: SR-YYYYMMDD-XXX
    Ejemplo: SR-20250105-F7G

    Returns:
        Codigo de servicio unico
    """
    fecha = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))

    return f"SR-{fecha}-{random_part}"
