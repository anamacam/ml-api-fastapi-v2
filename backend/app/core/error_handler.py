"""
🛡️ Sistema Avanzado de Manejo de Errores para ML

Implementación TDD - FASE REFACTOR
Aplicando: Factory Pattern, Strategy Pattern, DRY Principle
"""

import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable, Type
from datetime import datetime
from abc import ABC, abstractmethod


class ErrorTypes(Enum):
    """Tipos de errores específicos de ML"""
    MODEL_LOAD_ERROR = "model_load_error"
    PREDICTION_ERROR = "prediction_error"
    VALIDATION_ERROR = "validation_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    SYSTEM_ERROR = "system_error"
    NETWORK_ERROR = "network_error"


class ErrorSeverity(Enum):
    """Niveles de severidad de errores"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorPatternConfig:
    """Configuración para patrones de error - elimina duplicación"""
    error_type: ErrorTypes
    severity: ErrorSeverity
    is_retryable: bool
    patterns: list[str]
    friendly_message: str


@dataclass
class ClassifiedError:
    """Error clasificado con contexto"""
    error_type: ErrorTypes
    severity: ErrorSeverity
    should_retry: bool
    context: Dict[str, Any]
    original_error: Exception
    user_message: str
    timestamp: datetime = field(default_factory=datetime.now)


class ErrorClassificationStrategy(ABC):
    """Estrategia abstracta para clasificación de errores"""

    @abstractmethod
    def can_classify(self, error: Exception) -> bool:
        """Determinar si esta estrategia puede clasificar el error"""
        pass

    @abstractmethod
    def classify(self, error: Exception, context: str = "") -> ErrorPatternConfig:
        """Clasificar el error usando esta estrategia"""
        pass


class PatternBasedClassifier(ErrorClassificationStrategy):
    """Clasificador basado en patrones de texto - Strategy Pattern"""

    def __init__(self):
        # Configuración centralizada - elimina duplicación
        self.error_configs: Dict[ErrorTypes, ErrorPatternConfig] = {
            ErrorTypes.MODEL_LOAD_ERROR: ErrorPatternConfig(
                error_type=ErrorTypes.MODEL_LOAD_ERROR,
                severity=ErrorSeverity.HIGH,
                is_retryable=False,
                patterns=["model file not found", "no such file", "cannot load model"],
                friendly_message="The requested model is temporarily unavailable."
            ),
            ErrorTypes.PREDICTION_ERROR: ErrorPatternConfig(
                error_type=ErrorTypes.PREDICTION_ERROR,
                severity=ErrorSeverity.MEDIUM,
                is_retryable=False,
                patterns=["array shapes", "dimension mismatch"],
                friendly_message="The input data format doesn't match the expected model requirements."
            ),
            ErrorTypes.VALIDATION_ERROR: ErrorPatternConfig(
                error_type=ErrorTypes.VALIDATION_ERROR,
                severity=ErrorSeverity.LOW,
                is_retryable=False,
                patterns=["invalid input", "missing required"],
                friendly_message="Please check your input data format and try again."
            ),
            ErrorTypes.NETWORK_ERROR: ErrorPatternConfig(
                error_type=ErrorTypes.NETWORK_ERROR,
                severity=ErrorSeverity.MEDIUM,
                is_retryable=True,
                patterns=["connection", "timeout"],
                friendly_message="Network connectivity issue. Please try again in a moment."
            ),
            ErrorTypes.RATE_LIMIT_ERROR: ErrorPatternConfig(
                error_type=ErrorTypes.RATE_LIMIT_ERROR,
                severity=ErrorSeverity.MEDIUM,
                is_retryable=True,
                patterns=["rate limit"],
                friendly_message="Too many requests. Please wait a moment before trying again."
            )
        }

        # Crear índice invertido para búsqueda eficiente
        self.pattern_to_config: Dict[str, ErrorPatternConfig] = {}
        for config in self.error_configs.values():
            for pattern in config.patterns:
                self.pattern_to_config[pattern] = config

    def can_classify(self, error: Exception) -> bool:
        """Verificar si hay algún patrón que coincida"""
        error_message = str(error).lower()
        return any(pattern in error_message for pattern in self.pattern_to_config.keys())

    def classify(self, error: Exception, context: str = "") -> ErrorPatternConfig:
        """Clasificar error usando patrones"""
        error_message = str(error).lower()

        # Buscar el primer patrón que coincida
        for pattern, config in self.pattern_to_config.items():
            if pattern in error_message:
                return config

        # Fallback (no debería llegar aquí si can_classify() funcionó correctamente)
        raise ValueError(f"No pattern found for error: {error}")


class ExceptionTypeClassifier(ErrorClassificationStrategy):
    """Clasificador basado en tipo de excepción - Strategy Pattern"""

    def __init__(self):
        self.exception_mappings: Dict[Type[Exception], ErrorPatternConfig] = {
            ConnectionError: ErrorPatternConfig(
                error_type=ErrorTypes.NETWORK_ERROR,
                severity=ErrorSeverity.MEDIUM,
                is_retryable=True,
                patterns=[],
                friendly_message="Network connectivity issue. Please try again in a moment."
            ),
            TimeoutError: ErrorPatternConfig(
                error_type=ErrorTypes.NETWORK_ERROR,
                severity=ErrorSeverity.MEDIUM,
                is_retryable=True,
                patterns=[],
                friendly_message="The request took too long to process. Please try again."
            ),
            ValueError: ErrorPatternConfig(
                error_type=ErrorTypes.VALIDATION_ERROR,
                severity=ErrorSeverity.LOW,
                is_retryable=False,
                patterns=[],
                friendly_message="Please check your input data format and try again."
            )
        }

    def can_classify(self, error: Exception) -> bool:
        """Verificar si el tipo de excepción está mapeado"""
        return type(error) in self.exception_mappings

    def classify(self, error: Exception, context: str = "") -> ErrorPatternConfig:
        """Clasificar por tipo de excepción"""
        return self.exception_mappings[type(error)]


class MLErrorHandler:
    """
    Manejador avanzado de errores específicos para Machine Learning

    REFACTORED: Aplicando Strategy Pattern y eliminando duplicación
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Strategy Pattern - múltiples estrategias de clasificación
        self.classification_strategies: list[ErrorClassificationStrategy] = [
            PatternBasedClassifier(),
            ExceptionTypeClassifier()
        ]

        # Configuración por defecto para errores no clasificados
        self.default_config = ErrorPatternConfig(
            error_type=ErrorTypes.SYSTEM_ERROR,
            severity=ErrorSeverity.MEDIUM,
            is_retryable=False,
            patterns=[],
            friendly_message="The prediction service encountered an unexpected error. Please try again later."
        )

    def classify_error(self, error: Exception, context: str = "") -> ClassifiedError:
        """
        Clasificar error usando estrategias múltiples

        REFACTORED: Simplificado usando Strategy Pattern
        """
        # Intentar clasificar con cada estrategia
        config = self._find_classification_config(error)

        # Crear contexto enriquecido
        enriched_context = self._create_enriched_context(error, context)

        classified = ClassifiedError(
            error_type=config.error_type,
            severity=config.severity,
            should_retry=config.is_retryable,
            context=enriched_context,
            original_error=error,
            user_message=config.friendly_message
        )

        # Log para debugging
        self._log_classification(classified, context)

        return classified

    def get_user_friendly_message(self, error: Exception) -> str:
        """
        Convertir error técnico a mensaje amigable

        REFACTORED: Delegado a configuración centralizada
        """
        config = self._find_classification_config(error)
        return config.friendly_message

    def _find_classification_config(self, error: Exception) -> ErrorPatternConfig:
        """Encontrar configuración usando estrategias - Strategy Pattern"""
        for strategy in self.classification_strategies:
            if strategy.can_classify(error):
                return strategy.classify(error)

        # Fallback a configuración por defecto
        return self.default_config

    def _create_enriched_context(self, error: Exception, context: str) -> Dict[str, Any]:
        """Crear contexto enriquecido - método extraído para DRY"""
        return {
            "original_context": context,
            "error_class": error.__class__.__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat()
        }

    def _log_classification(self, classified: ClassifiedError, context: str) -> None:
        """Loggear clasificación - método extraído para DRY"""
        self.logger.warning(
            f"Error classified: {classified.error_type.value} "
            f"(severity: {classified.severity.value}) "
            f"in context: {context}"
        )


# Factory Pattern para creación de excepciones específicas
class MLExceptionFactory:
    """Factory para crear excepciones ML específicas - Factory Pattern"""

    @staticmethod
    def create_model_load_error(message: str, model_path: str = None,
                              model_type: str = None) -> 'ModelLoadError':
        """Crear error de carga de modelo"""
        return ModelLoadError(message, model_path, model_type)

    @staticmethod
    def create_prediction_error(message: str, model_id: str = None,
                              input_shape: tuple = None, expected_shape: tuple = None,
                              model_version: str = None) -> 'PredictionError':
        """Crear error de predicción"""
        return PredictionError(message, model_id, input_shape, expected_shape, model_version)

    @staticmethod
    def create_validation_error(message: str, field_name: str = None,
                              expected_type: str = None) -> 'ValidationError':
        """Crear error de validación"""
        return ValidationError(message, field_name, expected_type)

    @staticmethod
    def create_rate_limit_error(message: str, retry_after_seconds: int = None,
                              limit_type: str = None, current_usage: int = None) -> 'RateLimitError':
        """Crear error de rate limiting"""
        return RateLimitError(message, retry_after_seconds, limit_type, current_usage)


# Excepciones específicas para diferentes tipos de errores ML - sin cambios en interfaz

class ModelLoadError(Exception):
    """Error al cargar modelos ML"""

    def __init__(self, message: str, model_path: str = None, model_type: str = None):
        super().__init__(message)
        self.model_path = model_path
        self.model_type = model_type


class PredictionError(Exception):
    """Error durante predicción ML"""

    def __init__(self, message: str, model_id: str = None, input_shape: tuple = None,
                 expected_shape: tuple = None, model_version: str = None):
        super().__init__(message)
        self.model_id = model_id
        self.input_shape = input_shape
        self.expected_shape = expected_shape
        self.model_version = model_version
        self.should_retry = False


class ValidationError(Exception):
    """Error de validación de entrada"""

    def __init__(self, message: str, field_name: str = None, expected_type: str = None):
        super().__init__(message)
        self.field_name = field_name
        self.expected_type = expected_type


class RateLimitError(Exception):
    """Error de límite de rate limiting"""

    def __init__(self, message: str, retry_after_seconds: int = None,
                 limit_type: str = None, current_usage: int = None):
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds
        self.limit_type = limit_type
        self.current_usage = current_usage


class SystemError(Exception):
    """Error del sistema general"""

    def __init__(self, message: str, component: str = None, severity: str = "medium"):
        super().__init__(message)
        self.component = component
        self.severity = severity
