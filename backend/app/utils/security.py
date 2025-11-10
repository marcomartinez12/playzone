"""
Utilidades de seguridad - Hash de passwords y JWT
RF-01: Autenticacion segura
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config.settings import settings

# Contexto para hash de passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hashea una contrasena usando bcrypt

    Args:
        password: Contrasena en texto plano

    Returns:
        Hash de la contrasena
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contrasena coincide con su hash

    Args:
        plain_password: Contrasena en texto plano
        hashed_password: Hash almacenado

    Returns:
        True si coinciden, False si no
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT

    Args:
        data: Datos a codificar en el token
        expires_delta: Tiempo de expiracion (opcional)

    Returns:
        Token JWT como string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica un token JWT

    Args:
        token: Token JWT

    Returns:
        Datos decodificados o None si el token es invalido
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
