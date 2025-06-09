"""
Validadores para entrada de predicciones ML.

Sistema de validación robusto y extensible para datos de entrada
de modelos de machine learning.

Refactorizado: código limpio, modular y mantenible.
"""

from typing import Dict, Any, List, Union, Optional
import logging

# Configuración del logger
logger = logging.getLogger(__name__)

# Configuración de validación
REQUIRED_FIELDS = ["age", "income", "category", "score"]

# Tipos esperados para cada campo
FIELD_TYPES = {
    "age": (int, float),
    "income": (int, float), 
    "category": str,
    "score": (int, float)
}

# Rangos válidos para campos numéricos
NUMERIC_RANGES = {
    "age": (0, 150),        # Edad entre 0 y 150 años
    "income": (0, float('inf')),  # Ingreso no negativo
    "score": (0.0, 1.0)     # Score entre 0 y 1
}


class ValidationError:
    """Tipos de errores de validación."""
    EMPTY_DATA = "empty"
    INVALID_TYPES = "invalid_types" 
    MISSING_FIELDS = "missing_fields"
    OUT_OF_RANGE = "out_of_range"


def validate_prediction_input(data: Any) -> Dict[str, Any]:
    """
    Valida datos de entrada para predicciones ML.
    
    Realiza validación completa de:
    - Datos no vacíos
    - Tipos de datos correctos
    - Campos requeridos presentes
    - Rangos numéricos válidos
    
    Args:
        data: Datos de entrada para validar
        
    Returns:
        Dict con 'valid' (bool) y opcionalmente 'error' y 'missing_fields'
        
    Examples:
        >>> validate_prediction_input(None)
        {'valid': False, 'error': 'Data is empty or None'}
        
        >>> validate_prediction_input({'age': 25, 'income': 50000.0, 'category': 'premium', 'score': 0.85})
        {'valid': True}
    """
    try:
        # Validar datos no vacíos
        empty_result = _validate_not_empty(data)
        if not empty_result["valid"]:
            return empty_result
        
        # Validar tipos de datos
        types_result = _validate_field_types(data)
        if not types_result["valid"]:
            return types_result
            
        # Validar campos requeridos
        required_result = _validate_required_fields(data)
        if not required_result["valid"]:
            return required_result
            
        # Validar rangos numéricos
        ranges_result = _validate_numeric_ranges(data)
        if not ranges_result["valid"]:
            return ranges_result
            
        # Todo válido
        logger.info("Validation successful for prediction input")
        return {"valid": True}
        
    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}")
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}"
        }


def _validate_not_empty(data: Any) -> Dict[str, Any]:
    """Valida que los datos no estén vacíos."""
    if data is None:
        return {
            "valid": False,
            "error": "Data is empty or None"
        }
    
    if isinstance(data, dict) and len(data) == 0:
        return {
            "valid": False,
            "error": "Data dictionary is empty"
        }
    
    return {"valid": True}


def _validate_field_types(data: Any) -> Dict[str, Any]:
    """Valida que los tipos de campos sean correctos."""
    if not isinstance(data, dict):
        return {"valid": True}  # Skip if not dict
    
    for field_name, expected_types in FIELD_TYPES.items():
        if field_name in data:
            value = data[field_name]
            if not isinstance(value, expected_types):
                return {
                    "valid": False,
                    "error": f"invalid_types: {field_name} must be {expected_types}"
                }
    
    return {"valid": True}


def _validate_required_fields(data: Any) -> Dict[str, Any]:
    """Valida que estén presentes los campos requeridos."""
    if not isinstance(data, dict):
        return {"valid": True}  # Skip if not dict
    
    missing_fields = []
    for field in REQUIRED_FIELDS:
        if field not in data:
            missing_fields.append(field)
    
    if missing_fields:
        return {
            "valid": False,
            "error": "missing_fields detected",
            "missing_fields": missing_fields
        }
    
    return {"valid": True}


def _validate_numeric_ranges(data: Any) -> Dict[str, Any]:
    """Valida que los valores numéricos estén en rangos válidos."""
    if not isinstance(data, dict):
        return {"valid": True}  # Skip if not dict
    
    for field_name, (min_val, max_val) in NUMERIC_RANGES.items():
        if field_name in data:
            value = data[field_name]
            if isinstance(value, (int, float)):
                if value < min_val or value > max_val:
                    return {
                        "valid": False,
                        "error": f"out_of_range: {field_name} must be between {min_val} and {max_val}"
                    }
    
    return {"valid": True}


def get_validation_schema() -> Dict[str, Any]:
    """
    Retorna el schema de validación actual.
    
    Útil para documentación y debugging.
    
    Returns:
        Dict con configuración de validación
    """
    return {
        "required_fields": REQUIRED_FIELDS,
        "field_types": {k: str(v) for k, v in FIELD_TYPES.items()},
        "numeric_ranges": NUMERIC_RANGES,
        "version": "1.0.0"
    }
