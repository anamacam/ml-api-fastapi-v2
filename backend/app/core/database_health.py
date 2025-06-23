"""
Health checker de base de datos - Extraído de database.py

REFACTORED: Separando health checks en módulo independiente
- DatabaseHealthChecker avanzado
- Métricas de rendimiento
- Tests de conectividad
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Any, Dict

from sqlalchemy import func, text
from sqlalchemy.exc import SQLAlchemyError

from .database_manager import DatabaseManager

# Configurar logger específico para el módulo de base de datos
logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Estados de salud de la base de datos"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class DatabaseHealthChecker:
    """
    🏥 Health checker avanzado de base de datos

    Health checker con:
    - Verificaciones detalladas de conectividad
    - Métricas de rendimiento
    - Tests de latencia
    - Diagnóstico automático
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Inicializar health checker

        Args:
            db_manager: Gestor de base de datos
        """
        self.db_manager = db_manager

    async def check_detailed_health(self) -> Dict[str, Any]:
        """
        Verificar salud detallada de la base de datos

        Returns:
            Dict[str, Any]: Reporte detallado de salud
        """
        start_time = time.time()
        
        health_report = {
            "timestamp": time.time(),
            "status": HealthStatus.UNHEALTHY,
            "checks": {},
            "metrics": {},
            "errors": [],
        }

        try:
            # Check básico de conectividad
            connectivity_check = await self._check_connectivity()
            health_report["checks"]["connectivity"] = connectivity_check

            # Check de métricas de pool
            pool_metrics = await self.db_manager.get_connection_metrics()
            health_report["metrics"]["pool"] = pool_metrics

            # Check de rendimiento
            performance_check = await self._check_performance()
            health_report["checks"]["performance"] = performance_check

            # Determinar estado general
            if connectivity_check["status"] == "healthy" and performance_check["status"] == "healthy":
                health_report["status"] = HealthStatus.HEALTHY
                # Agregar detalles solo si está healthy
                health_report["details"] = {
                    "connectivity": connectivity_check,
                    "performance": performance_check,
                    "pool": pool_metrics,
                }
            elif connectivity_check["status"] == "healthy":
                health_report["status"] = HealthStatus.DEGRADED
            else:
                health_report["status"] = HealthStatus.UNHEALTHY

            # Agregar tiempo total
            health_report["response_time"] = time.time() - start_time

        except Exception as e:
            health_report["errors"].append(str(e))
            health_report["error"] = str(e)
            logger.error("Error en health check: %s", e)

        # Si hay errores en los checks, exponer 'error' en el nivel raíz
        if any(
            check.get("error")
            for check in health_report["checks"].values()
            if isinstance(check, dict)
        ):
            health_report["error"] = "; ".join(
                str(check.get("error"))
                for check in health_report["checks"].values()
                if isinstance(check, dict) and check.get("error")
            )
        return health_report

    async def _check_connectivity(self) -> Dict[str, Any]:
        """Verificar conectividad básica"""
        check_result = {
            "status": "unhealthy",
            "response_time": 0,
            "error": None,
        }

        try:
            start_time = time.time()
            async with self.db_manager.get_session() as session:
                await session.execute(text("SELECT 1"))
                check_result["response_time"] = time.time() - start_time
                check_result["status"] = "healthy"
        except Exception as e:
            check_result["error"] = str(e)
            logger.error("Error en check de conectividad: %s", e)

        return check_result

    async def _check_performance(self) -> Dict[str, Any]:
        """Verificar rendimiento de la base de datos"""
        check_result = {
            "status": "unhealthy",
            "queries_per_second": 0,
            "average_response_time": 0,
            "error": None,
        }

        try:
            # Ejecutar queries de prueba
            start_time = time.time()
            async with self.db_manager.get_session() as session:
                # Query simple
                await session.execute(text("SELECT 1"))
                
                # Query con función
                await session.execute(text("SELECT NOW()"))
                
                # Query con cálculo
                await session.execute(text("SELECT 1 + 1"))

            total_time = time.time() - start_time
            check_result["average_response_time"] = total_time / 3
            check_result["queries_per_second"] = 3 / total_time
            
            # Determinar estado basado en rendimiento
            if check_result["average_response_time"] < 0.1:  # Menos de 100ms
                check_result["status"] = "healthy"
            elif check_result["average_response_time"] < 1.0:  # Menos de 1 segundo
                check_result["status"] = "degraded"
            else:
                check_result["status"] = "unhealthy"

        except Exception as e:
            check_result["error"] = str(e)
            logger.error("Error en check de rendimiento: %s", e)

        return check_result

    async def run_performance_test(self, num_queries: int = 10) -> Dict[str, Any]:
        """
        Ejecutar test de rendimiento completo

        Args:
            num_queries: Número de queries a ejecutar

        Returns:
            Dict[str, Any]: Resultados del test de rendimiento
        """
        test_results = {
            "total_queries": num_queries,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_time": 0,
            "average_time": 0,
            "min_time": float('inf'),
            "max_time": 0,
            "errors": [],
        }

        start_time = time.time()

        for i in range(num_queries):
            query_start = time.time()
            try:
                async with self.db_manager.get_session() as session:
                    await session.execute(text(f"SELECT {i + 1}"))
                
                query_time = time.time() - query_start
                test_results["successful_queries"] += 1
                test_results["min_time"] = min(test_results["min_time"], query_time)
                test_results["max_time"] = max(test_results["max_time"], query_time)

            except Exception as e:
                test_results["failed_queries"] += 1
                test_results["errors"].append(f"Query {i + 1}: {str(e)}")

        test_results["total_time"] = time.time() - start_time
        
        if test_results["successful_queries"] > 0:
            test_results["average_time"] = test_results["total_time"] / test_results["successful_queries"]

        return test_results 