"""
Módulo de configuración - REFACTORED

REFACTORED: Módulo modularizado con baja complejidad ciclomática
- Separado en módulos especializados
- Mantenida funcionalidad completa
- Mejorada mantenibilidad
"""

from .environment import Environment
from .security_logger import SecurityLogger
from .security_validator import SecurityValidator
from .settings import Settings, get_settings
from .settings_factory import SettingsFactory
from .validation_strategies import (
    EnvironmentValidationStrategy,
    ValidationRule,
    ValidationStrategyFactory,
)

__all__ = [
    "Environment",
    "SecurityLogger",
    "SecurityValidator",
    "Settings",
    "SettingsFactory",
    "EnvironmentValidationStrategy",
    "ValidationRule",
    "ValidationStrategyFactory",
    "get_settings",
] 