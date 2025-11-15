"""
Utilidades de Validación y Sanitización
Previene inyecciones SQL, XSS y otros ataques
"""
import re
import html
from typing import Optional, Any
from fastapi import HTTPException, status


class InputValidator:
    """Validador y sanitizador de inputs"""

    # Patrones peligrosos
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bCREATE\b.*\bTABLE\b)",
        r"(--)",
        r"(;.*)",
        r"(\bOR\b.*=.*)",
        r"('.*OR.*'=')",
    ]

    XSS_PATTERNS = [
        r"<script[^>]*>.*</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
        r"<iframe",
        r"<embed",
        r"<object",
    ]

    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitiza un string eliminando caracteres peligrosos

        Args:
            value: String a sanitizar
            max_length: Longitud máxima permitida

        Returns:
            String sanitizado
        """
        if not isinstance(value, str):
            return str(value)

        # Eliminar espacios en blanco al inicio y fin
        value = value.strip()

        # HTML escape para prevenir XSS
        value = html.escape(value)

        # Limitar longitud
        if max_length and len(value) > max_length:
            value = value[:max_length]

        return value

    @staticmethod
    def validate_no_sql_injection(value: str) -> bool:
        """
        Valida que un string no contenga patrones de SQL injection

        Args:
            value: String a validar

        Returns:
            True si es seguro, False si contiene patrones peligrosos
        """
        if not isinstance(value, str):
            return True

        value_upper = value.upper()

        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return False

        return True

    @staticmethod
    def validate_no_xss(value: str) -> bool:
        """
        Valida que un string no contenga patrones de XSS

        Args:
            value: String a validar

        Returns:
            True si es seguro, False si contiene patrones peligrosos
        """
        if not isinstance(value, str):
            return True

        for pattern in InputValidator.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return False

        return True

    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Valida un nombre de usuario

        Reglas:
        - Solo letras, números, guiones y guiones bajos
        - Entre 3 y 50 caracteres
        - No puede comenzar con número

        Args:
            username: Nombre de usuario a validar

        Returns:
            True si es válido
        """
        if not username or len(username) < 3 or len(username) > 50:
            return False

        pattern = r"^[a-zA-Z][a-zA-Z0-9_-]{2,49}$"
        return bool(re.match(pattern, username))

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valida un email

        Args:
            email: Email a validar

        Returns:
            True si es válido
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
        """
        Valida la fortaleza de una contraseña

        Requisitos:
        - Mínimo 8 caracteres
        - Al menos una mayúscula
        - Al menos una minúscula
        - Al menos un número
        - Al menos un carácter especial (opcional pero recomendado)

        Args:
            password: Contraseña a validar

        Returns:
            Tuple (valido: bool, mensaje_error: str)
        """
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"

        if not re.search(r"[a-z]", password):
            return False, "La contraseña debe contener al menos una letra minúscula"

        if not re.search(r"[A-Z]", password):
            return False, "La contraseña debe contener al menos una letra mayúscula"

        if not re.search(r"\d", password):
            return False, "La contraseña debe contener al menos un número"

        # Opcional: verificar carácter especial
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=]", password):
            return False, "La contraseña debe contener al menos un carácter especial (!@#$%^&*(),.?\":{}|<>_-+=)"

        return True, None

    @staticmethod
    def sanitize_search_query(query: str) -> str:
        """
        Sanitiza una consulta de búsqueda

        Args:
            query: Consulta a sanitizar

        Returns:
            Consulta sanitizada
        """
        # Eliminar caracteres peligrosos
        query = re.sub(r"[;'\"\-\-]", "", query)

        # Limitar longitud
        query = query[:100]

        # Eliminar espacios múltiples
        query = re.sub(r"\s+", " ", query)

        return query.strip()

    @staticmethod
    def validate_numeric_id(value: Any, min_value: int = 1) -> bool:
        """
        Valida que un ID sea un número entero positivo

        Args:
            value: Valor a validar
            min_value: Valor mínimo permitido

        Returns:
            True si es válido
        """
        try:
            num = int(value)
            return num >= min_value
        except (ValueError, TypeError):
            return False

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitiza un nombre de archivo

        Args:
            filename: Nombre de archivo a sanitizar

        Returns:
            Nombre de archivo seguro
        """
        # Eliminar caracteres peligrosos
        filename = re.sub(r'[<>:"/\\|?*]', "", filename)

        # Eliminar puntos al inicio (prevenir directory traversal)
        filename = filename.lstrip(".")

        # Limitar longitud
        filename = filename[:255]

        return filename

    @staticmethod
    def validate_and_sanitize(
        value: str,
        field_name: str,
        max_length: Optional[int] = None,
        check_sql: bool = True,
        check_xss: bool = True
    ) -> str:
        """
        Valida y sanitiza un valor completo

        Args:
            value: Valor a procesar
            field_name: Nombre del campo (para mensajes de error)
            max_length: Longitud máxima
            check_sql: Verificar SQL injection
            check_xss: Verificar XSS

        Returns:
            Valor sanitizado

        Raises:
            HTTPException: Si la validación falla
        """
        # Sanitizar
        sanitized = InputValidator.sanitize_string(value, max_length)

        # Validar SQL injection
        if check_sql and not InputValidator.validate_no_sql_injection(sanitized):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El campo '{field_name}' contiene caracteres no permitidos"
            )

        # Validar XSS
        if check_xss and not InputValidator.validate_no_xss(sanitized):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El campo '{field_name}' contiene contenido no permitido"
            )

        return sanitized


# Decorador para validar inputs automáticamente
def validate_input(**validators):
    """
    Decorador para validar inputs de funciones

    Ejemplo:
        @validate_input(username=InputValidator.validate_username, email=InputValidator.validate_email)
        def crear_usuario(username: str, email: str):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for field, validator in validators.items():
                if field in kwargs:
                    if not validator(kwargs[field]):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"El campo '{field}' no es válido"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator
