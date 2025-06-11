"""
🧪 TDD CICLO 6 - DATABASE MODULE TESTS
Fase: RED - Escribir pruebas que fallan primero

Objetivo: Crear un módulo de base de datos robusto con:
- Configuración de base de datos SQLAlchemy + asyncio
- Pool de conexiones
- Repository pattern base
- Health checks
- Migraciones
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.pool import QueuePool
from sqlalchemy import text

# Configurar pytest-asyncio solo para pruebas async
# pytestmark = pytest.mark.asyncio

from app.core.database import (
    DatabaseConfig,
    DatabaseManager,
    BaseRepository,
    DatabaseHealthChecker,
    get_async_session,
    get_database_manager,
    init_database,
    close_database
)
from app.models.user import User


class TestDatabaseConfig:
    """
    🔧 Test de configuración de base de datos

    Verifica que la configuración de la base de datos
    sea flexible y segura para diferentes entornos.
    """

    def test_database_config_creation_with_defaults(self):
        """Test: crear configuración con valores por defecto"""
        config = DatabaseConfig()

        assert config.database_url is not None
        assert config.echo is False
        assert config.pool_size == 10
        assert config.max_overflow == 20
        assert config.pool_timeout == 30
        assert config.pool_recycle == 3600

    def test_database_config_creation_with_custom_values(self):
        """Test: crear configuración con valores personalizados"""
        config = DatabaseConfig(
            database_url="postgresql+asyncpg://test:test@localhost/test_db",
            echo=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=60
        )

        assert config.database_url == "postgresql+asyncpg://test:test@localhost/test_db"
        assert config.echo is True
        assert config.pool_size == 5
        assert config.max_overflow == 10
        assert config.pool_timeout == 60

    def test_database_config_validation(self):
        """Test: validación de configuración inválida"""
        with pytest.raises(ValueError):
            DatabaseConfig(pool_size=-1)

        with pytest.raises(ValueError):
            DatabaseConfig(max_overflow=-5)

    def test_database_config_from_env(self):
        """Test: configuración desde variables de entorno"""
        with patch.dict("os.environ", {
            "DATABASE_URL": "postgresql+asyncpg://env:test@localhost/env_db",
            "DB_POOL_SIZE": "15",
            "DB_ECHO": "true"
        }):
            config = DatabaseConfig.from_env()
            assert "postgresql+asyncpg://env:test@localhost/env_db" in config.database_url
            assert config.pool_size == 15
            assert config.echo is True


class TestDatabaseManager:
    """
    🗄️ Test del gestor de base de datos

    Verifica la gestión de conexiones, engine y sesiones.
    """

    @pytest.fixture
    def db_config(self):
        """Fixture de configuración de prueba"""
        return DatabaseConfig(
            database_url="sqlite+aiosqlite:///:memory:",
            echo=False,
            pool_size=5
        )

    @pytest_asyncio.fixture
    async def db_manager(self, db_config):
        """Fixture del gestor de base de datos"""
        manager = DatabaseManager(db_config)
        await manager.initialize()
        yield manager
        await manager.close()

    @pytest.mark.asyncio
    async def test_database_manager_initialization(self, db_config):
        """Test: inicialización del gestor de base de datos"""
        manager = DatabaseManager(db_config)

        assert manager.engine is None
        assert manager.session_factory is None
        assert not manager.is_initialized

        await manager.initialize()

        assert manager.engine is not None
        assert manager.session_factory is not None
        assert manager.is_initialized

        await manager.close()

    @pytest.mark.asyncio
    async def test_database_manager_engine_creation(self, db_manager):
        """Test: creación correcta del engine"""
        engine = db_manager.engine

        assert isinstance(engine, AsyncEngine)
        assert engine.pool.__class__.__name__ in ["QueuePool", "StaticPool"]

    @pytest.mark.asyncio
    async def test_database_manager_session_creation(self, db_manager):
        """Test: creación de sesiones"""
        async with db_manager.get_session() as session:
            assert isinstance(session, AsyncSession)
            assert session.bind == db_manager.engine

    @pytest.mark.asyncio
    async def test_database_manager_connection_health(self, db_manager):
        """Test: verificación de salud de conexión"""
        is_healthy = await db_manager.check_health()
        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_database_manager_connection_error_handling(self):
        """Test: manejo de errores de conexión"""
        bad_config = DatabaseConfig(
            database_url="postgresql+asyncpg://invalid:invalid@nonexistent:5432/invalid"
        )
        manager = DatabaseManager(bad_config)

        with pytest.raises(Exception):  # Should raise connection error
            await manager.initialize()

    @pytest.mark.asyncio
    async def test_database_manager_cleanup(self, db_config):
        """Test: limpieza correcta de recursos"""
        manager = DatabaseManager(db_config)
        await manager.initialize()

        assert manager.is_initialized

        await manager.close()

        assert not manager.is_initialized
        # Engine should be properly disposed


class TestBaseRepository:
    """
    📦 Test del patrón Repository base

    Verifica las operaciones CRUD básicas del repository.
    """

    @pytest.fixture
    def db_session(self):
        """Fixture de sesión de base de datos mock"""
        session = AsyncMock(spec=AsyncSession)
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=None)
        return session

    @pytest.fixture
    def user_repository(self, db_session):
        """Fixture de repository de usuario"""
        return BaseRepository(User, db_session)

    @pytest.mark.asyncio
    async def test_repository_create(self, user_repository, db_session):
        """Test: crear entidad en repository"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": "hashed123"
        }

        mock_user = User(**user_data)
        db_session.add = Mock()
        db_session.commit = AsyncMock()
        db_session.refresh = AsyncMock()

        result = await user_repository.create(user_data)

        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_repository_get_by_id(self, user_repository, db_session):
        """Test: obtener entidad por ID"""
        mock_user = User(id=1, username="testuser", email="test@example.com")
        db_session.get = AsyncMock(return_value=mock_user)

        result = await user_repository.get_by_id(1)

        assert result == mock_user
        db_session.get.assert_called_once_with(User, 1)

    @pytest.mark.asyncio
    async def test_repository_get_all(self, user_repository, db_session):
        """Test: obtener todas las entidades"""
        mock_users = [
            User(id=1, username="user1", email="user1@example.com"),
            User(id=2, username="user2", email="user2@example.com")
        ]

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_users
        db_session.execute = AsyncMock(return_value=mock_result)

        result = await user_repository.get_all()

        assert len(result) == 2
        assert result == mock_users

    @pytest.mark.asyncio
    async def test_repository_update(self, user_repository, db_session):
        """Test: actualizar entidad"""
        mock_user = User(id=1, username="oldname", email="old@example.com")
        db_session.get = AsyncMock(return_value=mock_user)
        db_session.commit = AsyncMock()
        db_session.refresh = AsyncMock()

        update_data = {"username": "newname", "email": "new@example.com"}
        result = await user_repository.update(1, update_data)

        assert mock_user.username == "newname"
        assert mock_user.email == "new@example.com"
        db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_repository_delete(self, user_repository, db_session):
        """Test: eliminar entidad"""
        mock_user = User(id=1, username="testuser", email="test@example.com")
        db_session.get = AsyncMock(return_value=mock_user)
        db_session.delete = Mock()
        db_session.commit = AsyncMock()

        success = await user_repository.delete(1)

        assert success is True
        db_session.delete.assert_called_once_with(mock_user)
        db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_repository_delete_nonexistent(self, user_repository, db_session):
        """Test: eliminar entidad que no existe"""
        db_session.get = AsyncMock(return_value=None)

        success = await user_repository.delete(999)

        assert success is False


class TestDatabaseHealthChecker:
    """
    🏥 Test del verificador de salud de base de datos

    Verifica el monitoreo de salud de la base de datos.
    """

    @pytest.fixture
    def health_checker(self):
        """Fixture del verificador de salud"""
        mock_manager = AsyncMock()
        return DatabaseHealthChecker(mock_manager)

    @pytest.mark.asyncio
    async def test_health_check_success(self, health_checker):
        """Test: verificación de salud exitosa"""
        # Configurar mock para check_health exitoso
        health_checker.db_manager.check_health = AsyncMock(return_value=True)

        # Configurar mock session con context manager async adecuado
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def mock_get_session():
            mock_session = AsyncMock()
            mock_result = Mock()
            mock_result.scalar.return_value = 1
            mock_session.execute = AsyncMock(return_value=mock_result)
            yield mock_session

        health_checker.db_manager.get_session = mock_get_session

        health_status = await health_checker.check_detailed_health()

        assert health_status["status"] == "healthy"
        assert health_status["database_responsive"] is True
        assert health_status["query_test"] is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, health_checker):
        """Test: verificación de salud con falla"""
        health_checker.db_manager.check_health = AsyncMock(side_effect=Exception("Connection failed"))

        health_status = await health_checker.check_detailed_health()

        assert health_status["status"] == "unhealthy"
        assert health_status["database_responsive"] is False
        assert "error" in health_status

    @pytest.mark.asyncio
    async def test_health_check_metrics(self, health_checker):
        """Test: métricas de rendimiento en health check"""
        health_checker.db_manager.check_health = AsyncMock(return_value=True)

        # Configurar mock session con context manager async adecuado
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def mock_get_session():
            mock_session = AsyncMock()
            mock_result = Mock()
            mock_result.scalar.return_value = 1
            mock_session.execute = AsyncMock(return_value=mock_result)
            yield mock_session

        health_checker.db_manager.get_session = mock_get_session

        health_status = await health_checker.check_detailed_health()

        assert "response_time_ms" in health_status
        assert isinstance(health_status["response_time_ms"], (int, float))
        assert health_status["response_time_ms"] >= 0


class TestDatabaseIntegration:
    """
    🔗 Test de integración de base de datos

    Verifica la integración completa del módulo de base de datos.
    """

    @pytest.mark.asyncio
    async def test_database_initialization_integration(self):
        """Test: inicialización completa del sistema de base de datos"""
        config = DatabaseConfig(database_url="sqlite+aiosqlite:///:memory:")

        # Test initialization
        await init_database(config)

        # Test getting manager
        manager = get_database_manager()
        assert manager is not None
        assert manager.is_initialized

        # Test getting session
        async with get_async_session() as session:
            assert isinstance(session, AsyncSession)

        # Test cleanup
        await close_database()

    @pytest.mark.asyncio
    async def test_database_session_dependency_integration(self):
        """Test: integración con sistema de dependencias de FastAPI"""
        config = DatabaseConfig(database_url="sqlite+aiosqlite:///:memory:")
        await init_database(config)

        # Test that we can get session multiple times
        session_gen1 = get_async_session()
        session_gen2 = get_async_session()

        async with session_gen1 as session1:
            async with session_gen2 as session2:
                assert isinstance(session1, AsyncSession)
                assert isinstance(session2, AsyncSession)
                # Should be different session instances
                assert session1 is not session2

        await close_database()

    @pytest.mark.asyncio
    async def test_database_transaction_handling(self):
        """Test: manejo correcto de transacciones"""
        config = DatabaseConfig(database_url="sqlite+aiosqlite:///:memory:")
        await init_database(config)

        async with get_async_session() as session:
            # Test simple query
            result = await session.execute(text("SELECT 1 as test"))
            value = result.scalar()
            assert value == 1

            # Test transaction rollback behavior
            try:
                await session.execute(text("SELECT invalid_column FROM invalid_table"))
                await session.commit()
            except Exception:
                await session.rollback()
                # Session should still be usable after rollback
                result = await session.execute(text("SELECT 2 as test"))
                value = result.scalar()
                assert value == 2

        await close_database()
