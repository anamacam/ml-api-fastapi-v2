"""
🔧 Excepciones Personalizadas del Sistema

Implementación siguiendo principios SOLID y Clean Code:
- Single Responsibility: Cada excepción tiene una responsabilidad específica
- Open/Closed: Fácil extensión sin modificar código existente
- Interface Segregation: Excepciones específicas para casos específicos
- Dependency Inversion: Dependencias abstractas, no concretas

Patrones aplicados:
- Factory Pattern: Para creación de excepciones con contexto
- Strategy Pattern: Para diferentes tipos de manejo de errores
"""

from typing import Optional, Dict, Any, Union
from datetime import datetime
import json


class BaseAppException(Exception):
    """
    Excepción base para toda la aplicación.

    Aplica principios SOLID:
    - Single Responsibility: Manejo centralizado de errores
    - Open/Closed: Extensible sin modificar código existente
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.context = context or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convertir excepción a diccionario para serialización"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "context": self.context,
            "timestamp": self.timestamp.isoformat()
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"


class ModelError(BaseAppException):
    """Excepción base para errores relacionados con modelos ML"""
    pass


class ModelNotFoundError(ModelError):
    """Error cuando no se encuentra un modelo específico"""

    def __init__(self, model_id: str, available_models: Optional[list] = None):
        message = f"Modelo '{model_id}' no encontrado"
        details = {
            "model_id": model_id,
            "available_models": available_models or []
        }
        super().__init__(message, "MODEL_NOT_FOUND", details)


class ModelLoadError(ModelError):
    """Error al cargar un modelo ML"""

    def __init__(self, model_path: str, original_error: Optional[str] = None):
        message = f"Error cargando modelo desde '{model_path}'"
        details = {
            "model_path": model_path,
            "original_error": original_error
        }
        super().__init__(message, "MODEL_LOAD_ERROR", details)


class ModelValidationError(ModelError):
    """Error de validación de modelo ML"""

    def __init__(self, validation_errors: list, model_info: Optional[Dict[str, Any]] = None):
        message = f"Error de validación del modelo: {len(validation_errors)} errores encontrados"
        details = {
            "validation_errors": validation_errors,
            "model_info": model_info or {}
        }
        super().__init__(message, "MODEL_VALIDATION_ERROR", details)


class PredictionError(BaseAppException):
    """Error durante la predicción"""

    def __init__(self, model_id: str, input_data: Optional[Dict[str, Any]] = None,
                 original_error: Optional[str] = None):
        message = f"Error durante predicción con modelo '{model_id}'"
        details = {
            "model_id": model_id,
            "input_data": input_data,
            "original_error": original_error
        }
        super().__init__(message, "PREDICTION_ERROR", details)


class DataValidationError(BaseAppException):
    """Error de validación de datos de entrada"""

    def __init__(self, field_errors: Dict[str, list], input_data: Optional[Dict[str, Any]] = None):
        message = f"Error de validación de datos: {len(field_errors)} campos inválidos"
        details = {
            "field_errors": field_errors,
            "input_data": input_data
        }
        super().__init__(message, "DATA_VALIDATION_ERROR", details)


class ConfigurationError(BaseAppException):
    """Error de configuración del sistema"""

    def __init__(self, config_key: str, expected_type: Optional[str] = None,
                 current_value: Optional[Any] = None):
        message = f"Error de configuración en '{config_key}'"
        details = {
            "config_key": config_key,
            "expected_type": expected_type,
            "current_value": str(current_value) if current_value is not None else None
        }
        super().__init__(message, "CONFIGURATION_ERROR", details)


class DatabaseError(BaseAppException):
    """Error de base de datos"""

    def __init__(self, operation: str, table: Optional[str] = None,
                 original_error: Optional[str] = None):
        message = f"Error de base de datos en operación '{operation}'"
        details = {
            "operation": operation,
            "table": table,
            "original_error": original_error
        }
        super().__init__(message, "DATABASE_ERROR", details)


class AuthenticationError(BaseAppException):
    """Error de autenticación"""

    def __init__(self, user_id: Optional[str] = None, reason: Optional[str] = None):
        message = "Error de autenticación"
        if reason:
            message += f": {reason}"
        details = {
            "user_id": user_id,
            "reason": reason
        }
        super().__init__(message, "AUTHENTICATION_ERROR", details)


class AuthorizationError(BaseAppException):
    """Error de autorización"""

    def __init__(self, user_id: str, required_permission: str,
                 user_permissions: Optional[list] = None):
        message = f"Usuario '{user_id}' no tiene permiso '{required_permission}'"
        details = {
            "user_id": user_id,
            "required_permission": required_permission,
            "user_permissions": user_permissions or []
        }
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class RateLimitError(BaseAppException):
    """Error de límite de tasa excedido"""

    def __init__(self, user_id: str, endpoint: str, limit: int,
                 current_usage: int, reset_time: Optional[datetime] = None):
        message = f"Límite de tasa excedido para endpoint '{endpoint}'"
        details = {
            "user_id": user_id,
            "endpoint": endpoint,
            "limit": limit,
            "current_usage": current_usage,
            "reset_time": reset_time.isoformat() if reset_time else None
        }
        super().__init__(message, "RATE_LIMIT_ERROR", details)


class SecurityError(BaseAppException):
    """Error de seguridad"""

    def __init__(self, threat_type: str, severity: str = "medium",
                 details: Optional[Dict[str, Any]] = None):
        message = f"Error de seguridad detectado: {threat_type}"
        security_details = {
            "threat_type": threat_type,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
        if details:
            security_details.update(details)
        super().__init__(message, "SECURITY_ERROR", security_details)


# Factory Pattern para creación de excepciones
class ExceptionFactory:
    """
    Factory para crear excepciones con contexto apropiado.

    Aplica Factory Pattern para centralizar la creación de excepciones
    y asegurar consistencia en el manejo de errores.
    """

    @staticmethod
    def create_model_error(error_type: str, **kwargs) -> ModelError:
        """Crear error de modelo específico"""
        error_map = {
            "not_found": ModelNotFoundError,
            "load_error": ModelLoadError,
            "validation_error": ModelValidationError
        }

        error_class = error_map.get(error_type, ModelError)
        return error_class(**kwargs)

    @staticmethod
    def create_prediction_error(model_id: str, **kwargs) -> PredictionError:
        """Crear error de predicción con contexto"""
        return PredictionError(model_id=model_id, **kwargs)

    @staticmethod
    def create_validation_error(field_errors: Dict[str, list], **kwargs) -> DataValidationError:
        """Crear error de validación de datos"""
        return DataValidationError(field_errors=field_errors, **kwargs)

    @staticmethod
    def create_security_error(threat_type: str, **kwargs) -> SecurityError:
        """Crear error de seguridad"""
        return SecurityError(threat_type=threat_type, **kwargs)


# Strategy Pattern para manejo de errores
class ErrorHandlingStrategy:
    """
    Estrategia base para manejo de errores.

    Aplica Strategy Pattern para diferentes tipos de manejo de errores
    según el contexto y tipo de aplicación.
    """

    def handle_error(self, error: BaseAppException) -> Dict[str, Any]:
        """Manejar error según la estrategia"""
        raise NotImplementedError("Subclases deben implementar handle_error")


class LoggingErrorStrategy(ErrorHandlingStrategy):
    """Estrategia que solo registra errores"""

    def __init__(self, logger):
        self.logger = logger

    def handle_error(self, error: BaseAppException) -> Dict[str, Any]:
        """Registrar error y retornar información básica"""
        self.logger.error(f"Error manejado: {error}")
        return {
            "error_type": error.__class__.__name__,
            "message": error.message,
            "timestamp": error.timestamp.isoformat()
        }


class DetailedErrorStrategy(ErrorHandlingStrategy):
    """Estrategia que proporciona detalles completos del error"""

    def handle_error(self, error: BaseAppException) -> Dict[str, Any]:
        """Retornar información detallada del error"""
        return error.to_dict()


class ProductionErrorStrategy(ErrorHandlingStrategy):
    """Estrategia para producción - información limitada"""

    def handle_error(self, error: BaseAppException) -> Dict[str, Any]:
        """Retornar información limitada para producción"""
        return {
            "error_type": error.__class__.__name__,
            "message": "An error occurred. Please contact support.",
            "error_code": error.error_code,
            "timestamp": error.timestamp.isoformat()
        }
