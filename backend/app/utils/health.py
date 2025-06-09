"""
Utilidades para verificación de health check.

Este módulo contiene funciones para verificar el estado de diferentes
servicios y componentes de la aplicación ML.
"""

from typing import Any, Optional


def check_ml_model_loaded(model: Optional[Any]) -> bool:
    """
    Verificar si el modelo de machine learning está cargado.

    Esta función verifica si un modelo de ML está disponible para su uso.
    Es una verificación básica que retorna False si el modelo es None.

    Args:
        model: Modelo de machine learning a verificar. Puede ser cualquier
               objeto que represente un modelo entrenado.

    Returns:
        bool: True si el modelo está cargado (no es None), False en caso contrario.

    Example:
        >>> from sklearn.linear_model import LinearRegression
        >>> model = LinearRegression()
        >>> check_ml_model_loaded(model)
        True
        >>> check_ml_model_loaded(None)
        False
    """
    return model is not None
