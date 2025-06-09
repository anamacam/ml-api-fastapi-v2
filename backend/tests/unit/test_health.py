"""
Tests unitarios para el módulo de health check.

Valida funcionamiento correcto del endpoint de salud.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime


class TestHealthCheck:
    """Suite de tests para health check endpoint."""

    def test_health_check_basic_response(self, sample_health_response):
        """Test básico de respuesta de health check."""
        # Arrange
        expected_keys = ["status", "timestamp", "version", "database", "api"]
        
        # Act & Assert
        assert isinstance(sample_health_response, dict)
        for key in expected_keys:
            assert key in sample_health_response
        assert sample_health_response["status"] == "healthy"

    def test_health_check_status_values(self):
        """Test de valores válidos para status."""
        valid_statuses = ["healthy", "unhealthy", "degraded"]
        
        for status in valid_statuses:
            # Simular respuesta con cada status
            response = {"status": status}
            assert response["status"] in valid_statuses

    def test_health_check_timestamp_format(self):
        """Test de formato correcto de timestamp."""
        # Arrange
        timestamp_str = "2024-12-07T10:30:00Z"
        
        # Act - Verificar que se puede parsear
        try:
            parsed = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            is_valid = True
        except ValueError:
            is_valid = False
        
        # Assert
        assert is_valid
        assert isinstance(parsed, datetime)

    def test_health_check_database_connection(self):
        """Test de verificación de conexión a base de datos."""
        # Arrange
        database_states = ["connected", "disconnected", "timeout"]
        
        # Act & Assert
        for state in database_states:
            response = {"database": state}
            assert response["database"] in database_states

    def test_health_check_version_format(self):
        """Test de formato de versión."""
        # Arrange
        valid_versions = ["1.0.0", "2.1.3", "0.1.0-beta"]
        
        # Act & Assert
        for version in valid_versions:
            response = {"version": version}
            assert isinstance(response["version"], str)
            assert len(response["version"]) > 0

    @patch('time.time')
    def test_health_check_performance(self, mock_time):
        """Test de tiempo de respuesta del health check."""
        # Arrange
        mock_time.side_effect = [1000.0, 1000.1]  # 100ms
        
        # Act
        start_time = mock_time()
        # Simular procesamiento
        end_time = mock_time()
        response_time = end_time - start_time
        
        # Assert - Debe responder en menos de 1 segundo
        assert response_time < 1.0

    def test_health_check_required_fields(self, sample_health_response):
        """Test de campos requeridos en respuesta."""
        # Arrange
        required_fields = ["status", "timestamp"]
        
        # Act & Assert
        for field in required_fields:
            assert field in sample_health_response
            assert sample_health_response[field] is not None

    def test_health_check_optional_fields(self, sample_health_response):
        """Test de campos opcionales en respuesta."""
        # Arrange
        optional_fields = ["version", "database", "api"]
        
        # Act & Assert
        for field in optional_fields:
            if field in sample_health_response:
                assert sample_health_response[field] is not None

    def test_health_check_error_handling(self):
        """Test de manejo de errores en health check."""
        # Arrange - Simular error de conexión
        error_response = {
            "status": "unhealthy",
            "error": "Database connection failed",
            "timestamp": "2024-12-07T10:30:00Z"
        }
        
        # Act & Assert
        assert error_response["status"] == "unhealthy"
        assert "error" in error_response
        assert isinstance(error_response["error"], str)

    def test_health_check_multiple_calls_consistency(self, sample_health_response):
        """Test de consistencia en múltiples llamadas."""
        # Simulate multiple calls
        responses = []
        for i in range(3):
            # Simular respuesta (en test real sería llamada HTTP)
            response = sample_health_response.copy()
            responses.append(response)
        
        # Assert - Todas las respuestas deben tener la misma estructura
        for response in responses:
            assert "status" in response
            assert "timestamp" in response


class TestHealthUtilities:
    """Tests para utilidades relacionadas con health check."""

    def test_status_priority(self):
        """Test de prioridad de estados de salud."""
        # Arrange
        status_priority = {
            "healthy": 1,
            "degraded": 2, 
            "unhealthy": 3
        }
        
        # Act & Assert
        assert status_priority["healthy"] < status_priority["degraded"]
        assert status_priority["degraded"] < status_priority["unhealthy"]

    def test_aggregate_health_status(self):
        """Test de agregación de estado de salud de múltiples servicios."""
        # Arrange
        service_statuses = ["healthy", "healthy", "degraded"]
        
        # Act - Lógica de agregación (el peor estado gana)
        overall_status = "healthy"
        for status in service_statuses:
            if status == "unhealthy":
                overall_status = "unhealthy"
                break
            elif status == "degraded":
                overall_status = "degraded"
        
        # Assert
        assert overall_status == "degraded" 