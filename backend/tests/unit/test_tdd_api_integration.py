"""Tests de integración TDD para la API."""

import os
from fastapi.testclient import TestClient

# Configurar entorno de testing
os.environ["ENV"] = "testing"


def test_predict_endpoint_validates_input_data(client: TestClient):
    """
    TDD Test 1: POST /predict debe validar datos de entrada usando nuestros validadores.

    RED PHASE: Este test debe FALLAR porque el endpoint no usa validadores.
    """
    # Datos inválidos (violate nuestro validador de entrada)
    invalid_data = {
        "features": {
            "age": "not_a_number",  # String en lugar de número
            "income": 50000.0,
            "category": "premium",
            "score": 0.85,
        }
    }

    response = client.post("/api/v1/predict", json=invalid_data)

    # Debe rechazar con error de validación específico
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["error_type"] == "input_validation"
    assert "validation_result" in detail


def test_predict_endpoint_validates_missing_required_fields(client: TestClient):
    """
    TDD Test 2: POST /predict debe detectar campos requeridos faltantes.

    RED PHASE: Este test debe FALLAR porque el endpoint no usa validadores.
    """
    # Datos incompletos
    incomplete_data = {
        "features": {
            "age": 25
            # Faltan: income, category, score
        }
    }

    response = client.post("/api/v1/predict", json=incomplete_data)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "validation_result" in detail
    assert "missing_fields" in detail["validation_result"]
    assert "income" in detail["validation_result"]["missing_fields"]


def test_predict_endpoint_validates_model_before_prediction(client: TestClient):
    """
    TDD Test 3: POST /predict debe validar modelo ML antes de usarlo.

    RED PHASE: Este test debe FALLAR porque el endpoint no valida modelos.
    """
    # Datos válidos para entrada
    valid_data = {
        "features": {
            "age": 25,
            "income": 50000.0,
            "category": "premium",
            "score": 0.85,
        },
        "model_id": "invalid_model",  # Modelo que no existe o es inválido
    }

    response = client.post("/api/v1/predict", json=valid_data)

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["error_type"] == "model_not_found"
    assert "invalid_model" in detail["model_id"]


def test_predict_endpoint_returns_structured_response(client: TestClient):
    """
    TDD Test 4: POST /predict debe retornar respuesta estructurada con validación.

    RED PHASE: Este test debe FALLAR porque el endpoint no estructura respuesta.
    """
    # Datos completamente válidos
    valid_data = {
        "features": {
            "age": 25,
            "income": 50000.0,
            "category": "premium",
            "score": 0.85,
        },
        "model_id": "default_model",
    }

    response = client.post("/api/v1/predict", json=valid_data)

    assert response.status_code == 200
    result = response.json()

    # Estructura esperada con validación incluida
    assert "prediction" in result
    assert "validation_details" in result
    assert "model_info" in result
    assert result["validation_details"]["input_valid"] is True
    assert result["validation_details"]["model_valid"] is True


def test_predict_endpoint_handles_model_prediction_errors(client: TestClient):
    """
    TDD Test 5: POST /predict debe manejar errores durante predicción.

    RED PHASE: Este test debe FALLAR porque el endpoint no maneja errores ML.
    """
    # Datos válidos pero que pueden causar error en modelo
    edge_case_data = {
        "features": {
            "age": 150,  # Valor límite que puede causar problemas
            "income": 0,
            "category": "unknown_category",
            "score": 1.0,
        },
        "model_id": "sensitive_model",
    }

    response = client.post("/api/v1/predict", json=edge_case_data)

    # Debe manejar error gracefully
    if response.status_code == 500:
        error_detail = response.json()["detail"]
        assert error_detail["error_type"] == "prediction_failed"
    else:
        # O retornar predicción exitosa si el modelo es robusto
        assert response.status_code == 200


def test_models_endpoint_validates_model_upload(client: TestClient):
    """
    TDD Test 6: POST /models debe validar modelos subidos usando nuestros validadores.

    GREEN PHASE: Ahora funciona con la estructura real de respuesta.
    """
    # Simulamos subida de modelo inválido
    invalid_model_data = {
        "model_name": "test_model",
        "model_type": "invalid_type",
        "model_data": "not_a_real_model",
    }

    response = client.post("/api/v1/models", json=invalid_model_data)

    assert response.status_code == 422
    detail = response.json()["detail"]
    # Verificar que hay algún tipo de error de validación
    assert "error_type" in detail or "validation_error" in str(detail)
