"""
Gestor de base de datos - Extraído de database.py

REFACTORED: Separando gestor de base de datos en módulo independiente
- DatabaseManager principal
- Gestión de conexiones y sesiones
- Health checks básicos
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional, Union

from sqlalchemy import text
from sqlalchemy.exc import DisconnectionError, SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import QueuePool, StaticPool

from .database_config import DatabaseConfig, VPSDatabaseConfig

# Configurar logger específico para el módulo de base de datos
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    🗄️ Gestor enterprise de base de datos

    Gestor robusto de conexiones con:
    - Pool de conexiones optimizado
    - Reconexión automática
    - Health checks integrados
    - Métricas de rendimiento
    - Manejo de errores avanzado
    """

    def __init__(
        self, config: Union[DatabaseConfig, VPSDatabaseConfig], is_test: bool = False
    ):
        """
        Inicializar gestor de base de datos

        Args:
            config: Configuración de la base de datos
            is_test: Si es para tests (usa configuración especial)
        """
        self.config = config
        self.is_test = is_test
        self._engine: Optional[AsyncEngine] = None
        self._session_maker: Optional[async_sessionmaker[AsyncSession]] = None
        self._initialized = False
        self._last_health_check = 0
        self._health_check_interval = 300  # 5 minutos

    @property
    def is_initialized(self) -> bool:
        """Verificar si el gestor está inicializado"""
        return self._initialized

    @property
    def engine(self) -> Optional[AsyncEngine]:
        """Proporciona acceso público al engine para compatibilidad con tests."""
        return self._engine

    @property
    def session_maker(self) -> Optional[async_sessionmaker[AsyncSession]]:
        """Proporciona acceso público al session_maker para compatibilidad con tests."""
        return self._session_maker

    @property
    def session_factory(self) -> Optional[async_sessionmaker[AsyncSession]]:
        """Alias para session_maker para compatibilidad con tests."""
        return self._session_maker

    async def initialize(self) -> None:
        """Inicializar el gestor de base de datos"""
        if self._initialized:
            logger.warning("DatabaseManager ya está inicializado")
            return

        await self._create_engine_and_session()
        await self._test_connection()
        self._initialized = True
        logger.info("DatabaseManager inicializado exitosamente")

    async def _create_engine_and_session(self) -> None:
        """Crear engine y session maker"""
        try:
            # Configurar pool según el tipo de base de datos
            if self.config.driver_type.value == "sqlite":
                # SQLite en memoria para tests
                pool_class = StaticPool
                pool_args = {}
            else:
                # Pool optimizado para PostgreSQL/MySQL
                pool_class = QueuePool
                pool_args = {
                    "pool_size": self.config.pool_size,
                    "max_overflow": self.config.max_overflow,
                    "pool_timeout": self.config.pool_timeout,
                    "pool_recycle": self.config.pool_recycle,
                    "pool_pre_ping": self.config.pool_pre_ping,
                }

            # Crear engine
            self._engine = create_async_engine(
                self.config.database_url,
                echo=self.config.echo,
                poolclass=pool_class,
                **pool_args,
                connect_args=self.config.connect_args,
            )

            # Crear session maker
            self._session_maker = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            logger.info(
                "Engine y session maker creados: %s",
                self.config.driver_type.value,
            )

        except Exception as e:
            logger.error("Error creando engine: %s", e)
            raise

    async def _test_connection(self) -> None:
        """Probar conexión a la base de datos"""
        try:
            if self._session_maker is None:
                raise RuntimeError("Session maker no está inicializado")
            
            async with self._session_maker() as session:
                await session.execute(text("SELECT 1"))
                logger.info("Conexión a base de datos verificada")
        except Exception as e:
            logger.error("Error probando conexión: %s", e)
            raise

    @asynccontextmanager
    async def get_session(self):
        """
        Obtener sesión de base de datos con manejo automático

        Yields:
            AsyncSession: Sesión de base de datos

        Raises:
            SQLAlchemyError: Si hay error en la base de datos
        """
        if not self._initialized:
            raise RuntimeError("DatabaseManager no está inicializado")

        if self._session_maker is None:
            raise RuntimeError("Session maker no está inicializado")

        session = self._session_maker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def check_health(self) -> bool:
        """Verificar salud de la base de datos"""
        try:
            async with self.get_session() as session:
                await session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error("Health check falló: %s", e)
            return False

    async def get_connection_metrics(self) -> dict:
        """Obtener métricas de conexión"""
        if not self._engine:
            return {"error": "Engine no inicializado"}

        pool = self._engine.pool
        
        # Verificar que el pool tenga los métodos necesarios
        try:
            pool_class = type(pool).__name__
            checked_in = getattr(pool, 'checkedin', lambda: 0)()
            checked_out = getattr(pool, 'checkedout', lambda: 0)()
            connections_in_pool = checked_in + checked_out
            
            return {
                "pool_class": pool_class,
                "pool_size": getattr(pool, 'size', lambda: 0)(),
                "checked_in": checked_in,
                "checked_out": checked_out,
                "connections_checked_out": checked_out,  # Alias para compatibilidad
                "connections_in_pool": connections_in_pool,
                "overflow": getattr(pool, 'overflow', lambda: 0)(),
                "current_overflow": getattr(pool, 'overflow', lambda: 0)(),  # Alias para compatibilidad
                "invalid": getattr(pool, 'invalid', lambda: 0)(),
            }
        except Exception as e:
            logger.warning(f"No se pudieron obtener métricas del pool: {e}")
            return {
                "pool_class": None,
                "pool_size": 0,
                "checked_in": 0,
                "checked_out": 0,
                "connections_checked_out": 0,  # Alias para compatibilidad
                "connections_in_pool": 0,
                "overflow": 0,
                "current_overflow": 0,  # Alias para compatibilidad
                "invalid": 0,
                "error": "Métricas no disponibles"
            }

    async def close(self) -> None:
        """Cerrar el gestor de base de datos"""
        if self._engine:
            await self._engine.dispose()
            self._initialized = False
            logger.info("DatabaseManager cerrado")

    async def cleanup(self):
        """Cleanup para tests"""
        await self.close() 