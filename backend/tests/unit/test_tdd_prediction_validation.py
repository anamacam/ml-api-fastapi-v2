"""
TDD para validación de entrada de predicciones ML.

Tests que definen cómo debe comportarse la validación de datos
de entrada para modelos de machine learning.
"""

import pytest


def test_validate_prediction_input_rejects_empty_data():
    """
    TDD Test 1: validate_prediction_input debe rechazar datos vacíos.

    RED PHASE: Este test debe FALLAR porque la función no existe.
    """
    from app.utils.prediction_validators import validate_prediction_input

    # Datos vacíos o None
    result = validate_prediction_input(None)
    assert result["valid"] is False
    assert "error" in result
    assert "empty" in result["error"].lower()


def test_validate_prediction_input_rejects_invalid_features():
    """
    TDD Test 2: validate_prediction_input debe rechazar features inválidas.

    RED PHASE: Este test debe FALLAR porque la función no existe.
    """
    from app.utils.prediction_validators import validate_prediction_input

    # Features con tipos incorrectos
    invalid_features = {
        "age": "not_a_number",  # String instead of number
        "income": [],           # List instead of number
        "category": 123         # Number instead of string
    }
    
    result = validate_prediction_input(invalid_features)
    assert result["valid"] is False
    assert "invalid_types" in result["error"]


def test_validate_prediction_input_accepts_valid_features():
    """
    TDD Test 3: validate_prediction_input debe aceptar features válidas.

    RED PHASE: Este test debe FALLAR porque la función no existe.
    """
    from app.utils.prediction_validators import validate_prediction_input

    # Features válidas
    valid_features = {
        "age": 25,
        "income": 50000.0,
        "category": "premium",
        "score": 0.85
    }
    
    result = validate_prediction_input(valid_features)
    assert result["valid"] is True
    assert "error" not in result


def test_validate_prediction_input_handles_missing_required_fields():
    """
    TDD Test 4: validate_prediction_input debe detectar campos requeridos faltantes.

    RED PHASE: Este test debe FALLAR porque la función no existe.
    """
    from app.utils.prediction_validators import validate_prediction_input

    # Features incompletas (faltan campos requeridos)
    incomplete_features = {
        "age": 25
        # Faltan: income, category, score
    }
    
    result = validate_prediction_input(incomplete_features)
    assert result["valid"] is False
    assert "missing_fields" in result["error"]
    assert "income" in result["missing_fields"]


def test_validate_prediction_input_validates_numeric_ranges():
    """
    TDD Test 5: validate_prediction_input debe validar rangos numéricos.

    RED PHASE: Este test debe FALLAR porque la función no existe.
    """
    from app.utils.prediction_validators import validate_prediction_input

    # Features con valores fuera de rango
    out_of_range_features = {
        "age": -5,           # Edad negativa
        "income": -1000,     # Ingreso negativo
        "category": "premium",
        "score": 1.5         # Score > 1.0
    }
    
    result = validate_prediction_input(out_of_range_features)
    assert result["valid"] is False
    assert "out_of_range" in result["error"] 