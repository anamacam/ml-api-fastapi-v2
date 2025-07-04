# -*- coding: utf-8 -*-
"""
⚡️ DATABASE MODULE - REFACTORED
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

from __future__ import annotations

import asyncio
import logging
import os
import time
import psutil
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
from sqlalchemy.pool import StaticPool, QueuePool

from .database_repository import Base

# Configurar logger específico para el módulo de base de datos
logger = logging.getLogger(__name__)

# Type hints para Generic Repository
ModelType = TypeVar("ModelType", bound=Base)

# Variable global para el gestor de base de datos
_database_manager: Optional[DatabaseManager] = None
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
        """Inicializa el engine y la sesión de la base de datos con reintentos"""
        if self.is_initialized:
            logger.warning("El gestor de base de datos ya está inicializado.")
            return

        last_exception = None
        for attempt in range(self.config.connection_retries + 1):
            try:
                await self._create_engine_and_session()
                self._is_initialized = True
                logger.info("El gestor de base de datos se ha inicializado correctamente.")
                return
            except Exception as e:
                last_exception = e
                if attempt < self.config.connection_retries:
                    await self._handle_connection_retry(attempt, e)
                else:
                    self._handle_connection_failure(last_exception)

    async def _create_engine_and_session(self) -> None:
        """Crear el engine y el sessionmaker con reintentos"""
        last_exception: Optional[Exception] = None
        
        for attempt in range(self.config.connection_retries + 1):
            try:
                engine_args = self._build_engine_args()
                self.engine = create_async_engine(
                    self.config.database_url, **engine_args
                )
                await self._test_connection()
                self._create_session_factory()
                logger.info(
                    "Motor de base de datos y fábrica de sesiones creados exitosamente."
                )
                return
            except (SQLAlchemyError, DisconnectionError) as e:
                logger.error(f"Error creando engine: {e}", exc_info=True)
                last_exception = e
                if attempt < self.config.connection_retries:
                    await self._handle_connection_retry(attempt, e)

        self._handle_connection_failure(last_exception)

    def _build_engine_args(self) -> Dict[str, Any]:
        """Construir argumentos del engine según el tipo de driver"""
        engine_args: Dict[str, Any] = {"echo": self.config.echo}

        if self.config.driver_type == DatabaseDriver.SQLITE:
            self._configure_sqlite_args(engine_args)
        else:
            self._configure_pool_args(engine_args)
            self._configure_connection_args(engine_args)

        return engine_args

    def _configure_sqlite_args(self, engine_args: Dict[str, Any]) -> None:
        """Configurar argumentos específicos para SQLite"""
        engine_args["poolclass"] = StaticPool
        engine_args["connect_args"] = {"check_same_thread": False}

    def _configure_pool_args(self, engine_args: Dict[str, Any]) -> None:
        """Configurar argumentos del pool de conexiones"""
        engine_args.update({
            "poolclass": QueuePool,
            "pool_size": self.config.pool_size,
            "max_overflow": self.config.max_overflow,
            "pool_timeout": self.config.pool_timeout,
            "pool_recycle": self.config.pool_recycle,
            "pool_pre_ping": self.config.pool_pre_ping,
        })

    def _configure_connection_args(self, engine_args: Dict[str, Any]) -> None:
        """Configurar argumentos de conexión específicos del driver"""
        if isinstance(self.config, VPSDatabaseConfig):
            engine_args["connect_args"] = self.config.get_connection_args()
        elif self.config.connect_args:
            engine_args["connect_args"] = self.config.connect_args

    def _create_session_factory(self) -> None:
        """Crear la fábrica de sesiones"""
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    async def _handle_connection_retry(self, attempt: int, error: Exception) -> None:
        """Manejar reintento de conexión con backoff exponencial"""
        wait_time = 2 ** (attempt + 1)
        logger.warning(
            "Intento %s fallido: %s. Reintentando en %ss...",
            attempt + 1,
            error,
            wait_time,
        )
        await asyncio.sleep(wait_time)

    def _handle_connection_failure(self, last_exception: Optional[Exception]) -> None:
        """Manejar fallo final de conexión"""
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
        if data is None:
            raise TypeError("Los datos para crear no pueden ser None")
        if not isinstance(data, dict) or not data:
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
            return self._create_unhealthy_response("DatabaseManager no está inicializado")

        try:
            start_time = time.time()
            query_time = await self._test_basic_connection()
            pool_metrics = self._get_pool_metrics()
            
            return self._create_healthy_response(start_time, query_time, pool_metrics)

        except Exception as e:
            return self._create_unhealthy_response(str(e))

    async def _test_basic_connection(self) -> float:
        """Probar conexión básica y retornar tiempo de respuesta"""
        async with self.db_manager.get_session() as session:
            start_time = time.time()
            await session.execute(text("SELECT 1"))
            return time.time() - start_time

    def _get_pool_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del pool de conexiones"""
        if not self._is_pool_available():
            return self._get_default_pool_metrics()
        
        return self._extract_pool_metrics()

    def _is_pool_available(self) -> bool:
        """Verificar si el pool de conexiones está disponible"""
        return (
            self.db_manager.engine is not None 
            and hasattr(self.db_manager.engine, "pool")
        )

    def _extract_pool_metrics(self) -> Dict[str, Any]:
        """Extraer métricas específicas del pool de conexiones"""
        if self.db_manager.engine is None:
            return self._get_default_pool_metrics()
            
        pool = self.db_manager.engine.pool
        return {
            "size": self._get_pool_attribute(pool, "size", 0),
            "checkedin": self._get_pool_attribute(pool, "checkedin", 0),
            "checkedout": self._get_pool_attribute(pool, "checkedout", 0),
            "overflow": self._get_pool_attribute(pool, "overflow", 0),
        }

    def _get_pool_attribute(self, pool, attribute: str, default: int) -> int:
        """Obtener atributo del pool de forma segura"""
        try:
            return getattr(pool, attribute, lambda: default)()
        except Exception:
            return default

    def _get_default_pool_metrics(self) -> Dict[str, Any]:
        """Obtener métricas por defecto cuando el pool no está disponible"""
        return {
            "size": 0,
            "checkedin": 0,
            "checkedout": 0,
            "overflow": 0,
        }

    def _create_healthy_response(self, start_time: float, query_time: float, pool_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Crear respuesta de salud exitosa"""
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

    def _create_unhealthy_response(self, error_message: str) -> Dict[str, Any]:
        """Crear respuesta de salud fallida"""
        return {
            "status": "unhealthy",
            "error": error_message,
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

        times, errors = await self._execute_performance_queries(num_queries)
        results = self._calculate_performance_metrics(times, errors, num_queries)

        self.logger.info(f"Test de rendimiento completado: {results}")
        return results

    async def _execute_performance_queries(self, num_queries: int) -> tuple[list[float], int]:
        """Ejecutar queries de rendimiento y retornar tiempos y errores"""
        times = []
        errors = 0

        for i in range(num_queries):
            query_time, success = await self._execute_single_query(i)
            if success:
                times.append(query_time)
            else:
                errors += 1

        return times, errors

    async def _execute_single_query(self, query_index: int) -> tuple[float, bool]:
        """Ejecutar una sola query de rendimiento"""
        start = time.time()
        try:
            async with self.db_manager.get_session() as session:
                await session.execute(text("SELECT 1"))
            return (time.time() - start) * 1000, True
        except Exception as e:
            self.logger.warning(f"Error en query {query_index}: {e}")
            return 0.0, False

    def _calculate_performance_metrics(self, times: list[float], errors: int, num_queries: int) -> Dict[str, Any]:
        """Calcular métricas de rendimiento basadas en los tiempos"""
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
        else:
            avg_time = min_time = max_time = 0

        return {
            "queries_executed": len(times),
            "queries_failed": errors,
            "avg_response_time_ms": round(avg_time, 2),
            "min_response_time_ms": round(min_time, 2),
            "max_response_time_ms": round(max_time, 2),
            "success_rate": (
                round((len(times) / num_queries) * 100, 2) if num_queries > 0 else 0
            ),
        }


# Funciones de utilidad global mejoradas
async def init_database(config: DatabaseConfig) -> None:
    """Inicializar base de datos globalmente"""
    global _database_manager
    _database_manager = DatabaseManager(config)
    if _database_manager:
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
