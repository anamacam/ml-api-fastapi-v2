# -*- coding: utf-8 -*-
"""
Manejadores de errores para la API FastAPI.

Este módulo contiene funciones para traducir errores internos del servicio
a respuestas HTTP apropiadas.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException

from app.models.api_models import ValidationDetails


def handle_prediction_error(error: Dict[str, Any]) -> HTTPException:
    """
    Traduce un error clasificado por el servicio a una HTTPException de FastAPI.
    
    Args:
        error: Diccionario con información del error
        
    Returns:
        HTTPException apropiada según el tipo de error
    """
    error_type = error.get("error_type", "")
    
    error_mapping = {
        "input_validation": (422, error),
        "model_not_found": (404, error),
        "prediction_failed": (500, error),
    }
    
    status_code, detail = error_mapping.get(error_type, (500, "Error interno de predicción."))
    return HTTPException(status_code=status_code, detail=detail)


def build_validation_details(
    request_include_details: bool, 
    result: Dict[str, Any]
) -> Optional[ValidationDetails]:
    """
    Construye el objeto de detalles de validación si fue solicitado.
    
    Args:
        request_include_details: Si el cliente solicitó detalles de validación
        result: Resultado de la predicción con detalles
        
    Returns:
        ValidationDetails si fue solicitado, None en caso contrario
    """
    if not request_include_details:
        return None

    details = result.get("validation_details", {})
    return ValidationDetails(
        input_valid=details.get("input_valid", False),
        model_valid=details.get("model_valid", False),
    )


def handle_service_error(service_name: str, error: Exception) -> HTTPException:
    """
    Maneja errores genéricos de servicios y los convierte en HTTPExceptions.
    
    Args:
        service_name: Nombre del servicio que falló
        error: Excepción original
        
    Returns:
        HTTPException con mensaje apropiado
    """
    error_message = f"Error interno en {service_name}: {str(error)}"
    return HTTPException(status_code=500, detail=error_message) 