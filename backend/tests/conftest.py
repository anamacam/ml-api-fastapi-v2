"""
Configuración global de pytest para el proyecto.

Fixtures compartidas y configuración de tests.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
import sys
from pathlib import Path

from app.core.database import DatabaseConfig, DatabaseManager
import os

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


@pytest.fixture(scope="session")
def test_db_config():
    """Configuración de la base de datos de prueba"""
    return DatabaseConfig(
        database_url=os.getenv(
            "TEST_DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/ml_api_test"
        ),
        echo=True
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
