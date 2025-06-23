# -*- coding: utf-8 -*-
"""
��️ DATABASE MODULE - REFACTORED
Fase: REFACTOR - Código modularizado y optimizado

Módulo enterprise de base de datos con:
- Configuración flexible y validada por entorno
- Gestor de conexiones con pool optimizado
- Repository pattern genérico type-safe
- Health checks avanzados con métricas
- Integración async/await robusta
- Logging y monitoreo integrado
- Manejo de errores avanzado
- Optimizaciones específicas para VPS

REFACTORED: Separado en módulos especializados para reducir complejidad
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy.ext.asyncio import AsyncSession

from .database_config import DatabaseConfig, VPSDatabaseConfig
from .database_manager import DatabaseManager
from .database_repository import Base, BaseRepository
from .database_health import DatabaseHealthChecker, HealthStatus

# Configurar logger específico para el módulo de base de datos
logger = logging.getLogger(__name__)

# Type hints para Generic Repository
ModelType = TypeVar("ModelType", bound=Base)

# Variable global para el gestor de base de datos
_database_manager: Optional[DatabaseManager] = None


async def init_database(config: DatabaseConfig) -> None:
    """Inicializar base de datos globalmente"""
    global _database_manager
    _database_manager = DatabaseManager(config)
    await _database_manager.initialize()


async def close_database() -> None:
    """Cerrar base de datos globalmente"""
    global _database_manager
    if _database_manager:
        await _database_manager.close()
        _database_manager = None


def get_database_manager() -> Optional[DatabaseManager]:
    """Obtener gestor de base de datos global"""
    return _database_manager


@asynccontextmanager
async def get_async_session():
    """
    Context manager para obtener sesión de base de datos

    Yields:
        AsyncSession: Sesión de base de datos

    Raises:
        RuntimeError: Si el gestor no está inicializado
    """
    if not _database_manager:
        raise RuntimeError("Database manager no inicializado")

    async with _database_manager.get_session() as session:
        yield session


async def get_db_health() -> Dict[str, Any]:
    """Obtener estado de salud de la base de datos"""
    if not _database_manager:
        return {
            "status": HealthStatus.UNHEALTHY,
            "error": "Database manager no inicializado",
        }

    health_checker = DatabaseHealthChecker(_database_manager)
    return await health_checker.check_detailed_health()


def create_repository(
    model: Type[ModelType], session: AsyncSession
) -> BaseRepository[ModelType]:
    """
    Crear repository para un modelo específico

    Args:
        model: Clase del modelo SQLAlchemy
        session: Sesión de base de datos

    Returns:
        BaseRepository[ModelType]: Repository configurado
    """
    return BaseRepository(model, session)
