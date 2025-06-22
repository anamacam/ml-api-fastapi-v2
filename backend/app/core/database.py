# -*- coding: utf-8 -*-
"""
🗄️ DATABASE MODULE - TDD CICLO 6 [REFACTORED]
Fase: REFACTOR - Código optimizado y mejorado

Módulo enterprise de base de datos con:
- Configuración flexible y validada por entorno
- Gestor de conexiones con pool optimizado
- Repository pattern genérico type-safe
- Health checks avanzados con métricas
- Integración async/await robusta
- Logging y monitoreo integrado
- Manejo de errores avanzado
- Optimizaciones específicas para VPS
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

import psutil
from sqlalchemy import func, select, text
from sqlalchemy.exc import DisconnectionError, SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import QueuePool, StaticPool

# Configurar logger específico para el módulo de base de datos
logger = logging.getLogger(__name__)


# Base para modelos SQLAlchemy
class Base(DeclarativeBase):
    pass


# Type hints para Generic Repository
ModelType = TypeVar("ModelType", bound=Base)

# Variable global para el gestor de base de datos
_database_manager: Optional["DatabaseManager"] = None


class DatabaseDriver(str, Enum):
    """Drivers de base de datos soportados"""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


class HealthStatus(str, Enum):
    """Estados de salud de la base de datos"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


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
        if driver.startswith("postgresql") or driver.startswith("mysql"):
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


class DatabaseManager:
    """
    🗄️ Gestor enterprise de base de datos

    Maneja el engine, pool de conexiones, sessions y health checks.
    Implementa async/await, retry logic y monitoreo avanzado.

    Attributes:
        config (DatabaseConfig): Configuración de la base de datos
        engine (AsyncEngine): Instancia del motor SQLAlchemy
        session_factory (async_sessionmaker): Fábrica de sesiones
        is_test (bool): Flag para entorno de pruebas
    """

    def __init__(
        self, config: Union[DatabaseConfig, VPSDatabaseConfig], is_test: bool = False
    ):
        if not isinstance(config, (DatabaseConfig, VPSDatabaseConfig)):
            raise TypeError(
                "config debe ser una instancia de DatabaseConfig o VPSDatabaseConfig"
            )
        self.config: Union[DatabaseConfig, VPSDatabaseConfig] = config
        self.is_test: bool = is_test
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._is_initialized = False
        self._connection_metrics: Dict[str, Any] = {}
        self._last_health_check: Optional[Dict[str, Any]] = None
        self._connection_attempts = 0
        self._last_error: Optional[str] = None
        logger.info(f"DatabaseManager inicializado con config: {config.to_dict()}")

    @property
    def is_initialized(self) -> bool:
        """Verifica si el gestor de BD está inicializado"""
        return self._is_initialized

    async def initialize(self) -> None:
        """Inicializa el engine y la sesión de la base de datos"""
        if self.is_initialized:
            logger.warning("El gestor de base de datos ya está inicializado.")
            return

        await self._create_engine_and_session()
        self._is_initialized = True
        logger.info("El gestor de base de datos se ha inicializado correctamente.")

    async def _create_engine_and_session(self) -> None:
        """Crear el engine y el sessionmaker con reintentos"""

        engine_args: Dict[str, Any] = {"echo": self.config.echo}

        if self.config.driver_type == DatabaseDriver.SQLITE:
            engine_args["poolclass"] = StaticPool
            engine_args["connect_args"] = {"check_same_thread": False}
        else:
            engine_args.update(
                {
                    "poolclass": QueuePool,
                    "pool_size": self.config.pool_size,
                    "max_overflow": self.config.max_overflow,
                    "pool_timeout": self.config.pool_timeout,
                    "pool_recycle": self.config.pool_recycle,
                    "pool_pre_ping": self.config.pool_pre_ping,
                }
            )
            if isinstance(self.config, VPSDatabaseConfig):
                engine_args["connect_args"] = self.config.get_connection_args()
            elif self.config.connect_args:
                engine_args["connect_args"] = self.config.connect_args

        last_exception: Optional[Exception] = None
        for attempt in range(self.config.connection_retries + 1):
            try:
                self.engine = create_async_engine(
                    self.config.database_url, **engine_args
                )
                await self._test_connection()
                self.session_factory = async_sessionmaker(
                    bind=self.engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                    autoflush=False,
                )
                logger.info(
                    "Motor de base de datos y fábrica de sesiones creados exitosamente."
                )
                return
            except (SQLAlchemyError, DisconnectionError) as e:
                logger.error(f"Error creando engine: {e}", exc_info=True)
                last_exception = e
                if attempt < self.config.connection_retries:
                    wait_time = 2 ** (attempt + 1)
                    logger.warning(
                        "Intento %s fallido: %s. Reintentando en %ss...",
                        attempt + 1,
                        e,
                        wait_time,
                    )
                    await asyncio.sleep(wait_time)

        logger.error(
            f"Todos los intentos de conexión fallaron: {last_exception}", exc_info=True
        )
        if last_exception:
            raise last_exception
        raise SQLAlchemyError(
            "No se pudo conectar a la base de datos después de múltiples reintentos."
        )

    async def _test_connection(self) -> None:
        """Verificar la conexión con la base de datos"""
        if not self.engine:
            raise RuntimeError("El motor de la base de datos no está inicializado.")
        try:
            async with self.engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            logger.info("Conexión con la base de datos verificada exitosamente.")
        except Exception as e:
            logger.error(
                f"Fallo en la verificación de conexión a la base de datos: {e}"
            )
            raise

    @asynccontextmanager
    async def get_session(self):
        """
        Proporciona una sesión de base de datos asíncrona

        Asegura que la sesión se cierre correctamente.
        """
        if not self.session_factory:
            raise RuntimeError("El gestor de base de datos no está inicializado.")

        session = self.session_factory()
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def check_health(self) -> bool:
        """Verifica la salud básica de la conexión"""
        try:
            await self._test_connection()
            return True
        except Exception:
            return False

    async def get_connection_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de la conexión y del pool"""
        if not self.engine:
            return {"error": "Engine no inicializado"}

        try:
            pool = self.engine.pool
            self._connection_metrics = {
                "pool_class": pool.__class__.__name__,
                "pool_size": getattr(pool, "size", lambda: 0)(),
                "connections_in_pool": getattr(pool, "checkedin", lambda: 0)(),
                "connections_checked_out": getattr(pool, "checkedout", lambda: 0)(),
                "current_overflow": getattr(pool, "overflow", lambda: 0)(),
            }
        except AttributeError:
            # Fallback si los métodos no están disponibles
            self._connection_metrics = {
                "pool_class": "unknown",
                "pool_size": 0,
                "connections_in_pool": 0,
                "connections_checked_out": 0,
                "current_overflow": 0,
            }
        return self._connection_metrics

    async def close(self) -> None:
        """Cierra el engine de la base de datos y limpia recursos"""
        if self.engine:
            logger.info("Cerrando el motor de la base de datos...")
            await self.engine.dispose()
            self.engine = None
            self._is_initialized = False
            logger.info("Motor de la base de datos cerrado.")

    async def cleanup(self):
        """Alias para close() para consistencia de API."""
        await self.close()


class BaseRepository(Generic[ModelType]):
    """
    🧩 Generic Repository Pattern

    Abstrae el acceso a datos para un modelo SQLAlchemy específico.
    Proporciona operaciones CRUD (Crear, Leer, Actualizar, Borrar)
    de forma type-safe y asíncrona.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        Inicializar el repositorio.

        Args:
            model: El modelo SQLAlchemy con el que operará el repositorio.
            session: La sesión de base de datos asíncrona.
        """
        self.model = model
        self.session = session
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def create(self, data: Dict[str, Any]) -> ModelType:
        """
        Crear un nuevo registro en la base de datos.

        Args:
            data: Diccionario con los datos para el nuevo registro.

        Returns:
            ModelType: La instancia del modelo creado.
        """
        self.logger.debug(
            f"Creando una nueva instancia de {self.model.__name__} con datos: {data}"
        )
        self._validate_create_data(data)

        db_obj = self.model(**data)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)

        self.logger.info(
            f"{self.model.__name__} creado con ID: {getattr(db_obj, 'id', 'N/A')}"
        )
        return db_obj

    async def get_by_id(self, entity_id: Union[int, str]) -> Optional[ModelType]:
        """
        Obtener un registro por su ID.

        Args:
            entity_id: El ID del registro a buscar.

        Returns:
            Optional[ModelType]: El registro encontrado o None.
        """
        self.logger.debug(f"Buscando {self.model.__name__} con ID: {entity_id}")
        # Usar getattr para acceder al atributo id de forma segura
        id_attr = getattr(self.model, "id", None)
        if id_attr is None:
            raise AttributeError(
                f"Model {self.model.__name__} doesn't have an 'id' attribute"
            )
        query = select(self.model).where(id_attr == entity_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Obtener todos los registros con paginación

        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a devolver

        Returns:
            List[ModelType]: Lista de registros
        """
        self.logger.debug(
            f"Obteniendo todos los {self.model.__name__} con skip={skip}, limit={limit}"
        )
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self, entity_id: Union[int, str], data: Dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Actualizar un registro por su ID

        Args:
            entity_id: ID del registro
            data: Datos para actualizar

        Returns:
            Optional[ModelType]: Registro actualizado o None si no existe
        """
        self.logger.debug(
            f"Actualizando {self.model.__name__} con ID {entity_id} con datos: {data}"
        )
        self._validate_update_data(data)

        db_obj = await self.get_by_id(entity_id)
        if db_obj:
            for key, value in data.items():
                setattr(db_obj, key, value)

            self.session.add(db_obj)
            await self.session.flush()
            await self.session.refresh(db_obj)
            self.logger.info(f"{self.model.__name__} con ID {entity_id} actualizado.")

        return db_obj

    async def delete(self, entity_id: Union[int, str]) -> bool:
        """
        Eliminar un registro por su ID.

        Args:
            entity_id: El ID del registro a eliminar.

        Returns:
            bool: True si se eliminó, False en caso contrario.
        """
        self.logger.debug(f"Eliminando {self.model.__name__} con ID: {entity_id}")
        db_obj = await self.get_by_id(entity_id)
        if db_obj:
            await self.session.delete(db_obj)
            await self.session.flush()
            self.logger.info(f"{self.model.__name__} con ID {entity_id} eliminado.")
            return True
        return False

    async def count(self) -> int:
        """Contar el número total de registros"""
        self.logger.debug(f"Contando registros de {self.model.__name__}")
        query = select(func.count()).select_from(self.model)
        result = await self.session.execute(query)
        count = result.scalar_one_or_none()
        return count or 0

    def _validate_create_data(self, data: Dict[str, Any]) -> None:
        """Hook de validación antes de crear"""
        if not data:
            raise ValueError("Los datos para crear no pueden estar vacíos")

    def _validate_update_data(self, data: Dict[str, Any]) -> None:
        """Hook de validación antes de actualizar"""
        if not data:
            raise ValueError("Los datos para actualizar no pueden estar vacíos")


class DatabaseHealthChecker:
    """
    🏥 Verificador enterprise de salud de base de datos

    Realiza checks detallados de salud con métricas avanzadas,
    alertas y monitoreo de rendimiento.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(f"{__name__}.HealthChecker")
        self._last_check_time = 0
        self._check_interval = 60  # 60 segundos entre checks
        self._degraded_threshold = 1000  # 1 segundo para estado degradado
        self._unhealthy_threshold = 5000  # 5 segundos para estado unhealthy

    async def check_detailed_health(self) -> Dict[str, Any]:
        """
        Verificación detallada de salud con métricas y alertas

        Returns:
            Dict[str, Any]: Estado detallado de salud con métricas
        """
        if not self.db_manager:
            return {
                "status": "unhealthy",
                "error": "DatabaseManager no está inicializado",
            }

        try:
            start_time = time.time()
            async with self.db_manager.get_session() as session:
                # Verificar conexión básica
                await session.execute(text("SELECT 1"))
                query_time = time.time() - start_time

                # Obtener métricas del pool con manejo seguro
                pool_metrics = {}
                if self.db_manager.engine and hasattr(self.db_manager.engine, "pool"):
                    pool = self.db_manager.engine.pool
                    pool_metrics = {
                        "size": getattr(pool, "size", lambda: 0)(),
                        "checkedin": getattr(pool, "checkedin", lambda: 0)(),
                        "checkedout": getattr(pool, "checkedout", lambda: 0)(),
                        "overflow": getattr(pool, "overflow", lambda: 0)(),
                    }
                else:
                    pool_metrics = {
                        "size": 0,
                        "checkedin": 0,
                        "checkedout": 0,
                        "overflow": 0,
                    }

                return {
                    "status": "healthy",
                    "details": {
                        "connection": "ok",
                        "query": "ok",
                        "pool": pool_metrics,
                    },
                    "metrics": {
                        "response_time": (time.time() - start_time) * 1000,
                        "query_time": query_time * 1000,
                    },
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def run_performance_test(self, num_queries: int = 10) -> Dict[str, Any]:
        """
        Ejecutar test de rendimiento con múltiples queries

        Args:
            num_queries: Número de queries a ejecutar

        Returns:
            Dict con métricas de rendimiento
        """
        self.logger.info(f"Iniciando test de rendimiento con {num_queries} queries")

        times = []
        errors = 0

        for i in range(num_queries):
            start = time.time()
            try:
                async with self.db_manager.get_session() as session:
                    await session.execute(text("SELECT 1"))
                times.append((time.time() - start) * 1000)
            except Exception as e:
                errors += 1
                self.logger.warning(f"Error en query {i}: {e}")

        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
        else:
            avg_time = min_time = max_time = 0

        results = {
            "queries_executed": len(times),
            "queries_failed": errors,
            "avg_response_time_ms": round(avg_time, 2),
            "min_response_time_ms": round(min_time, 2),
            "max_response_time_ms": round(max_time, 2),
            "success_rate": (
                round((len(times) / num_queries) * 100, 2) if num_queries > 0 else 0
            ),
        }

        self.logger.info(f"Test de rendimiento completado: {results}")
        return results


# Funciones de utilidad global mejoradas
async def init_database(config: DatabaseConfig) -> None:
    """Inicializa el gestor de base de datos global"""
    global _database_manager
    if not _database_manager:
        _database_manager = DatabaseManager(config)
    await _database_manager.initialize()


async def close_database() -> None:
    """Cierra la conexión del gestor de base de datos global"""
    if _database_manager and _database_manager.is_initialized:
        await _database_manager.close()


def get_database_manager() -> Optional[DatabaseManager]:
    """
    Obtiene la instancia global del gestor de base de datos.

    Returns:
        Optional[DatabaseManager]: Gestor de base de datos o None
        si no está inicializado.
    """
    return _database_manager


@asynccontextmanager
async def get_async_session():
    """
    Dependencia de FastAPI para obtener una sesión de base de datos

    Maneja el ciclo de vida de la sesión (abrir, commit, rollback, cerrar).
    """
    manager = get_database_manager()
    if not manager or not manager.session_factory:
        raise RuntimeError(
            "DatabaseManager no está inicializado. Llama a init_database() al inicio."
        )

    async with manager.session_factory() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error en la sesión de base de datos: {e}", exc_info=True)
            await session.rollback()
            raise
        finally:
            await session.close()


# Alias para compatibilidad y conveniencia
get_db = get_async_session


# Funciones de conveniencia para FastAPI
async def get_db_health() -> Dict[str, Any]:
    """Obtener el estado de salud de la base de datos"""
    manager = get_database_manager()
    if not manager:
        return {"status": "error", "details": "DatabaseManager no está inicializado"}

    checker = DatabaseHealthChecker(manager)
    return await checker.check_detailed_health()


def create_repository(
    model: Type[ModelType], session: AsyncSession
) -> BaseRepository[ModelType]:
    """
    Factory function para crear repositorios type-safe

    Args:
        model: Clase del modelo SQLAlchemy
        session: Sesión de base de datos

    Returns:
        BaseRepository configurado para el modelo
    """
    return BaseRepository(model, session)
