# -*- coding: utf-8 -*-
"""
Servicio Híbrido de Predicción - REFACTOR FINAL.

Integra modelos reales existentes con la arquitectura TDD
refactorizada. Mantiene compatibilidad con tests mientras usa modelos
LightGBM y Random Forest reales.

MEJORA 4: Métricas de Performance para Fallback
- Tiempo de respuesta de servicios primario y fallback
- Contadores de éxito/fallo por servicio
- Métricas de disponibilidad y latencia
- Análisis de patrones de fallo
"""

import json
import logging
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# import pandas as pd  # Unused import
import joblib  # type: ignore
import numpy as np

# from app.utils.ml_model_validators import validate_ml_model  # Unused
from app.config.settings import get_settings
from app.utils.prediction_validators import validate_prediction_input

logger = logging.getLogger(__name__)
settings = get_settings()


class PerformanceMetrics:
    """
    Métricas de performance para el sistema de fallback.

    Rastrea:
    - Tiempos de respuesta por servicio
    - Tasas de éxito/fallo
    - Patrones de uso de fallback
    - Disponibilidad de servicios

    Examples:
        >>> metrics = PerformanceMetrics()
        >>> metrics.record_prediction_time("primary", 0.15, True)
        >>> metrics.record_prediction_time("fallback", 0.05, True)
        >>>
        >>> # Obtener estadísticas
        >>> stats = metrics.get_performance_stats()
        >>> print(f"Primary avg time: "
        ...       f"{stats['primary']['avg_response_time']}")
        >>> print(f"Fallback usage rate: "
        ...       f"{stats['fallback_usage_rate']}")
    """

    def __init__(self, max_history: int = 1000):
        """
        Inicializar métricas de performance.

        Args:
            max_history: Máximo número de registros a mantener
                en memoria
        """
        self.max_history: int = max_history

        # Métricas por servicio
        self.service_metrics: Dict[str, Dict[str, Any]] = {
            "primary": {
                "response_times": deque(maxlen=max_history),
                "success_count": 0,
                "failure_count": 0,
                "last_success": None,
                "last_failure": None,
                "total_requests": 0,
            },
            "fallback": {
                "response_times": deque(maxlen=max_history),
                "success_count": 0,
                "failure_count": 0,
                "last_success": None,
                "last_failure": None,
                "total_requests": 0,
            },
        }

        # Métricas de fallback
        self.fallback_metrics: Dict[str, Any] = {
            "total_fallbacks": 0,
            "fallback_reasons": defaultdict(int),
            "fallback_times": deque(maxlen=max_history),
            "consecutive_fallbacks": 0,
            "max_consecutive_fallbacks": 0,
            "last_fallback_time": None,
        }

        # Métricas de disponibilidad
        self.availability_metrics: Dict[str, Any] = {
            "primary_availability": 1.0,
            "fallback_availability": 1.0,
            "combined_availability": 1.0,
            "uptime_start": datetime.now(),
            "downtime_periods": [],
        }

        # Ventana de tiempo para cálculos (últimos 5 minutos)
        self.time_window: timedelta = timedelta(minutes=5)

    def record_prediction_time(
        self,
        service: str,
        response_time: float,
        success: bool,
        failure_reason: Optional[str] = None,
    ) -> None:
        """
        Registrar tiempo de predicción para un servicio.

        Args:
            service: "primary" o "fallback"
            response_time: Tiempo de respuesta en segundos
            success: Si la predicción fue exitosa
            failure_reason: Razón del fallo si aplica

        Examples:
            >>> metrics.record_prediction_time("primary", 0.12, True)
            >>> metrics.record_prediction_time("primary", 2.5, False, "timeout")
        """
        if service not in self.service_metrics:
            return

        metrics = self.service_metrics[service]
        current_time = datetime.now()

        # Registrar tiempo de respuesta
        metrics["response_times"].append(
            {"time": response_time, "timestamp": current_time, "success": success}
        )

        # Actualizar contadores
        metrics["total_requests"] += 1
        if success:
            metrics["success_count"] += 1
            metrics["last_success"] = current_time
        else:
            metrics["failure_count"] += 1
            metrics["last_failure"] = current_time

            # Si es el servicio primario que falla, registrar
            # razón de fallback
            if service == "primary" and failure_reason:
                self.fallback_metrics["fallback_reasons"][failure_reason] += 1

    def record_fallback_usage(self, reason: str, response_time: float) -> None:
        """
        Registrar uso del sistema de fallback.

        Args:
            reason: Razón por la que se usó fallback
            response_time: Tiempo total incluyendo fallback

        Examples:
            >>> metrics.record_fallback_usage("primary_timeout", 0.25)
            >>> metrics.record_fallback_usage("primary_error", 0.18)
        """
        current_time = datetime.now()

        self.fallback_metrics["total_fallbacks"] += 1
        self.fallback_metrics["fallback_reasons"][reason] += 1
        self.fallback_metrics["fallback_times"].append(
            {"time": response_time, "timestamp": current_time, "reason": reason}
        )
        self.fallback_metrics["last_fallback_time"] = current_time

        # Rastrear fallbacks consecutivos
        last_fallback_time = self.fallback_metrics.get("last_fallback_time")
        if last_fallback_time and (
            current_time - last_fallback_time < timedelta(minutes=1)
        ):
            self.fallback_metrics["consecutive_fallbacks"] += 1
            if (
                self.fallback_metrics["consecutive_fallbacks"]
                > self.fallback_metrics["max_consecutive_fallbacks"]  # noqa: W503
            ):
                self.fallback_metrics[
                    "max_consecutive_fallbacks"
                ] = self.fallback_metrics["consecutive_fallbacks"]
        else:
            self.fallback_metrics["consecutive_fallbacks"] = 1

    def calculate_availability(self, service: str) -> float:
        """
        Calcular disponibilidad del servicio en la ventana de tiempo.

        Args:
            service: "primary" o "fallback"

        Returns:
            float: Disponibilidad como porcentaje (0.0 - 1.0)

        Examples:
            >>> availability = metrics.calculate_availability("primary")
            >>> print(f"Primary service availability: "
        ...       f"{availability:.2%}")
        """
        if service not in self.service_metrics:
            return 0.0

        metrics = self.service_metrics[service]
        if metrics["total_requests"] == 0:
            return 1.0  # Sin requests, asumimos disponible

        # Calcular en ventana de tiempo
        current_time = datetime.now()
        cutoff_time = current_time - self.time_window

        # Filtrar requests en ventana de tiempo
        recent_requests = [
            entry
            for entry in metrics["response_times"]
            if entry.get("timestamp") and entry["timestamp"] > cutoff_time
        ]

        if not recent_requests:
            return 1.0

        successful_requests = sum(
            1 for entry in recent_requests if entry.get("success")
        )
        total_recent_requests = len(recent_requests)

        return (
            successful_requests / total_recent_requests
            if total_recent_requests > 0
            else 1.0
        )

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas completas de performance.

        Returns:
            Dict con todas las métricas de performance

        Examples:
            >>> stats = metrics.get_performance_stats()
            >>> print(f"Fallback usage rate: {stats['fallback_usage_rate']:.2%}")
            >>> print(f"Primary avg response time: "
            ...       f"{stats['primary']['avg_response_time']:.3f}s")
        """
        current_time = datetime.now()
        cutoff_time = current_time - self.time_window

        stats: Dict[str, Any] = {
            "primary": self._get_service_stats("primary", cutoff_time),
            "fallback": self._get_service_stats("fallback", cutoff_time),
            "fallback_usage": self._get_fallback_stats(cutoff_time),
            "availability": {
                "primary": self.calculate_availability("primary"),
                "fallback": self.calculate_availability("fallback"),
                "combined": self._calculate_combined_availability(),
            },
            "metadata": {
                "report_generated_at": current_time.isoformat(),
                "time_window_minutes": self.time_window.total_seconds() / 60,
            },
        }
        return stats

    def _get_service_stats(self, service: str, cutoff_time: datetime) -> Dict[str, Any]:
        """Obtener estadísticas para un servicio específico."""
        metrics = self.service_metrics.get(service, {})
        response_times_deque = metrics.get("response_times", deque())

        recent_times = [
            entry["time"]
            for entry in response_times_deque
            if entry.get("timestamp") and entry["timestamp"] > cutoff_time
        ]

        last_success = metrics.get("last_success")
        last_failure = metrics.get("last_failure")

        return {
            "total_requests": metrics.get("total_requests", 0),
            "success_count": metrics.get("success_count", 0),
            "failure_count": metrics.get("failure_count", 0),
            "avg_response_time": np.mean(recent_times) if recent_times else 0,
            "last_success": last_success.isoformat() if last_success else None,
            "last_failure": last_failure.isoformat() if last_failure else None,
        }

    def _get_fallback_stats(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Obtener estadísticas del sistema de fallback."""
        total_requests_primary = self.service_metrics.get("primary", {}).get(
            "total_requests", 0
        )
        total_fallbacks = self.fallback_metrics.get("total_fallbacks", 0)

        fallback_times_deque = self.fallback_metrics.get("fallback_times", deque())
        recent_fallback_times = [
            entry["time"]
            for entry in fallback_times_deque
            if entry.get("timestamp") and entry["timestamp"] > cutoff_time
        ]

        last_fallback_time = self.fallback_metrics.get("last_fallback_time")

        return {
            "total_fallbacks": total_fallbacks,
            "fallback_rate": (
                total_fallbacks / total_requests_primary
                if total_requests_primary > 0
                else 0
            ),
            "avg_fallback_response_time": (
                np.mean(recent_fallback_times) if recent_fallback_times else 0
            ),
            "reasons": dict(self.fallback_metrics.get("fallback_reasons", {})),
            "consecutive_fallbacks": self.fallback_metrics.get(
                "consecutive_fallbacks", 0
            ),
            "max_consecutive_fallbacks": self.fallback_metrics.get(
                "max_consecutive_fallbacks", 0
            ),
            "last_fallback_time": (
                last_fallback_time.isoformat() if last_fallback_time else None
            ),
        }

    def _calculate_combined_availability(self) -> float:
        """Calcular disponibilidad combinada del sistema."""
        # Lógica de disponibilidad combinada (simplificada)
        return self.calculate_availability("primary") + self.calculate_availability(
            "fallback"
        ) * (1 - self.calculate_availability("primary"))

    def reset_metrics(self) -> None:
        """Reiniciar todas las métricas a su estado inicial."""
        # FIX: Re-inicializar explícitamente en lugar de llamar a __init__
        self.service_metrics = {
            "primary": {
                "response_times": deque(maxlen=self.max_history),
                "success_count": 0,
                "failure_count": 0,
                "last_success": None,
                "last_failure": None,
                "total_requests": 0,
            },
            "fallback": {
                "response_times": deque(maxlen=self.max_history),
                "success_count": 0,
                "failure_count": 0,
                "last_success": None,
                "last_failure": None,
                "total_requests": 0,
            },
        }
        self.fallback_metrics = {
            "total_fallbacks": 0,
            "fallback_reasons": defaultdict(int),
            "fallback_times": deque(maxlen=self.max_history),
            "consecutive_fallbacks": 0,
            "max_consecutive_fallbacks": 0,
            "last_fallback_time": None,
        }
        self.availability_metrics = {
            "primary_availability": 1.0,
            "fallback_availability": 1.0,
            "combined_availability": 1.0,
            "uptime_start": datetime.now(),
            "downtime_periods": [],
        }


class HybridPredictionService:
    """
    Servicio híbrido que combina modelos reales con funcionalidad TDD.

    - Usa modelos LightGBM y Random Forest reales para producción
    - Mantiene mocks para testing y desarrollo
    - Compatibilidad total con tests TDD existentes
    - MEJORA 4: Métricas de performance integradas
    """

    def __init__(self, use_real_models: Optional[bool] = None):
        """
        Inicializar el servicio híbrido de predicción.

        Args:
            use_real_models: Si usar modelos reales o mocks. Si es None,
                detecta automáticamente.
        """
        logger.info("🔧 Inicializando HybridPredictionService...")

        # TDD CYCLE 7 - GREEN PHASE: Atributos requeridos por tests
        self.primary_service: Dict[str, Any] = self._create_primary_service()
        self.fallback_service: Dict[str, Any] = self._create_fallback_service()
        self.fallback_enabled: bool = True
        self.fallback_count: int = 0
        self.last_fallback_reason: Optional[str] = None
        self.fallback_times: List[float] = []  # Para métricas de fallback
        self.fallback_threshold: float = 0.5
        self.is_hybrid_ready: bool = False

        # Configuración de modelos reales vs mocks
        self.use_real_models: bool = self._determine_model_usage(use_real_models)
        self.real_models: Dict[str, Any] = {}
        self.mock_models: Dict[str, Any] = self._create_mock_models()

        # Componentes adicionales
        self.strategy: Dict[str, Any] = self._create_strategy()
        self.health_checker: Dict[str, Any] = self._create_health_checker()
        self.performance_metrics: PerformanceMetrics = PerformanceMetrics()

        # Cargar modelos reales si está configurado
        if self.use_real_models:
            self._load_real_models()

        self.is_hybrid_ready = True
        logger.info("✅ HybridPredictionService inicializado correctamente")

    def _determine_model_usage(self, use_real_models: Optional[bool]) -> bool:
        """
        Determinar si usar modelos reales o mocks.

        Args:
            use_real_models: Configuración explícita o None para
                auto-detectar

        Returns:
            bool: True si usar modelos reales
        """
        if use_real_models is not None:
            return use_real_models

        # Auto-detectar basado en configuración de entorno
        return getattr(settings, "should_use_real_models", False)

    def _create_mock_models(self) -> Dict[str, Any]:
        """
        Crear modelos mock para testing.

        Returns:
            Dict[str, Any]: Diccionario de modelos mock
        """
        return {
            "default_model": {"status": "trained", "type": "sklearn"},
            "sensitive_model": {"status": "trained", "type": "sklearn"},
        }

    def _load_real_models(self) -> None:
        """Cargar modelos reales desde disco."""
        try:
            # Path a los modelos reales desde configuración
            models_path = settings.ml_models_path
            if not models_path.is_absolute():
                # Si es relativo, hacerlo relativo al directorio backend/
                models_path = Path("../").resolve() / models_path
            registry_path = models_path / "model_registry.json"

            if not models_path.exists():
                logger.warning(f"⚠️ Directorio de modelos no encontrado: {models_path}")
                logger.info("🔄 Fallback a modo mock")
                self.use_real_models = False
                return

            # Cargar metadata del registry
            if registry_path.exists():
                with open(registry_path, "r") as f:
                    self.model_metadata = json.load(f)
                logger.info("✅ Metadata de modelos cargada")

            # Cargar modelos directamente desde archivos
            model_files = {
                "lgbm_model": models_path / "lgbm_model.joblib",
                "optimized_lgbm": models_path / "optimized_lgbm_20250518_083628.joblib",
                # RF es muy pesado (3GB) - solo cargar si es necesario
                # "optimized_rf": models_path / "optimized_rf_20250518_083628.joblib"
            }

            for model_name, model_path in model_files.items():
                if model_path.exists():
                    try:
                        logger.info(f"🔄 Cargando modelo real: {model_name}")
                        self.real_models[model_name] = joblib.load(model_path)
                        size_kb = model_path.stat().st_size / 1024
                        logger.info(
                            f"✅ Modelo cargado: {model_name} ({size_kb: .1f}KB)"
                        )
                    except Exception as e:
                        logger.error(f"❌ Error cargando {model_name}: {e}")

            # Agregar alias para compatibilidad con tests
            if "lgbm_model" in self.real_models:
                self.real_models["default_model"] = self.real_models["lgbm_model"]

            logger.info(
                f"🚀 Modelos reales disponibles: {list(self.real_models.keys())}"
            )

        except Exception as e:
            logger.error(f"❌ Error crítico cargando modelos reales: {e}")
            logger.info("🔄 Fallback a modo mock")
            self.use_real_models = False

    def _create_primary_service(self) -> Dict[str, Any]:
        """TDD CYCLE 7 - GREEN PHASE: Crear servicio primario"""
        return {
            "name": "primary_prediction_service",
            "status": "active",
            "predict": self._primary_predict,
        }

    def _create_fallback_service(self) -> Dict[str, Any]:
        """TDD CYCLE 7 - GREEN PHASE: Crear servicio de fallback"""
        return {
            "name": "fallback_prediction_service",
            "status": "standby",
            "predict": self._fallback_predict,
        }

    def _create_strategy(self) -> Dict[str, Any]:
        """TDD CYCLE 7 - GREEN PHASE: Crear estrategia híbrida"""
        return {
            "type": "hybrid_failover",
            "primary_timeout": 5.0,
            "fallback_enabled": True,
        }

    def _create_health_checker(self) -> Dict[str, Any]:
        """TDD CYCLE 7 - GREEN PHASE: Crear health checker"""
        return {"check_interval": 30, "last_check": datetime.now(), "status": "healthy"}

    def _primary_predict(self, request):
        """Predicción usando servicio primario"""
        return self.validate_and_predict(
            request.features, request.model_id or "default_model"
        )

    def _fallback_predict(self, request):
        """Predicción usando servicio de fallback"""
        return self._mock_prediction(
            request.features, request.model_id or "default_model"
        )

    def _handle_primary_failure(self, reason: str) -> None:
        """
        MEJORA 3: Manejar fallo del servicio primario.

        Args:
            reason: Razón del fallo
        """
        self.fallback_count += 1
        self.last_fallback_reason = reason
        self.fallback_times.append(time.time())  # Almacenar timestamp como float

        # Registrar en métricas de performance
        self.performance_metrics.record_fallback_usage(reason, 0.0)

        logger.warning(
            f"Primary service failed: {reason}. Fallback count: {self.fallback_count}"
        )

    async def predict_hybrid(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        MEJORA 3: Predicción híbrida con manejo de fallos.

        Args:
            data: Datos de entrada

        Returns:
            Dict con resultado de predicción
        """
        start_time = time.time()

        try:
            # Intentar servicio primario
            result = await self._predict_with_primary(data)

            # Registrar métricas de éxito
            response_time = time.time() - start_time
            self.performance_metrics.record_prediction_time(
                "primary", response_time, True
            )

            return {
                "prediction": result,
                "service_used": "primary",
                "response_time": response_time,
                "fallback_used": False,
            }

        except Exception as primary_error:
            # Registrar fallo del primario
            primary_time = time.time() - start_time
            self.performance_metrics.record_prediction_time(
                "primary", primary_time, False, str(primary_error)
            )

            if not self.fallback_enabled:
                raise primary_error

            try:
                # Usar servicio de fallback
                fallback_start = time.time()
                result = await self._predict_with_fallback(data)

                # Registrar métricas de fallback
                fallback_time = time.time() - fallback_start
                total_time = time.time() - start_time

                self.performance_metrics.record_prediction_time(
                    "fallback", fallback_time, True
                )
                self.performance_metrics.record_fallback_usage(
                    str(primary_error), total_time
                )

                self._handle_primary_failure(str(primary_error))

                return {
                    "prediction": result,
                    "service_used": "fallback",
                    "response_time": total_time,
                    "fallback_used": True,
                    "primary_error": str(primary_error),
                }

            except Exception as fallback_error:
                # Ambos servicios fallaron
                fallback_time = time.time() - fallback_start
                self.performance_metrics.record_prediction_time(
                    "fallback", fallback_time, False, str(fallback_error)
                )

                raise Exception(
                    f"Both services failed. Primary: {primary_error}, "
                    f"Fallback: {fallback_error}"
                )

    async def _predict_with_primary(self, data: Dict[str, Any]) -> Any:
        """Predicción con servicio primario."""
        # Simular predicción primaria
        if self.use_real_models and "default_model" in self.real_models:
            return self._real_model_prediction(data, "default_model")
        else:
            return self._mock_prediction(data, "default_model")

    async def _predict_with_fallback(self, data: Dict[str, Any]) -> Any:
        """Predicción con servicio de fallback."""
        # El fallback siempre usa mock para garantizar disponibilidad
        return self._mock_prediction(data, "default_model")

    def get_performance_report(self) -> Dict[str, Any]:
        """
        MEJORA 4: Obtener reporte completo de performance.

        Returns:
            Dict con métricas completas de performance

        Examples:
            >>> service = HybridPredictionService()
            >>> report = service.get_performance_report()
            >>> print(f"System availability: {report['availability']['combined']:.2%}")
            >>> print(f"Fallback usage: {report['fallback_usage_rate']:.2%}")
        """
        base_stats = self.performance_metrics.get_performance_stats()

        # Agregar métricas específicas del servicio híbrido
        base_stats.update(
            {
                "hybrid_service_metrics": {
                    "total_fallback_count": self.fallback_count,
                    "last_fallback_reason": self.last_fallback_reason,
                    "fallback_enabled": self.fallback_enabled,
                    "fallback_threshold": self.fallback_threshold,
                    "is_hybrid_ready": self.is_hybrid_ready,
                    "use_real_models": self.use_real_models,
                    "available_models": (
                        list(self.real_models.keys())
                        if self.use_real_models
                        else list(self.mock_models.keys())
                    ),
                }
            }
        )

        return base_stats

    def predict_with_fallback(self, request):
        """TDD CYCLE 7 - GREEN PHASE: Predicción con mecanismo de fallback"""
        start_time = time.time()

        try:
            # Intentar servicio primario
            success, result = self.primary_service["predict"](request)

            # Registrar métricas
            response_time = time.time() - start_time
            self.performance_metrics.record_prediction_time(
                "primary", response_time, success
            )

            if success:
                result["used_fallback"] = False
                result["primary_error"] = None
                return result
            else:
                raise Exception("Primary service failed")

        except Exception as e:
            # Usar fallback
            logger.warning(f"Primary service failed, using fallback: {e}")

            fallback_start = time.time()
            fallback_result = self.fallback_service["predict"](request)
            fallback_time = time.time() - fallback_start
            total_time = time.time() - start_time

            # Registrar métricas de fallback
            self.performance_metrics.record_prediction_time(
                "fallback", fallback_time, True
            )
            self.performance_metrics.record_fallback_usage(str(e), total_time)

            self._handle_primary_failure(str(e))

            return {
                "prediction": fallback_result,
                "used_fallback": True,
                "primary_error": str(e),
                "response_time": total_time,
            }

    def validate_and_predict(
        self, features: Dict[str, Any], model_id: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Validar entrada y ejecutar predicción (compatibilidad TDD).

        Args:
            features: Características de entrada
            model_id: ID del modelo a usar

        Returns:
            Tuple[bool, Dict]: (success, result_or_error)
        """
        try:
            # Paso 1: Validar datos de entrada usando nuestro validador TDD
            validation_result = validate_prediction_input(features)

            if not validation_result["valid"]:
                return False, {
                    "error_type": "input_validation",
                    "validation_result": validation_result,
                }

            # Paso 2: Validar disponibilidad del modelo
            available_models = self._get_available_models()
            if model_id not in available_models:
                return False, {
                    "error_type": "model_not_found",
                    "model_id": model_id,
                    "available_models": list(available_models.keys()),
                }

            # Paso 3: Ejecutar predicción
            prediction = self._execute_prediction(features, model_id)

            # Paso 4: Retornar resultado estructurado (compatible con tests TDD)
            return True, {
                "prediction": prediction,
                "validation_details": {"input_valid": True, "model_valid": True},
                "model_info": {
                    "model_id": model_id,
                    "status": "trained",
                    "type": self._get_model_type(model_id),
                    "is_real_model": self.use_real_models
                    and model_id in self.real_models,  # noqa: W503
                },
            }

        except Exception as e:
            logger.error(f"❌ Error en predicción: {e}")
            return False, {"error_type": "prediction_failed", "error_message": str(e)}

    def _execute_prediction(
        self, features: Dict[str, Any], model_id: str
    ) -> List[float]:
        """
        Ejecutar predicción real o mock según configuración.
        """
        if self.use_real_models and model_id in self.real_models:
            return self._real_model_prediction(features, model_id)
        else:
            return self._mock_prediction(features, model_id)

    def _real_model_prediction(
        self, features: Dict[str, Any], model_id: str
    ) -> List[float]:
        """
        Predicción usando modelos reales LightGBM/Random Forest.
        """
        try:
            model = self.real_models[model_id]

            # Preparar datos para modelos reales
            # (Los modelos reales esperan cierto formato de features)
            input_data = self._prepare_real_model_input(features)

            # Ejecutar predicción
            prediction = model.predict(input_data)

            # Convertir a formato esperado por tests
            if isinstance(prediction, np.ndarray):
                if prediction.ndim > 1:
                    prediction = prediction.flatten()
                prediction = prediction.tolist()
            elif not isinstance(prediction, list):
                prediction = [float(prediction)]

            logger.info(f"🎯 Predicción real con {model_id}: {prediction}")
            return prediction

        except Exception as e:
            logger.error(f"❌ Error en predicción real: {e}")
            # Fallback a mock si falla el modelo real
            logger.info("🔄 Fallback a predicción mock")
            return self._mock_prediction(features, model_id)

    def _prepare_real_model_input(self, features: Dict[str, Any]) -> np.ndarray:
        """
        Preparar input para modelos reales.

        Los modelos LightGBM/RF fueron entrenados con features específicas.
        Aquí mapeamos las features de entrada a lo que esperan los modelos.
        """
        # Para este ejemplo, asumimos que los modelos esperan estas 4 features
        # En producción, esto vendría de la metadata del modelo
        # expected_features = ["age", "income", "score", "category_encoded"]

        # Convertir categoria a numérica (simple encoding)
        category_map = {"premium": 2, "standard": 1, "basic": 0, "unknown_category": -1}
        category_encoded = category_map.get(features.get("category", "basic"), 0)

        # Crear array con features en orden correcto
        feature_array = [
            features.get("age", 25),
            features.get("income", 50000),
            features.get("score", 0.5),
            category_encoded,
        ]

        # Convertir a numpy array con shape (1, n_features) para una sola predicción
        return np.array([feature_array])

    def _mock_prediction(self, features: Dict[str, Any], model_id: str) -> List[float]:
        """
        Predicción mock para testing (compatibilidad TDD).
        """
        # Mantener lógica mock original para tests
        if (
            model_id == "sensitive_model"
            and features.get("category") == "unknown_category"  # noqa: W503
        ):
            raise Exception("Model cannot handle unknown category")

        # Lógica mock mejorada
        age = features.get("age", 25)
        income = features.get("income", 50000)
        score = features.get("score", 0.5)

        if age < 30 and income > 60000:
            prediction_score = min(0.9, score + 0.2)
        elif age > 60:
            prediction_score = max(0.1, score - 0.3)
        else:
            prediction_score = score

        return [round(prediction_score, 3)]

    def _get_available_models(self) -> Dict[str, Any]:
        """Obtener modelos disponibles (reales + mocks)."""
        if self.use_real_models:
            # Combinar modelos reales con mocks para compatibilidad
            combined = {**self.real_models}
            # Agregar mocks que no están en reales
            for mock_id, mock_info in self.mock_models.items():
                if mock_id not in combined:
                    combined[mock_id] = mock_info
            return combined
        else:
            return self.mock_models

    def _get_model_type(self, model_id: str) -> str:
        """Obtener tipo del modelo."""
        if self.use_real_models and model_id in self.real_models:
            model = self.real_models[model_id]
            if hasattr(model, "__class__"):
                module = model.__class__.__module__
                if "lightgbm" in module:
                    return "lightgbm"
                elif "sklearn" in module:
                    return "sklearn"
            return "unknown"
        else:
            return self.mock_models.get(model_id, {}).get("type", "mock")

    def list_available_models(self) -> List[str]:
        """Listar modelos disponibles."""
        return list(self._get_available_models().keys())

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Obtener información detallada de un modelo."""
        available = self._get_available_models()
        if model_id not in available:
            return None

        info = {
            "model_id": model_id,
            "type": self._get_model_type(model_id),
            "is_real_model": self.use_real_models and model_id in self.real_models,
            "status": "trained",
        }

        # Agregar metadata si está disponible
        if model_id in self.model_metadata:
            metadata = self.model_metadata[model_id]
            info.update(
                {
                    "created_at": metadata.get("created_at"),
                    "description": metadata.get("description"),
                    "latest_version": metadata.get("latest_version"),
                }
            )

        return info

    def get_service_priority(self) -> str:
        """
        TDD STUB: Get current service priority
        RED: Returns default to make linter happy, test should fail on logic
        """
        return "primary"  # RED: Default return for TDD

    def switch_primary_service(self, service_name: str) -> bool:
        """
        TDD STUB: Switch primary service
        RED: Returns False by default for TDD failure
        """
        return False  # RED: Default return for TDD

    def get_fallback_history(self) -> List[Dict[str, Any]]:
        """
        TDD STUB: Get fallback usage history
        RED: Returns empty list by default for TDD failure
        """
        return []  # RED: Default return for TDD

    def reset_performance_metrics(self) -> bool:
        """
        TDD STUB: Reset performance metrics
        RED: Returns False by default for TDD failure
        """
        return False  # RED: Default return for TDD

    def configure_fallback_threshold(self, threshold: float) -> bool:
        """
        TDD STUB: Configure fallback threshold
        RED: Returns False by default for TDD failure
        """
        return False  # RED: Default return for TDD
