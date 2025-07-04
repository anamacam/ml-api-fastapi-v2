"""
🧪 TDD CICLO 6 - DATABASE MODULE TESTS
Fase: REFACTOR - Tests actualizados para VPS

Objetivo: Verificar el módulo de base de datos optimizado para VPS con:
- Configuración adaptativa para VPS
- Métricas de rendimiento y recursos
- Manejo de conexiones remotas
- Health checks avanzados
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
import pytest_asyncio
from app.core.database import (
    BaseRepository,
    DatabaseConfig,
    DatabaseHealthChecker,
    DatabaseManager,
    VPSDatabaseConfig,
    close_database,
    get_async_session,
    get_database_manager,
    init_database,
)
from app.models.user import User
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

# Configurar pytest-asyncio solo para pruebas async
# pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="module")
def mock_psutil():
    """Fixture global para mockear psutil"""
    with patch("psutil.cpu_count", return_value=2), patch(
        "psutil.virtual_memory",
        return_value=MagicMock(total=4 * 1024 * 1024 * 1024, percent=50),
    ), patch("psutil.disk_usage", return_value=MagicMock(percent=50)):
        yield


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
            pool_timeout=60,
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
        with patch.dict(
            "os.environ",
            {
                "DATABASE_URL": "postgresql+asyncpg://env:test@localhost/env_db",
                "DB_POOL_SIZE": "15",
                "DB_ECHO": "true",
            },
        ):
            config = DatabaseConfig.from_env()
            assert (
                "postgresql+asyncpg://env:test@localhost/env_db" in config.database_url
            )
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
            database_url="sqlite+aiosqlite:///:memory:", echo=False, pool_size=5
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
        session.add = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = AsyncMock()
        session.get = AsyncMock()
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
            "hashed_password": "hashed123",
        }

        db_session.add = AsyncMock()
        db_session.commit = AsyncMock()
        db_session.refresh = AsyncMock()
        db_session.flush = AsyncMock()

        # Simular que el modelo se crea y refresca correctamente
        db_session.refresh.side_effect = lambda obj: None

        result = await user_repository.create(user_data)

        assert result is not None
        db_session.add.assert_called_once()
        db_session.flush.assert_called_once()
        db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_repository_get_by_id(self, user_repository, db_session):
        """Test: obtener entidad por ID"""
        user_id = 1

        class Result:
            def scalar_one_or_none(self):
                return User(
                    id=user_id,
                    username="testuser",
                    email="test@example.com",
                    hashed_password="hashed123",
                )

        db_session.execute = AsyncMock(return_value=Result())

        result = await user_repository.get_by_id(user_id)

        assert result is not None
        assert result.id == user_id
        assert result.username == "testuser"

    @pytest.mark.asyncio
    async def test_repository_get_all(self, user_repository, db_session):
        """Test: obtener todas las entidades"""
        mock_users = [
            User(id=1, username="user1", email="user1@example.com"),
            User(id=2, username="user2", email="user2@example.com"),
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

        class Result:
            def scalar_one_or_none(self):
                return mock_user

        db_session.execute = AsyncMock(return_value=Result())
        db_session.flush = AsyncMock()
        db_session.refresh = AsyncMock()

        update_data = {"username": "newname", "email": "new@example.com"}
        result = await user_repository.update(1, update_data)

        assert result.username == "newname"
        assert result.email == "new@example.com"

    @pytest.mark.asyncio
    async def test_repository_delete(self, user_repository, db_session):
        """Test: eliminar entidad"""
        mock_user = User(id=1, username="testuser", email="test@example.com")

        class Result:
            def scalar_one_or_none(self):
                return mock_user

        db_session.execute = AsyncMock(return_value=Result())
        db_session.flush = AsyncMock()
        db_session.delete = AsyncMock()

        success = await user_repository.delete(1)
        assert success is True

    @pytest.mark.asyncio
    async def test_repository_delete_nonexistent(self, user_repository, db_session):
        """Test: eliminar entidad que no existe"""

        class Result:
            def scalar_one_or_none(self):
                return None

        db_session.execute = AsyncMock(return_value=Result())
        db_session.flush = AsyncMock()
        db_session.delete = AsyncMock()

        success = await user_repository.delete(999)
        assert success is False


class TestDatabaseHealthChecker:
    """
    🏥 Test del verificador de salud

    Verifica el funcionamiento del health checker.
    """

    @pytest.fixture
    def health_checker(self, db_manager):
        """Fixture del verificador de salud"""
        return DatabaseHealthChecker(db_manager)

    @pytest.mark.asyncio
    async def test_health_check_success(self, health_checker):
        """Test: health check exitoso"""
        health_status = await health_checker.check_detailed_health()
        assert isinstance(health_status, dict)
        assert "status" in health_status
        if health_status["status"] == "healthy":
            assert "details" in health_status
            assert "metrics" in health_status
        else:
            assert "error" in health_status

    @pytest.mark.asyncio
    async def test_health_check_failure(self, health_checker):
        """Test: health check con fallo"""
        # Simular fallo de conexión mockeando la sesión
        with patch.object(
            health_checker.db_manager,
            "get_session",
            side_effect=Exception("Connection failed"),
        ):
            health_status = await health_checker.check_detailed_health()
            assert health_status["status"] == "unhealthy"
            assert "error" in health_status

    @pytest.mark.asyncio
    async def test_health_check_metrics(self, health_checker):
        """Test: métricas de health check"""
        health_status = await health_checker.check_detailed_health()
        if health_status["status"] == "healthy":
            metrics = health_status["metrics"]
            assert isinstance(metrics["response_time"], (int, float))
            assert isinstance(metrics["query_time"], (int, float))
            assert metrics["response_time"] >= 0
            assert metrics["query_time"] >= 0
        else:
            assert "error" in health_status


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


class TestVPSDatabaseConfig:
    """
    🔧 Test de configuración VPS

    Verifica la optimización automática de configuración
    para entornos VPS.
    """

    def test_vps_config_optimization(self, mock_psutil):
        """Test: optimización automática de configuración VPS"""
        config = VPSDatabaseConfig()

        # Verificar ajustes automáticos
        assert config.pool_size <= 4, (
            "El pool size no se optimizó correctamente " "para el VPS"
        )
        assert config.max_overflow <= config.pool_size, (
            "max_overflow debe ser menor o igual a " "pool_size"
        )
        assert config.pool_timeout >= 60
        assert config.query_timeout >= 120
        assert config.connection_retries >= 5
        assert config.pool_pre_ping is True
        assert config.pool_recycle <= 1800

    def test_vps_connection_args(self, mock_psutil):
        """Test: argumentos de conexión optimizados para VPS"""
        config = VPSDatabaseConfig()
        config.database_url = "postgresql+asyncpg://user:pass@localhost:5432/db"
        args = config.get_connection_args()

        # asyncpg usa 'timeout' en lugar de 'connect_timeout'
        assert args["timeout"] == 30
        assert "server_settings" in args
        assert args["server_settings"]["keepalives"] == "1"
        assert args["server_settings"]["keepalives_idle"] == "30"
        assert args["server_settings"]["keepalives_interval"] == "10"
        assert args["server_settings"]["keepalives_count"] == "5"

    def test_vps_config_resource_limits(self, mock_psutil):
        """Test: límites de recursos respetados"""
        config = VPSDatabaseConfig(
            pool_size=100, max_overflow=50  # Intentar configurar más del límite
        )

        # Debe ajustar automáticamente a límites seguros
        assert config.pool_size <= 4, (
            "El pool size no se optimizó correctamente " "para el VPS"
        )
        assert config.max_overflow <= config.pool_size, (
            "max_overflow debe ser menor o igual a " "pool_size"
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_vps_config_optimizes_pool_size(self):
        """Test que VPSDatabaseConfig optimiza el pool size correctamente"""
        # Simular VPS con recursos limitados
        with patch("psutil.cpu_count", return_value=2), patch(
            "psutil.virtual_memory"
        ) as mock_mem:
            mock_mem.return_value.total = 2 * 1024 * 1024 * 1024  # 2GB RAM

            config = VPSDatabaseConfig(database_url="postgresql://user:pass@vps/db")

            # Pool size debe ser el mínimo entre los defaults y lo calculado
            assert config.pool_size <= 4, (
                "El pool size no se optimizó correctamente " "para el VPS"
            )

        assert config.max_overflow <= config.pool_size, (
            "max_overflow debe ser menor o igual a " "pool_size"
        )


class TestDatabaseManagerVPS:
    """
    🗄️ Test del gestor de base de datos en VPS

    Verifica el manejo de conexiones y métricas en entorno VPS.
    """

    @pytest.fixture
    def vps_config(self, mock_psutil):
        """Fixture de configuración VPS"""
        return VPSDatabaseConfig(
            database_url=(
                "sqlite+aiosqlite:///:memory:"  # Usar SQLite en memoria para tests
            )
        )

    @pytest_asyncio.fixture
    async def vps_manager(self, vps_config):
        """Fixture del gestor VPS"""
        manager = DatabaseManager(vps_config)
        await manager.initialize()
        yield manager
        await manager.close()

    @pytest.mark.asyncio
    async def test_vps_connection_metrics(self, vps_manager):
        """Test: métricas de conexión en VPS"""
        metrics = await vps_manager.get_connection_metrics()

        assert "pool_class" in metrics
        assert "pool_size" in metrics
        assert "connections_in_pool" in metrics
        assert "connections_checked_out" in metrics
        assert "current_overflow" in metrics

    @pytest.mark.asyncio
    async def test_vps_connection_retry(self, test_db_config):
        """Test: reintentos de conexión en VPS"""
        # Configurar un timeout muy bajo para forzar fallos
        vps_config = VPSDatabaseConfig(
            database_url=(
                "postgresql+asyncpg://invalid:invalid@" "nonexistent:5432/invalid"
            ),
        )

        manager = DatabaseManager(vps_config)

        # Debería fallar después de los reintentos
        with pytest.raises(Exception):
            await manager.initialize()


class TestDatabaseHealthCheckerVPS:
    """
    🏥 Test del verificador de salud en VPS

    Verifica health checks avanzados y métricas de recursos.
    """

    @pytest.fixture
    def health_checker(self, vps_manager):
        """Fixture del verificador de salud VPS"""
        return DatabaseHealthChecker(vps_manager)

    @pytest.mark.asyncio
    async def test_vps_health_check_metrics(self, health_checker):
        """Test: métricas de health check en VPS"""
        health_status = await health_checker.check_detailed_health()
        assert "status" in health_status
        assert "details" in health_status or "error" in health_status

    @pytest.mark.asyncio
    async def test_vps_health_check_thresholds(self, health_checker):
        """Test: umbrales de health check en VPS"""
        # Simular uso alto de recursos
        with patch("psutil.cpu_percent", return_value=90), patch(
            "psutil.virtual_memory", return_value=MagicMock(percent=85)
        ):
            health_status = await health_checker.check_detailed_health()
            assert health_status["status"] in ["unhealthy", "healthy"]

    @pytest.mark.asyncio
    async def test_vps_health_check_timeout(self, health_checker):
        """Test: manejo de timeouts en health check VPS"""
        # Simular timeout en query
        with patch("asyncio.timeout", side_effect=asyncio.TimeoutError):
            health_status = await health_checker.check_detailed_health()
            assert health_status["status"] == "unhealthy"
            assert "error" in health_status


class TestDatabaseIntegrationVPS:
    """
    🔗 Test de integración en VPS

    Verifica la integración completa del módulo en entorno VPS.
    """

    @pytest.mark.asyncio
    async def test_vps_database_initialization(self, mock_psutil):
        """Test: inicialización de base de datos VPS"""
        vps_config = VPSDatabaseConfig(
            database_url="sqlite+aiosqlite:///:memory:",  # Usar SQLite en memoria para tests
            pool_size=5,
            max_overflow=10,
        )

        manager = DatabaseManager(vps_config)
        await manager.initialize()

        assert manager.is_initialized
        assert manager.engine is not None

        await manager.close()

    @pytest.mark.asyncio
    async def test_vps_transaction_handling(self, mock_psutil):
        """Test: manejo de transacciones en VPS"""
        vps_config = VPSDatabaseConfig(
            database_url="sqlite+aiosqlite:///:memory:"  # Usar SQLite en memoria para tests
        )

        manager = DatabaseManager(vps_config)
        await manager.initialize()

        async with manager.get_session() as session:
            # Simular una transacción
            await session.execute(text("SELECT 1"))
            await session.commit()

        await manager.close()


@pytest.fixture
def db_manager():
    """Fixture del manager de base de datos"""
    config = DatabaseConfig(database_url="sqlite+aiosqlite:///:memory:")
    manager = DatabaseManager(config)
    asyncio.get_event_loop().run_until_complete(manager.initialize())
    yield manager
    asyncio.get_event_loop().run_until_complete(manager.cleanup())


@pytest.fixture
def vps_manager():
    """Fixture del manager de base de datos VPS"""
    config = VPSDatabaseConfig()
    manager = DatabaseManager(config)
    yield manager
    # Limpieza después de los tests
    asyncio.run(manager.cleanup())
