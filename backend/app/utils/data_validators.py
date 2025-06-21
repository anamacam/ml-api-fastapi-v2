"""
🔍 Sistema de Validación de Datos Avanzado

Implementación siguiendo principios SOLID y Clean Code:
- Single Responsibility: Cada validador tiene una responsabilidad específica
- Open/Closed: Extensible sin modificar código existente
- Liskov Substitution: Validadores intercambiables
- Interface Segregation: Interfaces específicas para cada tipo de validación
- Dependency Inversion: Dependencias abstractas

Patrones aplicados:
- Strategy Pattern: Para diferentes tipos de validación
- Chain of Responsibility: Para validaciones en cadena
- Factory Pattern: Para creación de validadores
- Template Method: Para flujos de validación estandarizados
- Decorator Pattern: Para validaciones adicionales
"""

import re
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, date
import numpy as np
import pandas as pd
from pathlib import Path

from ..utils.exceptions import DataValidationError
from ..core.security_logger import SecurityEventFactory, SecurityLevel, get_security_logger


class ValidationSeverity(Enum):
    """Niveles de severidad para validaciones"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Resultado de una validación"""
    is_valid: bool
    field_name: str
    value: Any
    severity: ValidationSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            "is_valid": self.is_valid,
            "field_name": self.field_name,
            "value": str(self.value),
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class Validator(ABC):
    """
    Validador abstracto base.

    Aplica Strategy Pattern para diferentes tipos de validación.
    """

    def __init__(self, field_name: str, severity: ValidationSeverity = ValidationSeverity.ERROR):
        self.field_name = field_name
        self.severity = severity

    @abstractmethod
    def validate(self, value: Any) -> ValidationResult:
        """Validar valor y retornar resultado"""
        pass

    def __call__(self, value: Any) -> ValidationResult:
        """Permitir usar el validador como función"""
        return self.validate(value)


class TypeValidator(Validator):
    """Validador de tipos de datos"""

    def __init__(self, field_name: str, expected_type: type, severity: ValidationSeverity = ValidationSeverity.ERROR):
        super().__init__(field_name, severity)
        self.expected_type = expected_type

    def validate(self, value: Any) -> ValidationResult:
        """Validar tipo de dato"""
        is_valid = isinstance(value, self.expected_type)
        message = f"Expected {self.expected_type.__name__}, got {type(value).__name__}"

        return ValidationResult(
            is_valid=is_valid,
            field_name=self.field_name,
            value=value,
            severity=self.severity,
            message=message if not is_valid else "Type validation passed",
            details={"expected_type": self.expected_type.__name__, "actual_type": type(value).__name__}
        )


class RangeValidator(Validator):
    """Validador de rangos numéricos"""

    def __init__(self, field_name: str, min_value: Optional[float] = None,
                 max_value: Optional[float] = None, severity: ValidationSeverity = ValidationSeverity.ERROR):
        super().__init__(field_name, severity)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> ValidationResult:
        """Validar rango numérico"""
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return ValidationResult(
                is_valid=False,
                field_name=self.field_name,
                value=value,
                severity=self.severity,
                message=f"Value must be numeric",
                details={"value": value}
            )

        errors = []
        if self.min_value is not None and num_value < self.min_value:
            errors.append(f"Value {num_value} is below minimum {self.min_value}")

        if self.max_value is not None and num_value > self.max_value:
            errors.append(f"Value {num_value} is above maximum {self.max_value}")

        is_valid = len(errors) == 0
        message = "; ".join(errors) if errors else "Range validation passed"

        return ValidationResult(
            is_valid=is_valid,
            field_name=self.field_name,
            value=value,
            severity=self.severity,
            message=message,
            details={
                "min_value": self.min_value,
                "max_value": self.max_value,
                "actual_value": num_value,
                "errors": errors
            }
        )


class StringValidator(Validator):
    """Validador de cadenas de texto"""

    def __init__(self, field_name: str, min_length: Optional[int] = None,
                 max_length: Optional[int] = None, pattern: Optional[str] = None,
                 allowed_values: Optional[List[str]] = None,
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        super().__init__(field_name, severity)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.allowed_values = allowed_values

    def validate(self, value: Any) -> ValidationResult:
        """Validar cadena de texto"""
        if not isinstance(value, str):
            return ValidationResult(
                is_valid=False,
                field_name=self.field_name,
                value=value,
                severity=self.severity,
                message="Value must be a string",
                details={"expected_type": "str", "actual_type": type(value).__name__}
            )

        errors = []

        # Validar longitud
        if self.min_length is not None and len(value) < self.min_length:
            errors.append(f"String length {len(value)} is below minimum {self.min_length}")

        if self.max_length is not None and len(value) > self.max_length:
            errors.append(f"String length {len(value)} is above maximum {self.max_length}")

        # Validar patrón regex
        if self.pattern and not re.match(self.pattern, value):
            errors.append(f"String does not match pattern {self.pattern}")

        # Validar valores permitidos
        if self.allowed_values and value not in self.allowed_values:
            errors.append(f"Value '{value}' is not in allowed values: {self.allowed_values}")

        is_valid = len(errors) == 0
        message = "; ".join(errors) if errors else "String validation passed"

        return ValidationResult(
            is_valid=is_valid,
            field_name=self.field_name,
            value=value,
            severity=self.severity,
            message=message,
            details={
                "min_length": self.min_length,
                "max_length": self.max_length,
                "pattern": self.pattern,
                "allowed_values": self.allowed_values,
                "actual_length": len(value),
                "errors": errors
            }
        )


class SecurityValidator(Validator):
    """Validador de seguridad para prevenir inyecciones y ataques"""

    def __init__(self, field_name: str, severity: ValidationSeverity = ValidationSeverity.CRITICAL):
        super().__init__(field_name, severity)
        self.dangerous_patterns = [
            r"<script.*?>.*?</script>",  # XSS
            r"javascript:",  # JavaScript injection
            r"on\w+\s*=",  # Event handlers
            r"union\s+select",  # SQL injection
            r"drop\s+table",  # SQL injection
            r"delete\s+from",  # SQL injection
            r"exec\s*\(",  # Command injection
            r"system\s*\(",  # Command injection
            r"eval\s*\(",  # Code injection
            r"\.\./",  # Path traversal
            r"\.\.\\",  # Path traversal (Windows)
        ]
        self.security_logger = get_security_logger()

    def validate(self, value: Any) -> ValidationResult:
        """Validar seguridad del valor"""
        if not isinstance(value, str):
            return ValidationResult(
                is_valid=True,  # No es string, no hay riesgo
                field_name=self.field_name,
                value=value,
                severity=self.severity,
                message="Security validation passed (non-string value)",
                details={"value_type": type(value).__name__}
            )

        threats_detected = []

        # Verificar patrones peligrosos
        for pattern in self.dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                threats_detected.append(pattern)

        # Verificar caracteres sospechosos
        suspicious_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '(', ')']
        if any(char in value for char in suspicious_chars):
            threats_detected.append("suspicious_characters")

        is_valid = len(threats_detected) == 0

        if not is_valid:
            # Log security threat
            threat_event = SecurityEventFactory.create_threat_event(
                threat_type="security_validation_failed",
                severity=SecurityLevel.HIGH,
                details={
                    "field_name": self.field_name,
                    "threats_detected": threats_detected,
                    "value_preview": value[:100]  # Solo primeros 100 caracteres
                }
            )
            self.security_logger.log_event(threat_event)

        message = f"Security threats detected: {threats_detected}" if threats_detected else "Security validation passed"

        return ValidationResult(
            is_valid=is_valid,
            field_name=self.field_name,
            value=value,
            severity=self.severity,
            message=message,
            details={
                "threats_detected": threats_detected,
                "value_length": len(value),
                "security_checked": True
            }
        )


class DataTypeValidator(Validator):
    """Validador específico para tipos de datos ML"""

    def __init__(self, field_name: str, expected_dtype: str,
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        super().__init__(field_name, severity)
        self.expected_dtype = expected_dtype

    def validate(self, value: Any) -> ValidationResult:
        """Validar tipo de dato ML"""
        try:
            if isinstance(value, (list, tuple)):
                # Convertir a numpy array para validación
                arr = np.array(value)
                actual_dtype = str(arr.dtype)
            elif isinstance(value, np.ndarray):
                actual_dtype = str(value.dtype)
            elif isinstance(value, pd.Series):
                actual_dtype = str(value.dtype)
            else:
                return ValidationResult(
                    is_valid=False,
                    field_name=self.field_name,
                    value=value,
                    severity=self.severity,
                    message="Value must be a list, tuple, numpy array, or pandas series",
                    details={"expected_type": "array-like", "actual_type": type(value).__name__}
                )

            is_valid = actual_dtype == self.expected_dtype
            message = f"Expected dtype {self.expected_dtype}, got {actual_dtype}"

            return ValidationResult(
                is_valid=is_valid,
                field_name=self.field_name,
                value=value,
                severity=self.severity,
                message=message if not is_valid else "Data type validation passed",
                details={
                    "expected_dtype": self.expected_dtype,
                    "actual_dtype": actual_dtype,
                    "shape": arr.shape if 'arr' in locals() else None
                }
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                field_name=self.field_name,
                value=value,
                severity=self.severity,
                message=f"Error validating data type: {str(e)}",
                details={"error": str(e)}
            )


class ValidationChain:
    """
    Cadena de validadores.

    Aplica Chain of Responsibility Pattern.
    """

    def __init__(self, validators: List[Validator]):
        self.validators = validators

    def validate(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Ejecutar validaciones en cadena"""
        results = []

        for validator in self.validators:
            if validator.field_name in data:
                result = validator.validate(data[validator.field_name])
                results.append(result)

                # Si es crítico y falló, detener la cadena
                if result.severity == ValidationSeverity.CRITICAL and not result.is_valid:
                    break

        return results

    def add_validator(self, validator: Validator) -> None:
        """Agregar validador a la cadena"""
        self.validators.append(validator)


class ValidationFactory:
    """
    Factory para crear validadores comunes.

    Aplica Factory Pattern.
    """

    @staticmethod
    def create_email_validator(field_name: str) -> StringValidator:
        """Crear validador de email"""
        return StringValidator(
            field_name=field_name,
            pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            min_length=5,
            max_length=254
        )

    @staticmethod
    def create_password_validator(field_name: str) -> StringValidator:
        """Crear validador de contraseña"""
        return StringValidator(
            field_name=field_name,
            pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
            min_length=8,
            max_length=128
        )

    @staticmethod
    def create_numeric_validator(field_name: str, min_value: Optional[float] = None,
                                max_value: Optional[float] = None) -> RangeValidator:
        """Crear validador numérico"""
        return RangeValidator(field_name=field_name, min_value=min_value, max_value=max_value)

    @staticmethod
    def create_security_validator(field_name: str) -> SecurityValidator:
        """Crear validador de seguridad"""
        return SecurityValidator(field_name=field_name)


class DataValidator:
    """
    Validador principal de datos.

    Aplica Template Method Pattern.
    """

    def __init__(self):
        self.validation_chains: Dict[str, ValidationChain] = {}
        self.security_logger = get_security_logger()

    def add_validation_chain(self, name: str, chain: ValidationChain) -> None:
        """Agregar cadena de validación"""
        self.validation_chains[name] = chain

    def validate_data(self, data: Dict[str, Any], chain_name: str) -> Dict[str, Any]:
        """
        Validar datos usando template method.

        Template Method Pattern:
        1. Pre-validación
        2. Ejecutar validaciones
        3. Post-validación
        4. Generar reporte
        """
        try:
            # 1. Pre-validación
            self._pre_validate(data, chain_name)

            # 2. Ejecutar validaciones
            results = self._execute_validations(data, chain_name)

            # 3. Post-validación
            self._post_validate(results)

            # 4. Generar reporte
            return self._generate_report(results)

        except Exception as e:
            # Log error
            error_event = SecurityEventFactory.create_threat_event(
                threat_type="validation_error",
                severity=SecurityLevel.MEDIUM,
                details={
                    "chain_name": chain_name,
                    "error": str(e),
                    "data_keys": list(data.keys()) if data else []
                }
            )
            self.security_logger.log_event(error_event)
            raise

    def _pre_validate(self, data: Dict[str, Any], chain_name: str) -> None:
        """Pre-validación básica"""
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        if chain_name not in self.validation_chains:
            raise ValueError(f"Validation chain '{chain_name}' not found")

    def _execute_validations(self, data: Dict[str, Any], chain_name: str) -> List[ValidationResult]:
        """Ejecutar validaciones"""
        chain = self.validation_chains[chain_name]
        return chain.validate(data)

    def _post_validate(self, results: List[ValidationResult]) -> None:
        """Post-validación de resultados"""
        # Verificar si hay errores críticos
        critical_errors = [r for r in results if r.severity == ValidationSeverity.CRITICAL and not r.is_valid]
        if critical_errors:
            # Log critical validation failures
            for error in critical_errors:
                threat_event = SecurityEventFactory.create_threat_event(
                    threat_type="critical_validation_failure",
                    severity=SecurityLevel.CRITICAL,
                    details={
                        "field_name": error.field_name,
                        "message": error.message,
                        "details": error.details
                    }
                )
                self.security_logger.log_event(threat_event)

    def _generate_report(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generar reporte de validación"""
        total_validations = len(results)
        passed_validations = sum(1 for r in results if r.is_valid)
        failed_validations = total_validations - passed_validations

        # Agrupar por severidad
        by_severity = {}
        for severity in ValidationSeverity:
            by_severity[severity.value] = [r for r in results if r.severity == severity]

        return {
            "summary": {
                "total_validations": total_validations,
                "passed_validations": passed_validations,
                "failed_validations": failed_validations,
                "success_rate": passed_validations / total_validations if total_validations > 0 else 0
            },
            "by_severity": by_severity,
            "all_results": [r.to_dict() for r in results],
            "is_valid": failed_validations == 0,
            "timestamp": datetime.utcnow().isoformat()
        }

    def validate_prediction_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar datos de entrada para predicción"""
        return self.validate_data(data, "prediction_input")

    def validate_model_upload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar datos de carga de modelo"""
        return self.validate_data(data, "model_upload")

    def validate_user_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar datos de usuario"""
        return self.validate_data(data, "user_data")


# Singleton para validador global
_global_validator: Optional[DataValidator] = None


def get_data_validator() -> DataValidator:
    """Obtener validador de datos global (Singleton)"""
    global _global_validator
    if _global_validator is None:
        _global_validator = DataValidator()

        # Configurar cadenas de validación por defecto
        _setup_default_validation_chains(_global_validator)

    return _global_validator


def _setup_default_validation_chains(validator: DataValidator) -> None:
    """Configurar cadenas de validación por defecto"""

    # Cadena para datos de predicción
    prediction_chain = ValidationChain([
        TypeValidator("model_id", str),
        SecurityValidator("model_id"),
        TypeValidator("input_data", list),
        SecurityValidator("input_data")
    ])
    validator.add_validation_chain("prediction_input", prediction_chain)

    # Cadena para carga de modelos
    model_upload_chain = ValidationChain([
        TypeValidator("model_name", str),
        StringValidator("model_name", min_length=1, max_length=100),
        SecurityValidator("model_name"),
        TypeValidator("model_type", str),
        StringValidator("model_type", allowed_values=["classification", "regression", "clustering"])
    ])
    validator.add_validation_chain("model_upload", model_upload_chain)

    # Cadena para datos de usuario
    user_data_chain = ValidationChain([
        TypeValidator("username", str),
        StringValidator("username", min_length=3, max_length=50),
        SecurityValidator("username"),
        ValidationFactory.create_email_validator("email"),
        SecurityValidator("email"),
        ValidationFactory.create_password_validator("password"),
        SecurityValidator("password")
    ])
    validator.add_validation_chain("user_data", user_data_chain)
