"""
Enumeraciones de entorno - Extraído de settings.py

REFACTORED: Separando enumeraciones en módulo independiente
"""

from enum import Enum


class Environment(str, Enum):
    """Entornos disponibles"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production" 