"""
Estrategias de validación por entorno - Extraído de settings.py

REFACTORED: Separando Strategy Pattern en módulo independiente
- Diferentes validadores por entorno
- Factory Pattern para creación de estrategias
- Validaciones centralizadas
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, List

from .environment import Environment


@dataclass
class ValidationRule:
    """Configuración de una regla de validación"""

    field_name: str
    validator_func: Callable[[Any], bool]
    error_message: str


class EnvironmentValidationStrategy(ABC):
    """Strategy abstracto para validación por entorno"""

    @abstractmethod
    def get_validation_rules(self) -> List[ValidationRule]:
        """Obtener reglas de validación específicas del entorno"""
        pass

    @abstractmethod
    def get_required_vars(self) -> List[str]:
        """Obtener variables requeridas para este entorno"""
        pass


class DevelopmentValidationStrategy(EnvironmentValidationStrategy):
    """Validación relajada para desarrollo"""

    def get_validation_rules(self) -> List[ValidationRule]:
        return [
            ValidationRule(
                "secret_key", lambda v: len(v) > 0, "Secret key cannot be empty"
            )
        ]

    def get_required_vars(self) -> List[str]:
        return []  # No variables requeridas en desarrollo


class ProductionValidationStrategy(EnvironmentValidationStrategy):
    """Validación estricta para producción"""

    def get_validation_rules(self) -> List[ValidationRule]:
        return [
            ValidationRule(
                "secret_key",
                lambda v: v != "dev-secret-key-change-in-production" and len(v) >= 32,
                "SECRET_KEY must be changed and at least 32 characters in production",
            ),
            ValidationRule(
                "debug",
                lambda v: v is False,
                "DEBUG must be False in production environment",
            ),
        ]

    def get_required_vars(self) -> List[str]:
        return ["secret_key"]


class TestingValidationStrategy(EnvironmentValidationStrategy):
    """Validación específica para testing"""

    def get_validation_rules(self) -> List[ValidationRule]:
        return [
            ValidationRule(
                "use_real_models",
                lambda v: v is False,
                "Testing environment must never use real models",
            )
        ]

    def get_required_vars(self) -> List[str]:
        return []


class StagingValidationStrategy(EnvironmentValidationStrategy):
    """Validación intermedia para staging"""

    def get_validation_rules(self) -> List[ValidationRule]:
        return [
            ValidationRule(
                "secret_key",
                lambda v: v != "dev-secret-key-change-in-production" and len(v) >= 16,
                "SECRET_KEY should be changed and at least 16 characters in staging",
            )
        ]

    def get_required_vars(self) -> List[str]:
        return ["secret_key"]


class ValidationStrategyFactory:
    """Factory para crear estrategias de validación por entorno"""

    _strategies = {
        Environment.DEVELOPMENT: DevelopmentValidationStrategy,
        Environment.TESTING: TestingValidationStrategy,
        Environment.STAGING: StagingValidationStrategy,
        Environment.PRODUCTION: ProductionValidationStrategy,
    }

    @classmethod
    def create_strategy(cls, environment: Environment) -> EnvironmentValidationStrategy:
        """Crear estrategia de validación para el entorno especificado"""
        strategy_class = cls._strategies.get(environment)
        if not strategy_class:
            raise ValueError(
                f"No validation strategy found for environment: {environment}"
            )
        return strategy_class() 