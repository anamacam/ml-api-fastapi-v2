"""
Logger de seguridad - Extraído de settings.py

REFACTORED: Separando logging de seguridad en módulo independiente
- Advertencias de seguridad centralizadas
- Eventos de seguridad estructurados
"""

import logging
from typing import Dict, Any

from app.core.security_logger import (
    SecurityEventFactory,
    SecurityLevel,
    get_security_logger,
)
from .environment import Environment

logger = logging.getLogger(__name__)


class SecurityLogger:
    """Logger centralizado para advertencias de seguridad"""

    @staticmethod
    def log_security_warnings(settings_instance) -> None:
        """
        Loggear advertencias de seguridad usando el sistema avanzado
        REFACTORED: Centralizado y usando el sistema de logging de seguridad
        """
        security_logger = get_security_logger()

        # Advertencia sobre secret key por defecto
        SecurityLogger._log_default_secret_key_warning(
            settings_instance, security_logger
        )

        # Advertencia sobre debug en no-desarrollo
        SecurityLogger._log_debug_mode_warning(settings_instance, security_logger)

        # Advertencia sobre modelos reales en testing
        SecurityLogger._log_real_models_warning(settings_instance, security_logger)

    @staticmethod
    def _log_default_secret_key_warning(settings_instance, security_logger):
        """Loggear advertencia sobre secret key por defecto"""
        if settings_instance.secret_key == "dev-secret-key-change-in-production":
            warning_event = SecurityEventFactory.create_threat_event(
                threat_type="default_secret_key",
                severity=SecurityLevel.HIGH,
                details={
                    "config_key": "secret_key",
                    "current_value": "dev-secret-key-change-in-production",
                    "recommendation": "Change secret key in production environment",
                },
            )
            security_logger.log_event(warning_event)
            logger.warning("Using default SECRET_KEY - change in production!")

    @staticmethod
    def _log_debug_mode_warning(settings_instance, security_logger):
        """Loggear advertencia sobre debug en no-desarrollo"""
        if settings_instance.debug and settings_instance.environment != Environment.DEVELOPMENT:
            warning_event = SecurityEventFactory.create_threat_event(
                threat_type="debug_mode_in_production",
                severity=SecurityLevel.MEDIUM,
                details={
                    "environment": settings_instance.environment,
                    "debug_enabled": settings_instance.debug,
                    "recommendation": "Disable debug mode in non-development environments",
                },
            )
            security_logger.log_event(warning_event)
            logger.warning(f"Debug mode enabled in {settings_instance.environment} environment")

    @staticmethod
    def _log_real_models_warning(settings_instance, security_logger):
        """Loggear advertencia sobre modelos reales en testing"""
        if settings_instance.is_testing and settings_instance.use_real_models:
            warning_event = SecurityEventFactory.create_threat_event(
                threat_type="real_models_in_testing",
                severity=SecurityLevel.MEDIUM,
                details={
                    "environment": "testing",
                    "use_real_models": settings_instance.use_real_models,
                    "recommendation": "Use mock models in testing environment",
                },
            )
            security_logger.log_event(warning_event)
            logger.warning("Testing environment should not use real models") 