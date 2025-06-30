# -*- coding: utf-8 -*-
"""
🛡️ Manejadores de errores centralizados

Utilidades para manejo consistente de errores en toda la aplicación,
proporcionando respuestas estructuradas y logging apropiado.
"""

# 🚨 ====== COPILOTO/CURSOR: MANEJO SEGURO DE ERRORES ====== 🚨
#
# 🔐 SEGURIDAD CRÍTICA - NO exponer información sensible:
#    ❌ PROHIBIDO: Stack traces completos al cliente
#    ❌ PROHIBIDO: Rutas de archivos del servidor
#    ❌ PROHIBIDO: Detalles de base de datos (esquemas, tablas)
#    ❌ PROHIBIDO: Configuración interna del sistema
#    ❌ PROHIBIDO: Credenciales en logs de error
#
# ✅ MANEJO SEGURO OBLIGATORIO:
#    ✅ Logs detallados SOLO en servidor (no al cliente)
#    ✅ Mensajes genéricos al cliente ("Error interno del servidor")
#    ✅ Error IDs únicos para correlacionar logs con requests
#    ✅ Sanitizar inputs antes de logging
#    ✅ Diferentes niveles de detalle por entorno (dev vs prod)
#
# 🏗️ PRINCIPIOS DE ERROR HANDLING:
#    ✅ DRY: Handlers centralizados, no duplicar lógica
#    ✅ KISS: Respuestas simples y consistentes
#    ✅ Single Responsibility: Un handler por tipo de error
#
# 🧪 TDD PARA ERROR HANDLERS:
#    🔴 RED: Tests que verifiquen que NO se expone info sensible
#    🟢 GREEN: Implementación que pase tests de seguridad
#    🔵 REFACTOR: Mejorar estructura sin exponer datos
#
# 📊 LOGGING LEVELS CORRECTOS:
#    🔴 ERROR: Errores críticos del sistema
#    🟡 WARNING: Problemas recuperables
#    🔵 INFO: Flujo normal de la aplicación
#    ⚪ DEBUG: Detalles técnicos (SOLO en development)
#
# ⚠️ EJEMPLOS INCORRECTOS:
#    ❌ return {"error": f"Database error: {str(db_exception)}"}
#    ❌ logging.error(f"User password: {password}")
#    ❌ {"detail": f"File not found: /etc/secrets/api_keys.txt"}
#
# ✅ EJEMPLOS CORRECTOS:
#    ✅ return {"error": "Error interno del servidor", "error_id": "ERR-123"}
#    ✅ logging.error(f"Database connection failed", extra={"error_id": error_id})
#    ✅ {"detail": "Recurso no encontrado", "error_code": "RESOURCE_NOT_FOUND"}
#
# 📚 REFERENCIA: /RULES.md sección "🔐 REGLAS DE SEGURIDAD"
# 
# =============================================================

from typing import Any, Dict, List, Optional, Union
import logging
import uuid

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