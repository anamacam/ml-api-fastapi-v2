# 🗄️ DATABASE MODULE - TDD CICLO 6 [REFACTORED]

## 📋 Resumen

Módulo enterprise de base de datos desarrollado siguiendo metodología TDD (Test-Driven Development) con 22 pruebas unitarias (100% de cobertura). Proporciona una abstracción robusta y escalable para operaciones de base de datos con soporte async/await.

## 🎯 Características Principales

### ✅ **Configuración Enterprise**
- Configuración flexible por variables de entorno
- Validación automática de parámetros
- Soporte para múltiples drivers (SQLite, PostgreSQL, MySQL)
- Optimizaciones automáticas por entorno (dev/prod)

### ✅ **Gestión de Conexiones Avanzada**
- Pool de conexiones optimizado (QueuePool/StaticPool)
- Retry logic con exponential backoff
- Health checks automáticos
- Manejo robusto de errores y timeouts

### ✅ **Repository Pattern Type-Safe**
- CRUD operations genéricas para cualquier modelo
- Validación de datos automática
- Logging detallado de operaciones
- Paginación optimizada

### ✅ **Monitoreo y Health Checks**
- Health checks detallados con métricas
- Tests de rendimiento integrados
- Alertas por tiempo de respuesta
- Información detallada del engine

### ✅ **Integración FastAPI**
- Dependency injection compatible
- Context managers async/await
- Manejo de transacciones automático
- Funciones de conveniencia incluidas

## 🚀 Guía de Uso Rápido

### 1. Configuración Básica

```python
from app.core.database import DatabaseConfig, init_database

# Configuración desde variables de entorno
config = DatabaseConfig.from_env()

# O configuración manual
config = DatabaseConfig(
    database_url="postgresql+asyncpg://user:pass@localhost/db",
    pool_size=10,
    max_overflow=20
)

# Inicializar sistema
await init_database(config)
```

### 2. Uso con FastAPI

```python
from fastapi import FastAPI, Depends
from app.core.database import get_async_session, get_db_health
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

@app.get("/health/db")
async def database_health():
    return await get_db_health()

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_async_session)):
    # Tu lógica aquí
    pass
```

### 3. Repository Pattern

```python
from app.core.database import BaseRepository, get_async_session
from app.models.user import User

# Usar repository genérico
async with get_async_session() as session:
    user_repo = BaseRepository(User, session)
    
    # Operaciones CRUD
    user = await user_repo.create({"name": "Juan", "email": "juan@example.com"})
    users = await user_repo.get_all(skip=0, limit=10)
    updated = await user_repo.update(user.id, {"name": "Juan Carlos"})
    deleted = await user_repo.delete(user.id)
    count = await user_repo.count()
```

### 4. Repository Personalizado

```python
from app.core.database import BaseRepository

class UserRepository(BaseRepository[User]):
    def _validate_create_data(self, data: Dict[str, Any]) -> None:
        super()._validate_create_data(data)
        if "@" not in data.get("email", ""):
            raise ValueError("Email inválido")
    
    async def get_by_email(self, email: str) -> Optional[User]:
        from sqlalchemy import select
        stmt = select(self.model).where(self.model.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
```

### 5. Health Checks Avanzados

```python
from app.core.database import DatabaseHealthChecker, get_database_manager

# Health check básico
manager = get_database_manager()
is_healthy = await manager.check_health()

# Health check detallado
health_checker = DatabaseHealthChecker(manager)
status = await health_checker.check_detailed_health()

# Test de rendimiento
performance = await health_checker.run_performance_test(num_queries=20)
```

## 🔧 Variables de Entorno

```bash
# Configuración de base de datos
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/mydb
DB_ECHO=false
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_QUERY_TIMEOUT=60
DB_CONNECTION_RETRIES=3

# Entorno (afecta optimizaciones automáticas)
ENVIRONMENT=production
```

## 📊 Estructura del Módulo

```
app/core/database.py
├── DatabaseConfig          # Configuración validada
├── DatabaseManager         # Gestor de conexiones
├── BaseRepository          # Repository pattern genérico
├── DatabaseHealthChecker   # Health checks y monitoreo
├── DatabaseDriver (Enum)   # Drivers soportados
├── HealthStatus (Enum)     # Estados de salud
└── Funciones de utilidad:
    ├── init_database()
    ├── close_database()
    ├── get_async_session()
    ├── get_db_health()
    └── create_repository()
```

## 🧪 Testing

El módulo incluye 22 pruebas completas:

```bash
# Ejecutar todas las pruebas
pytest tests/test_database_module.py -v

# Pruebas específicas
pytest tests/test_database_module.py::TestDatabaseConfig -v
pytest tests/test_database_module.py::TestDatabaseManager -v
pytest tests/test_database_module.py::TestBaseRepository -v
pytest tests/test_database_module.py::TestDatabaseHealthChecker -v
pytest tests/test_database_module.py::TestDatabaseIntegration -v
```

### Cobertura de Pruebas:
- ✅ **TestDatabaseConfig**: 4/4 pruebas (Configuración)
- ✅ **TestDatabaseManager**: 6/6 pruebas (Gestión de conexiones)
- ✅ **TestBaseRepository**: 6/6 pruebas (Repository pattern)
- ✅ **TestDatabaseHealthChecker**: 3/3 pruebas (Health checks)
- ✅ **TestDatabaseIntegration**: 3/3 pruebas (Integración completa)

## 🎯 Mejores Prácticas

### ✅ **DO - Hacer**
```python
# Usar async context managers
async with get_async_session() as session:
    # Operaciones de DB aquí
    pass

# Manejar errores específicos
try:
    await repo.create(data)
except ValueError as e:
    # Manejar error de validación
except SQLAlchemyError as e:
    # Manejar error de DB
```

### ❌ **DON'T - No hacer**
```python
# NO crear sesiones sin context manager
session = await get_async_session()  # ❌

# NO ignorar validaciones
await repo.create({})  # ❌ Datos vacíos

# NO usar queries síncronas en contexto async
session.execute(text("SELECT 1"))  # ❌ Falta await
```

## 🔐 Características de Seguridad

- **Validación de inputs**: Todos los datos son validados antes de llegar a la DB
- **SQL Injection protection**: Uso de SQLAlchemy ORM y parámetros bind
- **Connection pooling**: Límites de conexiones para evitar ataques DoS
- **Timeouts**: Protección contra queries que se cuelgan
- **Logging**: Auditoría completa de operaciones

## 📈 Métricas y Monitoreo

### Health Check Response:
```json
{
  "status": "healthy",
  "database_responsive": true,
  "query_test": true,
  "response_time_ms": 45.23,
  "timestamp": 1703123456.789,
  "checks_performed": ["basic_connection", "simple_query", "engine_info"],
  "engine_info": {
    "driver": "postgresql",
    "pool_class": "QueuePool",
    "pool_size": 10,
    "checked_in": 8,
    "checked_out": 2,
    "overflow": 0
  }
}
```

### Performance Test Response:
```json
{
  "queries_executed": 20,
  "queries_failed": 0,
  "avg_response_time_ms": 15.45,
  "min_response_time_ms": 12.1,
  "max_response_time_ms": 23.8,
  "success_rate": 100.0
}
```

## 🚀 Escalabilidad

El módulo está diseñado para escalar desde aplicaciones pequeñas hasta sistemas enterprise:

- **Desarrollo**: SQLite en memoria para pruebas rápidas
- **Staging**: PostgreSQL con pool pequeño
- **Producción**: PostgreSQL/MySQL con pool optimizado y monitoreo

## 📝 Changelog

### v2.0.0 (REFACTORED) - TDD CICLO 6
- ✅ 22 pruebas unitarias (100% cobertura)
- ✅ Logging y monitoreo integrado
- ✅ Retry logic con exponential backoff
- ✅ Health checks avanzados con métricas
- ✅ Validaciones de seguridad mejoradas
- ✅ Repository pattern type-safe
- ✅ Documentación completa
- ✅ Optimizaciones de rendimiento

### v1.0.0 (GREEN) - Implementación inicial
- ✅ Funcionalidad básica implementada
- ✅ Pruebas pasando
- ✅ Configuración flexible

---

## 🎯 **Desarrollado con TDD (Test-Driven Development)**

Este módulo fue desarrollado siguiendo estrictamente la metodología TDD:

1. **🔴 RED**: Escribir pruebas que fallan
2. **🟢 GREEN**: Implementar código mínimo para pasar pruebas
3. **🔵 REFACTOR**: Mejorar y optimizar manteniendo pruebas pasando

**Resultado: 22/22 pruebas pasando (100% éxito) - Código robusto y confiable** 