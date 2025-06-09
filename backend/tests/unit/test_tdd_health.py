"""
TDD para health check - Empezando con un test que falla.
"""

import pytest


def test_check_ml_model_loaded_returns_false_when_model_is_none():
    """
    TDD Test 1: check_ml_model_loaded debe retornar False cuando el modelo es None.

    Este test debe FALLAR primero porque la función no existe.
    """
    from app.utils.health import check_ml_model_loaded

    result = check_ml_model_loaded(None)

    assert result is False


def test_check_ml_model_loaded_returns_true_when_model_exists():
    """
    TDD Test 2: check_ml_model_loaded debe retornar True cuando hay un modelo.

    Este test debe FALLAR porque nuestra implementación siempre retorna False.
    """
    from unittest.mock import MagicMock

    from app.utils.health import check_ml_model_loaded

    mock_model = MagicMock()
    result = check_ml_model_loaded(mock_model)

    assert result is True
