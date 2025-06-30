# -*- coding: utf-8 -*-
"""
🏗️ Servicio Base - Implementación de Principios SOLID

Implementación siguiendo principios SOLID y Clean Code:
- Single Responsibility: Cada servicio tiene una responsabilidad específica
- Open/Closed: Extensible sin modificar código existente
- Liskov Substitution: Servicios intercambiables
- Interface Segregation: Interfaces específicas para cada necesidad
- Dependency Inversion: Dependencias abstractas

Patrones aplicados:
- Template Method: Para flujos estandarizados de servicios
- Strategy Pattern: Para diferentes tipos de operaciones
- Factory Pattern: Para creación de servicios
- Observer Pattern: Para notificaciones de eventos
- Decorator Pattern: Para funcionalidades adicionales
"""

# 🚨 ============ COPILOTO/CURSOR: REGLAS PARA SERVICIOS ============ 🚨
#
# 🏗️ PRINCIPIOS SOLID OBLIGATORIOS en servicios:
#    ✅ Single Responsibility: Un servicio = Una responsabilidad
#    ✅ Open/Closed: Extensible sin modificar código existente  
#    ✅ Liskov: Servicios intercambiables respetando contratos
#    ✅ Interface Segregation: Interfaces específicas, no genéricas
#    ✅ Dependency Inversion: Depender de abstracciones
#
# 🧪 TDD OBLIGATORIO para servicios:
#    🔴 RED: Test que falle por lógica de negocio
#    🟢 GREEN: Implementación mínima para pasar test
#    🔵 REFACTOR: Mejorar aplicando SOLID/DRY/KISS
#
# 📏 MÉTRICAS OBLIGATORIAS:
#    ✅ Funciones <= 20 líneas | Complejidad <= 10
#    ✅ Coverage >= 80% | No duplicación de código
#
# 🔐 SEGURIDAD en servicios:
#    ❌ NO logging de información sensible
#    ✅ Validar TODOS los inputs
#    ✅ Manejar errores sin exponer datos internos
#
# 📚 REFERENCIA: /RULES.md sección "🧠 REGLAS PARA COPILOTO/CURSOR"
# 
# ===============================================================

import logging
import traceback
import uuid
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from ..config.settings import get_settings

# from ..utils.exceptions import BaseAppException  # Unused import
from ..core.security_logger import (
    SecurityEventFactory,
    SecurityLevel,
    get_security_logger,
)

T = TypeVar("T")


@dataclass
class ServiceResult(Generic[T]):
    """Resultado de una operación de servicio"""

    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    execution_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "execution_time": self.execution_time,
        }


class ServiceObserver(ABC):
    """Observer abstracto para eventos de servicio"""

    @abstractmethod
    def on_service_event(
        self, event_type: str, service_name: str, details: Dict[str, Any]
    ) -> None:
        """Manejar evento de servicio"""
        pass


class ServiceStrategy(ABC):
    """Estrategia abstracta para operaciones de servicio"""

    @abstractmethod
    def execute(self, *args, **kwargs) -> ServiceResult:
        """Ejecutar estrategia"""
        pass


class BaseService(ABC):
    """
    Clase base para todos los servicios.

    Aplica Template Method Pattern para flujos estandarizados.
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(f"service.{service_name}")
        self.security_logger = get_security_logger()
        self.settings = get_settings()
        self.observers: List[ServiceObserver] = []
        self.strategies: Dict[str, ServiceStrategy] = {}
        self.metrics: Dict[str, Any] = {}

        # TDD CYCLE 7 - GREEN PHASE: Atributos requeridos por tests
        self.config = self.settings  # Alias para compatibilidad con tests
        self.error_handler = self._create_error_handler()
        self.is_initialized: bool = False
        self.last_error_context: Optional[Dict[str, Any]] = None

        # Configurar logging
        self._setup_logging()

        # Inicializar servicio
        try:
            self.initialize()
            self.is_initialized = True
        except Exception as e:
            self.logger.error(f"Failed to initialize service {service_name}: {e}")
            self.is_initialized = False

    def _setup_logging(self) -> None:
        """Configurar logging del servicio"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(getattr(logging, self.settings.log_level.upper()))

    def _create_error_handler(self) -> Dict[str, Any]:
        """TDD CYCLE 7 - GREEN PHASE: Crear manejador de errores"""
        return {
            "logger": self.logger,
            "security_logger": self.security_logger,
            "error_count": 0,
            "last_error": None,
        }

    def validate_input(self, data: Any) -> bool:
        """
        Valida la entrada cubriendo edge cases típicos de ML/API:
        - False para: None, listas vacías, tuplas vacías, sets vacíos,
          strings vacíos, diccionarios vacíos.
        - True para: 0, False, float('nan'), diccionarios anidados
          aunque tengan vacío, otros tipos.

        Estrategia TDD:
        - RED PHASE: Inicialmente falla solo por lógica
          (no AttributeError).
        - GREEN PHASE: Lógica completa para cubrir tests de
          edge cases.
        - REFACTOR: Optimización y documentación completa.

        Args:
            data: Datos a validar (cualquier tipo)

        Returns:
            bool: True si los datos son válidos
                para procesamiento ML

        Examples:
            >>> service.validate_input({"features": [1, 2, 3]})
            # True
            >>> service.validate_input([1, 2, 3])  # True
            >>> service.validate_input([])  # False
            >>> service.validate_input("")  # False
            >>> service.validate_input({})  # False
            >>> service.validate_input(())  # False
            >>> service.validate_input(set())  # False
            >>> service.validate_input(None)  # False
            >>> service.validate_input(0)  # True (cero es válido)
            >>> service.validate_input(False)  # True
            # (booleano es válido)
            >>> service.validate_input(float('nan'))  # True
            # (NaN es válido)
            >>> service.validate_input({"nested": {}})
            # True (dict anidado)
        """
        # Edge case: None
        if data is None:
            return False
        # Edge case: empty str, empty list, empty tuple,
        # empty set
        if isinstance(data, (str, list, tuple, set)) and not data:
            return False
        # Edge case: empty dict
        if isinstance(data, dict) and not data:
            return False
        # Otros edge cases se consideran válidos
        # (0, False, float('nan'), dicts anidados)
        return True

    def handle_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """
        TDD CYCLE 7 - GREEN PHASE: Manejar errores con contexto

        Args:
            error: Excepción a manejar
            context: Contexto del error
        """
        self.last_error_context = context
        self.logger.error(f"Service error: {error}", extra=context)

        if self.error_handler:
            self.error_handler["error_count"] += 1
            self.error_handler["last_error"] = str(error)

    def add_observer(self, observer: ServiceObserver) -> None:
        """
        Agregar observer al servicio

        Args:
            observer: Observer a agregar
        """
        self.observers.append(observer)

    def add_strategy(self, name: str, strategy: ServiceStrategy) -> None:
        """
        Agregar estrategia al servicio

        Args:
            name: Nombre de la estrategia
            strategy: Estrategia a agregar
        """
        self.strategies[name] = strategy

    def notify_observers(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Notificar a todos los observers

        Args:
            event_type: Tipo de evento
            details: Detalles del evento
        """
        for observer in self.observers:
            try:
                observer.on_service_event(event_type, self.service_name, details)
            except Exception as e:
                self.logger.error(f"Error notifying observer: {e}")

    @contextmanager
    def service_context(self, operation: str, **context_data: Any):
        """
        Context manager para operaciones de servicio.

        Template Method Pattern:
        1. Pre-operación
        2. Ejecutar operación
        3. Post-operación
        4. Manejo de errores

        Args:
            operation: Nombre de la operación
            **context_data: Datos de contexto adicionales
        """
        operation_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        try:
            # 1. Pre-operación
            self._pre_operation(operation, operation_id, context_data)

            # 2. Ejecutar operación
            yield operation_id

            # 3. Post-operación (éxito)
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            self._post_operation_success(
                operation, operation_id, execution_time, context_data
            )

        except Exception as e:
            # 4. Manejo de errores
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            self._post_operation_error(
                operation, operation_id, e, execution_time, context_data
            )
            raise

    def _pre_operation(
        self, operation: str, operation_id: str, context_data: Dict[str, Any]
    ) -> None:
        """Preparar operación"""
        self.logger.info(f"Starting operation: {operation} (ID: {operation_id})")

        # Log security event
        security_event = SecurityEventFactory.create_threat_event(
            threat_type="service_operation_start",
            severity=SecurityLevel.LOW,
            details={
                "service_name": self.service_name,
                "operation": operation,
                "operation_id": operation_id,
                "context_data": context_data,
            },
        )
        self.security_logger.log_event(security_event)

        # Notificar observers
        self.notify_observers(
            "operation_start",
            {
                "operation": operation,
                "operation_id": operation_id,
                "context_data": context_data,
            },
        )

    def _post_operation_success(
        self,
        operation: str,
        operation_id: str,
        execution_time: float,
        context_data: Dict[str, Any],
    ) -> None:
        """Post-operación exitosa"""
        self.logger.info(
            f"Operation completed: {operation} (ID: {operation_id}) "
            f"in {execution_time: .3f}s"
        )

        # Actualizar métricas
        self._update_metrics(operation, execution_time, success=True)

        # Notificar observers
        self.notify_observers(
            "operation_success",
            {
                "operation": operation,
                "operation_id": operation_id,
                "execution_time": execution_time,
                "context_data": context_data,
            },
        )

    def _post_operation_error(
        self,
        operation: str,
        operation_id: str,
        error: Exception,
        execution_time: float,
        context_data: Dict[str, Any],
    ) -> None:
        """Post-operación con error"""
        error_msg = str(error)
        self.logger.error(
            f"Operation failed: {operation} (ID: {operation_id}) - {error_msg}"
        )

        # Establecer contexto de error
        error_context = {
            "operation": operation,
            "operation_id": operation_id,
            "error": error_msg,
            "execution_time": execution_time,
            "context_data": context_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.handle_error(error, error_context)

        # Log security event
        security_event = SecurityEventFactory.create_threat_event(
            threat_type="service_operation_error",
            severity=SecurityLevel.MEDIUM,
            details={
                "service_name": self.service_name,
                "operation": operation,
                "operation_id": operation_id,
                "error": error_msg,
                "execution_time": execution_time,
                "context_data": context_data,
                "traceback": traceback.format_exc(),
            },
        )
        self.security_logger.log_event(security_event)

        # Actualizar métricas
        self._update_metrics(operation, execution_time, success=False)

        # Notificar observers
        self.notify_observers(
            "operation_error",
            {
                "operation": operation,
                "operation_id": operation_id,
                "error": error_msg,
                "execution_time": execution_time,
                "context_data": context_data,
            },
        )

    def _update_metrics(
        self, operation: str, execution_time: float, success: bool
    ) -> None:
        """Actualizar métricas del servicio"""
        if "operations" not in self.metrics:
            self.metrics["operations"] = {}

        if operation not in self.metrics["operations"]:
            self.metrics["operations"][operation] = {
                "total_count": 0,
                "success_count": 0,
                "error_count": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "min_time": float("inf"),
                "max_time": 0.0,
            }

        op_metrics = self.metrics["operations"][operation]
        op_metrics["total_count"] += 1
        op_metrics["total_time"] += execution_time

        if success:
            op_metrics["success_count"] += 1
        else:
            op_metrics["error_count"] += 1

        # Actualizar estadísticas de tiempo
        op_metrics["avg_time"] = op_metrics["total_time"] / op_metrics["total_count"]
        op_metrics["min_time"] = min(op_metrics["min_time"], execution_time)
        op_metrics["max_time"] = max(op_metrics["max_time"], execution_time)

    def execute_strategy(
        self, strategy_name: str, *args: Any, **kwargs: Any
    ) -> ServiceResult:
        """
        Ejecutar estrategia específica

        Args:
            strategy_name: Nombre de la estrategia
            *args: Argumentos posicionales
            **kwargs: Argumentos con nombre

        Returns:
            ServiceResult: Resultado de la estrategia
        """
        if strategy_name not in self.strategies:
            return ServiceResult(
                success=False,
                error=f"Strategy '{strategy_name}' not found",
                details={"available_strategies": list(self.strategies.keys())},
            )

        strategy = self.strategies[strategy_name]

        with self.service_context(f"strategy_{strategy_name}"):
            return strategy.execute(*args, **kwargs)

    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del servicio"""
        return {
            "service_name": self.service_name,
            "metrics": self.metrics,
            "observers_count": len(self.observers),
            "strategies_count": len(self.strategies),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def health_check(self) -> Dict[str, Any]:
        """Verificar estado de salud del servicio"""
        return {
            "service_name": self.service_name,
            "is_initialized": self.is_initialized,
            "observers_count": len(self.observers),
            "strategies_count": len(self.strategies),
            "timestamp": datetime.utcnow().isoformat(),
        }

    # TDD STUB METHODS - Following RED-GREEN-REFACTOR philosophy
    # These methods return default values to pass linting,
    # RED phase should fail on business logic, not missing methods

    def get_service_info(self) -> Dict[str, Any]:
        """
        TDD STUB: Get detailed service information
        RED: Returns minimal info by default for TDD failure
        """
        return {"name": self.service_name}  # RED: Minimal return for TDD

    def restart_service(self) -> bool:
        """
        TDD STUB: Restart service
        RED: Returns False by default for TDD failure
        """
        return False  # RED: Default return for TDD

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        TDD STUB: Get performance statistics
        RED: Returns empty dict by default for TDD failure
        """
        return {}  # RED: Default return for TDD

    def configure_service(self, config: Dict[str, Any]) -> bool:
        """
        TDD STUB: Configure service settings
        RED: Returns False by default for TDD failure
        """
        return False  # RED: Default return for TDD

    def backup_service_state(self) -> str:
        """
        TDD STUB: Backup current service state
        RED: Returns empty string by default for TDD failure
        """
        return ""  # RED: Default return for TDD

    @abstractmethod
    def initialize(self) -> None:
        """Inicializar servicio"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Limpiar recursos del servicio"""
        pass


class ServiceFactory:
    """
    Factory para crear servicios.

    Aplica Factory Pattern.
    """

    _services: Dict[str, type] = {}

    @classmethod
    def register_service(cls, name: str, service_class: type) -> None:
        """Registrar servicio en el factory"""
        cls._services[name] = service_class

    @classmethod
    def create_service(cls, name: str, **kwargs) -> BaseService:
        """Crear servicio por nombre"""
        if name not in cls._services:
            raise ValueError(f"Service '{name}' not registered")

        service_class = cls._services[name]
        return service_class(**kwargs)

    @classmethod
    def get_available_services(cls) -> List[str]:
        """Obtener lista de servicios disponibles"""
        return list(cls._services.keys())


class ServiceManager:
    """
    Gestor de servicios.

    Aplica Singleton Pattern para gestión centralizada.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.services: Dict[str, BaseService] = {}
        self.logger = logging.getLogger("service_manager")
        self._initialized = True

    def register_service(self, name: str, service: BaseService) -> None:
        """Registrar servicio en el manager"""
        self.services[name] = service
        self.logger.info(f"Service registered: {name}")

    def get_service(self, name: str) -> Optional[BaseService]:
        """Obtener servicio por nombre"""
        return self.services.get(name)

    def get_all_services(self) -> Dict[str, BaseService]:
        """Obtener todos los servicios"""
        return self.services.copy()

    def initialize_all_services(self) -> None:
        """Inicializar todos los servicios"""
        for name, service in self.services.items():
            try:
                service.initialize()
                self.logger.info(f"Service initialized: {name}")
            except Exception as e:
                self.logger.error(f"Error initializing service {name}: {e}")

    def cleanup_all_services(self) -> None:
        """Limpiar todos los servicios"""
        for name, service in self.services.items():
            try:
                service.cleanup()
                self.logger.info(f"Service cleaned up: {name}")
            except Exception as e:
                self.logger.error(f"Error cleaning up service {name}: {e}")

    def health_check_all(self) -> Dict[str, Any]:
        """Verificar salud de todos los servicios"""
        results = {}
        for name, service in self.services.items():
            try:
                results[name] = service.health_check()
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        return results


# Singleton para service manager global
def get_service_manager() -> ServiceManager:
    """Obtener service manager global (Singleton)"""
    return ServiceManager()
