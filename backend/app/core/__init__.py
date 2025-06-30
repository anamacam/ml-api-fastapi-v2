"""
Módulo core - REFACTORED

REFACTORED: Módulo modularizado con baja complejidad ciclomática
- Separado en módulos especializados
- Mantenida funcionalidad completa
- Mejorada mantenibilidad
"""

# Database module exports
from .database import (
    Base,
    ModelType,
    init_database,
    close_database,
    get_database_manager,
    get_async_session,
    get_db_health,
    create_repository,
)
from .database_config import DatabaseConfig, VPSDatabaseConfig, DatabaseDriver
from .database_manager import DatabaseManager
from .database_repository import BaseRepository
from .database_health import DatabaseHealthChecker, HealthStatus

__all__ = [
    # Database
    "Base",
    "ModelType",
    "DatabaseConfig",
    "VPSDatabaseConfig", 
    "DatabaseDriver",
    "DatabaseManager",
    "BaseRepository",
    "DatabaseHealthChecker",
    "HealthStatus",
    "init_database",
    "close_database",
    "get_database_manager",
    "get_async_session",
    "get_db_health",
    "create_repository",
] 