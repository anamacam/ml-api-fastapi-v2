"""
Validadores para modelos ML.

Sistema de validación robusto y extensible para modelos de machine learning.
Verifica integridad, capacidad de predicción y formato de salida.

Refactorizado: código limpio, modular y mantenible.
"""

from typing import Dict, Any, Optional, List, Union, Type
import numpy as np
import logging
from abc import ABC, abstractmethod

# Configuración del logger
logger = logging.getLogger(__name__)

# Métodos requeridos para modelos ML
REQUIRED_MODEL_METHODS = ["predict"]

# Atributos que indican modelo sklearn entrenado
SKLEARN_FITTED_ATTRIBUTES = [
    'coef_', 'intercept_', 'n_features_in_',
    'feature_names_in_', 'classes_', 'n_iter_'
]

# Tipos de salida válidos para predicciones
VALID_PREDICTION_TYPES = (np.ndarray, list, tuple)


class ModelValidationError:
    """Tipos de errores de validación de modelos."""
    NULL_MODEL = "null_model"
    MISSING_METHODS = "missing_methods"
    NOT_FITTED = "not_fitted"
    PREDICTION_FAILED = "prediction_failed"
    INVALID_OUTPUT_FORMAT = "invalid_output_format"


class ModelValidator(ABC):
    """Validador base abstracto para modelos ML."""

    @abstractmethod
    def validate(self, model: Any) -> Dict[str, Any]:
        """Valida el modelo específico."""
        pass

    @abstractmethod
    def supports_model(self, model: Any) -> bool:
        """Verifica si el validador soporta este tipo de modelo."""
        pass


class SklearnModelValidator(ModelValidator):
    """Validador específico para modelos Scikit-learn."""

    def supports_model(self, model: Any) -> bool:
        """Verifica si es un modelo sklearn."""
        if not hasattr(model, '__class__'):
            return False

        module_name = getattr(model.__class__, '__module__', '')
        class_name = getattr(model.__class__, '__name__', '')

        # Verificar que el módulo comience con 'sklearn'
        # y no sea solo que contenga 'sklearn' en el path del test
        return (module_name.startswith('sklearn.') or
                module_name == 'sklearn')

    def validate(self, model: Any) -> Dict[str, Any]:
        """Valida modelo sklearn específicamente."""
        # Verificar si está entrenado
        if not self._is_fitted(model):
            return {
                "valid": False,
                "error": f"Model {ModelValidationError.NOT_FITTED}: sklearn model appears to be untrained"
            }

        return {"valid": True}

    def _is_fitted(self, model: Any) -> bool:
        """Verifica si el modelo sklearn está entrenado."""
        return any(hasattr(model, attr) for attr in SKLEARN_FITTED_ATTRIBUTES)


class GenericModelValidator(ModelValidator):
    """Validador genérico para cualquier modelo ML."""

    def supports_model(self, model: Any) -> bool:
        """Soporta cualquier modelo."""
        return True

    def validate(self, model: Any) -> Dict[str, Any]:
        """Validación genérica básica."""
        return {"valid": True}


def validate_ml_model(model: Any, test_data: Optional[np.ndarray] = None) -> Dict[str, Any]:
    """
    Valida modelo ML antes de usar para predicciones.

    Realiza validación completa de:
    - Modelo no nulo
    - Métodos requeridos presentes
    - Estado de entrenamiento (para modelos conocidos)
    - Capacidad de predicción (opcional)
    - Formato de salida válido (opcional)

    Args:
        model: Modelo ML para validar
        test_data: Datos de prueba opcionales para validar predicción

    Returns:
        Dict con 'valid' (bool) y opcionalmente 'error' y 'missing_methods'

    Examples:
        >>> validate_ml_model(None)
        {'valid': False, 'error': 'Model is None'}

        >>> from sklearn.linear_model import LinearRegression
        >>> import numpy as np
        >>> model = LinearRegression()
        >>> model.fit([[1], [2]], [1, 2])
        >>> validate_ml_model(model)
        {'valid': True}
    """
    try:
        # Validación básica: modelo no nulo
        null_result = _validate_not_null(model)
        if not null_result["valid"]:
            return null_result

        # Validación de métodos requeridos
        methods_result = _validate_required_methods(model)
        if not methods_result["valid"]:
            return methods_result

        # Validación específica por tipo de modelo
        type_result = _validate_model_by_type(model)
        if not type_result["valid"]:
            return type_result

        # Validación de capacidad de predicción (opcional)
        if test_data is not None:
            prediction_result = _validate_prediction_capability(model, test_data)
            if not prediction_result["valid"]:
                return prediction_result

        # Todo válido
        logger.info(f"Model validation successful for {type(model).__name__}")
        return {"valid": True}

    except Exception as e:
        logger.error(f"Unexpected error during model validation: {e}")
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}"
        }


def _validate_not_null(model: Any) -> Dict[str, Any]:
    """Valida que el modelo no sea nulo."""
    if model is None:
        return {
            "valid": False,
            "error": "Model is None"
        }
    return {"valid": True}


def _validate_required_methods(model: Any) -> Dict[str, Any]:
    """Valida que el modelo tenga métodos requeridos."""
    missing_methods = []

    for method in REQUIRED_MODEL_METHODS:
        if not hasattr(model, method) or not callable(getattr(model, method)):
            missing_methods.append(method)

    if missing_methods:
        return {
            "valid": False,
            "error": "missing_methods detected",
            "missing_methods": missing_methods
        }

    return {"valid": True}


def _validate_model_by_type(model: Any) -> Dict[str, Any]:
    """Valida modelo usando validador específico por tipo."""
    validators = [
        SklearnModelValidator(),
        GenericModelValidator()  # Siempre último (catch-all)
    ]

    for validator in validators:
        if validator.supports_model(model):
            return validator.validate(model)

    return {"valid": True}


def _validate_prediction_capability(model: Any, test_data: np.ndarray) -> Dict[str, Any]:
    """Valida capacidad de predicción y formato de salida."""
    try:
        prediction = model.predict(test_data)

        # Validar formato de salida
        if not isinstance(prediction, VALID_PREDICTION_TYPES):
            return {
                "valid": False,
                "error": f"invalid_output_format: prediction must be one of {VALID_PREDICTION_TYPES}"
            }

        # Validar que la predicción no esté vacía
        if hasattr(prediction, '__len__') and len(prediction) == 0:
            return {
                "valid": False,
                "error": "invalid_output_format: prediction is empty"
            }

        return {"valid": True}

    except Exception as e:
        return {
            "valid": False,
            "error": f"prediction_failed: {str(e)}"
        }


def get_supported_model_types() -> List[str]:
    """
    Retorna lista de tipos de modelos soportados.

    Returns:
        Lista de strings con tipos de modelos
    """
    return [
        "sklearn.*",
        "tensorflow.keras.*",
        "torch.nn.*",
        "xgboost.*",
        "lightgbm.*",
        "generic (any object with predict method)"
    ]


def get_validation_config() -> Dict[str, Any]:
    """
    Retorna configuración actual de validación.

    Returns:
        Dict con configuración de validación
    """
    return {
        "required_methods": REQUIRED_MODEL_METHODS,
        "sklearn_fitted_attributes": SKLEARN_FITTED_ATTRIBUTES,
        "valid_prediction_types": [t.__name__ for t in VALID_PREDICTION_TYPES],
        "supported_model_types": get_supported_model_types(),
        "version": "2.0.0"
    }
