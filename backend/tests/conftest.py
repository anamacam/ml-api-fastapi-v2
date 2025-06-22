"""
Configuración global de pytest para el proyecto.

Fixtures compartidas y configuración de tests.
"""

import os
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, Mock

import numpy as np
import pytest
from app.core.database import DatabaseConfig, DatabaseManager
from app.main import app
from fastapi.testclient import TestClient

# Agregar el directorio app al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


@pytest.fixture
def mock_client():
    """Cliente mock para tests HTTP."""
    return Mock()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """Cliente de prueba para la API que maneja el ciclo de vida."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_user_data():
    """Datos de usuario de prueba."""
    from datetime import datetime

    from app.models.user import UserStatus

    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
        "status": UserStatus.ACTIVE,
        "created_at": datetime.utcnow(),
        "hashed_password": (
            "e7fca264bc39d9a39a1b89e6ed819f9e28290be64c265c361df1967441462a4e"
        ),
    }


@pytest.fixture
def sample_health_response():
    """Respuesta de salud estándar."""
    return {
        "status": "healthy",
        "timestamp": "2024-12-07T00:00:00Z",
        "version": "1.0.0",
        "database": "connected",
        "api": "operational",
    }


@pytest.fixture
def mock_prediction_data():
    """Datos de predicción de prueba."""
    return {
        "input_features": [1.0, 2.0, 3.0, 4.0],
        "model_version": "v1.0",
        "prediction": 0.85,
        "confidence": 0.92,
    }


@pytest.fixture
def mock_ml_model():
    """Mock del modelo ML para tests."""
    mock_model = MagicMock()

    # Configurar métodos del modelo
    mock_model.predict.return_value = [0.8, 0.2]
    mock_model.predict_proba.return_value = [[0.2, 0.8]]
    mock_model.score.return_value = 0.85

    # Configurar atributos
    mock_model.feature_names_in_ = np.array(["feature1", "feature2", "feature3"])
    mock_model.n_features_in_ = 3
    mock_model.classes_ = np.array([0, 1])

    return mock_model


@pytest.fixture
def sample_prediction_data():
    """Datos de ejemplo para predicciones."""
    return {
        "features": {
            "age": 30.0,
            "income": 50000.0,
            "category": "premium",
            "score": 0.85,
        },
        "model_id": "default_model",
        "include_validation_details": True,
        "prediction_id": "pred_123456",
        "confidence": 0.85,
        "probability": [0.15, 0.85],
    }


@pytest.fixture(scope="session")
def test_db_config():
    """Configuración de la base de datos de prueba"""
    # fmt: off
    test_db_url = os.getenv(
        "TEST_DATABASE_URL",
        (
            "postgresql+asyncpg://postgres:postgres@"
            "localhost:5432/ml_api_test"
        ),
    )
    # fmt: on
    return DatabaseConfig(
        database_url=test_db_url,
        echo=True,
    )


@pytest.fixture(scope="session")
async def test_db_manager(test_db_config):
    """Manager de base de datos para tests"""
    manager = DatabaseManager(test_db_config)
    await manager.initialize()
    yield manager
    await manager.cleanup()


@pytest.fixture(scope="function")
async def test_db_session(test_db_manager):
    """Sesión de base de datos para tests"""
    async with test_db_manager.get_session() as session:
        yield session
        await session.rollback()  # Rollback después de cada test


# Configuración de pytest
def pytest_configure(config):
    """Configuración global de pytest."""
    config.addinivalue_line("markers", "unit: Tests unitarios")
    config.addinivalue_line("markers", "integration: Tests de integración")
    config.addinivalue_line("markers", "e2e: Tests end-to-end")
    config.addinivalue_line("markers", "slow: Tests lentos")
