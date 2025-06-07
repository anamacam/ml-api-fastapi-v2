#!/usr/bin/env python3
"""
✅ TDD Setup - ML API FastAPI v2
Script para configurar Test-Driven Development en el proyecto.

Este script automatiza la configuración de TDD y genera estructuras
de tests siguiendo las mejores prácticas.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
import subprocess
import argparse
from dataclasses import dataclass


@dataclass
class TestStructure:
    """Define la estructura de tests a crear."""
    path: str
    test_type: str
    description: str
    dependencies: List[str]


class TDDSetup:
    """Configurador de Test-Driven Development."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.test_structures = [
            TestStructure(
                path="backend/tests/unit",
                test_type="unit",
                description="Tests unitarios para lógica de negocio",
                dependencies=["pytest", "pytest-asyncio", "pytest-mock"]
            ),
            TestStructure(
                path="backend/tests/integration", 
                test_type="integration",
                description="Tests de integración con DB y APIs",
                dependencies=["pytest", "httpx", "pytest-postgresql"]
            ),
            TestStructure(
                path="backend/tests/e2e",
                test_type="e2e", 
                description="Tests end-to-end del flujo completo",
                dependencies=["pytest", "selenium", "requests"]
            ),
            TestStructure(
                path="frontend/web-app/src/__tests__",
                test_type="frontend_unit",
                description="Tests unitarios de componentes React",
                dependencies=["@testing-library/react", "jest", "vitest"]
            ),
            TestStructure(
                path="frontend/web-app/src/e2e",
                test_type="frontend_e2e",
                description="Tests E2E del frontend con Playwright",
                dependencies=["@playwright/test"]
            )
        ]
    
    def setup_tdd_environment(self) -> None:
        """Configurar ambiente completo de TDD."""
        print("🚀 Configurando ambiente TDD para ML API FastAPI v2")
        print("=" * 60)
        
        # 1. Crear estructura de directorios
        self._create_test_directories()
        
        # 2. Configurar pytest
        self._setup_pytest()
        
        # 3. Crear tests de ejemplo
        self._create_example_tests()
        
        # 4. Configurar coverage
        self._setup_coverage()
        
        # 5. Configurar CI/CD para tests
        self._setup_github_actions()
        
        # 6. Crear documentación TDD
        self._create_tdd_documentation()
        
        print("\n✅ TDD configurado exitosamente!")
        print("💡 Próximos pasos:")
        print("   1. cd backend && pytest")
        print("   2. cd frontend/web-app && npm test")
        print("   3. Seguir el ciclo Red-Green-Refactor")
    
    def _create_test_directories(self) -> None:
        """Crear estructura de directorios para tests."""
        print("📁 Creando estructura de tests...")
        
        for structure in self.test_structures:
            test_dir = self.project_root / structure.path
            test_dir.mkdir(parents=True, exist_ok=True)
            
            # Crear __init__.py para directorios Python
            if "backend" in structure.path:
                (test_dir / "__init__.py").touch()
            
            print(f"   ✅ {structure.path} ({structure.description})")
    
    def _setup_pytest(self) -> None:
        """Configurar pytest con todas las opciones."""
        print("🔧 Configurando pytest...")
        
        pytest_ini_content = """[tool:pytest]
# Configuración pytest para ML API FastAPI v2
minversion = 6.0
addopts = 
    -ra
    --strict-markers
    --strict-config
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=80
    --tb=short
    --maxfail=1
    -v

testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

markers =
    unit: tests unitarios rápidos
    integration: tests de integración con BD/APIs
    e2e: tests end-to-end completos
    slow: tests que toman más tiempo
    ml: tests específicos de modelos ML
    api: tests de endpoints API
    db: tests que requieren base de datos
    redis: tests que requieren Redis
    
filterwarnings =
    ignore::UserWarning
    ignore::DeprecationWarning
"""
        
        pytest_file = self.project_root / "backend" / "pytest.ini"
        with open(pytest_file, 'w', encoding='utf-8') as f:
            f.write(pytest_ini_content)
        
        print("   ✅ pytest.ini configurado")
    
    def _create_example_tests(self) -> None:
        """Crear tests de ejemplo siguiendo TDD."""
        print("📝 Creando tests de ejemplo...")
        
        # Test unitario de ejemplo
        unit_test_content = '''"""
✅ Tests Unitarios - Ejemplo TDD
Tests para funciones de utilidad y lógica de negocio.
"""
import pytest
from unittest.mock import Mock, patch
from app.utils.validators import validate_email
from app.models.schemas import ModelCreateRequest


class TestValidators:
    """Tests para validadores."""
    
    def test_validate_email_valid(self):
        """Test: Email válido debe retornar True."""
        # Arrange
        valid_email = "test@example.com"
        
        # Act
        result = validate_email(valid_email)
        
        # Assert
        assert result is True
    
    def test_validate_email_invalid(self):
        """Test: Email inválido debe retornar False."""
        # Arrange
        invalid_email = "invalid-email"
        
        # Act
        result = validate_email(invalid_email)
        
        # Assert
        assert result is False


class TestModelSchemas:
    """Tests para schemas de modelos."""
    
    def test_model_create_request_valid(self):
        """Test: Request válido debe crear schema correctamente."""
        # Arrange
        valid_data = {
            "name": "test_model",
            "type": "sklearn",
            "description": "Modelo de prueba"
        }
        
        # Act
        schema = ModelCreateRequest(**valid_data)
        
        # Assert
        assert schema.name == "test_model"
        assert schema.type == "sklearn"
        assert schema.description == "Modelo de prueba"
    
    def test_model_create_request_invalid_name(self):
        """Test: Nombre vacío debe fallar validación."""
        # Arrange
        invalid_data = {
            "name": "",
            "type": "sklearn"
        }
        
        # Act & Assert
        with pytest.raises(ValueError):
            ModelCreateRequest(**invalid_data)


@pytest.mark.ml
class TestMLModels:
    """Tests específicos para modelos ML."""
    
    @patch('joblib.load')
    def test_load_model_success(self, mock_joblib_load):
        """Test: Cargar modelo debe retornar objeto correcto."""
        # Arrange
        mock_model = Mock()
        mock_joblib_load.return_value = mock_model
        
        # Act
        from app.services.model_service import load_model
        result = load_model("test_model.joblib")
        
        # Assert
        assert result == mock_model
        mock_joblib_load.assert_called_once_with("test_model.joblib")
'''
        
        unit_test_file = self.project_root / "backend/tests/unit/test_example.py"
        with open(unit_test_file, 'w', encoding='utf-8') as f:
            f.write(unit_test_content)
        
        # Test de integración de ejemplo
        integration_test_content = '''"""
🔗 Tests de Integración - Ejemplo TDD
Tests para endpoints API y base de datos.
"""
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Configuración de BD de test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dependencia de BD para tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.mark.integration
class TestHealthEndpoints:
    """Tests de integración para endpoints de salud."""
    
    def test_health_check_basic(self):
        """Test: Health check básico debe retornar 200."""
        # Act
        response = client.get("/health")
        
        # Assert
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"
    
    def test_health_check_detailed(self):
        """Test: Health check detallado debe incluir servicios."""
        # Act
        response = client.get("/health/detailed")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "database" in data
        assert "redis" in data
        assert "timestamp" in data


@pytest.mark.integration
@pytest.mark.api
class TestModelEndpoints:
    """Tests de integración para endpoints de modelos."""
    
    def test_list_models_empty(self):
        """Test: Lista de modelos vacía debe retornar array vacío."""
        # Act
        response = client.get("/api/v1/models/")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_model_valid(self):
        """Test: Crear modelo válido debe retornar 201."""
        # Arrange
        model_data = {
            "name": "test_model",
            "type": "sklearn",
            "description": "Modelo de prueba"
        }
        
        # Act
        response = client.post("/api/v1/models/", json=model_data)
        
        # Assert
        assert response.status_code == 201
        created_model = response.json()
        assert created_model["name"] == "test_model"
        assert created_model["type"] == "sklearn"
    
    def test_create_model_invalid(self):
        """Test: Crear modelo inválido debe retornar 422."""
        # Arrange
        invalid_data = {
            "name": "",  # Nombre vacío inválido
            "type": "sklearn"
        }
        
        # Act
        response = client.post("/api/v1/models/", json=invalid_data)
        
        # Assert
        assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.db
class TestDatabaseOperations:
    """Tests de integración con base de datos."""
    
    def test_model_crud_operations(self):
        """Test: Operaciones CRUD completas de modelo."""
        # Create
        model_data = {
            "name": "crud_test_model",
            "type": "tensorflow",
            "description": "Test CRUD"
        }
        
        create_response = client.post("/api/v1/models/", json=model_data)
        assert create_response.status_code == 201
        
        model_id = create_response.json()["id"]
        
        # Read
        read_response = client.get(f"/api/v1/models/{model_id}")
        assert read_response.status_code == 200
        assert read_response.json()["name"] == "crud_test_model"
        
        # Update
        update_data = {"description": "Updated description"}
        update_response = client.put(f"/api/v1/models/{model_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["description"] == "Updated description"
        
        # Delete
        delete_response = client.delete(f"/api/v1/models/{model_id}")
        assert delete_response.status_code == 200
        
        # Verify deletion
        verify_response = client.get(f"/api/v1/models/{model_id}")
        assert verify_response.status_code == 404
'''
        
        integration_test_file = self.project_root / "backend/tests/integration/test_api.py"
        with open(integration_test_file, 'w', encoding='utf-8') as f:
            f.write(integration_test_content)
        
        print("   ✅ Tests de ejemplo creados")
    
    def _setup_coverage(self) -> None:
        """Configurar coverage para medir cobertura de tests."""
        print("📊 Configurando coverage...")
        
        coverage_config = """[run]
source = app
omit = 
    */venv/*
    */tests/*
    */__pycache__/*
    */migrations/*
    */alembic/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\\bProtocol\\):
    @(abc\\.)?abstractmethod

[html]
directory = htmlcov

[xml]
output = coverage.xml
"""
        
        coverage_file = self.project_root / "backend" / ".coveragerc"
        with open(coverage_file, 'w', encoding='utf-8') as f:
            f.write(coverage_config)
        
        print("   ✅ Coverage configurado")
    
    def _setup_github_actions(self) -> None:
        """Configurar GitHub Actions para CI/CD de tests."""
        print("🔄 Configurando GitHub Actions...")
        
        github_workflow = """name: 🧪 Tests & Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements/base.txt') }}
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements/base.txt
        pip install pytest pytest-cov pytest-asyncio
    
    - name: Run tests with coverage
      run: |
        cd backend
        pytest --cov=app --cov-report=xml --cov-report=term-missing
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: backend/coverage.xml
        flags: backend
        name: backend-coverage

  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/web-app/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend/web-app
        npm ci
    
    - name: Run tests
      run: |
        cd frontend/web-app
        npm test -- --coverage --watchAll=false
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: frontend/web-app/coverage/lcov.info
        flags: frontend
        name: frontend-coverage

  quality-checks:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Run tech debt analyzer
      run: |
        python infrastructure/scripts/tech_debt_analyzer.py --format json
    
    - name: Check critical issues
      run: |
        critical=$(jq '.summary.by_severity.critical // 0' tech_debt_report.json)
        if [ "$critical" -gt 0 ]; then
          echo "❌ $critical critical issues found"
          exit 1
        fi
        echo "✅ No critical issues"
"""
        
        github_dir = self.project_root / ".github/workflows"
        github_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_file = github_dir / "tests.yml"
        with open(workflow_file, 'w', encoding='utf-8') as f:
            f.write(github_workflow)
        
        print("   ✅ GitHub Actions configurado")
    
    def _create_tdd_documentation(self) -> None:
        """Crear documentación completa de TDD."""
        print("📚 Creando documentación TDD...")
        
        tdd_doc = """# 🧪 Test-Driven Development (TDD) Guide

## 🎯 Filosofía TDD

**Red → Green → Refactor**

1. 🔴 **RED**: Escribir test que falle
2. 🟢 **GREEN**: Escribir código mínimo para pasar
3. 🔵 **REFACTOR**: Mejorar código manteniendo tests

## 📁 Estructura de Tests

```
backend/tests/
├── unit/           # Tests unitarios (lógica de negocio)
├── integration/    # Tests de integración (API + BD)
└── e2e/           # Tests end-to-end (flujo completo)

frontend/web-app/src/
├── __tests__/     # Tests unitarios de componentes
└── e2e/          # Tests E2E con Playwright
```

## 🏃‍♂️ Comandos Esenciales

### Backend (Python)
```bash
# Ejecutar todos los tests
cd backend && pytest

# Tests con coverage
pytest --cov=app --cov-report=html

# Solo tests unitarios
pytest tests/unit/ -m unit

# Solo tests de integración
pytest tests/integration/ -m integration

# Tests específicos
pytest tests/unit/test_models.py::TestModelCreation

# Watch mode (con pytest-watch)
ptw tests/
```

### Frontend (React)
```bash
# Ejecutar tests
cd frontend/web-app && npm test

# Tests con coverage
npm test -- --coverage

# Watch mode
npm test -- --watch

# E2E tests
npx playwright test
```

## 📋 Convenciones de Naming

### Tests Python
```python
# Archivo: test_nombre_modulo.py
class TestNombreClase:
    def test_funcion_condicion_resultado(self):
        \"\"\"Test: Descripción clara del comportamiento esperado.\"\"\"
        pass

# Ejemplos:
def test_validate_email_valid_email_returns_true(self):
def test_create_model_invalid_data_raises_validation_error(self):
def test_predict_model_not_found_returns_404(self):
```

### Tests React
```javascript
// Archivo: ComponentName.test.tsx
describe('ComponentName', () => {
  test('should render correctly with valid props', () => {
    // Test implementation
  });
  
  test('should handle click events properly', () => {
    // Test implementation
  });
});
```

## 🎨 Patterns TDD

### 1. Arrange-Act-Assert (AAA)
```python
def test_calculate_prediction_accuracy():
    # Arrange
    predictions = [0.8, 0.9, 0.7]
    actual = [1, 1, 0]
    
    # Act
    result = calculate_accuracy(predictions, actual)
    
    # Assert
    assert result == 0.67
```

### 2. Given-When-Then (BDD Style)
```python
def test_user_can_upload_model():
    # Given: Usuario autenticado y archivo válido
    user = create_authenticated_user()
    model_file = create_valid_model_file()
    
    # When: Usuario sube el archivo
    response = client.post("/upload", files={"file": model_file})
    
    # Then: Archivo se sube exitosamente
    assert response.status_code == 201
    assert "model_id" in response.json()
```

### 3. Test Doubles (Mocks, Stubs, Fakes)
```python
@patch('app.services.model_service.joblib.load')
def test_load_model_file_not_found(mock_load):
    # Arrange
    mock_load.side_effect = FileNotFoundError()
    
    # Act & Assert
    with pytest.raises(ModelNotFoundError):
        load_model("nonexistent.joblib")
```

## 🚀 Workflow TDD Típico

### 1. Nueva Feature: Endpoint de Predicción
```python
# 1. RED: Test que falla
def test_predict_endpoint_valid_input_returns_prediction():
    # Arrange
    model_data = {"features": [1, 2, 3, 4]}
    
    # Act
    response = client.post("/api/v1/predict", json=model_data)
    
    # Assert
    assert response.status_code == 200
    assert "prediction" in response.json()
    assert isinstance(response.json()["prediction"], float)

# 2. GREEN: Implementación mínima
@app.post("/api/v1/predict")
def predict(data: PredictRequest):
    return {"prediction": 0.5}  # Hardcoded para pasar test

# 3. REFACTOR: Implementación real
@app.post("/api/v1/predict")
def predict(data: PredictRequest):
    model = load_model("current_model.joblib")
    prediction = model.predict([data.features])
    return {"prediction": float(prediction[0])}
```

## 📊 Métricas de Calidad

### Objetivos de Coverage
- **Unitarios**: 90%+ coverage
- **Integración**: 80%+ coverage  
- **E2E**: Flujos críticos cubiertos

### Configuración pytest.ini
```ini
[tool:pytest]
addopts = --cov=app --cov-fail-under=80
markers =
    unit: tests unitarios
    integration: tests de integración
    e2e: tests end-to-end
    slow: tests lentos
```

## 🔧 Herramientas Esenciales

### Backend
- **pytest**: Framework de testing
- **pytest-cov**: Coverage reporting
- **pytest-asyncio**: Tests async
- **pytest-mock**: Mocking fácil
- **factory-boy**: Test data factories
- **freezegun**: Mock de tiempo

### Frontend  
- **Jest/Vitest**: Framework de testing
- **Testing Library**: Utils para React
- **Playwright**: E2E testing
- **MSW**: Mock de APIs

## 💡 Best Practices

### ✅ Hacer
- Escribir test ANTES del código
- Tests independientes y determinísticos
- Nombres descriptivos y claros
- Un assert por test (generalmente)
- Setup/teardown apropiado
- Mock dependencias externas

### ❌ Evitar
- Tests que dependen de otros tests
- Hardcodear valores en múltiples lugares
- Tests muy largos o complejos
- Ignorar tests que fallan
- 100% coverage como objetivo ciego

## 🎯 Próximos Pasos

1. **Ejecutar tests existentes**: `pytest backend/tests/`
2. **Escribir primer test**: Elegir una función simple
3. **Aplicar ciclo TDD**: Red → Green → Refactor
4. **Medir coverage**: Mantener >80%
5. **Integrar CI/CD**: Tests automáticos en cada commit

---

💡 **Recuerda**: TDD no es solo sobre testing, es sobre **diseño**. Los tests guían hacia código más limpio y mantenible.
"""
        
        tdd_doc_file = self.project_root / "TDD_GUIDE.md"
        with open(tdd_doc_file, 'w', encoding='utf-8') as f:
            f.write(tdd_doc)
        
        print("   ✅ Documentación TDD creada")
    
    def create_tdd_starter_kit(self) -> None:
        """Crear kit de inicio con templates y ejemplos."""
        print("🎁 Creando TDD Starter Kit...")
        
        # Test template
        test_template = '''"""
✅ Test Template - TDD
Plantilla para nuevos tests siguiendo convenciones.
"""
import pytest
from unittest.mock import Mock, patch
# Importar clases/funciones a testear


class TestNombreClase:
    """Tests para [describir qué se testea]."""
    
    def test_metodo_condicion_resultado(self):
        """Test: [Descripción clara del comportamiento esperado]."""
        # Arrange (Given)
        # Preparar datos y mocks
        
        # Act (When)  
        # Ejecutar código bajo test
        
        # Assert (Then)
        # Verificar resultado esperado
        pass
    
    @pytest.mark.unit
    def test_caso_unitario(self):
        """Test unitario aislado."""
        pass
    
    @pytest.mark.integration  
    def test_caso_integracion(self):
        """Test de integración con dependencias."""
        pass
    
    @pytest.mark.parametrize("input,expected", [
        ("caso1", "resultado1"),
        ("caso2", "resultado2"),
    ])
    def test_casos_parametrizados(self, input, expected):
        """Test con múltiples casos."""
        pass
'''
        
        template_file = self.project_root / "backend/tests/test_template.py"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(test_template)
        
        print("   ✅ Templates creados")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Configurar TDD en el proyecto")
    parser.add_argument('--full', action='store_true',
                       help='Configuración completa de TDD')
    parser.add_argument('--examples', action='store_true',
                       help='Solo crear ejemplos de tests')
    parser.add_argument('--docs', action='store_true',
                       help='Solo crear documentación')
    
    args = parser.parse_args()
    
    print("🧪 TDD Setup - ML API FastAPI v2")
    print("=" * 40)
    
    tdd_setup = TDDSetup()
    
    if args.full or not any([args.examples, args.docs]):
        tdd_setup.setup_tdd_environment()
    elif args.examples:
        tdd_setup._create_test_directories()
        tdd_setup._create_example_tests()
    elif args.docs:
        tdd_setup._create_tdd_documentation()
    
    tdd_setup.create_tdd_starter_kit()
    
    print(f"\n🎯 TDD configurado exitosamente!")
    print(f"📚 Lee TDD_GUIDE.md para empezar")
    print(f"🔴 Recuerda: Red → Green → Refactor")


if __name__ == "__main__":
    main()