"""
TDD Ciclo 4: Configuración por Entornos Robusta

Tests que definen el comportamiento esperado para:
- Validación de configuración
- Comportamiento por entorno
- Manejo de errores
- Fallbacks seguros

FASE RED → GREEN → REFACTOR
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

# Configurar entorno de testing antes de imports
os.environ["ENV"] = "testing"

def test_configuration_validates_required_environment_variables():
    """
    TDD Test 1: La configuración debe validar variables de entorno requeridas.
    
    RED PHASE: Este test debe FALLAR porque no validamos variables críticas.
    """
    from app.config.settings import Settings
    
    # Simular entorno sin variables críticas
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            # Debe fallar si falta SECRET_KEY en producción
            Settings(environment="production")
        
        assert "secret_key" in str(exc_info.value)


def test_testing_environment_never_uses_real_models():
    """
    TDD Test 2: El entorno TESTING debe SIEMPRE usar mocks, sin excepciones.
    
    GREEN PHASE (REFACTORED): Ahora funciona con Strategy Pattern.
    """
    from app.config.settings import Settings
    import pytest
    
    # Incluso si explícitamente se pide usar modelos reales, debe fallar
    with pytest.raises(ValueError) as exc_info:
        Settings(environment="testing", use_real_models=True)
    
    assert "Testing environment must never use real models" in str(exc_info.value)
    
    # Verificar que con False funciona correctamente
    config = Settings(environment="testing", use_real_models=False)
    assert config.should_use_real_models is False
    assert config.is_testing is True


def test_invalid_environment_raises_validation_error():
    """
    TDD Test 3: Entornos inválidos deben provocar error de validación.
    
    RED PHASE: Este test debe FALLAR porque no validamos entornos permitidos.
    """
    from app.config.settings import Settings
    
    with pytest.raises(ValueError) as exc_info:
        Settings(environment="invalid_environment")
    
    assert "invalid_environment" in str(exc_info.value)


def test_env_file_loading_handles_missing_files_gracefully():
    """
    TDD Test 4: Archivos .env faltantes deben manejarse gracefully.
    
    RED PHASE: Este test debe FALLAR porque no manejamos archivos faltantes.
    """
    from app.config.settings import Settings
    
    # Simular archivo .env inexistente
    with patch("pathlib.Path.exists", return_value=False):
        # No debe explotar, debe usar valores por defecto
        config = Settings()
        
        # Debe cargar configuración por defecto
        assert config.environment is not None
        assert config.debug is not None


def test_production_environment_enforces_security_requirements():
    """
    TDD Test 5: Producción debe exigir configuraciones de seguridad.
    
    RED PHASE: Este test debe FALLAR porque no validamos seguridad en producción.
    """
    from app.config.settings import Settings
    
    with pytest.raises(ValueError) as exc_info:
        # Producción con configuración insegura debe fallar
        Settings(
            environment="production",
            secret_key="dev-secret-key-change-in-production",  # Valor por defecto inseguro
            debug=True  # Debug activado en producción = inseguro
        )
    
    assert "production" in str(exc_info.value).lower()
    assert any(word in str(exc_info.value).lower() for word in ["secret", "debug", "security"])


def test_configuration_provides_safe_fallbacks():
    """
    TDD Test 6: La configuración debe proveer fallbacks seguros.
    
    RED PHASE: Este test debe FALLAR porque no implementamos fallbacks.
    """
    from app.config.settings import Settings
    
    # Simular configuración corrupta
    with patch.dict(os.environ, {"USE_REAL_MODELS": "maybe_yes_maybe_no"}, clear=True):
        config = Settings()
        
        # Debe usar fallback seguro (False para testing)
        assert isinstance(config.use_real_models, bool)
        assert config.use_real_models in [True, False]  # Valor booleano válido


def test_models_path_validation_prevents_dangerous_paths():
    """
    TDD Test 7: Los paths de modelos deben validarse para prevenir ataques.
    
    RED PHASE: Este test debe FALLAR porque no validamos paths peligrosos.
    """
    from app.config.settings import Settings
    
    dangerous_paths = [
        "../../etc/passwd",
        "/etc/shadow", 
        "C:\\Windows\\System32",
        "../../../../../secrets"
    ]
    
    for dangerous_path in dangerous_paths:
        with pytest.raises(ValueError) as exc_info:
            Settings(ml_models_path=dangerous_path)
        
        assert "path" in str(exc_info.value).lower()


def test_configuration_logs_security_warnings():
    """
    TDD Test 8: La configuración debe loggear advertencias de seguridad.
    
    RED PHASE: Este test debe FALLAR porque no loggeamos advertencias.
    """
    import logging
    from app.config.settings import Settings
    
    with patch('app.config.settings.logger') as mock_logger:
        # Configuración con valores por defecto potencialmente inseguros
        Settings(environment="development")
        
        # Debe haber advertencias sobre configuración por defecto
        mock_logger.warning.assert_called()
        warning_calls = [call[0][0] for call in mock_logger.warning.call_args_list]
        
        # Al menos una advertencia debe mencionar configuración por defecto
        assert any("default" in warning.lower() for warning in warning_calls)


def test_environment_specific_validation_rules():
    """
    TDD Test 9: Cada entorno debe tener reglas de validación específicas.
    
    GREEN PHASE (REFACTORED): Ahora funciona con Strategy Pattern por entorno.
    """
    from app.config.settings import Settings
    
    # Development: Debe permitir debug=True
    dev_config = Settings(environment="development", debug=True)
    assert dev_config.debug is True
    
    # Production: Debe rechazar debug=True  
    with pytest.raises(ValueError):
        Settings(environment="production", debug=True)
    
    # Testing: Debe rechazar use_real_models=True
    with pytest.raises(ValueError) as exc_info:
        Settings(environment="testing", use_real_models=True)
    
    assert "Testing environment must never use real models" in str(exc_info.value)
    
    # Testing: Debe permitir use_real_models=False
    test_config = Settings(environment="testing", use_real_models=False)
    assert test_config.should_use_real_models is False


def test_configuration_immutability_after_creation():
    """
    TDD Test 10: La configuración debe ser inmutable después de creación.
    
    RED PHASE: Este test debe FALLAR porque no implementamos inmutabilidad.
    """
    from app.config.settings import Settings
    
    config = Settings()
    
    # Intentar modificar después de creación debe fallar
    with pytest.raises(Exception):  # Puede ser AttributeError, TypeError, etc.
        config.environment = "hacked"
    
    with pytest.raises(Exception):
        config.secret_key = "compromised" 