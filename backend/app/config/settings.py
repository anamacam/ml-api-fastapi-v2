"""
⚙️ Configuración de la aplicación por entornos - FASE REFACTOR TDD

REFACTORED: Aplicando Strategy Pattern, Factory Pattern y DRY Principle
- Strategy Pattern: Diferentes validadores por entorno
- Factory Pattern: Creación centralizada de configuraciones
- DRY: Eliminación de duplicación en validaciones
"""
import os
import logging
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from pydantic import Field, field_validator, ValidationError, ConfigDict
from pydantic_settings import BaseSettings

# Configurar logger
logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Entornos disponibles"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


# REFACTORED: Strategy Pattern - Validadores por Entorno
@dataclass
class ValidationRule:
    """Configuración de una regla de validación"""
    field_name: str
    validator_func: callable
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
                "secret_key",
                lambda v: len(v) > 0,
                "Secret key cannot be empty"
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
                "SECRET_KEY must be changed and at least 32 characters in production"
            ),
            ValidationRule(
                "debug",
                lambda v: v is False,
                "DEBUG must be False in production environment"
            )
        ]

    def get_required_vars(self) -> List[str]:
        return ['secret_key']


class TestingValidationStrategy(EnvironmentValidationStrategy):
    """Validación específica para testing"""

    def get_validation_rules(self) -> List[ValidationRule]:
        return [
            ValidationRule(
                "use_real_models",
                lambda v: v is False,
                "Testing environment must never use real models"
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
                "SECRET_KEY should be changed and at least 16 characters in staging"
            )
        ]

    def get_required_vars(self) -> List[str]:
        return ['secret_key']


# REFACTORED: Factory Pattern - Creación de Validadores
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
            raise ValueError(f"No validation strategy found for environment: {environment}")
        return strategy_class()


# REFACTORED: DRY - Centralizando Patrones Peligrosos
class SecurityValidator:
    """Validador centralizado para seguridad"""

    DANGEROUS_PATH_PATTERNS = [
        "..", "/etc/", "/var/", "/root/", "System32",
        "Windows\\System32", "passwd", "shadow", "secrets"
    ]

    BOOLEAN_TRUE_VALUES = ['true', '1', 'yes', 'on']
    BOOLEAN_FALSE_VALUES = ['false', '0', 'no', 'off']

    @classmethod
    def validate_safe_path(cls, path: Path) -> Path:
        """Validar que un path sea seguro"""
        path_str = str(path)
        for pattern in cls.DANGEROUS_PATH_PATTERNS:
            if pattern in path_str:
                raise ValueError(f"Dangerous path detected: {path_str}")
        return path

    @classmethod
    def parse_boolean_with_fallback(cls, value: Any, environment: str = 'development') -> bool:
        """Parse booleano con fallback seguro"""
        if isinstance(value, str):
            if value.lower() in cls.BOOLEAN_TRUE_VALUES:
                return True
            elif value.lower() in cls.BOOLEAN_FALSE_VALUES:
                return False
            else:
                # Fallback seguro basado en entorno
                return environment == 'production'
        return bool(value)


class Settings(BaseSettings):
    """
    Configuración de la aplicación basada en variables de entorno
    REFACTORED: Usando Strategy Pattern para validación por entorno
    """

    # 🌍 Entorno
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Entorno de ejecución"
    )
    debug: bool = Field(
        default=True,
        description="Modo debug"
    )

    # 🤖 Machine Learning
    ml_models_path: Path = Field(
        default=Path("data/models"),
        description="Directorio de modelos ML"
    )
    use_real_models: bool = Field(
        default=True,
        description="Usar modelos reales (false para mocks en testing)"
    )
    max_prediction_batch_size: int = Field(
        default=100,
        description="Tamaño máximo de batch para predicciones"
    )

    # 🗄️ Base de datos
    database_url: Optional[str] = Field(
        default=None,
        description="URL de conexión a la base de datos"
    )

    # 🔐 Seguridad
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Clave secreta para JWT"
    )

    # 📊 API
    api_title: str = Field(
        default="ML API FastAPI v2",
        description="Título de la API"
    )
    api_version: str = Field(
        default="2.0.0",
        description="Versión de la API"
    )
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="Orígenes permitidos para CORS"
    )

    # 📁 Archivos
    upload_dir: Path = Field(
        default=Path("data/uploads"),
        description="Directorio de uploads"
    )
    max_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Tamaño máximo de archivo en bytes"
    )

    # 📝 Logging
    log_level: str = Field(
        default="INFO",
        description="Nivel de logging"
    )
    log_file: Optional[Path] = Field(
        default=Path("data/logs/app.log"),
        description="Archivo de logs"
    )



    @property
    def is_development(self) -> bool:
        """¿Está en modo desarrollo?"""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        """¿Está en modo testing?"""
        return self.environment == Environment.TESTING

    @property
    def is_production(self) -> bool:
        """¿Está en modo producción?"""
        return self.environment == Environment.PRODUCTION

    @property
    def should_use_real_models(self) -> bool:
        """¿Debería usar modelos reales?"""
        # En testing siempre usar mocks, en otros entornos según configuración
        if self.is_testing:
            return False
        return self.use_real_models

    # REFACTORED: DRY - Validadores usando Strategy Pattern (Pydantic V2)
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v, info):
        """Validar secret key usando strategy pattern"""
        environment = info.data.get('environment', Environment.DEVELOPMENT)
        strategy = ValidationStrategyFactory.create_strategy(environment)

        for rule in strategy.get_validation_rules():
            if rule.field_name == 'secret_key':
                if not rule.validator_func(v):
                    raise ValueError(rule.error_message)
        return v

    @field_validator('debug')
    @classmethod
    def validate_debug(cls, v, info):
        """Validar debug usando strategy pattern"""
        environment = info.data.get('environment', Environment.DEVELOPMENT)
        strategy = ValidationStrategyFactory.create_strategy(environment)

        for rule in strategy.get_validation_rules():
            if rule.field_name == 'debug':
                if not rule.validator_func(v):
                    raise ValueError(rule.error_message)
        return v

    @field_validator('ml_models_path')
    @classmethod
    def validate_models_path(cls, v):
        """Validar path usando SecurityValidator centralizado"""
        return SecurityValidator.validate_safe_path(v)

    @field_validator('use_real_models', mode='before')
    @classmethod
    def validate_use_real_models(cls, v, info):
        """Validar use_real_models con fallback seguro"""
        environment = info.data.get('environment', 'development')
        parsed_value = SecurityValidator.parse_boolean_with_fallback(v, environment)

        # Aplicar reglas específicas del entorno
        strategy = ValidationStrategyFactory.create_strategy(Environment(environment))
        for rule in strategy.get_validation_rules():
            if rule.field_name == 'use_real_models':
                if not rule.validator_func(parsed_value):
                    raise ValueError(rule.error_message)

        return parsed_value

    def __init__(self, **values):
        """
        Inicialización con validaciones usando Strategy Pattern
        REFACTORED: Usando Factory Pattern para validación por entorno
        """
        environment = values.get('environment', Environment.DEVELOPMENT)

        # Validar variables requeridas usando strategy
        self._validate_required_environment_variables(values, environment)

        # Inicialización normal
        super().__init__(**values)

        # Logging de advertencias de seguridad
        self._log_security_warnings()

        # Hacer configuración inmutable
        self.__dict__['_frozen'] = True

    def _validate_required_environment_variables(self, values: Dict[str, Any], environment: Environment):
        """
        Validar variables requeridas usando Strategy Pattern
        REFACTORED: Centralizado y usando strategy específico por entorno
        """
        validation_strategy = ValidationStrategyFactory.create_strategy(environment)
        required_vars = validation_strategy.get_required_vars()
        missing = []

        for var in required_vars:
            # Verificar en values o variables de entorno
            if var not in values:
                env_var = var.upper()
                if env_var not in os.environ:
                    missing.append(var)

        if missing:
            raise ValueError(
                f"Required environment variables missing for {environment}: {missing}"
            )

    def _log_security_warnings(self):
        """
        Loggear advertencias de seguridad
        REFACTORED: Usando patrones centralizados
        """
        # Advertencia sobre secret key por defecto
        if self.secret_key == "dev-secret-key-change-in-production":
            logger.warning("Using default SECRET_KEY - change in production!")

        # Advertencia sobre debug en no-desarrollo
        if self.debug and self.environment != Environment.DEVELOPMENT:
            logger.warning(f"Debug mode enabled in {self.environment} environment")

        # Advertencia sobre modelos reales en testing
        if self.is_testing and self.use_real_models:
            logger.warning("Testing environment should not use real models")

    def __setattr__(self, name, value):
        """Prevenir modificaciones después de inicialización"""
        if hasattr(self, '_frozen') and self._frozen:
            raise AttributeError(f"Configuration is immutable - cannot modify {name}")
        super().__setattr__(name, value)

    # REFACTORED: Pydantic V2 Configuration
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Mapeo de variables de entorno
        env_prefix="",
        extra="ignore"
    )


# REFACTORED: Factory Pattern - Configuración por Entorno
class SettingsFactory:
    """Factory para crear configuraciones optimizadas por entorno"""

    @classmethod
    def create_development_settings(cls, **overrides) -> Settings:
        """Crear configuración optimizada para desarrollo"""
        defaults = {
            "environment": Environment.DEVELOPMENT,
            "debug": True,
            "use_real_models": False,
            "log_level": "DEBUG"
        }
        defaults.update(overrides)
        return Settings(**defaults)

    @classmethod
    def create_testing_settings(cls, **overrides) -> Settings:
        """Crear configuración optimizada para testing"""
        defaults = {
            "environment": Environment.TESTING,
            "debug": False,
            "use_real_models": False,
            "log_level": "WARNING"
        }
        defaults.update(overrides)
        return Settings(**defaults)

    @classmethod
    def create_production_settings(cls, **overrides) -> Settings:
        """Crear configuración optimizada para producción"""
        # Verificar que se proporcionen valores seguros
        required_production_keys = ['secret_key']
        for key in required_production_keys:
            if key not in overrides and key.upper() not in os.environ:
                raise ValueError(f"Production settings require {key}")

        defaults = {
            "environment": Environment.PRODUCTION,
            "debug": False,
            "use_real_models": True,
            "log_level": "INFO"
        }
        defaults.update(overrides)
        return Settings(**defaults)


# 🌍 Instancia global de configuración
settings = Settings()


def get_settings() -> Settings:
    """Obtener configuración (útil para inyección de dependencias)"""
    return settings
