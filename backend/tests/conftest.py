"""
Configuración global de pytest para el proyecto.

Fixtures compartidas y configuración de tests.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
import sys
from pathlib import Path

# Agregar el directorio app al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


@pytest.fixture
def mock_client():
    """Cliente mock para tests HTTP."""
    return Mock()


@pytest.fixture
def sample_user_data():
    """Datos de usuario de prueba."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True
    }


@pytest.fixture
def sample_health_response():
    """Respuesta de salud estándar."""
    return {
        "status": "healthy",
        "timestamp": "2024-12-07T00:00:00Z",
        "version": "1.0.0",
        "database": "connected",
        "api": "operational"
    }


@pytest.fixture
def mock_prediction_data():
    """Datos de predicción de prueba."""
    return {
        "input_features": [1.0, 2.0, 3.0, 4.0],
        "model_version": "v1.0",
        "prediction": 0.85,
        "confidence": 0.92
    }


# Configuración de pytest
def pytest_configure(config):
    """Configuración global de pytest."""
    config.addinivalue_line("markers", "unit: Tests unitarios")
    config.addinivalue_line("markers", "integration: Tests de integración")
    config.addinivalue_line("markers", "e2e: Tests end-to-end")
    config.addinivalue_line("markers", "slow: Tests lentos")
