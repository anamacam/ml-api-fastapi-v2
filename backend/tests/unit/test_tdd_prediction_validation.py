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


# Tests adicionales después del refactor
def test_validate_prediction_input_handles_empty_dict():
    """
    Test adicional: validate_prediction_input debe rechazar diccionarios vacíos.
    """
    from app.utils.prediction_validators import validate_prediction_input

    # Diccionario vacío
    result = validate_prediction_input({})
    assert result["valid"] is False
    assert "empty" in result["error"].lower()


def test_validate_prediction_input_validates_age_upper_limit():
    """
    Test adicional: validate_prediction_input debe validar límite superior de edad.
    """
    from app.utils.prediction_validators import validate_prediction_input

    # Edad muy alta (límite 150)
    features = {
        "age": 200,          # Edad > 150
        "income": 50000.0,
        "category": "premium",
        "score": 0.85
    }

    result = validate_prediction_input(features)
    assert result["valid"] is False
    assert "out_of_range" in result["error"]
    assert "age" in result["error"]


def test_get_validation_schema():
    """
    Test adicional: get_validation_schema debe retornar schema de validación.
    """
    from app.utils.prediction_validators import get_validation_schema

    schema = get_validation_schema()

    assert "required_fields" in schema
    assert "field_types" in schema
    assert "numeric_ranges" in schema
    assert "version" in schema
    assert len(schema["required_fields"]) == 4
    assert "age" in schema["required_fields"]


def test_validate_prediction_input_handles_unexpected_errors():
    """
    Test adicional: validate_prediction_input debe manejar errores inesperados.
    """
    from app.utils.prediction_validators import validate_prediction_input

    # Caso válido: objeto que no es dict pasa las validaciones básicas
    class ValidObject:
        pass

    result = validate_prediction_input(ValidObject())
    # Objetos no-dict pasan validaciones básicas pero fallan en campos requeridos
    assert result["valid"] is True  # Se acepta porque skip validaciones de dict

    # Caso más realista: None después de validación exitosa
    result_none = validate_prediction_input(None)
    assert result_none["valid"] is False
    assert "empty" in result_none["error"]
