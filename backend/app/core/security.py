"""
🔐 SECURITY MODULE - Stub mínimo para TDD Database Module

Funciones básicas de seguridad para hashing de passwords.
"""

import hashlib


def get_password_hash(password: str) -> str:
    """
    Generar hash de password (implementación simple para pruebas)
    
    Args:
        password: Password en texto plano
        
    Returns:
        str: Hash del password
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar password contra hash
    
    Args:
        plain_password: Password en texto plano
        hashed_password: Hash del password
        
    Returns:
        bool: True si coinciden
    """
    return get_password_hash(plain_password) == hashed_password 