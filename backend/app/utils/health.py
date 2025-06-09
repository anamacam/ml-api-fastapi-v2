"""
Utilidades para verificación de health check.

Este módulo contiene funciones para verificar el estado de diferentes
servicios y componentes de la aplicación ML.

Incluye verificaciones para:
- Modelos de machine learning
- Conexiones de base de datos
- Otros componentes críticos del sistema

Author: ML API Team
Version: 1.0.0
"""

import logging
from typing import Any, Optional, Union

# Configurar logger específico para health checks
logger = logging.getLogger(__name__)

# Tipos específicos para mejor tipado
ModelType = Union[Any, None]
ConnectionType = Union[Any, None]


def check_ml_model_loaded(model: ModelType) -> bool:
    """
    Verificar si el modelo de machine learning está cargado y disponible.

    Esta función realiza una verificación básica de disponibilidad del modelo.
    Es una verificación no intrusiva que solo verifica si el objeto existe.

    Args:
        model: Modelo de machine learning a verificar. Puede ser cualquier
               objeto que represente un modelo entrenado (sklearn, tensorflow,
               pytorch, etc.).

    Returns:
        bool: True si el modelo está cargado (no es None), False en caso contrario.

    Raises:
        No levanta excepciones. Maneja todos los casos gracefully.

    Example:
        >>> from sklearn.linear_model import LinearRegression
        >>> model = LinearRegression()
        >>> check_ml_model_loaded(model)
        True
        >>> check_ml_model_loaded(None)
        False

    Note:
        Esta función NO verifica la validez interna del modelo,
        solo su existencia como objeto en memoria.
    """
    try:
        result = model is not None
        logger.debug(f"Model check result: {result}")
        return result
    except Exception as e:
        logger.warning(f"Error checking model: {e}")
        return False


def check_database_connection(connection: ConnectionType) -> bool:
    """
    Verificar si la conexión a la base de datos está activa y disponible.

    Esta función realiza una verificación básica de disponibilidad de la conexión.
    Es una verificación no intrusiva que solo verifica si el objeto de conexión existe.

    Args:
        connection: Conexión a la base de datos a verificar. Puede ser cualquier
                   objeto que represente una conexión activa (sqlite3, pymongo,
                   sqlalchemy, psycopg2, etc.).

    Returns:
        bool: True si la conexión está disponible (no es None), False en caso contrario.

    Raises:
        No levanta excepciones. Maneja todos los casos gracefully.

    Example:
        >>> import sqlite3
        >>> conn = sqlite3.connect(':memory:')
        >>> check_database_connection(conn)
        True
        >>> check_database_connection(None)
        False

    Note:
        Esta función NO ejecuta queries ni verifica la conectividad real,
        solo la existencia del objeto de conexión en memoria.
    """
    try:
        result = connection is not None
        logger.debug(f"Database connection check result: {result}")
        return result
    except Exception as e:
        logger.warning(f"Error checking database connection: {e}")
        return False


# Función helper para configurar logging si es necesario
def check_api_endpoints(endpoints: Optional[list]) -> bool:
    """
    Verificar si hay endpoints API disponibles.

    Función refactorizada que verifica la disponibilidad de endpoints API
    con validaciones mejoradas y manejo robusto de errores.

    Args:
        endpoints: Lista de endpoints a verificar. Puede ser None.

    Returns:
        bool: True si hay endpoints válidos disponibles, False en caso contrario.

    Raises:
        No levanta excepciones. Maneja todos los casos gracefully.

    Example:
        >>> check_api_endpoints([])
        False
        >>> check_api_endpoints(['/health', '/predict'])
        True
        >>> check_api_endpoints(None)
        False

    Note:
        Refactorizado desde implementación TDD para mayor robustez.
        Valida tanto existencia como contenido de endpoints.
    """
    try:
        # Validación explícita de None
        if endpoints is None:
            logger.debug("Endpoints list is None")
            return False

        # Validación de tipo
        if not isinstance(endpoints, list):
            logger.warning(f"Expected list, got {type(endpoints)}")
            return False

        # Verificación de contenido
        has_endpoints = len(endpoints) > 0

        # Log detallado para debugging
        if has_endpoints:
            logger.debug(f"Found {len(endpoints)} endpoints: {endpoints[:3]}...")
        else:
            logger.debug("No endpoints found in list")

        return has_endpoints

    except Exception as e:
        logger.error(f"Unexpected error checking API endpoints: {e}")
        return False


def configure_health_logging(level: int = logging.INFO) -> None:
    """
    Configurar el logging para el módulo health.

    Args:
        level: Nivel de logging (default: INFO).
    """
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
