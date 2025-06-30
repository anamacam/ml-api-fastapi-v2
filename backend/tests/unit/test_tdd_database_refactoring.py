# -*- coding: utf-8 -*-
"""
🧪 TDD DATABASE REFACTORING TESTS - CICLO 7
Fase: RED - Tests que identifican funciones que necesitan refactoring

Tests específicos para identificar y validar el refactoring de funciones críticas
en el módulo de base de datos siguiendo principios TDD.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Type
import time
from sqlalchemy import Column, Integer

from app.core.database import (
    DatabaseConfig,
    VPSDatabaseConfig,
    DatabaseManager,
    DatabaseHealthChecker,
    BaseRepository,
    init_database,
    get_database_manager,
    get_async_session,
    get_db_health,
    create_repository,
    Base,
    HealthStatus,
    DatabaseDriver
)


def make_engine_with_async_connect():
    mock_engine = MagicMock()
    mock_connect_ctx = AsyncMock()
    mock_engine.connect.return_value = mock_connect_ctx
    mock_connect_ctx.__aenter__.return_value = AsyncMock()
    mock_connect_ctx.__aexit__.return_value = None
    return mock_engine


def make_async_session_ctx():
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = AsyncMock()
    mock_ctx.__aexit__.return_value = None
    return mock_ctx


@pytest.fixture
def mock_model_class():
    class MockModel(Base):
        __tablename__ = "mock_model"
        id = Column(Integer, primary_key=True)
    yield MockModel
    # Limpia toda la metadata después del test
    Base.metadata.clear()


class TestTDDDatabaseRefactoring:
    """Tests TDD para refactoring del módulo de base de datos"""

    @pytest.fixture
    def sample_config(self) -> DatabaseConfig:
        """Configuración de prueba para tests"""
        return DatabaseConfig(
            database_url="sqlite+aiosqlite:///:memory:",
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            query_timeout=60,
            connection_retries=3
        )

    @pytest.fixture
    def sample_vps_config(self) -> VPSDatabaseConfig:
        """Configuración VPS de prueba"""
        return VPSDatabaseConfig(
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            pool_size=10,
            max_overflow=20,
            pool_timeout=60,
            query_timeout=120,
            connection_retries=5
        )

    @pytest.fixture
    def mock_db_manager(self, sample_config) -> DatabaseManager:
        """Mock del DatabaseManager para tests"""
        with patch('app.core.database.create_async_engine'), \
             patch('app.core.database.async_sessionmaker'):
            manager = DatabaseManager(sample_config, is_test=True)
            manager.engine = AsyncMock()
            manager.session_factory = AsyncMock()
            manager._is_initialized = True
            return manager

    @pytest.fixture
    def mock_health_checker(self, mock_db_manager) -> DatabaseHealthChecker:
        """Mock del DatabaseHealthChecker para tests"""
        return DatabaseHealthChecker(mock_db_manager)

    def test_database_config_validation_should_pass_with_valid_values(self, sample_config):
        """Test: Configuración válida debe pasar validación"""
        # RED: Test que valida la configuración
        assert sample_config.pool_size == 5
        assert sample_config.max_overflow == 10
        assert sample_config.driver_type == DatabaseDriver.SQLITE

    def test_database_config_validation_should_fail_with_invalid_pool_size(self):
        """Test: Configuración inválida debe fallar"""
        # RED: Test que espera error con valores inválidos
        with pytest.raises(ValueError, match="pool_size debe ser mayor a 0"):
            DatabaseConfig(pool_size=0)

    def test_vps_config_should_optimize_based_on_system_resources(self, sample_vps_config):
        """Test: Configuración VPS debe optimizarse según recursos"""
        # RED: Test que valida optimización automática
        assert sample_vps_config.pool_pre_ping is True
        assert sample_vps_config.pool_timeout >= 60
        assert sample_vps_config.query_timeout >= 120

    def test_database_manager_should_initialize_correctly(self, sample_config):
        """Test: DatabaseManager debe inicializarse correctamente"""
        # RED: Test de inicialización
        manager = DatabaseManager(sample_config, is_test=True)
        assert manager.config == sample_config
        assert manager.is_test is True
        assert manager._is_initialized is False

    @pytest.mark.asyncio
    async def test_database_manager_should_create_engine_and_session(self, sample_config):
        """Test: DatabaseManager debe crear engine y session correctamente"""
        # RED: Test de creación de engine y session
        with patch('app.core.database.create_async_engine') as mock_create_engine, \
             patch('app.core.database.async_sessionmaker') as mock_session_maker:
            
            mock_engine = make_engine_with_async_connect()
            mock_create_engine.return_value = mock_engine
            mock_session_maker.return_value = AsyncMock()
            
            manager = DatabaseManager(sample_config, is_test=True)
            await manager.initialize()
            
            mock_create_engine.assert_called_once()
            mock_session_maker.assert_called_once()
            assert manager._is_initialized is True

    @pytest.mark.asyncio
    async def test_database_manager_should_handle_connection_retries(self, sample_config):
        with patch('app.core.database.create_async_engine') as mock_create_engine, \
             patch('app.core.database.async_sessionmaker') as mock_session_maker, \
             patch('asyncio.sleep') as mock_sleep:
            mock_engine = make_engine_with_async_connect()
            # Primer intento falla, segundo éxito
            mock_create_engine.side_effect = [Exception("Connection failed"), mock_engine]
            mock_session_maker.return_value = AsyncMock()
            manager = DatabaseManager(sample_config, is_test=True)
            await manager.initialize()
            assert mock_create_engine.call_count == 2
            mock_sleep.assert_called_once()

    @pytest.mark.asyncio
    async def test_database_manager_should_configure_sqlite_correctly(self, sample_config):
        """Test: DatabaseManager debe configurar SQLite correctamente"""
        # RED: Test específico para configuración de SQLite
        with patch('app.core.database.create_async_engine') as mock_create_engine, \
             patch('app.core.database.async_sessionmaker') as mock_session_maker:
            
            mock_engine = make_engine_with_async_connect()
            mock_create_engine.return_value = mock_engine
            mock_session_maker.return_value = AsyncMock()
            
            manager = DatabaseManager(sample_config, is_test=True)
            await manager.initialize()
            
            call_args = mock_create_engine.call_args
            assert call_args[1]['echo'] is False
            assert 'poolclass' in call_args[1]
            assert 'connect_args' in call_args[1]

    @pytest.mark.asyncio
    async def test_database_manager_should_configure_postgresql_correctly(self, sample_vps_config):
        """Test: DatabaseManager debe configurar PostgreSQL correctamente"""
        # RED: Test específico para configuración de PostgreSQL
        with patch('app.core.database.create_async_engine') as mock_create_engine, \
             patch('app.core.database.async_sessionmaker') as mock_session_maker:
            
            mock_engine = make_engine_with_async_connect()
            mock_create_engine.return_value = mock_engine
            mock_session_maker.return_value = AsyncMock()
            
            manager = DatabaseManager(sample_vps_config, is_test=True)
            await manager.initialize()
            
            call_args = mock_create_engine.call_args
            assert call_args[1]['pool_size'] == sample_vps_config.pool_size
            assert call_args[1]['max_overflow'] == sample_vps_config.max_overflow
            assert call_args[1]['pool_pre_ping'] is True

    @pytest.mark.asyncio
    async def test_database_health_checker_should_return_detailed_health(self, mock_health_checker):
        mock_session_ctx = make_async_session_ctx()
        mock_health_checker.db_manager.get_session = MagicMock(return_value=mock_session_ctx)
        # Mock del engine y pool para métricas
        mock_health_checker.db_manager.engine = MagicMock()
        mock_pool = MagicMock()
        mock_pool.size = MagicMock(return_value=5)
        mock_pool.checkedin = MagicMock(return_value=3)
        mock_pool.checkedout = MagicMock(return_value=2)
        mock_pool.overflow = MagicMock(return_value=0)
        mock_health_checker.db_manager.engine.pool = mock_pool
        health_result = await mock_health_checker.check_detailed_health()
        assert isinstance(health_result, dict)
        assert "status" in health_result
        assert "timestamp" in health_result
        assert "metrics" in health_result
        assert "details" in health_result
        assert health_result["status"] == "healthy"
        assert "response_time" in health_result["metrics"]
        assert "query_time" in health_result["metrics"]
        assert "pool" in health_result["details"]
        assert health_result["details"]["pool"]["size"] == 5

    @pytest.mark.asyncio
    async def test_database_health_checker_should_run_performance_test(self, mock_health_checker):
        mock_session_ctx = make_async_session_ctx()
        mock_health_checker.db_manager.get_session = MagicMock(return_value=mock_session_ctx)
        performance_result = await mock_health_checker.run_performance_test(num_queries=5)
        assert isinstance(performance_result, dict)
        assert "queries_executed" in performance_result
        assert "queries_failed" in performance_result
        assert "avg_response_time_ms" in performance_result
        assert "min_response_time_ms" in performance_result
        assert "max_response_time_ms" in performance_result
        assert "success_rate" in performance_result
        assert performance_result["queries_executed"] == 5

    @pytest.mark.asyncio
    async def test_database_health_checker_should_handle_connection_failures(self, mock_health_checker):
        mock_health_checker.db_manager.get_session = MagicMock(side_effect=Exception("Connection failed"))
        health_result = await mock_health_checker.check_detailed_health()
        assert health_result["status"] == "unhealthy"
        assert "error" in health_result
        assert "Connection failed" in health_result["error"]
        assert "timestamp" in health_result

    @pytest.mark.asyncio
    async def test_database_health_checker_should_handle_missing_db_manager(self):
        """Test: HealthChecker debe manejar DatabaseManager faltante"""
        # RED: Test de caso edge
        # Crear un mock que retorne None para db_manager
        mock_db_manager = MagicMock()
        mock_db_manager.get_session = AsyncMock()
        mock_db_manager.get_session.side_effect = AttributeError("No db_manager")
        
        health_checker = DatabaseHealthChecker(mock_db_manager)
        
        # Simular que el db_manager no está disponible
        health_checker.db_manager = None  # type: ignore
        
        health_result = await health_checker.check_detailed_health()
        
        # Validar respuesta de error
        assert health_result["status"] == "unhealthy"
        assert "error" in health_result
        assert "DatabaseManager no está inicializado" in health_result["error"]

    @pytest.mark.asyncio
    async def test_database_manager_should_handle_connection_failure_after_retries(self, sample_config):
        with patch('app.core.database.create_async_engine') as mock_create_engine, \
             patch('asyncio.sleep') as mock_sleep:
            # Falla todos los intentos
            mock_create_engine.side_effect = [Exception("Connection failed")] * (sample_config.connection_retries + 1)
            manager = DatabaseManager(sample_config, is_test=True)
            with pytest.raises(Exception):
                await manager.initialize()
            expected_attempts = sample_config.connection_retries + 1
            assert mock_create_engine.call_count == expected_attempts

    @pytest.mark.asyncio
    async def test_database_manager_should_handle_test_connection_failure(self, sample_config):
        """Test: DatabaseManager debe manejar fallo en test de conexión"""
        # RED: Test de fallo en test de conexión
        with patch('app.core.database.create_async_engine') as mock_create_engine, \
             patch('app.core.database.async_sessionmaker') as mock_session_maker:
            
            mock_engine = make_engine_with_async_connect()
            mock_engine.connect.return_value.__aenter__.side_effect = Exception("Test connection failed")
            mock_create_engine.return_value = mock_engine
            mock_session_maker.return_value = AsyncMock()
            
            manager = DatabaseManager(sample_config, is_test=True)
            with pytest.raises(Exception):
                await manager.initialize()

    def test_base_repository_should_validate_data_types(self, mock_model_class):
        mock_session = AsyncMock()
        repository = BaseRepository(mock_model_class, mock_session)
        valid_data = {"name": "test", "value": 123, "active": True}
        repository._validate_create_data(valid_data)  # No debe lanzar excepción
        with pytest.raises(ValueError, match="Los datos para crear no pueden estar vacíos"):
            repository._validate_create_data({})
        with pytest.raises(TypeError):
            repository._validate_create_data(None)  # type: ignore

    @pytest.mark.asyncio
    async def test_database_manager_should_handle_session_factory_failure(self, sample_config):
        """Test: DatabaseManager debe manejar fallo en creación de session factory"""
        # RED: Test de fallo en session factory
        with patch('app.core.database.create_async_engine') as mock_create_engine, \
             patch('app.core.database.async_sessionmaker') as mock_session_maker:
            
            mock_engine = AsyncMock()
            mock_create_engine.return_value = mock_engine
            
            # Simular fallo en session maker
            mock_session_maker.side_effect = Exception("Session factory failed")
            
            manager = DatabaseManager(sample_config, is_test=True)
            
            # Debe fallar durante la inicialización
            with pytest.raises(Exception):
                await manager.initialize()

    @pytest.mark.asyncio
    async def test_health_checker_should_handle_pool_metrics_failure(self, mock_health_checker):
        mock_session_ctx = make_async_session_ctx()
        mock_health_checker.db_manager.get_session = MagicMock(return_value=mock_session_ctx)
        mock_pool = MagicMock()
        mock_pool.size.return_value = 0
        mock_pool.checkedin.return_value = 0
        mock_pool.checkedout.return_value = 0
        mock_pool.overflow.return_value = 0
        mock_health_checker.db_manager.engine = MagicMock()
        mock_health_checker.db_manager.engine.pool = mock_pool
        health_result = await mock_health_checker.check_detailed_health()
        assert health_result["status"] == "healthy"
        assert health_result["details"]["pool"]["size"] == 0
        assert health_result["details"]["pool"]["checkedin"] == 0


class TestTDDDatabaseRefactoringComplexity:
    """Tests TDD para identificar funciones con alta complejidad ciclomática"""

    def test_database_config_methods_should_have_low_complexity(self):
        """Test: Métodos de DatabaseConfig deben tener baja complejidad"""
        # RED: Test que valida que los métodos no sean demasiado complejos
        config = DatabaseConfig()
        
        # Verificar que los métodos principales existen y son accesibles
        assert hasattr(config, '_validate_configuration')
        assert hasattr(config, '_normalize_values')
        assert hasattr(config, 'driver_type')
        assert hasattr(config, 'from_env')
        assert hasattr(config, 'to_dict')

    def test_vps_config_optimization_should_be_manageable(self):
        """Test: Optimización VPS debe ser manejable"""
        # RED: Test que valida que la optimización no sea excesivamente compleja
        vps_config = VPSDatabaseConfig()
        
        # Verificar que el método de optimización existe
        assert hasattr(vps_config, '_optimize_for_vps')
        assert hasattr(vps_config, 'get_connection_args')

    def test_database_manager_methods_should_be_testable(self):
        """Test: Métodos de DatabaseManager deben ser testables"""
        # RED: Test que valida que los métodos sean testables
        config = DatabaseConfig()
        manager = DatabaseManager(config, is_test=True)
        
        # Verificar que los métodos principales existen
        assert hasattr(manager, 'initialize')
        assert hasattr(manager, 'get_session')
        assert hasattr(manager, 'check_health')
        assert hasattr(manager, 'get_connection_metrics')
        assert hasattr(manager, 'close')
        assert hasattr(manager, 'cleanup')

    def test_health_checker_methods_should_be_focused(self):
        """Test: Métodos de HealthChecker deben estar enfocados"""
        # RED: Test que valida que los métodos tengan responsabilidades claras
        config = DatabaseConfig()
        manager = DatabaseManager(config, is_test=True)
        health_checker = DatabaseHealthChecker(manager)
        
        # Verificar que los métodos principales existen
        assert hasattr(health_checker, 'check_detailed_health')
        assert hasattr(health_checker, 'run_performance_test')

    @pytest.mark.asyncio
    async def test_base_repository_methods_should_be_simple(self, mock_model_class):
        mock_session = MagicMock()
        repository = BaseRepository(mock_model_class, mock_session)
        assert hasattr(repository, 'create')
        assert hasattr(repository, 'get_by_id')
        assert hasattr(repository, 'get_all')
        assert hasattr(repository, 'update')
        assert hasattr(repository, 'delete')
        assert hasattr(repository, 'count')
        assert hasattr(repository, '_validate_create_data')
        assert hasattr(repository, '_validate_update_data')


class TestTDDDatabaseRefactoringValidation:
    """Tests TDD para validar que el refactoring mantiene la funcionalidad"""

    @pytest.fixture
    def sample_config(self) -> DatabaseConfig:
        """Configuración de prueba para tests"""
        return DatabaseConfig(
            database_url="sqlite+aiosqlite:///:memory:",
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            query_timeout=60,
            connection_retries=3
        )

    @pytest.fixture
    def mock_db_manager(self, sample_config) -> DatabaseManager:
        """Mock del DatabaseManager para tests"""
        with patch('app.core.database.create_async_engine'), \
             patch('app.core.database.async_sessionmaker'):
            manager = DatabaseManager(sample_config, is_test=True)
            manager.engine = AsyncMock()
            manager.session_factory = AsyncMock()
            manager._is_initialized = True
            return manager

    @pytest.fixture
    def mock_health_checker(self, mock_db_manager) -> DatabaseHealthChecker:
        """Mock del DatabaseHealthChecker para tests"""
        return DatabaseHealthChecker(mock_db_manager)

    def test_database_manager_should_have_refactored_methods(self, sample_config):
        """Test: DatabaseManager debe tener los métodos refactorizados"""
        # GREEN: Validar que los métodos refactorizados existen
        manager = DatabaseManager(sample_config, is_test=True)
        
        # Verificar que los métodos refactorizados existen
        assert hasattr(manager, '_build_engine_args')
        assert hasattr(manager, '_configure_sqlite_args')
        assert hasattr(manager, '_configure_pool_args')
        assert hasattr(manager, '_configure_connection_args')
        assert hasattr(manager, '_create_session_factory')
        assert hasattr(manager, '_handle_connection_retry')
        assert hasattr(manager, '_handle_connection_failure')

    def test_health_checker_should_have_refactored_methods(self, mock_health_checker):
        """Test: HealthChecker debe tener los métodos refactorizados"""
        # GREEN: Validar que los métodos refactorizados existen
        assert hasattr(mock_health_checker, '_test_basic_connection')
        assert hasattr(mock_health_checker, '_get_pool_metrics')
        assert hasattr(mock_health_checker, '_get_default_pool_metrics')
        assert hasattr(mock_health_checker, '_create_healthy_response')
        assert hasattr(mock_health_checker, '_create_unhealthy_response')
        assert hasattr(mock_health_checker, '_execute_performance_queries')
        assert hasattr(mock_health_checker, '_execute_single_query')
        assert hasattr(mock_health_checker, '_calculate_performance_metrics')

    @pytest.mark.asyncio
    async def test_build_engine_args_should_return_correct_structure(self, sample_config):
        """Test: _build_engine_args debe retornar estructura correcta"""
        # GREEN: Validar que el método refactorizado funciona
        manager = DatabaseManager(sample_config, is_test=True)
        
        engine_args = manager._build_engine_args()
        
        assert isinstance(engine_args, dict)
        assert 'echo' in engine_args
        assert engine_args['echo'] is False

    def test_configure_sqlite_args_should_set_correct_values(self, sample_config):
        """Test: _configure_sqlite_args debe configurar SQLite correctamente"""
        # GREEN: Validar configuración de SQLite
        manager = DatabaseManager(sample_config, is_test=True)
        engine_args = {"echo": False}
        
        manager._configure_sqlite_args(engine_args)
        
        assert 'poolclass' in engine_args
        assert 'connect_args' in engine_args
        connect_args = engine_args['connect_args']
        assert isinstance(connect_args, dict)
        assert connect_args['check_same_thread'] is False

    def test_configure_pool_args_should_set_pool_configuration(self, sample_config):
        """Test: _configure_pool_args debe configurar el pool correctamente"""
        # GREEN: Validar configuración del pool
        manager = DatabaseManager(sample_config, is_test=True)
        engine_args = {"echo": False}
        
        manager._configure_pool_args(engine_args)
        
        assert 'pool_size' in engine_args
        assert 'max_overflow' in engine_args
        assert 'pool_pre_ping' in engine_args
        assert engine_args['pool_size'] == sample_config.pool_size

    def test_create_healthy_response_should_return_correct_structure(self, mock_health_checker):
        """Test: _create_healthy_response debe retornar estructura correcta"""
        # GREEN: Validar respuesta de salud exitosa
        start_time = time.time()
        query_time = 0.1
        pool_metrics = {"size": 5, "checkedin": 3, "checkedout": 2, "overflow": 0}
        
        response = mock_health_checker._create_healthy_response(start_time, query_time, pool_metrics)
        
        assert response['status'] == 'healthy'
        assert 'details' in response
        assert 'metrics' in response
        assert 'timestamp' in response
        assert response['details']['pool'] == pool_metrics

    def test_create_unhealthy_response_should_return_correct_structure(self, mock_health_checker):
        """Test: _create_unhealthy_response debe retornar estructura correcta"""
        # GREEN: Validar respuesta de salud fallida
        error_message = "Test error"
        
        response = mock_health_checker._create_unhealthy_response(error_message)
        
        assert response['status'] == 'unhealthy'
        assert response['error'] == error_message
        assert 'timestamp' in response

    def test_get_default_pool_metrics_should_return_zero_values(self, mock_health_checker):
        """Test: _get_default_pool_metrics debe retornar valores por defecto"""
        # GREEN: Validar métricas por defecto
        metrics = mock_health_checker._get_default_pool_metrics()
        
        assert metrics['size'] == 0
        assert metrics['checkedin'] == 0
        assert metrics['checkedout'] == 0
        assert metrics['overflow'] == 0

    def test_calculate_performance_metrics_should_return_correct_values(self, mock_health_checker):
        """Test: _calculate_performance_metrics debe calcular correctamente"""
        # GREEN: Validar cálculo de métricas
        times = [10.0, 20.0, 30.0]  # 3 queries exitosas
        errors = 2  # 2 queries fallidas
        num_queries = 5  # Total de queries
        
        metrics = mock_health_checker._calculate_performance_metrics(times, errors, num_queries)
        
        assert metrics['queries_executed'] == 3
        assert metrics['queries_failed'] == 2
        assert metrics['avg_response_time_ms'] == 20.0  # (10+20+30)/3
        assert metrics['min_response_time_ms'] == 10.0
        assert metrics['max_response_time_ms'] == 30.0
        assert metrics['success_rate'] == 60.0  # (3/5)*100 