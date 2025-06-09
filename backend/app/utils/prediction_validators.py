"""
Validadores para entrada de predicciones ML.

Implementación mínima para satisfacer tests TDD.
Fase GREEN: código mínimo para pasar tests.
"""

from typing import Dict, Any, List


def validate_prediction_input(data: Any) -> Dict[str, Any]:
    """
    Valida datos de entrada para predicciones ML.
    
    Args:
        data: Datos de entrada para validar
        
    Returns:
        Dict con 'valid' (bool) y opcionalmente 'error' y 'missing_fields'
    """
    # Test 1: Rechazar datos vacíos
    if data is None:
        return {
            "valid": False,
            "error": "Data is empty or None"
        }
    
    # Test 2: Rechazar features inválidas (tipos incorrectos)
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "age" and not isinstance(value, (int, float)):
                return {
                    "valid": False,
                    "error": "invalid_types: age must be numeric"
                }
            elif key == "income" and not isinstance(value, (int, float)):
                return {
                    "valid": False,
                    "error": "invalid_types: income must be numeric"
                }
            elif key == "category" and not isinstance(value, str):
                return {
                    "valid": False,
                    "error": "invalid_types: category must be string"
                }
    
    # Test 4: Detectar campos requeridos faltantes
    if isinstance(data, dict):
        required_fields = ["age", "income", "category", "score"]
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            return {
                "valid": False,
                "error": "missing_fields detected",
                "missing_fields": missing_fields
            }
    
    # Test 5: Validar rangos numéricos
    if isinstance(data, dict):
        if "age" in data and data["age"] < 0:
            return {
                "valid": False,
                "error": "out_of_range: age cannot be negative"
            }
        if "income" in data and data["income"] < 0:
            return {
                "valid": False, 
                "error": "out_of_range: income cannot be negative"
            }
        if "score" in data and (data["score"] < 0 or data["score"] > 1.0):
            return {
                "valid": False,
                "error": "out_of_range: score must be between 0 and 1"
            }
    
    # Test 3: Aceptar features válidas
    return {
        "valid": True
    } 