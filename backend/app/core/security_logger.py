"""
🛡️ Sistema de Logging de Seguridad Avanzado

Implementación siguiendo principios SOLID y Clean Code:
- Single Responsibility: Cada clase tiene una responsabilidad específica
- Open/Closed: Extensible sin modificar código existente
- Liskov Substitution: Implementaciones intercambiables
- Interface Segregation: Interfaces específicas para cada necesidad
- Dependency Inversion: Dependencias abstractas

Patrones aplicados:
- Observer Pattern: Para notificaciones de eventos de seguridad
- Strategy Pattern: Para diferentes tipos de logging
- Factory Pattern: Para creación de eventos de seguridad
- Chain of Responsibility: Para procesamiento de eventos
- Template Method: Para flujos de logging estandarizados
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any, List, Callable, Union
from pathlib import Path
import hashlib
import uuid


class SecurityLevel(Enum):
    """Niveles de seguridad para eventos"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventType(Enum):
    """Tipos de eventos de seguridad"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMIT = "rate_limit"
    MODEL_ACCESS = "model_access"
    DATA_ACCESS = "data_access"
    CONFIGURATION = "configuration"
    SYSTEM = "system"
    THREAT = "threat"


@dataclass
class SecurityEvent:
    """
    Evento de seguridad estructurado.
    
    Aplica principios SOLID:
    - Single Responsibility: Solo maneja datos del evento
    - Immutability: Datos inmutables para seguridad
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.SYSTEM
    security_level: SecurityLevel = SecurityLevel.LOW
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Información del usuario
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Información del contexto
    endpoint: Optional[str] = None
    method: Optional[str] = None
    request_id: Optional[str] = None
    
    # Detalles del evento
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Metadatos
    source: str = "security_logger"
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        result["event_type"] = self.event_type.value
        result["security_level"] = self.security_level.value
        return result
    
    def to_json(self) -> str:
        """Convertir a JSON"""
        return json.dumps(self.to_dict(), default=str)
    
    def get_hash(self) -> str:
        """Generar hash único del evento"""
        content = f"{self.event_id}{self.timestamp}{self.user_id}{self.ip_address}"
        return hashlib.sha256(content.encode()).hexdigest()


class SecurityEventObserver(ABC):
    """
    Observer abstracto para eventos de seguridad.
    
    Aplica Observer Pattern para notificaciones de eventos.
    """
    
    @abstractmethod
    def on_security_event(self, event: SecurityEvent) -> None:
        """Manejar evento de seguridad"""
        pass


class SecurityEventProcessor(ABC):
    """
    Procesador abstracto de eventos de seguridad.
    
    Aplica Chain of Responsibility Pattern.
    """
    
    def __init__(self, next_processor: Optional['SecurityEventProcessor'] = None):
        self.next_processor = next_processor
    
    @abstractmethod
    def process(self, event: SecurityEvent) -> bool:
        """Procesar evento, retornar True si se procesó"""
        pass
    
    def process_chain(self, event: SecurityEvent) -> bool:
        """Procesar en cadena"""
        if self.process(event):
            return True
        if self.next_processor:
            return self.next_processor.process_chain(event)
        return False


class LoggingStrategy(ABC):
    """
    Estrategia abstracta para logging.
    
    Aplica Strategy Pattern para diferentes tipos de logging.
    """
    
    @abstractmethod
    def log_event(self, event: SecurityEvent) -> None:
        """Loggear evento según la estrategia"""
        pass


class FileLoggingStrategy(LoggingStrategy):
    """Estrategia de logging a archivo"""
    
    def __init__(self, log_file: Path, max_size_mb: int = 100):
        self.log_file = log_file
        self.max_size_mb = max_size_mb
        self.logger = logging.getLogger("security_file")
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Configurar logger para archivo"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler(self.log_file, encoding='utf-8')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_event(self, event: SecurityEvent) -> None:
        """Loggear evento a archivo"""
        level = self._get_log_level(event.security_level)
        self.logger.log(level, event.to_json())
        self._check_file_size()
    
    def _get_log_level(self, security_level: SecurityLevel) -> int:
        """Mapear nivel de seguridad a nivel de logging"""
        mapping = {
            SecurityLevel.LOW: logging.INFO,
            SecurityLevel.MEDIUM: logging.WARNING,
            SecurityLevel.HIGH: logging.ERROR,
            SecurityLevel.CRITICAL: logging.CRITICAL
        }
        return mapping.get(security_level, logging.INFO)
    
    def _check_file_size(self) -> None:
        """Verificar tamaño del archivo de log"""
        if self.log_file.exists():
            size_mb = self.log_file.stat().st_size / (1024 * 1024)
            if size_mb > self.max_size_mb:
                self._rotate_log_file()
    
    def _rotate_log_file(self) -> None:
        """Rotar archivo de log"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.log_file.parent / f"{self.log_file.stem}_{timestamp}.log"
        self.log_file.rename(backup_file)


class DatabaseLoggingStrategy(LoggingStrategy):
    """Estrategia de logging a base de datos"""
    
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
    
    def log_event(self, event: SecurityEvent) -> None:
        """Loggear evento a base de datos"""
        # Implementación para guardar en BD
        # Por ahora solo simula
        pass


class AlertingStrategy(LoggingStrategy):
    """Estrategia de alertas para eventos críticos"""
    
    def __init__(self, alert_threshold: SecurityLevel = SecurityLevel.HIGH):
        self.alert_threshold = alert_threshold
        self.alert_handlers: List[Callable] = []
    
    def add_alert_handler(self, handler: Callable[[SecurityEvent], None]) -> None:
        """Agregar manejador de alertas"""
        self.alert_handlers.append(handler)
    
    def log_event(self, event: SecurityEvent) -> None:
        """Loggear evento y generar alertas si es necesario"""
        if event.security_level.value >= self.alert_threshold.value:
            self._send_alerts(event)
    
    def _send_alerts(self, event: SecurityEvent) -> None:
        """Enviar alertas a todos los manejadores"""
        for handler in self.alert_handlers:
            try:
                handler(event)
            except Exception as e:
                logging.error(f"Error en alert handler: {e}")


class SecurityEventFactory:
    """
    Factory para crear eventos de seguridad.
    
    Aplica Factory Pattern para centralizar creación de eventos.
    """
    
    @staticmethod
    def create_auth_event(
        user_id: str,
        success: bool,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> SecurityEvent:
        """Crear evento de autenticación"""
        event_type = EventType.AUTHENTICATION
        security_level = SecurityLevel.MEDIUM if not success else SecurityLevel.LOW
        
        return SecurityEvent(
            event_type=event_type,
            security_level=security_level,
            user_id=user_id,
            ip_address=ip_address,
            message=f"Authentication {'failed' if not success else 'successful'} for user {user_id}",
            details=details or {}
        )
    
    @staticmethod
    def create_rate_limit_event(
        user_id: str,
        endpoint: str,
        current_usage: int,
        limit: int,
        ip_address: Optional[str] = None
    ) -> SecurityEvent:
        """Crear evento de límite de tasa"""
        return SecurityEvent(
            event_type=EventType.RATE_LIMIT,
            security_level=SecurityLevel.MEDIUM,
            user_id=user_id,
            endpoint=endpoint,
            ip_address=ip_address,
            message=f"Rate limit exceeded for endpoint {endpoint}",
            details={
                "current_usage": current_usage,
                "limit": limit,
                "exceeded_by": current_usage - limit
            }
        )
    
    @staticmethod
    def create_model_access_event(
        user_id: str,
        model_id: str,
        operation: str,
        success: bool,
        ip_address: Optional[str] = None
    ) -> SecurityEvent:
        """Crear evento de acceso a modelo"""
        return SecurityEvent(
            event_type=EventType.MODEL_ACCESS,
            security_level=SecurityLevel.HIGH if not success else SecurityLevel.LOW,
            user_id=user_id,
            ip_address=ip_address,
            message=f"Model access {'failed' if not success else 'successful'} for {operation}",
            details={
                "model_id": model_id,
                "operation": operation,
                "success": success
            }
        )
    
    @staticmethod
    def create_threat_event(
        threat_type: str,
        severity: SecurityLevel,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> SecurityEvent:
        """Crear evento de amenaza"""
        return SecurityEvent(
            event_type=EventType.THREAT,
            security_level=severity,
            user_id=user_id,
            ip_address=ip_address,
            message=f"Security threat detected: {threat_type}",
            details=details or {}
        )


class SecurityLogger:
    """
    Logger principal de seguridad.
    
    Aplica Template Method Pattern para flujos estandarizados.
    """
    
    def __init__(self):
        self.strategies: List[LoggingStrategy] = []
        self.observers: List[SecurityEventObserver] = []
        self.processors: List[SecurityEventProcessor] = []
        self.event_history: List[SecurityEvent] = []
        self.max_history_size = 1000
    
    def add_strategy(self, strategy: LoggingStrategy) -> None:
        """Agregar estrategia de logging"""
        self.strategies.append(strategy)
    
    def add_observer(self, observer: SecurityEventObserver) -> None:
        """Agregar observer"""
        self.observers.append(observer)
    
    def add_processor(self, processor: SecurityEventProcessor) -> None:
        """Agregar procesador"""
        self.processors.append(processor)
    
    def log_event(self, event: SecurityEvent) -> None:
        """
        Loggear evento siguiendo template method.
        
        Template Method Pattern:
        1. Validar evento
        2. Procesar en cadena
        3. Ejecutar estrategias de logging
        4. Notificar observers
        5. Guardar en historial
        """
        try:
            # 1. Validar evento
            self._validate_event(event)
            
            # 2. Procesar en cadena
            self._process_event(event)
            
            # 3. Ejecutar estrategias de logging
            self._execute_logging_strategies(event)
            
            # 4. Notificar observers
            self._notify_observers(event)
            
            # 5. Guardar en historial
            self._save_to_history(event)
            
        except Exception as e:
            logging.error(f"Error logging security event: {e}")
    
    def _validate_event(self, event: SecurityEvent) -> None:
        """Validar evento antes de procesar"""
        if not event.event_id:
            raise ValueError("Event must have an ID")
        if not event.message:
            raise ValueError("Event must have a message")
    
    def _process_event(self, event: SecurityEvent) -> None:
        """Procesar evento en cadena"""
        for processor in self.processors:
            if processor.process(event):
                break
    
    def _execute_logging_strategies(self, event: SecurityEvent) -> None:
        """Ejecutar todas las estrategias de logging"""
        for strategy in self.strategies:
            try:
                strategy.log_event(event)
            except Exception as e:
                logging.error(f"Error in logging strategy: {e}")
    
    def _notify_observers(self, event: SecurityEvent) -> None:
        """Notificar a todos los observers"""
        for observer in self.observers:
            try:
                observer.on_security_event(event)
            except Exception as e:
                logging.error(f"Error notifying observer: {e}")
    
    def _save_to_history(self, event: SecurityEvent) -> None:
        """Guardar evento en historial"""
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)
    
    @contextmanager
    def security_context(self, context_info: Dict[str, Any]):
        """Context manager para eventos de seguridad"""
        start_time = time.time()
        try:
            yield
        except Exception as e:
            # Log error event
            error_event = SecurityEventFactory.create_threat_event(
                threat_type="exception_in_security_context",
                severity=SecurityLevel.MEDIUM,
                details={
                    "context_info": context_info,
                    "error": str(e),
                    "duration": time.time() - start_time
                }
            )
            self.log_event(error_event)
            raise
        finally:
            # Log completion event
            completion_event = SecurityEvent(
                event_type=EventType.SYSTEM,
                security_level=SecurityLevel.LOW,
                message="Security context completed",
                details={
                    "context_info": context_info,
                    "duration": time.time() - start_time
                }
            )
            self.log_event(completion_event)
    
    def get_events_by_user(self, user_id: str, limit: int = 100) -> List[SecurityEvent]:
        """Obtener eventos de un usuario específico"""
        return [
            event for event in self.event_history[-limit:]
            if event.user_id == user_id
        ]
    
    def get_events_by_level(self, level: SecurityLevel, limit: int = 100) -> List[SecurityEvent]:
        """Obtener eventos por nivel de seguridad"""
        return [
            event for event in self.event_history[-limit:]
            if event.security_level == level
        ]
    
    def get_recent_events(self, minutes: int = 60) -> List[SecurityEvent]:
        """Obtener eventos recientes"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return [
            event for event in self.event_history
            if event.timestamp >= cutoff_time
        ]


# Singleton para logger global
_global_security_logger: Optional[SecurityLogger] = None


def get_security_logger() -> SecurityLogger:
    """Obtener logger de seguridad global (Singleton)"""
    global _global_security_logger
    if _global_security_logger is None:
        _global_security_logger = SecurityLogger()
    return _global_security_logger


def log_security_event(event: SecurityEvent) -> None:
    """Función helper para loggear eventos de seguridad"""
    logger = get_security_logger()
    logger.log_event(event) 