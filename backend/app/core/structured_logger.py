# -*- coding: utf-8 -*-
"""
📊 Sistema de Logging Estructurado con Contexto
from typing import Any, Dict, Optional

Implementación TDD - FASE REFACTOR
Aplicando: DRY Principle, Template Method Pattern
"""

import json
import logging
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class LogLevel(Enum):
    """Niveles de logging"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogContext:
    """Contexto de logging estructurado"""

    request_id: Optional[str] = None
    user_id: Optional[str] = None
    model_id: Optional[str] = None
    operation: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario filtrando valores None"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class SecurityEvent:
    """Evento de seguridad para audit logging"""

    event_type: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    endpoint: Optional[str] = None
    threat_level: str = "low"
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        result = asdict(self)
        result["category"] = "security_audit"
        result["timestamp"] = datetime.now().isoformat()
        return {k: v for k, v in result.items() if v is not None}


@dataclass
class PerformanceMetrics:
    """Métricas de performance"""

    operation: str
    start_time: float
    end_time: Optional[float] = None
    execution_time: Optional[float] = None
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

    def set_custom_metric(self, key: str, value: Any):
        """Agregar métrica personalizada"""
        self.custom_metrics[key] = value

    def finish(self):
        """Finalizar medición"""
        self.end_time = time.time()
        self.execution_time = self.end_time - self.start_time

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para logging"""
        return {
            "operation": self.operation,
            "execution_time": self.execution_time,
            "category": "performance",
            "timestamp": datetime.now().isoformat(),
            **self.custom_metrics,
        }


class StructuredLogger:
    """
    Logger estructurado que produce logs en formato JSON con contexto enriquecido

    REFACTORED: Eliminando duplicación con Template Method Pattern
    """

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)
        self.default_context = LogContext()

        # Mapeo de niveles a métodos del logger - DRY
        self._log_methods = {
            LogLevel.DEBUG: self.logger.debug,
            LogLevel.INFO: self.logger.info,
            LogLevel.WARNING: self.logger.warning,
            LogLevel.ERROR: self.logger.error,
            LogLevel.CRITICAL: self.logger.critical,
        }

    def _create_log_entry(
        self, level: str, message: str, context: Optional[LogContext] = None, **kwargs
    ) -> str:
        """
        Crear entrada de log estructurada en JSON

        REFACTORED: Método central para creación de logs
        """
        # Combinar contexto por defecto con contexto específico
        effective_context = self._merge_contexts(context)

        # Crear entrada de log
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "logger": self.name,
            **effective_context.to_dict(),
            **kwargs,
        }

        # Filtrar valores None
        log_entry = {k: v for k, v in log_entry.items() if v is not None}

        return json.dumps(log_entry, default=str)

    def _merge_contexts(self, context: Optional[LogContext]) -> LogContext:
        """Combinar contexto por defecto con contexto específico - DRY"""
        if not context:
            return self.default_context

        # Crear nuevo contexto combinando ambos
        context_dict = self.default_context.to_dict()
        context_dict.update(context.to_dict())
        return LogContext(
            **{
                k: v
                for k, v in context_dict.items()
                if k in LogContext.__dataclass_fields__
            }
        )

    def _log(
        self,
        level: LogLevel,
        message: str,
        context: Optional[LogContext] = None,
        **kwargs
    ):
        """
        Método plantilla para logging - Template Method Pattern

        REFACTORED: Elimina duplicación de los 5 métodos de logging
        """
        log_json = self._create_log_entry(level.value, message, context, **kwargs)
        log_method = self._log_methods[level]
        log_method(log_json)

    def set_default_context(self, context: LogContext):
        """Establecer contexto por defecto para todos los logs"""
        self.default_context = context

    # Métodos simplificados usando Template Method Pattern
    def debug(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log nivel DEBUG"""
        self._log(LogLevel.DEBUG, message, context, **kwargs)

    def info(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log nivel INFO"""
        self._log(LogLevel.INFO, message, context, **kwargs)

    def warning(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log nivel WARNING"""
        self._log(LogLevel.WARNING, message, context, **kwargs)

    def error(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log nivel ERROR"""
        self._log(LogLevel.ERROR, message, context, **kwargs)

    def critical(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log nivel CRITICAL"""
        self._log(LogLevel.CRITICAL, message, context, **kwargs)

    @contextmanager
    def performance_context(self, operation: str):
        """
        Context manager para métricas de performance automáticas

        Usage:
            with logger.performance_context("model_prediction") as metrics:
                # ... operación ...
                metrics.set_custom_metric("input_size", 1000)
        """
        metrics = PerformanceMetrics(operation=operation, start_time=time.time())

        try:
            yield metrics
        finally:
            metrics.finish()
            # Log automático de métricas
            log_json = json.dumps(metrics.to_dict(), default=str)
            self.logger.info(log_json)


class AuditLogger:
    """
    Logger especializado para eventos de seguridad y auditoría

    REFACTORED: Usando Factory Pattern para creación de eventos
    """

    def __init__(self):
        self.logger = logging.getLogger("security_audit")

        # Mapeo de threat levels a métodos de logging - DRY
        self._threat_level_methods = {
            "low": self.logger.info,
            "medium": self.logger.warning,
            "high": self.logger.error,
            "critical": self.logger.error,
        }

    def log_security_event(self, event: SecurityEvent):
        """
        Loggear evento de seguridad

        REFACTORED: Simplificado usando mapeo de threat levels
        """
        log_json = json.dumps(event.to_dict(), default=str)
        log_method = self._threat_level_methods.get(
            event.threat_level, self.logger.info
        )
        log_method(log_json)

    def log_unauthorized_access(
        self,
        user_id: str,
        endpoint: str,
        ip_address: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log de acceso no autorizado"""
        event = self._create_security_event(
            event_type="unauthorized_access",
            user_id=user_id,
            endpoint=endpoint,
            ip_address=ip_address,
            threat_level="medium",
            details=details,
        )
        self.log_security_event(event)

    def log_rate_limit_exceeded(
        self,
        user_id: str,
        endpoint: str,
        ip_address: str,
        current_usage: int,
        limit: int,
    ):
        """Log de límite de rate excedido"""
        details = {
            "current_usage": current_usage,
            "limit": limit,
            "timestamp": datetime.now().isoformat(),
        }
        event = self._create_security_event(
            event_type="rate_limit_exceeded",
            user_id=user_id,
            endpoint=endpoint,
            ip_address=ip_address,
            threat_level="low",
            details=details,
        )
        self.log_security_event(event)

    def log_model_access(
        self,
        user_id: str,
        model_id: str,
        operation: str,
        ip_address: str,
        success: bool,
    ):
        """Log de acceso a modelos ML"""
        details = {
            "model_id": model_id,
            "operation": operation,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }
        event = self._create_security_event(
            event_type="model_access",
            user_id=user_id,
            ip_address=ip_address,
            threat_level="low" if success else "medium",
            details=details,
        )
        self.log_security_event(event)

    def _create_security_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        ip_address: Optional[str] = None,
        threat_level: str = "low",
        details: Optional[Dict[str, Any]] = None,
    ) -> SecurityEvent:
        """Crear evento de seguridad - método helper"""
        return SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            endpoint=endpoint,
            ip_address=ip_address,
            threat_level=threat_level,
            details=details,
        )


# Instancia global para facilitar uso
audit_logger = AuditLogger()
