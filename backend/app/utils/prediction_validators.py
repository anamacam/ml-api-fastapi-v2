"""
Validadores para entrada de predicciones ML - FASE REFACTOR TDD Ciclo 3.

REFACTORED: Aplicando Template Method Pattern y Chain of Responsibility
- Template Method Pattern: Estructura común para validaciones de endpoints
- Chain of Responsibility: Manejo escalado de errores de validación
- DRY: Eliminación de duplicación en validaciones repetitivas
"""

from typing import Dict, Any, List, Union, Optional
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

# Configuración del logger
logger = logging.getLogger(__name__)

# REFACTORED: Usando Enum en lugar de strings para tipos de error
class ValidationErrorType(Enum):
    """Tipos de errores de validación centralizados."""
    EMPTY_DATA = "empty"
    INVALID_TYPES = "invalid_types"
    MISSING_FIELDS = "missing_fields"
    OUT_OF_RANGE = "out_of_range"
    MALFORMED_DATA = "malformed_data"


# REFACTORED: Configuración centralizada eliminando duplicación
@dataclass
class ValidationConfig:
    """Configuración centralizada de validación."""
    required_fields: List[str]
    field_types: Dict[str, tuple]
    numeric_ranges: Dict[str, tuple]

    @classmethod
    def get_prediction_config(cls) -> 'ValidationConfig':
        """Factory method para configuración de predicciones."""
        return cls(
            required_fields=["age", "income", "category", "score"],
            field_types={
                "age": (int, float),
                "income": (int, float),
                "category": str,
                "score": (int, float)
            },
            numeric_ranges={
                "age": (0, 150),
                "income": (0, float('inf')),
                "score": (0.0, 1.0)
            }
        )


# REFACTORED: Template Method Pattern - Validación Base Abstracta
class BaseValidator(ABC):
    """Template Method: Estructura común para validaciones de endpoints."""

    def validate(self, data: Any) -> Dict[str, Any]:
        """
        Template method que define el flujo de validación.
        REFACTORED: Estructura común elimina duplicación entre validadores.
        """
        try:
            # Pasos definidos en template method
            result = self._validate_format(data)
            if not result["valid"]:
                return result

            result = self._validate_content(data)
            if not result["valid"]:
                return result

            result = self._validate_business_rules(data)
            if not result["valid"]:
                return result

            # Hook method para validación específica
            result = self._validate_specific(data)
            if not result["valid"]:
                return result

            return self._create_success_result(data)

        except Exception as e:
            return self._handle_unexpected_error(e)

    # Template method steps - implementados por subclases
    @abstractmethod
    def _validate_format(self, data: Any) -> Dict[str, Any]:
        """Validar formato básico de datos."""
        pass

    @abstractmethod
    def _validate_content(self, data: Any) -> Dict[str, Any]:
        """Validar contenido de datos."""
        pass

    @abstractmethod
    def _validate_business_rules(self, data: Any) -> Dict[str, Any]:
        """Validar reglas de negocio."""
        pass

    def _validate_specific(self, data: Any) -> Dict[str, Any]:
        """Hook method para validación específica (opcional)."""
        return {"valid": True}

    def _create_success_result(self, data: Any) -> Dict[str, Any]:
        """REFACTORED: Resultado exitoso estandarizado."""
        logger.info(f"Validation successful for {self.__class__.__name__}")
        return {"valid": True}

    def _handle_unexpected_error(self, error: Exception) -> Dict[str, Any]:
        """REFACTORED: Manejo de errores centralizado."""
        logger.error(f"Unexpected error in {self.__class__.__name__}: {error}")
        return {
            "valid": False,
            "error": f"Validation error: {str(error)}"
        }


# REFACTORED: Chain of Responsibility - Manejadores de Error
class ValidationErrorHandler(ABC):
    """Chain of Responsibility: Base para manejo escalado de errores."""

    def __init__(self):
        self._next_handler: Optional['ValidationErrorHandler'] = None

    def set_next(self, handler: 'ValidationErrorHandler') -> 'ValidationErrorHandler':
        """Configurar siguiente handler en la cadena."""
        self._next_handler = handler
        return handler

    def handle(self, error_type: ValidationErrorType, context: Dict[str, Any]) -> Dict[str, Any]:
        """Template method para manejo de errores."""
        if self._can_handle(error_type):
            return self._do_handle(error_type, context)
        elif self._next_handler:
            return self._next_handler.handle(error_type, context)
        else:
            return self._default_handle(error_type, context)

    @abstractmethod
    def _can_handle(self, error_type: ValidationErrorType) -> bool:
        """¿Puede este handler manejar este tipo de error?"""
        pass

    @abstractmethod
    def _do_handle(self, error_type: ValidationErrorType, context: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar el error específico."""
        pass

    def _default_handle(self, error_type: ValidationErrorType, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handler por defecto para errores no manejados."""
        return {
            "valid": False,
            "error": f"Unhandled validation error: {error_type.value}",
            "context": context
        }


class EmptyDataErrorHandler(ValidationErrorHandler):
    """Handler específico para datos vacíos."""

    def _can_handle(self, error_type: ValidationErrorType) -> bool:
        return error_type == ValidationErrorType.EMPTY_DATA

    def _do_handle(self, error_type: ValidationErrorType, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "valid": False,
            "error": "Data is empty or None"
        }


class TypeErrorHandler(ValidationErrorHandler):
    """Handler específico para errores de tipo."""

    def _can_handle(self, error_type: ValidationErrorType) -> bool:
        return error_type == ValidationErrorType.INVALID_TYPES

    def _do_handle(self, error_type: ValidationErrorType, context: Dict[str, Any]) -> Dict[str, Any]:
        field = context.get("field")
        expected_types = context.get("expected_types")
        return {
            "valid": False,
            "error": f"invalid_types: {field} must be {expected_types}"
        }


class MissingFieldsErrorHandler(ValidationErrorHandler):
    """Handler específico para campos faltantes."""

    def _can_handle(self, error_type: ValidationErrorType) -> bool:
        return error_type == ValidationErrorType.MISSING_FIELDS

    def _do_handle(self, error_type: ValidationErrorType, context: Dict[str, Any]) -> Dict[str, Any]:
        missing_fields = context.get("missing_fields", [])
        return {
            "valid": False,
            "error": "missing_fields detected",
            "missing_fields": missing_fields
        }


class RangeErrorHandler(ValidationErrorHandler):
    """Handler específico para errores de rango."""

    def _can_handle(self, error_type: ValidationErrorType) -> bool:
        return error_type == ValidationErrorType.OUT_OF_RANGE

    def _do_handle(self, error_type: ValidationErrorType, context: Dict[str, Any]) -> Dict[str, Any]:
        field = context.get("field")
        min_val = context.get("min_val")
        max_val = context.get("max_val")
        return {
            "valid": False,
            "error": f"out_of_range: {field} must be between {min_val} and {max_val}"
        }


# REFACTORED: Implementación Concreta usando Template Method
class PredictionInputValidator(BaseValidator):
    """Validador de entrada de predicciones usando Template Method Pattern."""

    def __init__(self, config: ValidationConfig = None):
        self.config = config or ValidationConfig.get_prediction_config()
        # REFACTORED: Chain of Responsibility para manejo de errores
        self.error_handler = self._setup_error_chain()

    def _setup_error_chain(self) -> ValidationErrorHandler:
        """REFACTORED: Configurar cadena de manejo de errores."""
        empty_handler = EmptyDataErrorHandler()
        type_handler = TypeErrorHandler()
        missing_handler = MissingFieldsErrorHandler()
        range_handler = RangeErrorHandler()

        # Configurar cadena
        empty_handler.set_next(type_handler).set_next(missing_handler).set_next(range_handler)
        return empty_handler

    def _validate_format(self, data: Any) -> Dict[str, Any]:
        """Validar formato básico: no vacío."""
        if data is None or (isinstance(data, dict) and len(data) == 0):
            return self.error_handler.handle(ValidationErrorType.EMPTY_DATA, {"data": data})
        return {"valid": True}

    def _validate_content(self, data: Any) -> Dict[str, Any]:
        """Validar contenido: tipos de datos."""
        if not isinstance(data, dict):
            return {"valid": True}  # Skip if not dict

        for field_name, expected_types in self.config.field_types.items():
            if field_name in data:
                value = data[field_name]
                if not isinstance(value, expected_types):
                    return self.error_handler.handle(
                        ValidationErrorType.INVALID_TYPES,
                        {"field": field_name, "expected_types": expected_types}
                    )

        return {"valid": True}

    def _validate_business_rules(self, data: Any) -> Dict[str, Any]:
        """Validar reglas de negocio: campos requeridos y rangos."""
        if not isinstance(data, dict):
            return {"valid": True}

        # Validar campos requeridos
        missing_fields = [field for field in self.config.required_fields if field not in data]
        if missing_fields:
            return self.error_handler.handle(
                ValidationErrorType.MISSING_FIELDS,
                {"missing_fields": missing_fields}
            )

        # Validar rangos numéricos
        for field_name, (min_val, max_val) in self.config.numeric_ranges.items():
            if field_name in data:
                value = data[field_name]
                if isinstance(value, (int, float)) and (value < min_val or value > max_val):
                    return self.error_handler.handle(
                        ValidationErrorType.OUT_OF_RANGE,
                        {"field": field_name, "min_val": min_val, "max_val": max_val}
                    )

        return {"valid": True}


# REFACTORED: Facade Pattern - Interface Simplificada
class ValidationFacade:
    """
    Facade Pattern: Interface simplificada para todas las validaciones.
    REFACTORED: Punto único de acceso elimina duplicación en uso.
    """

    def __init__(self):
        self.prediction_validator = PredictionInputValidator()

    def validate_prediction_input(self, data: Any) -> Dict[str, Any]:
        """Validar entrada de predicción con facade simplificado."""
        return self.prediction_validator.validate(data)

    def get_validation_schema(self) -> Dict[str, Any]:
        """Schema de validación para documentación."""
        config = ValidationConfig.get_prediction_config()
        return {
            "required_fields": config.required_fields,
            "field_types": {k: str(v) for k, v in config.field_types.items()},
            "numeric_ranges": config.numeric_ranges,
            "version": "2.0.0-refactored"
        }


# REFACTORED: Interface de compatibilidad hacia atrás
_validation_facade = ValidationFacade()

def validate_prediction_input(data: Any) -> Dict[str, Any]:
    """
    Interface de compatibilidad hacia atrás.
    REFACTORED: Delegación a facade elimina duplicación.
    """
    return _validation_facade.validate_prediction_input(data)

def get_validation_schema() -> Dict[str, Any]:
    """
    Interface de compatibilidad hacia atrás para schema.
    REFACTORED: Delegación a facade.
    """
    return _validation_facade.get_validation_schema()
