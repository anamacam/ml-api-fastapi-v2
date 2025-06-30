# -*- coding: utf-8 -*-
"""
🏥 Sistema de Monitoreo de Salud y Métricas
from typing import Any, Dict, List, Optional, Union

Implementación TDD - FASE GREEN
"""

import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class HealthStatus(Enum):
    """Estados de salud del sistema"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class AnomalySeverity(Enum):
    """Severidad de anomalías detectadas"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Anomaly:
    """Anomalía detectada en métricas"""

    metric_name: str
    value: float
    threshold: float
    threshold_exceeded: bool
    severity: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Optional[Dict[str, Any]] = None


@dataclass
class SystemMetrics:
    """Métricas actuales del sistema"""

    avg_prediction_latency: float = 0.0
    model_load_times: Dict[str, float] = field(default_factory=dict)
    error_count_by_type: Dict[str, int] = field(default_factory=dict)
    total_requests: int = 0
    successful_requests: int = 0
    health_score: float = 1.0
    uptime_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0

    @property
    def success_rate(self) -> float:
        """Calcular tasa de éxito"""
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests

    @property
    def error_rate(self) -> float:
        """Calcular tasa de error"""
        return 1.0 - self.success_rate


@dataclass
class ComponentStatus:
    """Estado de un componente del sistema"""

    status: HealthStatus
    last_check: datetime = field(default_factory=datetime.now)
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class DetailedHealth:
    """Estado de salud detallado del sistema"""

    overall_status: HealthStatus
    models: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    database: Dict[str, Any] = field(default_factory=dict)
    external_services: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


class HealthMonitor:
    """
    Monitor de salud del sistema con detección de anomalías

    Funcionalidades:
    - Tracking de métricas de performance
    - Detección automática de anomalías
    - Monitoreo de componentes individuales
    - Health checks detallados
    """

    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.start_time = time.time()

        # Métricas de latencia
        self.latency_measurements: deque[float] = deque(maxlen=window_size)

        # Tracking de modelos
        self.model_load_times: Dict[str, float] = {}
        self.model_statuses: Dict[str, HealthStatus] = {}

        # Tracking de errores
        self.error_counts: defaultdict[str, int] = defaultdict(int)
        self.total_requests = 0
        self.successful_requests = 0

        # Estados de componentes
        self.database_status = HealthStatus.HEALTHY
        self.external_services: Dict[str, HealthStatus] = {}

        # Umbrales para detección de anomalías
        self.thresholds: Dict[str, Dict[str, float]] = {
            "prediction_latency": {
                "warning": 1.0,  # 1 segundo
                "critical": 5.0,  # 5 segundos
            },
            "error_rate": {"warning": 0.05, "critical": 0.15},  # 5%  # 15%
            "memory_usage": {"warning": 1024, "critical": 2048},  # 1GB  # 2GB
        }

    def record_prediction_latency(self, latency_seconds: float):
        """
        Registrar latencia de predicción

        Args:
            latency_seconds: Latencia en segundos
        """
        self.latency_measurements.append(latency_seconds)
        self.total_requests += 1
        self.successful_requests += 1

    def record_model_load_time(self, model_id: str, load_time_seconds: float):
        """
        Registrar tiempo de carga de modelo

        Args:
            model_id: ID del modelo
            load_time_seconds: Tiempo de carga en segundos
        """
        self.model_load_times[model_id] = load_time_seconds
        self.set_model_status(model_id, HealthStatus.HEALTHY)

    def record_error(self, error_type: str, severity: str = "medium"):
        """
        Registrar error del sistema

        Args:
            error_type: Tipo de error
            severity: Severidad del error
        """
        self.error_counts[error_type] += 1
        self.total_requests += 1

        # Ajustar health score basado en severidad
        if severity == "high":
            self._adjust_health_score(-0.1)
        elif severity == "medium":
            self._adjust_health_score(-0.05)
        else:
            self._adjust_health_score(-0.01)

    def set_model_status(self, model_id: str, status: Union[str, HealthStatus]):
        """Establecer estado de un modelo"""
        if isinstance(status, str):
            status = HealthStatus(status)
        self.model_statuses[model_id] = status

    def set_database_status(self, status: Union[str, HealthStatus]):
        """Establecer estado de la base de datos"""
        if isinstance(status, str):
            status = HealthStatus(status)
        self.database_status = status

    def set_external_service_status(
        self, service_name: str, status: Union[str, HealthStatus]
    ):
        """Establecer estado de servicio externo"""
        if isinstance(status, str):
            status = HealthStatus(status)
        self.external_services[service_name] = status

    def _adjust_health_score(self, delta: float):
        """Ajustar puntaje de salud del sistema"""
        current_score = getattr(self, "_health_score", 1.0)
        self._health_score = max(0.0, min(1.0, current_score + delta))

    def get_current_metrics(self) -> SystemMetrics:
        """
        Obtener métricas actuales del sistema

        Returns:
            Métricas del sistema
        """
        # Calcular latencia promedio
        avg_latency = 0.0
        if self.latency_measurements:
            avg_latency = statistics.mean(self.latency_measurements)

        # Calcular health score
        health_score = getattr(self, "_health_score", 1.0)

        # Calcular uptime
        uptime = time.time() - self.start_time

        return SystemMetrics(
            avg_prediction_latency=avg_latency,
            model_load_times=self.model_load_times.copy(),
            error_count_by_type=dict(self.error_counts),
            total_requests=self.total_requests,
            successful_requests=self.successful_requests,
            health_score=health_score,
            uptime_seconds=uptime,
        )

    def detect_anomalies(self) -> List[Anomaly]:
        """
        Detectar anomalías en las métricas

        Returns:
            Lista de anomalías detectadas
        """
        anomalies = []
        metrics = self.get_current_metrics()

        # Verificar latencia de predicción
        latency_anomalies = self._check_prediction_latency_anomalies(metrics)
        anomalies.extend(latency_anomalies)

        # Verificar tasa de error
        error_anomalies = self._check_error_rate_anomalies(metrics)
        anomalies.extend(error_anomalies)

        return anomalies

    def _check_prediction_latency_anomalies(self, metrics: SystemMetrics) -> List[Anomaly]:
        """Verificar anomalías en latencia de predicción"""
        anomalies = []
        critical_threshold = self.thresholds["prediction_latency"]["critical"]
        warning_threshold = self.thresholds["prediction_latency"]["warning"]

        if metrics.avg_prediction_latency > critical_threshold:
            anomalies.append(
                Anomaly(
                    metric_name="prediction_latency",
                    value=metrics.avg_prediction_latency,
                    threshold=critical_threshold,
                    threshold_exceeded=True,
                    severity="critical",
                )
            )
        elif metrics.avg_prediction_latency > warning_threshold:
            anomalies.append(
                Anomaly(
                    metric_name="prediction_latency",
                    value=metrics.avg_prediction_latency,
                    threshold=warning_threshold,
                    threshold_exceeded=True,
                    severity="warning",
                )
            )

        return anomalies

    def _check_error_rate_anomalies(self, metrics: SystemMetrics) -> List[Anomaly]:
        """Verificar anomalías en tasa de error"""
        anomalies = []
        critical_threshold = self.thresholds["error_rate"]["critical"]
        warning_threshold = self.thresholds["error_rate"]["warning"]

        if metrics.error_rate > critical_threshold:
            anomalies.append(
                Anomaly(
                    metric_name="error_rate",
                    value=metrics.error_rate,
                    threshold=critical_threshold,
                    threshold_exceeded=True,
                    severity="critical",
                )
            )
        elif metrics.error_rate > warning_threshold:
            anomalies.append(
                Anomaly(
                    metric_name="error_rate",
                    value=metrics.error_rate,
                    threshold=warning_threshold,
                    threshold_exceeded=True,
                    severity="warning",
                )
            )

        return anomalies

    def get_detailed_health(self) -> DetailedHealth:
        """
        Obtener estado de salud detallado

        Returns:
            Estado detallado de todos los componentes
        """
        issues = []
        overall_status = HealthStatus.HEALTHY

        # Evaluar modelos
        models_status, model_issues, model_status = self._evaluate_models()
        issues.extend(model_issues)
        overall_status = self._update_overall_status(overall_status, model_status)

        # Evaluar base de datos
        database_info, db_issues, db_status = self._evaluate_database()
        issues.extend(db_issues)
        overall_status = self._update_overall_status(overall_status, db_status)

        # Evaluar servicios externos
        external_services_info, service_issues, service_status = self._evaluate_external_services()
        issues.extend(service_issues)
        overall_status = self._update_overall_status(overall_status, service_status)

        # Verificar anomalías
        anomaly_issues, anomaly_status = self._evaluate_anomalies()
        issues.extend(anomaly_issues)
        overall_status = self._update_overall_status(overall_status, anomaly_status)

        return DetailedHealth(
            overall_status=overall_status,
            models=models_status,
            database=database_info,
            external_services=external_services_info,
            issues=issues,
        )

    def _evaluate_models(self) -> tuple[Dict[str, Dict[str, Any]], List[str], HealthStatus]:
        """Evaluar estado de los modelos"""
        models_status = {}
        issues = []
        overall_status = HealthStatus.HEALTHY

        for model_id, status in self.model_statuses.items():
            models_status[model_id] = {
                "status": status.value,
                "load_time": self.model_load_times.get(model_id, 0),
                "last_check": datetime.now().isoformat(),
            }

            if status != HealthStatus.HEALTHY:
                issues.append(f"Model {model_id} is {status.value}")
                if status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                    overall_status = HealthStatus.DEGRADED

        return models_status, issues, overall_status

    def _evaluate_database(self) -> tuple[Dict[str, Any], List[str], HealthStatus]:
        """Evaluar estado de la base de datos"""
        database_info = {
            "status": self.database_status.value,
            "last_check": datetime.now().isoformat(),
        }

        issues = []
        if self.database_status != HealthStatus.HEALTHY:
            issues.append(f"Database is {self.database_status.value}")

        return database_info, issues, self.database_status

    def _evaluate_external_services(self) -> tuple[Dict[str, Dict[str, Any]], List[str], HealthStatus]:
        """Evaluar estado de servicios externos"""
        external_services_info = {}
        issues = []
        overall_status = HealthStatus.HEALTHY

        for service, status in self.external_services.items():
            external_services_info[service] = {
                "status": status.value,
                "last_check": datetime.now().isoformat(),
            }

            if status != HealthStatus.HEALTHY:
                issues.append(f"External service {service} is {status.value}")
                if status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                    overall_status = HealthStatus.DEGRADED

        return external_services_info, issues, overall_status

    def _evaluate_anomalies(self) -> tuple[List[str], HealthStatus]:
        """Evaluar anomalías detectadas"""
        issues = []
        overall_status = HealthStatus.HEALTHY

        anomalies = self.detect_anomalies()
        for anomaly in anomalies:
            if anomaly.severity in ["high", "critical"]:
                issues.append(f"High {anomaly.metric_name}: {anomaly.value}")
                overall_status = HealthStatus.DEGRADED

        return issues, overall_status

    def _update_overall_status(self, current_status: HealthStatus, new_status: HealthStatus) -> HealthStatus:
        """Actualizar estado general basado en nuevo estado"""
        if current_status == HealthStatus.HEALTHY and new_status != HealthStatus.HEALTHY:
            return new_status
        return current_status

    def reset_metrics(self):
        """Resetear todas las métricas"""
        self.latency_measurements.clear()
        self.error_counts.clear()
        self.total_requests = 0
        self.successful_requests = 0
        self._health_score = 1.0
        self.start_time = time.time()
