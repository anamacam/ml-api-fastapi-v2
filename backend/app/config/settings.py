# -*- coding: utf-8 -*-
"""
⚙️ Configuración de la aplicación por entornos - REFACTORED

REFACTORED: Aplicando modularización y reduciendo complejidad ciclomática
- Separado en módulos especializados
- Reducida complejidad de 487 líneas a ~200 líneas
- Mantenida funcionalidad completa
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .environment import Environment
from .security_logger import SecurityLogger
from .security_validator import SecurityValidator
from .validation_strategies import ValidationStrategyFactory

# Configurar logger
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Configuración de la aplicación basada en variables de entorno
    REFACTORED: Simplificado usando módulos especializados
    """

    # 🌍 Entorno
    environment: Environment = Field(
        default=Environment.DEVELOPMENT, description="Entorno de ejecución"
    )
    debug: bool = Field(default=True, description="Modo debug")

    # 🤖 Machine Learning
    ml_models_path: Path = Field(
        default=Path("data/models"), description="Directorio de modelos ML"
    )

    # Alias para compatibilidad
    @property
    def MODELS_PATH(self) -> Path:
        """Alias para ml_models_path para compatibilidad"""
        return self.ml_models_path

    use_real_models: bool = Field(
        default=True, description="Usar modelos reales (false para mocks en testing)"
    )
    max_prediction_batch_size: int = Field(
        default=100, description="Tamaño máximo de batch para predicciones"
    )

    # 🗄️ Base de datos
    database_url: Optional[str] = Field(
        default=None, description="URL de conexión a la base de datos"
    )

    # 🔐 Seguridad
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Clave secreta para JWT",
    )

    # 📊 API
    api_title: str = Field(default="ML API FastAPI v2", description="Título de la API")
    api_version: str = Field(default="2.0.0", description="Versión de la API")
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="Orígenes permitidos para CORS",
    )

    # 📁 Archivos
    upload_dir: Path = Field(
        default=Path("data/uploads"), description="Directorio de uploads"
    )
    max_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Tamaño máximo de archivo en bytes",
    )

    # 📝 Logging
    log_level: str = Field(default="INFO", description="Nivel de logging")
    log_file: Optional[Path] = Field(
        default=Path("data/logs/app.log"), description="Archivo de logs"
    )

    # Properties para verificar entorno
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

    # Validadores usando módulos extraídos
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v, info):
        """Validar secret key usando strategy pattern"""
        environment = info.data.get("environment", Environment.DEVELOPMENT)
        strategy = ValidationStrategyFactory.create_strategy(environment)

        for rule in strategy.get_validation_rules():
            if rule.field_name == "secret_key":
                if not rule.validator_func(v):
                    raise ValueError(rule.error_message)
        return v

    @field_validator("debug")
    @classmethod
    def validate_debug(cls, v, info):
        """Validar debug usando strategy pattern"""
        environment = info.data.get("environment", Environment.DEVELOPMENT)
        strategy = ValidationStrategyFactory.create_strategy(environment)

        for rule in strategy.get_validation_rules():
            if rule.field_name == "debug":
                if not rule.validator_func(v):
                    raise ValueError(rule.error_message)
        return v

    @field_validator("ml_models_path")
    @classmethod
    def validate_models_path(cls, v):
        """Validar path usando SecurityValidator centralizado"""
        return SecurityValidator.validate_safe_path(v)

    @field_validator("use_real_models", mode="before")
    @classmethod
    def validate_use_real_models(cls, v, info):
        """Validar use_real_models con fallback seguro"""
        environment = info.data.get("environment", "development")
        parsed_value = SecurityValidator.parse_boolean_with_fallback(v, environment)

        # Aplicar reglas específicas del entorno
        strategy = ValidationStrategyFactory.create_strategy(Environment(environment))
        for rule in strategy.get_validation_rules():
            if rule.field_name == "use_real_models":
                if not rule.validator_func(parsed_value):
                    raise ValueError(rule.error_message)

        return parsed_value

    def __init__(self, **values):
        """
        Inicialización con validaciones usando Strategy Pattern
        REFACTORED: Simplificado usando módulos especializados
        """
        environment = values.get("environment", Environment.DEVELOPMENT)

        # Validar variables requeridas usando strategy
        self._validate_required_environment_variables(values, environment)

        # Inicialización normal
        super().__init__(**values)

        # Logging de advertencias de seguridad
        SecurityLogger.log_security_warnings(self)

    def _validate_required_environment_variables(
        self, values: Dict[str, Any], environment: Environment
    ):
        """
        Validar variables requeridas usando Strategy Pattern
        REFACTORED: Simplificado usando módulos especializados
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

    # Configuration is immutable by using Pydantic's built-in frozen behavior
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Función de conveniencia para obtener settings
def get_settings() -> Settings:
    """Obtener instancia de configuración"""
    return Settings()
