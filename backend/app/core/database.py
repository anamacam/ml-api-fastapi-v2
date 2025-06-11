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
"""

import os
import asyncio
import time
import logging
from typing import Optional, Dict, Any, List, TypeVar, Generic, Type, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError, TimeoutError

# Configurar logger específico para el módulo de base de datos
logger = logging.getLogger(__name__)

# Base para modelos SQLAlchemy
Base = declarative_base()

# Type hints para Generic Repository
ModelType = TypeVar("ModelType", bound=Base)

# Variable global para el gestor de base de datos
_database_manager: Optional['DatabaseManager'] = None


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
            logger.warning(f"pool_recycle muy bajo ({self.pool_recycle}s), recomendado >= 300s")
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
    def from_env(cls) -> 'DatabaseConfig':
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
                connection_retries=int(os.getenv("DB_CONNECTION_RETRIES", "3"))
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
            "connection_retries": self.connection_retries
        }


class DatabaseManager:
    """
    🗄️ Gestor enterprise de base de datos
    
    Maneja el engine, pool de conexiones, sessions y health checks.
    Implementa async/await, retry logic y monitoreo avanzado.
    
    Attributes:
        config: Configuración de base de datos
        engine: Engine asíncrono de SQLAlchemy
        session_factory: Factory para crear sesiones
        _is_initialized: Estado de inicialización
        _connection_retries: Contador de reintentos
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker] = None
        self._is_initialized = False
        self._connection_retries = 0
        
        logger.info(f"DatabaseManager inicializado con configuración: {config.to_dict()}")
    
    @property
    def is_initialized(self) -> bool:
        """Verificar si el manager está inicializado"""
        return self._is_initialized and self.engine is not None
    
    async def initialize(self) -> None:
        """
        Inicializar el engine y session factory con retry logic
        
        Raises:
            Exception: Si hay problemas de conexión después de todos los reintentos
        """
        last_exception = None
        
        for attempt in range(self.config.connection_retries + 1):
            try:
                await self._create_engine_and_session()
                await self._test_connection()
                self._is_initialized = True
                self._connection_retries = 0
                
                logger.info(f"DatabaseManager inicializado exitosamente (intento {attempt + 1})")
                return
                
            except Exception as e:
                last_exception = e
                self._connection_retries = attempt + 1
                
                if attempt < self.config.connection_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"Fallo en inicialización (intento {attempt + 1}): {e}. "
                        f"Reintentando en {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Fallo definitivo en inicialización después de {attempt + 1} intentos")
        
        await self.close()
        raise last_exception
    
    async def _create_engine_and_session(self) -> None:
        """Crear engine y session factory según el tipo de driver"""
        connect_args = self.config.connect_args.copy()
        
        if self.config.driver_type == DatabaseDriver.SQLITE:
            connect_args.setdefault("check_same_thread", False)
            # Para SQLite, usar StaticPool sin parámetros de pool
            self.engine = create_async_engine(
                self.config.database_url,
                echo=self.config.echo,
                connect_args=connect_args,
                poolclass=StaticPool
            )
        else:
            # Para PostgreSQL/MySQL, usar QueuePool con configuración completa
            self.engine = create_async_engine(
                self.config.database_url,
                echo=self.config.echo,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                pool_pre_ping=self.config.pool_pre_ping,
                connect_args=connect_args,
                poolclass=QueuePool
            )
        
        # Crear factory de sesiones con configuración optimizada
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False
        )
    
    async def _test_connection(self) -> None:
        """Probar la conexión inicial"""
        # Usar session_factory directamente para evitar check de is_initialized
        async with self.session_factory() as session:
            await session.execute(text("SELECT 1"))
    
    @asynccontextmanager
    async def get_session(self):
        """
        Context manager para obtener sesión de base de datos con manejo de errores
        
        Yields:
            AsyncSession: Sesión de base de datos
            
        Raises:
            RuntimeError: Si el manager no está inicializado
            SQLAlchemyError: Si hay errores de base de datos
        """
        if not self.is_initialized:
            raise RuntimeError("DatabaseManager no está inicializado")
        
        async with self.session_factory() as session:
            try:
                yield session
            except DisconnectionError as e:
                logger.error(f"Error de desconexión: {e}")
                await session.rollback()
                raise
            except TimeoutError as e:
                logger.error(f"Timeout en base de datos: {e}")
                await session.rollback()
                raise
            except SQLAlchemyError as e:
                logger.error(f"Error de SQLAlchemy: {e}")
                await session.rollback()
                raise
            except Exception as e:
                logger.error(f"Error inesperado en sesión: {e}")
                await session.rollback()
                raise
    
    async def check_health(self) -> bool:
        """
        Verificar salud básica de la conexión con timeout
        
        Returns:
            bool: True si la conexión está saludable
        """
        try:
            # Usar timeout para evitar bloqueos
            async with self.get_session() as session:
                await asyncio.wait_for(
                    session.execute(text("SELECT 1")),
                    timeout=self.config.query_timeout
                )
                return True
        except Exception as e:
            logger.warning(f"Health check falló: {e}")
            return False
    
    async def get_engine_info(self) -> Dict[str, Any]:
        """
        Obtener información detallada del engine
        
        Returns:
            Dict con información del engine y pool
        """
        if not self.is_initialized:
            return {"status": "not_initialized"}
        
        pool = self.engine.pool
        return {
            "driver": str(self.engine.dialect.name),
            "pool_class": pool.__class__.__name__,
            "pool_size": getattr(pool, 'size', lambda: 'N/A')(),
            "checked_in": getattr(pool, 'checkedin', lambda: 'N/A')(),
            "checked_out": getattr(pool, 'checkedout', lambda: 'N/A')(),
            "overflow": getattr(pool, 'overflow', lambda: 'N/A')(),
            "connection_retries": self._connection_retries
        }
    
    async def close(self) -> None:
        """Cerrar engine y limpiar recursos de forma segura"""
        if self.engine:
            try:
                await self.engine.dispose()
                logger.info("Engine de base de datos cerrado correctamente")
            except Exception as e:
                logger.error(f"Error al cerrar engine: {e}")
        
        self.engine = None
        self.session_factory = None
        self._is_initialized = False


class BaseRepository(Generic[ModelType]):
    """
    📦 Repository pattern enterprise genérico
    
    Proporciona operaciones CRUD robustas para cualquier modelo.
    Implementa async/await, logging, validaciones y manejo de errores.
    
    Type Parameters:
        ModelType: Tipo del modelo SQLAlchemy
        
    Attributes:
        model: Clase del modelo SQLAlchemy
        session: Sesión de base de datos
    """
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
        self.logger = logging.getLogger(f"{__name__}.{model.__name__}Repository")
    
    async def create(self, data: Dict[str, Any]) -> ModelType:
        """
        Crear nueva entidad con validación y logging
        
        Args:
            data: Datos para crear la entidad
            
        Returns:
            ModelType: Entidad creada
            
        Raises:
            ValueError: Si los datos son inválidos
            SQLAlchemyError: Si hay errores de base de datos
        """
        try:
            self._validate_create_data(data)
            
            entity = self.model(**data)
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            
            self.logger.info(f"Entidad {self.model.__name__} creada con ID: {getattr(entity, 'id', 'N/A')}")
            return entity
            
        except Exception as e:
            self.logger.error(f"Error creando {self.model.__name__}: {e}")
            raise
    
    async def get_by_id(self, entity_id: Union[int, str]) -> Optional[ModelType]:
        """
        Obtener entidad por ID con logging
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            Optional[ModelType]: Entidad encontrada o None
        """
        try:
            entity = await self.session.get(self.model, entity_id)
            if entity:
                self.logger.debug(f"{self.model.__name__} encontrado con ID: {entity_id}")
            else:
                self.logger.debug(f"{self.model.__name__} no encontrado con ID: {entity_id}")
            return entity
        except Exception as e:
            self.logger.error(f"Error obteniendo {self.model.__name__} por ID {entity_id}: {e}")
            raise
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Obtener todas las entidades con paginación optimizada
        
        Args:
            skip: Número de registros a saltar
            limit: Límite de registros a obtener (máximo 1000)
            
        Returns:
            List[ModelType]: Lista de entidades
            
        Raises:
            ValueError: Si los parámetros de paginación son inválidos
        """
        # Validar parámetros de paginación
        if skip < 0:
            raise ValueError("skip debe ser mayor o igual a 0")
        if limit <= 0 or limit > 1000:
            raise ValueError("limit debe estar entre 1 y 1000")
        
        try:
            from sqlalchemy import select
            
            stmt = select(self.model).offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            entities = result.scalars().all()
            
            self.logger.debug(f"Obtenidos {len(entities)} {self.model.__name__} (skip={skip}, limit={limit})")
            return entities
            
        except Exception as e:
            self.logger.error(f"Error obteniendo lista de {self.model.__name__}: {e}")
            raise
    
    async def update(self, entity_id: Union[int, str], data: Dict[str, Any]) -> Optional[ModelType]:
        """
        Actualizar entidad existente con validación
        
        Args:
            entity_id: ID de la entidad
            data: Datos para actualizar
            
        Returns:
            Optional[ModelType]: Entidad actualizada o None si no existe
        """
        try:
            entity = await self.get_by_id(entity_id)
            if not entity:
                self.logger.warning(f"Intento de actualizar {self.model.__name__} inexistente: {entity_id}")
                return None
            
            self._validate_update_data(data)
            
            # Actualizar solo atributos válidos
            updated_fields = []
            for key, value in data.items():
                if hasattr(entity, key):
                    old_value = getattr(entity, key)
                    setattr(entity, key, value)
                    updated_fields.append(f"{key}: {old_value} -> {value}")
            
            await self.session.commit()
            await self.session.refresh(entity)
            
            self.logger.info(f"{self.model.__name__} ID {entity_id} actualizado: {', '.join(updated_fields)}")
            return entity
            
        except Exception as e:
            self.logger.error(f"Error actualizando {self.model.__name__} ID {entity_id}: {e}")
            raise
    
    async def delete(self, entity_id: Union[int, str]) -> bool:
        """
        Eliminar entidad por ID de forma segura
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        try:
            entity = await self.get_by_id(entity_id)
            if not entity:
                self.logger.warning(f"Intento de eliminar {self.model.__name__} inexistente: {entity_id}")
                return False
            
            self.session.delete(entity)
            await self.session.commit()
            
            self.logger.info(f"{self.model.__name__} ID {entity_id} eliminado exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error eliminando {self.model.__name__} ID {entity_id}: {e}")
            raise
    
    async def count(self) -> int:
        """
        Contar total de entidades
        
        Returns:
            int: Número total de entidades
        """
        try:
            from sqlalchemy import select, func
            
            stmt = select(func.count()).select_from(self.model)
            result = await self.session.execute(stmt)
            count = result.scalar()
            
            self.logger.debug(f"Total de {self.model.__name__}: {count}")
            return count
            
        except Exception as e:
            self.logger.error(f"Error contando {self.model.__name__}: {e}")
            raise
    
    def _validate_create_data(self, data: Dict[str, Any]) -> None:
        """Validar datos para creación (override en repositorios específicos)"""
        if not data:
            raise ValueError("Los datos para crear no pueden estar vacíos")
    
    def _validate_update_data(self, data: Dict[str, Any]) -> None:
        """Validar datos para actualización (override en repositorios específicos)"""
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
    
    async def check_detailed_health(self) -> Dict[str, Any]:
        """
        Verificación detallada de salud con métricas y alertas
        
        Returns:
            Dict[str, Any]: Estado detallado de salud con métricas
        """
        start_time = time.time()
        
        health_status = {
            "status": HealthStatus.HEALTHY.value,
            "database_responsive": True,
            "query_test": True,
            "response_time_ms": 0,
            "timestamp": time.time(),
            "checks_performed": [],
            "engine_info": {}
        }
        
        try:
            # 1. Test básico de conexión
            self.logger.debug("Iniciando health check básico")
            basic_health = await self.db_manager.check_health()
            health_status["database_responsive"] = basic_health
            health_status["checks_performed"].append("basic_connection")
            
            if not basic_health:
                health_status["status"] = HealthStatus.UNHEALTHY.value
                health_status["error"] = "Fallo en conexión básica"
                return health_status
            
            # 2. Test de query simple
            self.logger.debug("Ejecutando test de query")
            async with self.db_manager.get_session() as session:
                result = await session.execute(text("SELECT 1 as test"))
                test_value = result.scalar()
                health_status["query_test"] = (test_value == 1)
                health_status["checks_performed"].append("simple_query")
            
            # 3. Información del engine
            health_status["engine_info"] = await self.db_manager.get_engine_info()
            health_status["checks_performed"].append("engine_info")
            
            # 4. Calcular tiempo de respuesta
            response_time = (time.time() - start_time) * 1000
            health_status["response_time_ms"] = round(response_time, 2)
            
            # 5. Evaluar estado basado en métricas
            if response_time > 1000:  # > 1 segundo
                health_status["status"] = HealthStatus.DEGRADED.value
                health_status["warning"] = f"Tiempo de respuesta alto: {response_time:.2f}ms"
            
            self.logger.info(f"Health check completado: {health_status['status']} en {response_time:.2f}ms")
            
        except Exception as e:
            error_msg = f"Health check falló: {str(e)}"
            self.logger.error(error_msg)
            
            health_status.update({
                "status": HealthStatus.UNHEALTHY.value,
                "database_responsive": False,
                "query_test": False,
                "error": error_msg,
                "response_time_ms": round((time.time() - start_time) * 1000, 2)
            })
        
        return health_status
    
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
            "success_rate": round((len(times) / num_queries) * 100, 2) if num_queries > 0 else 0
        }
        
        self.logger.info(f"Test de rendimiento completado: {results}")
        return results


# Funciones de utilidad global mejoradas
async def init_database(config: DatabaseConfig) -> None:
    """
    Inicializar sistema de base de datos global con validación
    
    Args:
        config: Configuración validada de base de datos
        
    Raises:
        RuntimeError: Si ya existe un manager inicializado
        Exception: Si falla la inicialización
    """
    global _database_manager
    
    if _database_manager and _database_manager.is_initialized:
        logger.warning("Database manager ya está inicializado")
        return
    
    logger.info("Inicializando sistema de base de datos global")
    _database_manager = DatabaseManager(config)
    await _database_manager.initialize()
    
    logger.info("Sistema de base de datos global inicializado exitosamente")


async def close_database() -> None:
    """Cerrar sistema de base de datos global de forma segura"""
    global _database_manager
    
    if _database_manager:
        logger.info("Cerrando sistema de base de datos global")
        await _database_manager.close()
        _database_manager = None
        logger.info("Sistema de base de datos global cerrado")


def get_database_manager() -> Optional[DatabaseManager]:
    """
    Obtener instancia global del gestor de base de datos
    
    Returns:
        Optional[DatabaseManager]: Gestor de base de datos o None si no está inicializado
    """
    return _database_manager


@asynccontextmanager
async def get_async_session():
    """
    Context manager enterprise para obtener sesión de base de datos
    
    Para uso con FastAPI dependency injection y patrones async/await.
    Incluye manejo robusto de errores y logging.
    
    Yields:
        AsyncSession: Sesión de base de datos configurada
        
    Raises:
        RuntimeError: Si el sistema no está inicializado
        SQLAlchemyError: Si hay errores de base de datos
    """
    if not _database_manager:
        raise RuntimeError("Sistema de base de datos no inicializado. Llama a init_database() primero.")
    
    if not _database_manager.is_initialized:
        raise RuntimeError("Database manager no está inicializado")
    
    async with _database_manager.get_session() as session:
        yield session


# Alias para compatibilidad y conveniencia
get_db = get_async_session


# Funciones de conveniencia para FastAPI
async def get_db_health() -> Dict[str, Any]:
    """
    Función de conveniencia para health checks en FastAPI
    
    Returns:
        Dict con estado de salud de la base de datos
    """
    if not _database_manager:
        return {"status": "not_initialized", "error": "Database manager not initialized"}
    
    health_checker = DatabaseHealthChecker(_database_manager)
    return await health_checker.check_detailed_health()


def create_repository(model: Type[ModelType], session: AsyncSession) -> BaseRepository[ModelType]:
    """
    Factory function para crear repositorios type-safe
    
    Args:
        model: Clase del modelo SQLAlchemy
        session: Sesión de base de datos
        
    Returns:
        BaseRepository configurado para el modelo
    """
    return BaseRepository(model, session) 