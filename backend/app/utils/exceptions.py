# -*- coding: utf-8 -*-
"""
Excepciones personalizadas para la aplicación ML API.

Este módulo define una jerarquía completa de excepciones personalizadas
para diferentes tipos de errores que pueden ocurrir en la aplicación.

Ejemplos de uso:
    >>> from app.utils.exceptions import ModelNotFoundError, PredictionError
    >>>
    >>> # Error cuando un modelo no existe
    >>> try:
    ...     model = load_model("inexistent_model")
    ... except ModelNotFoundError as e:
    ...     print(f"Error: {e.message}")
    ...     print(f"Modelos disponibles: {e.details['available_models']}")
    >>>
    >>> # Error durante predicción
    >>> try:
    ...     prediction = model.predict(invalid_data)
    ... except PredictionError as e:
    ...     print(f"Error en predicción: {e.message}")
    ...     print(f"Modelo usado: {e.details['model_id']}")
"""

import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ErrorSeverity(Enum):
    """
    Niveles de severidad para errores.

    Permite clasificar errores por su impacto en el sistema:
    - LOW: Errores menores que no afectan funcionalidad crítica
    - MEDIUM: Errores que pueden afectar algunas funcionalidades
    - HIGH: Errores críticos que pueden comprometer el sistema
    - CRITICAL: Errores que requieren atención inmediata
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaseAppException(Exception):
    """
    Excepción base para toda la aplicación.

    Proporciona funcionalidad común para todas las excepciones:
    - Timestamping automático
    - Contexto adicional
    - Serialización a diccionario
    - Logging estructurado

    Attributes:
        message (str): Mensaje de error legible
        error_code (str): Código de error único
        details (Dict): Contexto adicional del error
        timestamp (datetime): Momento cuando ocurrió el error
        severity (ErrorSeverity): Nivel de severidad

    Examples:
        >>> error = BaseAppException("Error general", "GENERAL_ERROR")
        >>> print(error.to_dict())
        {
            'message': 'Error general',
            'error_code': 'GENERAL_ERROR',
            'details': {},
            'timestamp': '2024-01-15T10:30:00.123456',
            'severity': 'medium'
        }
    """

    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        self.severity = severity
        self.traceback = traceback.format_exc()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializar excepción a diccionario.

        Útil para logging estructurado y APIs REST.

        Returns:
            Dict con toda la información del error
        """
        return {
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "traceback": (
                self.traceback if self.traceback != "NoneType: None\n" else None
            ),
        }

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


# === EXCEPCIONES ESPECÍFICAS DE MODELOS ML ===


class ModelError(BaseAppException):
    """
    Excepción base para errores relacionados con modelos ML.

    Agrupa todos los errores relacionados con la gestión de modelos:
    carga, validación, entrenamiento, etc.
    """

    def __init__(self, message: str, error_code: str = "MODEL_ERROR", **kwargs):
        super().__init__(message, error_code, severity=ErrorSeverity.HIGH, **kwargs)


class ModelNotFoundError(ModelError):
    """
    Error cuando no se encuentra un modelo específico.

    Este error ocurre cuando:
    - Se solicita un modelo que no existe en el registry
    - El archivo del modelo fue eliminado del sistema de archivos
    - El modelo existe pero no está disponible temporalmente

    Attributes:
        model_id (str): ID del modelo solicitado
        available_models (List[str]): Lista de modelos disponibles

    Examples:
        >>> # Caso típico: modelo no encontrado
        >>> try:
        ...     model = model_registry.get_model("gpt-5")
        ... except ModelNotFoundError as e:
        ...     print(f"Modelo {e.details['model_id']} no encontrado")
        ...     print(f"Disponibles: {e.details['available_models']}")

        >>> # Para APIs REST
        >>> return {
        ...     "error": e.to_dict(),
        ...     "suggestions": e.details['available_models'][:3]  # Top 3
        ... }
    """

    def __init__(self, model_id: str, available_models: Optional[List[str]] = None):
        message = f"Modelo '{model_id}' no encontrado"
        if available_models:
            message += f". Modelos disponibles: {', '.join(available_models[:3])}"
            if len(available_models) > 3:
                message += f" y {len(available_models) - 3} más"

        details = {
            "model_id": model_id,
            "available_models": available_models or [],
            "error_type": "model_not_found",
            "suggested_action": "Verificar ID del modelo o usar uno de los disponibles",
        }
        super().__init__(message, "MODEL_NOT_FOUND", details=details)


class ModelLoadError(ModelError):
    """
    Error al cargar un modelo ML desde disco.

    Este error ocurre cuando:
    - El archivo del modelo está corrupto
    - Falta memoria para cargar el modelo
    - El formato del modelo no es compatible
    - Faltan dependencias requeridas por el modelo

    Attributes:
        model_path (str): Ruta del modelo que falló al cargar
        original_error (str): Error original del sistema
        model_size_mb (float): Tamaño del modelo en MB (si disponible)

    Examples:
        >>> # Modelo corrupto
        >>> try:
        ...     model = joblib.load("/models/corrupted_model.pkl")
        ... except Exception as e:
        ...     raise ModelLoadError(
        ...         "/models/corrupted_model.pkl",
        ...         original_error=str(e)
        ...     )

        >>> # Manejo en servicio
        >>> try:
        ...     self._load_model(model_path)
        ... except ModelLoadError as e:
        ...     logger.error(f"Failed to load model: {e.to_dict()}")
        ...     # Intentar modelo de fallback
        ...     self._load_fallback_model()
    """

    def __init__(
        self,
        model_path: str,
        original_error: Optional[str] = None,
        model_size_mb: Optional[float] = None,
    ):
        message = f"Error cargando modelo desde '{model_path}'"
        if original_error:
            message += f": {original_error}"

        details = {
            "model_path": model_path,
            "original_error": original_error,
            "model_size_mb": model_size_mb,
            "error_type": "model_load_failed",
            "suggested_actions": [
                "Verificar que el archivo existe y no está corrupto",
                "Comprobar memoria disponible del sistema",
                "Validar formato del modelo",
                "Verificar dependencias requeridas",
            ],
        }
        super().__init__(message, "MODEL_LOAD_ERROR", details=details)


class ModelValidationError(ModelError):
    """
    Error de validación de modelo ML.

    Este error ocurre cuando:
    - El modelo no tiene los métodos requeridos (predict, etc.)
    - El modelo no está entrenado (fitted)
    - La salida del modelo no tiene el formato esperado
    - Los metadatos del modelo son inconsistentes

    Attributes:
        validation_errors (List[str]): Lista de errores encontrados
        model_info (Dict): Información del modelo validado

    Examples:
        >>> # Modelo no entrenado
        >>> errors = ["Model not fitted", "Missing predict method"]
        >>> model_info = {"type": "sklearn", "version": "1.0"}
        >>> raise ModelValidationError(errors, model_info)

        >>> # En pipeline de validación
        >>> validation_result = validate_model(model)
        >>> if not validation_result.is_valid:
        ...     raise ModelValidationError(
        ...         validation_result.errors,
        ...         validation_result.model_info
        ...     )
    """

    def __init__(
        self, validation_errors: List[str], model_info: Optional[Dict[str, Any]] = None
    ):
        error_count = len(validation_errors)
        message = f"Error de validación del modelo: {error_count} errores encontrados"

        details = {
            "validation_errors": validation_errors,
            "model_info": model_info or {},
            "error_count": error_count,
            "error_type": "model_validation_failed",
            "suggested_actions": [
                "Revisar que el modelo esté entrenado (fitted)",
                "Verificar métodos requeridos (predict, etc.)",
                "Validar formato de salida del modelo",
                "Comprobar metadatos del modelo",
            ],
        }
        super().__init__(message, "MODEL_VALIDATION_ERROR", details=details)


# === EXCEPCIONES DE PREDICCIÓN ===


class PredictionError(BaseAppException):
    """
    Error durante la predicción ML.

    Este error ocurre cuando:
    - Los datos de entrada no tienen el formato correcto
    - El modelo falla durante la predicción
    - Hay incompatibilidad entre entrada y modelo
    - Timeout durante la predicción

    Attributes:
        model_id (str): ID del modelo usado
        input_data (Dict): Datos de entrada (sanitizados)
        original_error (str): Error original del modelo
        prediction_context (Dict): Contexto adicional de la predicción

    Examples:
        >>> # Error de formato de entrada
        >>> try:
        ...     prediction = model.predict(malformed_data)
        ... except Exception as e:
        ...     raise PredictionError(
        ...         model_id="lgbm_v1",
        ...         input_data={"shape": malformed_data.shape},
        ...         original_error=str(e)
        ...     )

        >>> # En servicio híbrido con fallback
        >>> try:
        ...     result = primary_model.predict(data)
        ... except PredictionError as e:
        ...     logger.warning(f"Primary model failed: {e.message}")
        ...     result = fallback_model.predict(data)
        ...     result["used_fallback"] = True
        ...     result["primary_error"] = e.to_dict()
    """

    def __init__(
        self,
        model_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        original_error: Optional[str] = None,
        prediction_context: Optional[Dict[str, Any]] = None,
    ):
        message = f"Error durante predicción con modelo '{model_id}'"
        if original_error:
            message += f": {original_error}"

        # Sanitizar input_data para logging (remover datos sensibles)
        safe_input_data = None
        if input_data:
            safe_input_data = {
                k: v if k not in ["password", "token", "key"] else "[REDACTED]"
                for k, v in input_data.items()
            }

        details = {
            "model_id": model_id,
            "input_data": safe_input_data,
            "original_error": original_error,
            "prediction_context": prediction_context or {},
            "error_type": "prediction_failed",
            "suggested_actions": [
                "Verificar formato de datos de entrada",
                "Comprobar compatibilidad con el modelo",
                "Revisar logs del modelo para más detalles",
                "Intentar con modelo de fallback si disponible",
            ],
        }
        super().__init__(
            message, "PREDICTION_ERROR", details=details, severity=ErrorSeverity.MEDIUM
        )


# === EXCEPCIONES DE VALIDACIÓN DE DATOS ===


class DataValidationError(BaseAppException):
    """
    Error de validación de datos de entrada.

    Examples:
        >>> field_errors = {
        ...     "age": ["Debe ser un número positivo"],
        ...     "email": ["Formato de email inválido"]
        ... }
        >>> raise DataValidationError(field_errors)
    """

    def __init__(
        self,
        field_errors: Dict[str, List[str]],
        input_data: Optional[Dict[str, Any]] = None,
    ):
        error_count = sum(len(errors) for errors in field_errors.values())
        message = f"Error de validación de datos inválidos: {error_count} errores en {len(field_errors)} campos"  # noqa: E501

        details = {
            "field_errors": field_errors,
            "input_data": input_data,
            "error_count": error_count,
            "affected_fields": list(field_errors.keys()),
        }
        super().__init__(
            message,
            "DATA_VALIDATION_ERROR",
            details=details,
            severity=ErrorSeverity.LOW,
        )


# === EXCEPCIONES DE CONFIGURACIÓN ===


class ConfigurationError(BaseAppException):
    """
    Error de configuración del sistema.

    Examples:
        >>> raise ConfigurationError(
        ...     "Database URL not configured",
        ...     missing_keys=["DATABASE_URL"],
        ...     config_file="settings.py"
        ... )
    """

    def __init__(
        self,
        message: str,
        missing_keys: Optional[List[str]] = None,
        config_file: Optional[str] = None,
    ):
        details = {
            "missing_keys": missing_keys or [],
            "config_file": config_file,
            "error_type": "configuration_error",
        }
        super().__init__(
            message, "CONFIGURATION_ERROR", details=details, severity=ErrorSeverity.HIGH
        )


# === EXCEPCIONES DE SEGURIDAD ===


class SecurityError(BaseAppException):
    """
    Error de seguridad del sistema.

    Examples:
        >>> raise SecurityError(
        ...     "Unauthorized access attempt",
        ...     threat_type="unauthorized_access",
        ...     user_id="user123",
        ...     ip_address="192.168.1.100"
        ... )
    """

    def __init__(self, message: str, threat_type: str, **context):
        details = {
            "threat_type": threat_type,
            "context": context,
            "error_type": "security_violation",
        }
        super().__init__(
            message, "SECURITY_ERROR", details=details, severity=ErrorSeverity.CRITICAL
        )


# === FACTORY PATTERN PARA CREACIÓN DE EXCEPCIONES ===


class ExceptionFactory:
    """
    Factory para crear excepciones con contexto apropiado.

    Aplica Factory Pattern para centralizar la creación de excepciones
    y asegurar consistencia en el manejo de errores.

    Examples:
        >>> # Crear error de modelo no encontrado
        >>> error = ExceptionFactory.create_model_error(
        ...     "not_found",
        ...     model_id="gpt-4",
        ...     available_models=["gpt-3", "bert"]
        ... )

        >>> # Crear error de predicción con contexto
        >>> error = ExceptionFactory.create_prediction_error(
        ...     model_id="lgbm_v1",
        ...     input_data={"features": 10},
        ...     original_error="Shape mismatch"
        ... )
    """

    @staticmethod
    def create_model_error(error_type: str, **kwargs) -> ModelError:
        """
        Crear error de modelo específico.

        Args:
            error_type: Tipo de error ("not_found", "load_error", "validation_error")
            **kwargs: Argumentos específicos para cada tipo de error

        Returns:
            ModelError: Instancia de la excepción apropiada

        Examples:
            >>> error = ExceptionFactory.create_model_error(
            ...     "not_found",
            ...     model_id="missing_model",
            ...     available_models=["model1", "model2"]
            ... )
        """
        error_map = {
            "not_found": ModelNotFoundError,
            "load_error": ModelLoadError,
            "validation_error": ModelValidationError,
        }

        error_class = error_map.get(error_type, ModelError)
        return error_class(**kwargs)

    @staticmethod
    def create_prediction_error(model_id: str, **kwargs) -> PredictionError:
        """
        Crear error de predicción con contexto.

        Args:
            model_id: ID del modelo que falló
            **kwargs: Contexto adicional del error

        Returns:
            PredictionError: Instancia con contexto completo
        """
        return PredictionError(model_id=model_id, **kwargs)

    @staticmethod
    def create_validation_error(
        field_errors: Dict[str, List[str]], **kwargs
    ) -> DataValidationError:
        """
        Crear error de validación de datos.

        Args:
            field_errors: Errores por campo
            **kwargs: Contexto adicional

        Returns:
            DataValidationError: Instancia con errores estructurados
        """
        return DataValidationError(field_errors=field_errors, **kwargs)

    @staticmethod
    def create_security_error(threat_type: str, **kwargs) -> SecurityError:
        """
        Crear error de seguridad.

        Args:
            threat_type: Tipo de amenaza detectada
            **kwargs: Contexto de seguridad

        Returns:
            SecurityError: Instancia con contexto de seguridad
        """
        return SecurityError(threat_type=threat_type, **kwargs)
