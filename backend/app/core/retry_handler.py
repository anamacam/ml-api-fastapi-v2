"""
🔄 Sistema de Retry Logic para Operaciones Críticas

Implementación TDD - FASE GREEN
"""

import asyncio
import random
import time
import logging
from dataclasses import dataclass
from typing import Callable, Optional, Any, Type, Tuple, Union
from enum import Enum


class BackoffStrategy(Enum):
    """Estrategias de backoff"""
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    EXPONENTIAL_JITTER = "exponential_jitter"


@dataclass
class RetryConfig:
    """Configuración para retry logic"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    exponential_backoff: bool = True  # Para compatibilidad con tests
    circuit_breaker_enabled: bool = False
    failure_threshold: int = 5
    reset_timeout: int = 60


class CircuitBreakerState(Enum):
    """Estados del circuit breaker"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker para prevenir cascading failures"""

    def __init__(self, failure_threshold: int, reset_timeout: int):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    @property
    def is_open(self) -> bool:
        """Verificar si el circuit breaker está abierto"""
        if self.state == CircuitBreakerState.OPEN:
            # Verificar si es tiempo de intentar half-open
            if (time.time() - self.last_failure_time) > self.reset_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                return False
            return True
        return False

    def record_success(self):
        """Registrar operación exitosa"""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED

    def record_failure(self):
        """Registrar falla de operación"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN


class RetryHandler:
    """
    Manejador de reintentos con múltiples estrategias

    Funcionalidades:
    - Múltiples estrategias de backoff
    - Circuit breaker integrado
    - Clasificación de errores (permanentes vs transitorios)
    - Retry tanto síncrono como asíncrono
    """

    # Errores que se consideran permanentes (no se reintenta)
    PERMANENT_ERRORS = (
        ValueError,
        TypeError,
        AttributeError,
        KeyError,
        ImportError,
        SyntaxError,
    )

    # Errores que se consideran transitorios (se reintenta)
    TRANSIENT_ERRORS = (
        ConnectionError,
        TimeoutError,
        OSError,  # Incluye errores de red
    )

    def __init__(self, config: RetryConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.last_attempt_count = 0

        # Circuit breaker si está habilitado
        self.circuit_breaker = None
        if config.circuit_breaker_enabled:
            self.circuit_breaker = CircuitBreaker(
                config.failure_threshold,
                config.reset_timeout
            )

    def get_last_attempt_count(self) -> int:
        """Obtener número de intentos de la última operación"""
        return self.last_attempt_count

    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Determinar si un error es retriable

        Args:
            error: Excepción a evaluar

        Returns:
            True si el error puede ser reintentado
        """
        # Errores permanentes nunca se reintentan
        if isinstance(error, self.PERMANENT_ERRORS):
            return False

        # Errores transitorios se reintentan
        if isinstance(error, self.TRANSIENT_ERRORS):
            return True

        # Por defecto, errores desconocidos se consideran transitorios
        # pero con logging para análisis
        self.logger.warning(f"Unknown error type for retry logic: {type(error)}")
        return True

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calcular delay para el próximo intento

        Args:
            attempt: Número de intento (1-based)

        Returns:
            Segundos a esperar
        """
        if self.config.backoff_strategy == BackoffStrategy.FIXED:
            delay = self.config.base_delay
        elif self.config.backoff_strategy == BackoffStrategy.LINEAR:
            delay = self.config.base_delay * attempt
        elif self.config.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = self.config.base_delay * (2 ** (attempt - 1))
        elif self.config.backoff_strategy == BackoffStrategy.EXPONENTIAL_JITTER:
            base_delay = self.config.base_delay * (2 ** (attempt - 1))
            # Agregar jitter (± 25%)
            jitter = base_delay * 0.25 * (random.random() * 2 - 1)
            delay = base_delay + jitter
        else:
            delay = self.config.base_delay

        # Aplicar límite máximo
        return min(delay, self.config.max_delay)

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ejecutar función con retry logic

        Args:
            func: Función a ejecutar
            *args: Argumentos posicionales
            **kwargs: Argumentos con nombre

        Returns:
            Resultado de la función

        Raises:
            Exception: La última excepción si todos los intentos fallan
        """
        last_error = None
        self.last_attempt_count = 0

        for attempt in range(1, self.config.max_attempts + 1):
            self.last_attempt_count = attempt

            # Verificar circuit breaker
            if self.circuit_breaker and self.circuit_breaker.is_open:
                raise Exception("Circuit breaker is open")

            try:
                result = func(*args, **kwargs)

                # Éxito - registrar en circuit breaker si existe
                if self.circuit_breaker:
                    self.circuit_breaker.record_success()

                self.logger.debug(f"Operation succeeded on attempt {attempt}")
                return result

            except Exception as error:
                last_error = error

                # Registrar falla en circuit breaker
                if self.circuit_breaker:
                    self.circuit_breaker.record_failure()

                # Verificar si el error es retriable
                if not self._is_retryable_error(error):
                    self.logger.warning(f"Non-retryable error: {error}")
                    raise error

                # Si es el último intento, no esperar
                if attempt == self.config.max_attempts:
                    self.logger.error(f"All {self.config.max_attempts} attempts failed")
                    break

                # Calcular delay y esperar
                delay = self._calculate_delay(attempt)
                self.logger.warning(
                    f"Attempt {attempt} failed: {error}. Retrying in {delay:.2f}s"
                )
                time.sleep(delay)

        # Si llegamos aquí, todos los intentos fallaron
        raise last_error

    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ejecutar función asíncrona con retry logic

        Args:
            func: Función asíncrona a ejecutar
            *args: Argumentos posicionales
            **kwargs: Argumentos con nombre

        Returns:
            Resultado de la función

        Raises:
            Exception: La última excepción si todos los intentos fallan
        """
        last_error = None
        self.last_attempt_count = 0

        for attempt in range(1, self.config.max_attempts + 1):
            self.last_attempt_count = attempt

            # Verificar circuit breaker
            if self.circuit_breaker and self.circuit_breaker.is_open:
                raise Exception("Circuit breaker is open")

            try:
                result = await func(*args, **kwargs)

                # Éxito - registrar en circuit breaker si existe
                if self.circuit_breaker:
                    self.circuit_breaker.record_success()

                self.logger.debug(f"Async operation succeeded on attempt {attempt}")
                return result

            except Exception as error:
                last_error = error

                # Registrar falla en circuit breaker
                if self.circuit_breaker:
                    self.circuit_breaker.record_failure()

                # Verificar si el error es retriable
                if not self._is_retryable_error(error):
                    self.logger.warning(f"Non-retryable async error: {error}")
                    raise error

                # Si es el último intento, no esperar
                if attempt == self.config.max_attempts:
                    self.logger.error(f"All {self.config.max_attempts} async attempts failed")
                    break

                # Calcular delay y esperar
                delay = self._calculate_delay(attempt)
                self.logger.warning(
                    f"Async attempt {attempt} failed: {error}. Retrying in {delay:.2f}s"
                )
                await asyncio.sleep(delay)

        # Si llegamos aquí, todos los intentos fallaron
        raise last_error

    def reset_circuit_breaker(self):
        """Resetear circuit breaker manualmente"""
        if self.circuit_breaker:
            self.circuit_breaker.failure_count = 0
            self.circuit_breaker.state = CircuitBreakerState.CLOSED
