"""
TDD para integración de validadores con endpoints API.

Tests que definen cómo deben integrarse los validadores de entrada
y modelos ML con los endpoints FastAPI.

Tercer ciclo TDD: RED -> GREEN -> REFACTOR
"""

import pytest
import os
from fastapi.testclient import TestClient
import numpy as np

# Configurar entorno de testing
os.environ["ENV"] = "testing"


def test_predict_endpoint_validates_input_data():
    """
    TDD Test 1: POST /predict debe validar datos de entrada usando nuestros validadores.

    RED PHASE: Este test debe FALLAR porque el endpoint no usa validadores.
    """
    from app.main import app
    
    client = TestClient(app)
    
    # Datos inválidos (violate nuestro validador de entrada)
    invalid_data = {
        "features": {
            "age": "not_a_number",  # String en lugar de número
            "income": 50000.0,
            "category": "premium",
            "score": 0.85
        }
    }
    
    response = client.post("/api/v1/predict", json=invalid_data)
    
    # Debe rechazar con error de validación específico
    assert response.status_code == 422
    assert "validation_error" in response.json()["detail"]
    assert "invalid_types" in response.json()["detail"]


def test_predict_endpoint_validates_missing_required_fields():
    """
    TDD Test 2: POST /predict debe detectar campos requeridos faltantes.

    RED PHASE: Este test debe FALLAR porque el endpoint no usa validadores.
    """
    from app.main import app
    
    client = TestClient(app)
    
    # Datos incompletos
    incomplete_data = {
        "features": {
            "age": 25
            # Faltan: income, category, score
        }
    }
    
    response = client.post("/api/v1/predict", json=incomplete_data)
    
    assert response.status_code == 422
    assert "missing_fields" in response.json()["detail"]
    assert "income" in response.json()["detail"]["missing_fields"]


def test_predict_endpoint_validates_model_before_prediction():
    """
    TDD Test 3: POST /predict debe validar modelo ML antes de usarlo.

    RED PHASE: Este test debe FALLAR porque el endpoint no valida modelos.
    """
    from app.main import app
    
    client = TestClient(app)
    
    # Datos válidos para entrada
    valid_data = {
        "features": {
            "age": 25,
            "income": 50000.0,
            "category": "premium",
            "score": 0.85
        },
        "model_id": "invalid_model"  # Modelo que no existe o es inválido
    }
    
    response = client.post("/api/v1/predict", json=valid_data)
    
    assert response.status_code == 400
    assert "model_validation_error" in response.json()["detail"]


def test_predict_endpoint_returns_structured_response():
    """
    TDD Test 4: POST /predict debe retornar respuesta estructurada con validación.

    RED PHASE: Este test debe FALLAR porque el endpoint no estructura respuesta.
    """
    from app.main import app
    
    client = TestClient(app)
    
    # Datos completamente válidos
    valid_data = {
        "features": {
            "age": 25,
            "income": 50000.0,
            "category": "premium", 
            "score": 0.85
        },
        "model_id": "default_model"
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


def test_predict_endpoint_handles_model_prediction_errors():
    """
    TDD Test 5: POST /predict debe manejar errores durante predicción.

    RED PHASE: Este test debe FALLAR porque el endpoint no maneja errores ML.
    """
    from app.main import app
    
    client = TestClient(app)
    
    # Datos válidos pero que pueden causar error en modelo
    edge_case_data = {
        "features": {
            "age": 150,  # Valor límite que puede causar problemas
            "income": 0,
            "category": "unknown_category",
            "score": 1.0
        },
        "model_id": "sensitive_model"
    }
    
    response = client.post("/api/v1/predict", json=edge_case_data)
    
    # Debe manejar error gracefully
    if response.status_code == 500:
        error_detail = response.json()["detail"]
        assert "prediction_failed" in error_detail
    else:
        # O retornar predicción exitosa si el modelo es robusto
        assert response.status_code == 200


def test_models_endpoint_validates_model_upload():
    """
    TDD Test 6: POST /models debe validar modelos subidos usando nuestros validadores.

    RED PHASE: Este test debe FALLAR porque el endpoint no existe o no valida.
    """
    from app.main import app
    
    client = TestClient(app)
    
    # Simulamos subida de modelo inválido
    invalid_model_data = {
        "model_name": "test_model",
        "model_type": "invalid_type",
        "model_data": "not_a_real_model"
    }
    
    response = client.post("/api/v1/models", json=invalid_model_data)
    
    assert response.status_code == 422
    assert "model_validation_error" in response.json()["detail"] 