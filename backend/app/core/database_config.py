"""
Configuración de base de datos - Extraído de database.py

REFACTORED: Separando configuraciones en módulo independiente
- DatabaseConfig base
- VPSDatabaseConfig optimizada
- Validaciones y normalización
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

import psutil

# Configurar logger específico para el módulo de base de datos
logger = logging.getLogger(__name__)


class DatabaseDriver(str, Enum):
    """Drivers de base de datos soportados"""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


@dataclass
class DatabaseConfig:
    """
    🔧 Configuración enterprise de base de datos

    Configuración robusta y validada para diferentes entornos
    con valores por defecto optimizados para producción.

    Attributes:
        database_url: URL de conexión a la base de datos
        echo: Si mostrar logs de SQL (solo para development)
        pool_size: Tamaño base del pool de conexiones
        max_overflow: Conexiones adicionales permitidas
        pool_timeout: Timeout para obtener conexión del pool
        pool_recycle: Tiempo para reciclar conexiones (segundos)
        pool_pre_ping: Verificar conexiones antes de usar
        connect_args: Argumentos adicionales para la conexión
        query_timeout: Timeout para queries individuales
        connection_retries: Intentos de reconexión automática
    """

    database_url: str = "sqlite+aiosqlite:///:memory:"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    connect_args: Dict[str, Any] = field(default_factory=dict)
    query_timeout: int = 60
    connection_retries: int = 3

    def __post_init__(self):
        """Validar configuración después de inicialización"""
        self._validate_configuration()
        self._normalize_values()

    def _validate_configuration(self) -> None:
        """Validar todos los parámetros de configuración"""
        if self.pool_size < 1:
            raise ValueError("pool_size debe ser mayor a 0")
        if self.max_overflow < 0:
            raise ValueError("max_overflow debe ser mayor o igual a 0")
        if self.pool_timeout < 1:
            raise ValueError("pool_timeout debe ser mayor a 0")
        if self.pool_recycle < 300:  # Mínimo 5 minutos
            logger.warning(
                f"pool_recycle muy bajo ({self.pool_recycle}s), recomendado >= 300s"
            )
        if self.query_timeout < 10:
            raise ValueError("query_timeout debe ser al menos 10 segundos")
        if self.connection_retries < 0 or self.connection_retries > 10:
            raise ValueError("connection_retries debe estar entre 0 y 10")

    def _normalize_values(self) -> None:
        """Normalizar y optimizar valores de configuración"""
        # Asegurar que echo esté deshabilitado en producción
        if os.getenv("ENVIRONMENT", "development") == "production":
            self.echo = False

    @property
    def driver_type(self) -> DatabaseDriver:
        """Detectar el tipo de driver de la URL"""
        url_lower = self.database_url.lower()
        if "sqlite" in url_lower:
            return DatabaseDriver.SQLITE
        elif "postgresql" in url_lower:
            return DatabaseDriver.POSTGRESQL
        elif "mysql" in url_lower:
            return DatabaseDriver.MYSQL
        else:
            raise ValueError(f"Driver no soportado en URL: {self.database_url}")

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """
        Crear configuración desde variables de entorno con validación

        Returns:
            DatabaseConfig: Configuración construida desde el entorno

        Raises:
            ValueError: Si la configuración del entorno es inválida
        """
        try:
            return cls(
                database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:"),
                echo=os.getenv("DB_ECHO", "false").lower() == "true",
                pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
                max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
                pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
                pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
                query_timeout=int(os.getenv("DB_QUERY_TIMEOUT", "60")),
                connection_retries=int(os.getenv("DB_CONNECTION_RETRIES", "3")),
            )
        except ValueError as e:
            raise ValueError(f"Error en configuración de entorno: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convertir configuración a diccionario para logging"""
        return {
            "driver_type": self.driver_type.value,
            "echo": self.echo,
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "pool_recycle": self.pool_recycle,
            "pool_pre_ping": self.pool_pre_ping,
            "query_timeout": self.query_timeout,
            "connection_retries": self.connection_retries,
        }


@dataclass
class VPSDatabaseConfig(DatabaseConfig):
    """
    🔧 Configuración optimizada para VPS

    Extiende DatabaseConfig con ajustes automáticos basados en:
    - Recursos disponibles del VPS
    - Latencia de red
    - Uso de memoria
    - CPU disponible
    """

    def __post_init__(self):
        """Validar y optimizar configuración para VPS"""
        super().__post_init__()
        self._optimize_for_vps()

    def _optimize_for_vps(self) -> None:
        """Optimizar configuración basada en recursos del VPS"""
        # Obtener recursos del sistema
        cpu_count = psutil.cpu_count(logical=False) or 1
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024 * 1024 * 1024)  # Convertir a GB

        # Ajustar pool size basado en CPU y memoria
        optimal_pool_size = min(
            cpu_count * 2,  # 2 conexiones por CPU
            int(memory_gb * 2),  # 2 conexiones por GB de RAM
            20,  # Máximo 20 conexiones
        )
        self.pool_size = min(self.pool_size, optimal_pool_size)

        # Ajustar max_overflow basado en pool_size
        self.max_overflow = min(self.max_overflow, self.pool_size)

        # Ajustar timeouts para conexiones remotas
        self.pool_timeout = max(self.pool_timeout, 60)  # Mínimo 60 segundos
        self.query_timeout = max(self.query_timeout, 120)  # Mínimo 120 segundos

        # Ajustar retries para conexiones remotas
        self.connection_retries = max(self.connection_retries, 5)

        # Habilitar pre-ping para detectar conexiones muertas
        self.pool_pre_ping = True

        # Ajustar pool_recycle para conexiones remotas
        self.pool_recycle = min(self.pool_recycle, 1800)  # Máximo 30 minutos

        logger.info(
            "Configuración VPS optimizada: CPU=%s, RAM=%.1fGB, "
            "pool_size=%s, max_overflow=%s",
            cpu_count,
            memory_gb,
            self.pool_size,
            self.max_overflow,
        )

    def get_connection_args(self) -> Dict[str, Any]:
        """
        Devuelve argumentos de conexión optimizados para drivers
        compatibles (PostgreSQL/MySQL).
        """
        driver = self.database_url.split(":")[0]
        if driver.startswith("postgresql"):
            # asyncpg no soporta connect_timeout, statement_timeout, command_timeout
            # usar solo parámetros compatibles
            return {
                "timeout": 30,
                "server_settings": {
                    "keepalives": "1",
                    "keepalives_idle": "30",
                    "keepalives_interval": "10",
                    "keepalives_count": "5",
                }
            }
        elif driver.startswith("mysql"):
            return {
                "connect_timeout": 30,
                "command_timeout": self.query_timeout,
                "statement_timeout": self.query_timeout,
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
            }
        # Para SQLite y otros, no pasar argumentos avanzados
        return {} 